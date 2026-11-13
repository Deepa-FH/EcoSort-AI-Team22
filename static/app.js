/* app.js - the Assistant page: photo upload / camera, result cards, AI review polling,
   chat, confidence threshold, optional public tunnel.
   Talks to the Flask API:  POST /api/analyze  GET /api/review/<id>  POST /api/chat  /api/tunnel/*  */
(() => {
  const { $, esc, toast, bootData } = window.EcoSort;
  const boot = bootData();
  const RULES = boot.rules || {};

  const conversation = $("#conversation");
  const fileInput = $("#file-input");
  const chatInput = $("#chat-input");
  const sendButton = $("#send-button");
  const slider = $("#threshold-slider");
  let threshold = clamp(Number(safeGet("ecosort-threshold")) || boot.threshold || 50);
  let currentContext = { imageName: "", prediction: "" };   // sent along with chat questions

  function clamp(v) { return Math.min(95, Math.max(10, Number(v))); }
  function safeGet(key) { try { return localStorage.getItem(key); } catch (_e) { return null; } }
  function safeSet(key, value) { try { localStorage.setItem(key, value); } catch (_e) { /* ignore */ } }
  const AVATAR = '<div class="avatar"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7.5 4.2A8.8 8.8 0 0 1 20 10.4c-3.9.4-7.3-.8-9.7-3.6-1.5 2.4-1.9 5.2-1.1 8.3"/><path d="M4.2 19.5c2.5-5.8 6.8-9.1 12.9-9.8"/></svg></div>';

  /* ---------------------------------------------------------------- panels (Assistant / Settings) */
  function showPanel(name) {
    $("#panel-home").classList.toggle("active", name === "home");
    $("#panel-settings").classList.toggle("active", name === "settings");
    document.querySelectorAll("[data-page]").forEach((item) => {
      if (item.dataset.page === "home" || item.dataset.page === "settings") item.classList.toggle("active", item.dataset.page === name);
    });
  }
  document.querySelectorAll('[data-page="home"], [data-page="settings"]').forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();                      // stay on the page: keeps the conversation
      const name = link.dataset.page;
      history.replaceState(null, "", name === "settings" ? "#settings" : location.pathname);
      showPanel(name);
    });
  });
  showPanel(location.hash === "#settings" ? "settings" : "home");

  /* ---------------------------------------------------------------- threshold slider */
  function setThreshold(value, announce = false) {
    threshold = clamp(value);
    safeSet("ecosort-threshold", String(threshold));
    slider.value = threshold;
    const pct = (threshold - 10) / 0.85;
    slider.style.background = `linear-gradient(90deg,var(--accent) ${pct}%,rgba(127,127,127,.25) ${pct}%)`;
    ["#threshold-output", "#local-value", "#ai-value"].forEach((sel) => { $(sel).textContent = `${threshold}%`; });
    if (announce) toast(`Confidence threshold saved at ${threshold}%`);
  }
  slider.addEventListener("input", () => setThreshold(slider.value));
  slider.addEventListener("change", () => setThreshold(slider.value, true));
  setThreshold(threshold);

  /* ---------------------------------------------------------------- chat bubbles */
  function scrollToLatest() {
    requestAnimationFrame(() => conversation.scrollTo({ top: conversation.scrollHeight, behavior: "smooth" }));
  }
  function addNode(html, cls = "message") {
    const node = document.createElement("div");
    node.className = cls;
    node.innerHTML = html;
    conversation.appendChild(node);
    scrollToLatest();
    return node;
  }
  const addUserImage = (url) => addNode(`<div class="bubble me"><img src="${esc(url)}" alt="Photo to identify"><span>Please identify this item.</span></div>`, "message user");
  const addUserText = (text) => addNode(`<div class="bubble me"><p>${esc(text)}</p></div>`, "message user");
  const addThinking = (label) => addNode(`${AVATAR}<div class="bubble thinking"><span>${esc(label)}</span><span class="dots"><i></i><i></i><i></i></span></div>`);
  const addError = (message) => addNode(`${AVATAR}<div class="bubble err"><p>${esc(message)}</p></div>`);
  const addAnswer = (text, source) => addNode(`${AVATAR}<div class="bubble wide"><span class="eyebrow">${source === "llm" ? "Ask AI" : "Local rules"}</span><p style="margin-top:6px">${esc(text)}</p></div>`);

  /* ---------------------------------------------------------------- bin visuals */
  function binFromAnswer(answer) {      // last-resort guess when the server found no matching rule
    const t = answer.toLowerCase();
    if (/yellow|gelbe|packaging/.test(t)) return { color: "Yellow", hex: "#F4C542", bin: "Yellow bin / deposit return" };
    if (/blue|papier|paper bin/.test(t)) return { color: "Blue", hex: "#3178C6", bin: "Blue paper bin" };
    if (/brown|biotonne|organic|bio bin/.test(t)) return { color: "Brown", hex: "#8B5E3C", bin: "Brown organic bin" };
    if (/glass container|altglas|green container|white container/.test(t)) return { color: "Glass", hex: "#4F8A67", bin: "Matching glass container" };
    if (/special|hazard|battery|collection point|schadstoff/.test(t)) return { color: "Special", hex: "#D94B4B", bin: "Special waste collection point" };
    if (/textile|clothing|altkleider/.test(t)) return { color: "Textile", hex: "#D9822B", bin: "Reuse or textile collection" };
    if (/residual|restmüll|general waste|grey|black bin/.test(t)) return { color: "Grey", hex: "#626A66", bin: "Residual waste bin" };
    return { color: "Check", hex: "#7160B7", bin: "Follow the Ask AI recommendation" };
  }
  const binVisual = (hex, caption) => `<div class="bin-visual" style="--bin:${esc(hex)}"><div class="bin"><i class="lid"></i><i class="body"></i></div><small>${esc(caption)}</small></div>`;

  function routeMarkup(route, label, answer = "", notice = "") {
    return `<div class="route">${binVisual(route.hex, route.color)}<div>
      <span class="eyebrow">${esc(label)}</span><h3>${esc(route.bin)}</h3>${route.bin_de ? `<span class="de">${esc(route.bin_de)}</span>` : ""}
      <p class="${answer ? "answer" : ""}">${esc(answer || route.note)}</p>${notice ? `<p class="notice">ℹ ${esc(notice)}</p>` : ""}
      <div class="actions"><button class="btn btn-sm take-another" type="button">Take another photo</button><button class="btn btn-sm ask-more" type="button">Ask a follow-up</button></div></div></div>`;
  }
  function bindActions(scope) {
    scope.querySelectorAll(".take-another").forEach((b) => b.addEventListener("click", openCamera));
    scope.querySelectorAll(".ask-more").forEach((b) => b.addEventListener("click", () => { chatInput.focus(); chatInput.placeholder = "Ask about this item…"; }));
  }

  /* ---------------------------------------------------------------- result card */
  function boxOverlay(data) {
    if (!data.top || !data.image_size) return "";
    const [w, h] = data.image_size;
    const [x1, y1, x2, y2] = data.top.box;
    const color = data.route ? data.route.hex : "#1f9d63";
    return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="xMidYMid meet"><rect x="${x1}" y="${y1}" width="${x2 - x1}" height="${y2 - y1}" rx="8" fill="${color}22" stroke="${color}" stroke-width="3" vector-effect="non-scaling-stroke"/></svg>`;
  }
  function resultCard(data) {
    const top = data.top;
    const pct = top ? Math.round(top.confidence * 100) : 0;
    const title = top ? top.label.replaceAll("_", " ") : "No clear object";
    const review = data.needs_review;
    const alts = (data.detections || []).slice(1, 4).map((d) => `<span>${esc(d.label.replaceAll("_", " "))} ${Math.round(d.confidence * 100)}%</span>`).join("");
    const node = addNode(`${AVATAR}<div class="bubble wide result">
      <div class="photo-frame"><img src="${esc(data.photo_url)}" alt="Analysed photo">${boxOverlay(data)}</div>
      <div class="result-top"><div class="ring" style="--score:${pct};--ring:${review ? "#7160b7" : "#1f9d63"}"><strong>${pct}%</strong></div>
        <div><small class="k">MODEL PREDICTION</small><h3>${esc(title)}</h3>
        <span class="badge ${review ? "ai" : ""}" id="src-badge">${review ? `Below your ${Math.round(data.threshold * 100)}% threshold · asking AI` : "Analysed locally"}</span></div></div>
      ${alts ? `<div class="alts"><small class="k" style="align-self:center;color:var(--muted)">Also considered:</small>${alts}</div>` : ""}
      <div class="route-slot"></div></div>`);
    const slot = node.querySelector(".route-slot");
    if (!review && data.route) {
      slot.innerHTML = routeMarkup(data.route, "German disposal route");
      bindActions(slot);
    } else {
      slot.innerHTML = `<div class="route">${binVisual("#7160B7", "Review")}<div><span class="eyebrow">Ask AI is checking</span><h3>Taking a closer look</h3><p>The model is not confident enough, so the photo and its prediction were passed on.</p><span class="dots" style="margin-top:8px"><i></i><i></i><i></i></span></div></div>`;
    }
    return { node, slot };
  }

  async function pollReview(jobId, slot, node) {
    const badge = node.querySelector("#src-badge");
    for (let n = 0; n < 90; n += 1) {
      await new Promise((r) => setTimeout(r, 1400));
      let job;
      try { job = await (await fetch(`/api/review/${jobId}`)).json(); } catch (_e) { continue; }
      if (job.status === "done") {
        const route = (job.label && RULES[job.label]) || binFromAnswer(job.answer);
        const local = job.source !== "llm";
        slot.innerHTML = routeMarkup(route, local ? "Local rule (AI unavailable)" : "Ask AI recommendation", job.answer, job.notice || "");
        badge.textContent = local ? "Local rules" : "Reviewed by Ask AI";
        bindActions(slot);
        scrollToLatest();
        return;
      }
      if (job.status === "error") {
        slot.innerHTML = `<div class="route"><div><span class="eyebrow">Review failed</span><h3>Ask AI could not finish</h3><p>${esc(job.message || "Please try again.")}</p></div></div>`;
        return;
      }
    }
    slot.innerHTML = `<div class="route"><div><h3>The review is taking too long</h3><p>Please try the image again.</p></div></div>`;
  }

  /* ---------------------------------------------------------------- upload / analyse */
  async function analyzeImage(blob, previewUrl) {
    addUserImage(previewUrl);
    const thinking = addThinking("Analysing with the YOLO model");
    const form = new FormData();
    form.append("photo", blob, "waste-photo.jpg");
    form.append("threshold", String(threshold));
    try {
      const response = await fetch("/api/analyze", { method: "POST", body: form });
      const data = await response.json();
      thinking.remove();
      if (response.status === 401) { location.assign("/login"); return; }
      if (!response.ok) throw new Error(data.error || "The image could not be analysed.");
      currentContext = {
        imageName: data.photo_url.split("/").pop(),
        prediction: data.top ? `${data.top.label} (${Math.round(data.top.confidence * 100)}% confidence)` : "No object detected",
      };
      const card = resultCard(data);
      if (data.needs_review && data.job_id) pollReview(data.job_id, card.slot, card.node);
    } catch (error) {
      thinking.remove();
      addError(error.message);
    }
  }
  function handleFile(file) {
    if (!file) return;
    if (!file.type.startsWith("image/")) return toast("Please choose an image file.");
    if (file.size > 8 * 1024 * 1024) return toast("Please use an image smaller than 8 MB.");
    analyzeImage(file, URL.createObjectURL(file));
  }
  const openUpload = () => fileInput.click();
  fileInput.addEventListener("change", () => { handleFile(fileInput.files[0]); fileInput.value = ""; });
  $("#upload-button").addEventListener("click", openUpload);
  $("#welcome-upload").addEventListener("click", openUpload);

  /* ---------------------------------------------------------------- camera */
  const cameraModal = $("#camera-modal");
  const video = $("#camera-video");
  const canvas = $("#capture-canvas");
  let stream = null;
  async function openCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      return toast("Camera needs HTTPS or localhost. You can upload a photo instead.");
    }
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false });
      video.srcObject = stream;
      cameraModal.classList.add("open");
      cameraModal.setAttribute("aria-hidden", "false");
    } catch (_e) { toast("Camera access failed. You can upload a photo instead."); }
  }
  function closeCamera() {
    cameraModal.classList.remove("open");
    cameraModal.setAttribute("aria-hidden", "true");
    if (stream) stream.getTracks().forEach((t) => t.stop());
    stream = null; video.srcObject = null;
  }
  $("#camera-button").addEventListener("click", openCamera);
  $("#welcome-camera").addEventListener("click", openCamera);
  $("#close-camera").addEventListener("click", closeCamera);
  $("#cancel-camera").addEventListener("click", closeCamera);
  cameraModal.addEventListener("click", (e) => { if (e.target === cameraModal) closeCamera(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && cameraModal.classList.contains("open")) closeCamera(); });
  $("#capture-button").addEventListener("click", () => {
    if (!video.videoWidth) return toast("The camera is still starting.");
    canvas.width = video.videoWidth; canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    canvas.toBlob((blob) => {
      if (!blob) return toast("Could not capture the photo.");
      const preview = URL.createObjectURL(blob);
      closeCamera();
      analyzeImage(blob, preview);
    }, "image/jpeg", 0.9);
  });

  /* ---------------------------------------------------------------- chat */
  async function sendChat() {
    const message = chatInput.value.trim();
    if (!message) return;
    addUserText(message);
    chatInput.value = "";
    sendButton.disabled = true;
    const thinking = addThinking("Checking German recycling guidance");
    try {
      const response = await fetch("/api/chat", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, image_name: currentContext.imageName, prediction: currentContext.prediction }),
      });
      const data = await response.json();
      thinking.remove();
      if (!response.ok) throw new Error(data.error || "Ask AI could not answer.");
      addAnswer(data.answer, data.source);
    } catch (error) {
      thinking.remove();
      addError(error.message);
    } finally { sendButton.disabled = false; chatInput.focus(); }
  }
  sendButton.addEventListener("click", sendChat);
  chatInput.addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendChat(); } });

  /* ---------------------------------------------------------------- public tunnel (local Python only) */
  const tunnelCard = $("#tunnel-card");
  if (tunnelCard) {
    const statusEl = $("#tunnel-status"), msgEl = $("#tunnel-message"), urlBox = $("#public-url"), urlLink = $("#public-url-link");
    const startBtn = $("#start-tunnel"), stopBtn = $("#stop-tunnel");
    const LABELS = { stopped: "Offline", starting: "Starting", online: "Live", stopping: "Stopping", error: "Error", unavailable: "Unavailable" };
    let timer = null;
    function render(state) {
      const status = state.status || "stopped";
      statusEl.className = `status-chip ${status}`;
      statusEl.textContent = LABELS[status] || status;
      msgEl.textContent = state.error || state.message || "Your application is private.";
      startBtn.disabled = ["starting", "online", "stopping"].includes(status);
      startBtn.hidden = ["online", "stopping"].includes(status);
      stopBtn.hidden = !["online", "starting"].includes(status);
      urlBox.hidden = !(status === "online" && state.url);
      if (!urlBox.hidden) { urlLink.href = state.url; urlLink.textContent = state.url; }
    }
    async function refresh() {
      try { const state = await (await fetch("/api/tunnel/status", { cache: "no-store" })).json(); render(state); return state; }
      catch (_e) { render({ status: "error", message: "Could not contact the tunnel controller." }); return null; }
    }
    startBtn.addEventListener("click", async () => {
      render({ status: "starting", message: "Cloudflare is creating a secure public URL…" });
      try {
        const res = await fetch("/api/tunnel/start", { method: "POST" });
        const state = await res.json();
        render(state);
        if (res.ok) {
          clearInterval(timer);
          let tries = 0;
          timer = setInterval(async () => { tries += 1; const s = await refresh(); if (!s || s.status !== "starting" || tries > 45) clearInterval(timer); }, 1000);
        }
      } catch (e) { render({ status: "error", message: e.message }); }
    });
    stopBtn.addEventListener("click", async () => {
      clearInterval(timer);
      try { render(await (await fetch("/api/tunnel/stop", { method: "POST" })).json()); } catch (e) { render({ status: "error", message: e.message }); }
    });
    $("#copy-url").addEventListener("click", async () => {
      try { await navigator.clipboard.writeText(urlLink.href); toast("Public link copied"); } catch (_e) { toast("Select and copy the URL manually"); }
    });
    refresh();
  }
})();
