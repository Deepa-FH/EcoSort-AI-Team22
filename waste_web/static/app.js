const $ = (selector) => document.querySelector(selector);
const conversation = $("#conversation");
const fileInput = $("#file-input");
const chatInput = $("#chat-input");
const sendButton = $("#send-button");
const cameraModal = $("#camera-modal");
const cameraVideo = $("#camera-video");
const canvas = $("#capture-canvas");
const slider = $("#threshold-slider");
const defaultThreshold = Number(document.body.dataset.defaultThreshold || 50);
let threshold = Math.min(95, Math.max(10, Number(localStorage.getItem("sortly-threshold")) || defaultThreshold));
let cameraStream = null;
let currentContext = { imageName: "", prediction: "" };

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => toast.classList.remove("show"), 2500);
}

function scrollToLatest() {
  requestAnimationFrame(() => conversation.scrollTo({ top: conversation.scrollHeight, behavior: "smooth" }));
}

function setThreshold(value, announce = false) {
  threshold = Math.min(95, Math.max(10, Number(value)));
  localStorage.setItem("sortly-threshold", String(threshold));
  slider.value = threshold;
  $("#threshold-output").value = `${threshold}%`;
  $("#local-value").textContent = `${threshold}%`;
  $("#codex-value").textContent = `${threshold}%`;
  slider.style.background = `linear-gradient(90deg,#247b4e 0%,#247b4e ${(threshold - 10) / 0.85}%,#e2e8e3 ${(threshold - 10) / 0.85}%,#e2e8e3 100%)`;
  if (announce) showToast(`Confidence threshold saved at ${threshold}%`);
}

document.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach((item) => item.classList.toggle("active", item === button));
    document.querySelectorAll(".tab-panel").forEach((panel) => panel.classList.remove("active"));
    $(`#${button.dataset.tab}-panel`).classList.add("active");
  });
});

slider.addEventListener("input", () => setThreshold(slider.value));
slider.addEventListener("change", () => setThreshold(slider.value, true));
setThreshold(threshold);

function addUserImage(url, label = "Photo to identify") {
  const node = document.createElement("div");
  node.className = "message user-message";
  node.innerHTML = `<div class="bubble user-bubble"><img class="user-photo" src="${escapeHtml(url)}" alt="${escapeHtml(label)}"><div class="user-text">Please identify this item.</div></div>`;
  conversation.appendChild(node);
  scrollToLatest();
}

function addUserText(text) {
  const node = document.createElement("div");
  node.className = "message user-message";
  const bubble = document.createElement("div");
  bubble.className = "bubble user-bubble user-text";
  bubble.textContent = text;
  node.appendChild(bubble);
  conversation.appendChild(node);
  scrollToLatest();
}

function addThinking(label) {
  const node = document.createElement("div");
  node.className = "message assistant-message";
  node.innerHTML = `<div class="avatar">S</div><div class="bubble thinking-bubble"><span>${escapeHtml(label)}</span><span class="thinking-dots"><i></i><i></i><i></i></span></div>`;
  conversation.appendChild(node);
  scrollToLatest();
  return node;
}

function addError(message) {
  const node = document.createElement("div");
  node.className = "message assistant-message";
  node.innerHTML = `<div class="avatar">S</div><div class="bubble error-bubble"><p>${escapeHtml(message)}</p></div>`;
  conversation.appendChild(node);
  scrollToLatest();
}

function addAssistantText(text, badge = "Codex answer") {
  const node = document.createElement("div");
  node.className = "message assistant-message";
  node.innerHTML = `<div class="avatar">S</div><div class="bubble"><span class="eyebrow">${escapeHtml(badge)}</span><p class="codex-answer"></p></div>`;
  node.querySelector("p").textContent = text;
  conversation.appendChild(node);
  scrollToLatest();
}

function binFromAnswer(answer) {
  const text = answer.toLowerCase();
  if (/yellow|gelbe|packaging/.test(text)) return { color: "Yellow", hex: "#F4C542", bin: "Yellow bin / deposit return" };
  if (/blue|papier|paper bin/.test(text)) return { color: "Blue", hex: "#3178C6", bin: "Blue paper bin" };
  if (/brown|biotonne|organic|bio bin/.test(text)) return { color: "Brown", hex: "#8B5E3C", bin: "Brown organic bin" };
  if (/glass container|altglas|green container|white container/.test(text)) return { color: "Glass containers", hex: "#4F8A67", bin: "Matching glass container" };
  if (/special|hazard|battery|collection point|schadstoff/.test(text)) return { color: "Special collection", hex: "#D94B4B", bin: "Special waste collection point" };
  if (/textile|clothing|altkleider/.test(text)) return { color: "Textile collection", hex: "#D9822B", bin: "Reuse or textile collection" };
  if (/residual|restmüll|general waste|grey|black bin/.test(text)) return { color: "Grey / black", hex: "#626A66", bin: "Residual waste bin" };
  return { color: "Check guidance", hex: "#7160B7", bin: "Follow the Codex recommendation" };
}

function resultCard(data) {
  const top = data.top;
  const confidence = top ? Math.round(top.confidence * 100) : 0;
  const node = document.createElement("div");
  node.className = "message assistant-message";
  const route = data.route;
  const title = top ? top.label.replaceAll("_", " ") : "No clear object";
  const subtitle = data.needs_review ? `Below your ${Math.round(data.threshold * 100)}% threshold` : "Confident local prediction";
  node.innerHTML = `<div class="avatar">S</div><div class="bubble result-card">
    <div class="result-top"><div class="confidence-ring" style="--score:${confidence};--ring:${data.needs_review ? "#7160b7" : "#278556"}"><strong>${confidence}%</strong></div><div class="prediction-copy"><small>MODEL PREDICTION</small><h3>${escapeHtml(title)}</h3><p>${escapeHtml(subtitle)}</p></div><span class="source-badge ${data.needs_review ? "codex" : ""}">${data.needs_review ? "Reviewing with Codex" : "Analyzed locally"}</span></div>
    <div class="route-slot"></div>
  </div>`;
  conversation.appendChild(node);
  const slot = node.querySelector(".route-slot");
  if (!data.needs_review && route) {
    slot.innerHTML = routeMarkup(route, "German disposal route");
  } else {
    slot.innerHTML = `<div class="route-panel"><div class="bin-visual" style="--bin:#7160B7"><div class="large-bin"></div><small>Expert review</small></div><div class="route-copy"><span class="route-label">CODEX IS CHECKING</span><h3>Taking a closer look</h3><p>The local model is not confident enough, so the photo and its prediction were passed to Codex.</p><div class="thinking-dots"><i></i><i></i><i></i></div></div></div>`;
  }
  scrollToLatest();
  return { node, slot };
}

function routeMarkup(route, label, answer = "") {
  return `<div class="route-panel"><div class="bin-visual" style="--bin:${escapeHtml(route.hex)}"><div class="large-bin"></div><small>${escapeHtml(route.color)}</small></div><div class="route-copy"><span class="route-label">${escapeHtml(label)}</span><h3>${escapeHtml(route.bin)}</h3>${route.bin_de ? `<span class="german-name">${escapeHtml(route.bin_de)}</span>` : ""}<p class="${answer ? "codex-answer" : ""}">${escapeHtml(answer || route.note)}</p><div class="result-actions"><button class="small-action take-another">Take another photo</button><button class="small-action ask-more">Ask a follow-up</button></div></div></div>`;
}

function bindResultActions(scope = document) {
  scope.querySelectorAll(".take-another").forEach((button) => button.addEventListener("click", openCamera));
  scope.querySelectorAll(".ask-more").forEach((button) => button.addEventListener("click", () => { chatInput.focus(); chatInput.placeholder = "Ask about this item…"; }));
}

async function pollReview(jobId, slot, cardNode) {
  for (let count = 0; count < 90; count += 1) {
    await new Promise((resolve) => setTimeout(resolve, 1400));
    const response = await fetch(`/api/review/${jobId}`);
    const job = await response.json();
    if (job.status === "done") {
      const route = binFromAnswer(job.answer);
      slot.innerHTML = routeMarkup(route, "Codex recommendation", job.answer);
      const badge = cardNode.querySelector(".source-badge");
      badge.textContent = "Reviewed by Codex";
      bindResultActions(slot);
      scrollToLatest();
      return;
    }
    if (job.status === "error" || !response.ok) {
      slot.innerHTML = `<div class="route-panel"><div class="route-copy"><span class="route-label">REVIEW FAILED</span><h3>Codex could not complete the review</h3><p>${escapeHtml(job.message || job.error || "Please try again.")}</p></div></div>`;
      return;
    }
  }
  slot.innerHTML = `<div class="route-panel"><div class="route-copy"><h3>The review is taking too long</h3><p>Please try the image again.</p></div></div>`;
}

async function analyzeImage(blob, previewUrl) {
  addUserImage(previewUrl);
  const thinking = addThinking("Analyzing with your YOLO26 model");
  const form = new FormData();
  form.append("photo", blob, "waste-photo.jpg");
  form.append("threshold", String(threshold));
  try {
    const response = await fetch("/api/analyze", { method: "POST", body: form });
    const data = await response.json();
    thinking.remove();
    if (!response.ok) throw new Error(data.error || "The image could not be analyzed.");
    currentContext = {
      imageName: data.photo_url.split("/").pop(),
      prediction: data.top ? `${data.top.label} (${Math.round(data.top.confidence * 100)}% confidence)` : "No object detected",
    };
    const rendered = resultCard(data);
    if (data.needs_review && data.job_id) pollReview(data.job_id, rendered.slot, rendered.node);
    else bindResultActions(rendered.slot);
  } catch (error) {
    thinking.remove();
    addError(error.message);
  }
}

function handleFile(file) {
  if (!file) return;
  if (!file.type.startsWith("image/")) return showToast("Please choose an image file.");
  if (file.size > 8 * 1024 * 1024) return showToast("Please use an image smaller than 8 MB.");
  analyzeImage(file, URL.createObjectURL(file));
}

function openUpload() { fileInput.click(); }
fileInput.addEventListener("change", () => { handleFile(fileInput.files[0]); fileInput.value = ""; });
$("#upload-button").addEventListener("click", openUpload);
$("#welcome-upload").addEventListener("click", openUpload);

async function openCamera() {
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false });
    cameraVideo.srcObject = cameraStream;
    cameraModal.classList.add("open");
    cameraModal.setAttribute("aria-hidden", "false");
  } catch (error) {
    showToast("Camera access failed. You can upload a photo instead.");
  }
}

function closeCamera() {
  cameraModal.classList.remove("open");
  cameraModal.setAttribute("aria-hidden", "true");
  if (cameraStream) cameraStream.getTracks().forEach((track) => track.stop());
  cameraStream = null;
  cameraVideo.srcObject = null;
}

$("#camera-button").addEventListener("click", openCamera);
$("#welcome-camera").addEventListener("click", openCamera);
$("#close-camera").addEventListener("click", closeCamera);
$("#cancel-camera").addEventListener("click", closeCamera);
cameraModal.addEventListener("click", (event) => { if (event.target === cameraModal) closeCamera(); });

$("#capture-button").addEventListener("click", () => {
  if (!cameraVideo.videoWidth) return showToast("The camera is still starting.");
  canvas.width = cameraVideo.videoWidth;
  canvas.height = cameraVideo.videoHeight;
  canvas.getContext("2d").drawImage(cameraVideo, 0, 0);
  canvas.toBlob((blob) => {
    if (!blob) return showToast("Could not capture the photo.");
    const preview = URL.createObjectURL(blob);
    closeCamera();
    analyzeImage(blob, preview);
  }, "image/jpeg", 0.9);
});

async function sendChat() {
  const message = chatInput.value.trim();
  if (!message) return;
  addUserText(message);
  chatInput.value = "";
  sendButton.disabled = true;
  const thinking = addThinking("Checking German recycling guidance with Codex");
  try {
    const response = await fetch("/api/chat", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, image_name: currentContext.imageName, prediction: currentContext.prediction }),
    });
    const data = await response.json();
    thinking.remove();
    if (!response.ok) throw new Error(data.error || "Codex could not answer.");
    addAssistantText(data.answer);
  } catch (error) {
    thinking.remove();
    addError(error.message);
  } finally {
    sendButton.disabled = false;
    chatInput.focus();
  }
}

sendButton.addEventListener("click", sendChat);
chatInput.addEventListener("keydown", (event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); sendChat(); } });
document.addEventListener("keydown", (event) => { if (event.key === "Escape" && cameraModal.classList.contains("open")) closeCamera(); });

const tunnelStatus = $("#tunnel-status");
const tunnelTitle = $("#tunnel-title");
const tunnelMessage = $("#tunnel-message");
const publicUrl = $("#public-url");
const publicUrlLink = $("#public-url-link");
const startTunnelButton = $("#start-tunnel");
const stopTunnelButton = $("#stop-tunnel");
let tunnelPollTimer = null;

function renderTunnel(state) {
  const status = state.status || "stopped";
  tunnelStatus.className = `tunnel-status ${status}`;
  tunnelStatus.querySelector("b").textContent = ({
    stopped: "Offline", starting: "Starting", online: "Live", stopping: "Stopping", error: "Error", unavailable: "Unavailable",
  })[status] || status;
  tunnelMessage.textContent = state.message || "The public tunnel is off.";
  startTunnelButton.disabled = status === "starting" || status === "online" || status === "stopping";
  startTunnelButton.hidden = status === "online" || status === "stopping";
  stopTunnelButton.hidden = status !== "online" && status !== "starting";
  if (status === "online" && state.url) {
    tunnelTitle.textContent = "Your protected public link is live";
    publicUrl.hidden = false;
    publicUrlLink.href = state.url;
    publicUrlLink.textContent = state.url;
  } else {
    publicUrl.hidden = true;
    publicUrlLink.href = "#";
    publicUrlLink.textContent = "";
    if (status === "starting") tunnelTitle.textContent = "Creating your public link";
    else if (status === "error" || status === "unavailable") tunnelTitle.textContent = "The tunnel could not start";
    else if (status === "stopping") tunnelTitle.textContent = "Closing public access";
    else tunnelTitle.textContent = "Your application is private";
  }
}

async function getTunnelStatus() {
  try {
    const response = await fetch("/api/tunnel/status", { cache: "no-store" });
    if (response.status === 401) return window.location.assign("/login");
    const state = await response.json();
    renderTunnel(state);
    return state;
  } catch (error) {
    renderTunnel({ status: "error", message: "Could not contact the local tunnel controller." });
    return null;
  }
}

function pollTunnelUntilReady() {
  clearInterval(tunnelPollTimer);
  let attempts = 0;
  tunnelPollTimer = setInterval(async () => {
    attempts += 1;
    const state = await getTunnelStatus();
    if (!state || state.status !== "starting" || attempts >= 45) clearInterval(tunnelPollTimer);
  }, 1000);
}

startTunnelButton.addEventListener("click", async () => {
  startTunnelButton.disabled = true;
  renderTunnel({ status: "starting", message: "Cloudflare is creating a secure public URL…" });
  try {
    const response = await fetch("/api/tunnel/start", { method: "POST" });
    const state = await response.json();
    if (!response.ok) throw new Error(state.error || "The tunnel could not start.");
    renderTunnel(state);
    pollTunnelUntilReady();
  } catch (error) {
    renderTunnel({ status: "error", message: error.message });
  }
});

stopTunnelButton.addEventListener("click", async () => {
  clearInterval(tunnelPollTimer);
  stopTunnelButton.disabled = true;
  renderTunnel({ status: "stopping", message: "Closing the public tunnel…" });
  try {
    const response = await fetch("/api/tunnel/stop", { method: "POST" });
    const state = await response.json();
    if (!response.ok) throw new Error(state.error || "The tunnel could not be closed.");
    renderTunnel(state);
  } catch (error) {
    renderTunnel({ status: "error", message: error.message });
  } finally {
    stopTunnelButton.disabled = false;
  }
});

$("#copy-url").addEventListener("click", async () => {
  if (!publicUrlLink.href || publicUrlLink.getAttribute("href") === "#") return;
  try {
    await navigator.clipboard.writeText(publicUrlLink.href);
    showToast("Public link copied");
  } catch (_error) {
    showToast("Select and copy the URL manually");
  }
});

getTunnelStatus();
