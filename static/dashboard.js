/* dashboard.js - loads /api/dashboard/stats and draws KPI cards, donuts, bars, trend line and
   municipality rings as plain SVG (no chart library => works offline, e.g. inside Docker). */
(() => {
  const { $, esc, bootData } = window.EcoSort;
  const RULES = bootData().rules || {};
  const NS = "http://www.w3.org/2000/svg";
  const SOURCE_STYLE = {
    local: { name: "Local model", color: "#1f9d63" },
    llm: { name: "Ask AI", color: "#7160b7" },
    "local-fallback": { name: "Local rules (AI offline)", color: "#d9822b" },
  };
  const FALLBACK = ["#1f9d63", "#14b8a6", "#6366f1", "#f59e0b", "#ec4899", "#0ea5e9", "#8b5cf6", "#84cc16"];
  const selected = { waste: new Set(), category: new Set(), confidence: new Set(), city: new Set(), month: new Set() };
  let filtersBuilt = false;
  const tooltip = $("#tooltip");

  /* ------------------------------------------------------------ helpers */
  const pretty = (s) => String(s).replaceAll("_", " ");
  function colorsFor(items) {
    // Metal and Plastic share a bin colour; lighten repeats so legend entries stay distinguishable.
    const seen = new Set();
    return items.map((item, i) => {
      let c = (RULES[item.label] && RULES[item.label].hex) || (SOURCE_STYLE[item.label] && SOURCE_STYLE[item.label].color) || FALLBACK[i % FALLBACK.length];
      if (seen.has(c)) c = `color-mix(in srgb, ${c}, white 42%)`;
      seen.add(c);
      return c;
    });
  }
  function showTip(event, html) {
    tooltip.innerHTML = html;
    tooltip.classList.add("show");
    tooltip.style.left = `${Math.min(window.innerWidth - 160, event.clientX + 14)}px`;
    tooltip.style.top = `${event.clientY + 14}px`;
  }
  const hideTip = () => tooltip.classList.remove("show");
  function el(name, attrs = {}, parent) {
    const node = document.createElementNS(NS, name);
    Object.entries(attrs).forEach(([k, v]) => node.setAttribute(k, v));
    if (parent) parent.appendChild(node);
    return node;
  }
  function countUp(node, target) {
    const start = Number(node.dataset.count || 0), t0 = performance.now(), dur = 700;
    node.dataset.count = target;
    function frame(now) {
      const p = Math.min(1, (now - t0) / dur), eased = 1 - Math.pow(1 - p, 3);
      node.textContent = Math.round(start + (target - start) * eased).toLocaleString();
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  /* ------------------------------------------------------------ donut chart */
  function donut(svgId, legendId, items, nameOf) {
    const svg = $(svgId), legend = $(legendId);
    svg.innerHTML = "";
    const total = items.reduce((a, x) => a + x.count, 0);
    const R = 78, C = 2 * Math.PI * R, colors = colorsFor(items);
    el("circle", { cx: 110, cy: 110, r: R, fill: "none", stroke: "rgba(127,127,127,.2)", "stroke-width": 26 }, svg);
    let offset = 0;
    items.forEach((item, i) => {
      const len = (item.count / Math.max(1, total)) * C;
      const seg = el("circle", {
        class: "seg", cx: 110, cy: 110, r: R, fill: "none", stroke: colors[i], "stroke-width": 26,
        "stroke-dasharray": `${Math.max(0, len - 2)} ${C}`, "stroke-dashoffset": -offset, transform: "rotate(-90 110 110)",
      }, svg);
      seg.addEventListener("mousemove", (e) => showTip(e, `${esc(nameOf(item))}: <b>${item.count}</b> (${Math.round((item.count / total) * 100)}%)`));
      seg.addEventListener("mouseleave", hideTip);
      offset += len;
    });
    const t = el("text", { x: 110, y: 112, "text-anchor": "middle", class: "val", style: "font-size:30px" }, svg);
    t.textContent = total;
    const sub = el("text", { x: 110, y: 134, "text-anchor": "middle" }, svg);
    sub.textContent = total ? "scans" : "no scans yet";
    legend.innerHTML = items.length
      ? items.map((x, i) => `<div><i style="background:${colors[i]}"></i>${esc(nameOf(x))}<b>${x.count}</b></div>`).join("")
      : '<div style="color:var(--muted)">Scan a photo to see data here.</div>';
  }

  /* ------------------------------------------------------------ horizontal bars */
  function bars(items) {
    const host = $("#bars-bins");
    if (!items.length) { host.innerHTML = '<p class="empty">No data for the current filters.</p>'; return; }
    const max = Math.max(...items.map((x) => x.count)), colors = colorsFor(items);
    host.innerHTML = items.slice(0, 8).map((x, i) => `<div class="hbar"><div class="row"><span>${esc(pretty(x.label))}</span><b>${x.count}</b></div>
      <div class="track"><div class="fill" data-w="${(x.count / max) * 100}" style="background:${colors[i]}"></div></div></div>`).join("");
    requestAnimationFrame(() => host.querySelectorAll(".fill").forEach((f) => { f.style.width = `${f.dataset.w}%`; }));
  }

  /* ------------------------------------------------------------ trend (area + line) */
  function trend(values) {
    const svg = $("#trend");
    svg.innerHTML = "";
    const W = 640, H = 230, L = 38, R = 14, T = 16, B = 30;
    const lo = Math.floor((Math.min(...values) - 4) / 5) * 5, hi = Math.ceil((Math.max(...values) + 2) / 5) * 5;
    const x = (i) => L + (i * (W - L - R)) / (values.length - 1), y = (v) => T + (1 - (v - lo) / (hi - lo)) * (H - T - B);
    const defs = el("defs", {}, svg);
    const grad = el("linearGradient", { id: "area-grad", x1: 0, y1: 0, x2: 0, y2: 1 }, defs);
    el("stop", { offset: "0%", "stop-color": "#1f9d63", "stop-opacity": ".45" }, grad);
    el("stop", { offset: "100%", "stop-color": "#1f9d63", "stop-opacity": "0" }, grad);
    for (let v = lo; v <= hi; v += 5) {
      el("line", { class: "grid", x1: L, x2: W - R, y1: y(v), y2: y(v) }, svg);
      el("text", { x: L - 8, y: y(v) + 4, "text-anchor": "end" }, svg).textContent = `${v}%`;
    }
    const now = new Date();
    values.forEach((_v, i) => {
      const d = new Date(now.getFullYear(), now.getMonth() - (values.length - 1 - i), 1);
      el("text", { x: x(i), y: H - 8, "text-anchor": "middle" }, svg).textContent = d.toLocaleString("en", { month: "short" });
    });
    const line = values.map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`).join(" ");
    el("path", { d: `${line} L${x(values.length - 1)},${H - B} L${x(0)},${H - B} Z`, fill: "url(#area-grad)" }, svg);
    const path = el("path", { d: line, fill: "none", stroke: "#1f9d63", "stroke-width": 3, "stroke-linecap": "round", "stroke-linejoin": "round" }, svg);
    const length = path.getTotalLength();
    path.style.strokeDasharray = length; path.style.strokeDashoffset = length;
    path.getBoundingClientRect();                       // force layout so the transition starts
    path.style.transition = "stroke-dashoffset 1.1s ease"; path.style.strokeDashoffset = 0;
    values.forEach((v, i) => {
      const dot = el("circle", { class: "dot", cx: x(i), cy: y(v), r: 4.5, fill: "#fff", stroke: "#1f9d63", "stroke-width": 2.5 }, svg);
      dot.addEventListener("mousemove", (e) => showTip(e, `Recycling rate: <b>${v}%</b>`));
      dot.addEventListener("mouseleave", hideTip);
    });
  }

  /* ------------------------------------------------------------ municipality rings */
  function areas(list) {
    $("#areas").innerHTML = list.map((a) => {
      const C = 2 * Math.PI * 22, filled = (a.recycling_rate / 100) * C;
      return `<div class="area"><svg viewBox="0 0 54 54"><circle cx="27" cy="27" r="22" fill="none" stroke="rgba(127,127,127,.22)" stroke-width="6"/>
        <circle cx="27" cy="27" r="22" fill="none" stroke="#1f9d63" stroke-width="6" stroke-linecap="round" stroke-dasharray="${filled} ${C}" transform="rotate(-90 27 27)"/>
        <text x="27" y="31" text-anchor="middle" class="val" style="font-size:12px">${a.recycling_rate}%</text></svg>
        <div><strong>${esc(a.name)}</strong><small>${a.monthly_tons} t / month</small></div></div>`;
    }).join("");
  }

  /* ------------------------------------------------------------ filter chips */
  function buildFilters(filters) {
    const groups = [["waste", "Item", filters.waste], ["category", "Category", filters.categories],
                    ["confidence", "Confidence", filters.confidence], ["city", "City", filters.cities], ["month", "Month", filters.months]];
    const host = $("#filters");
    host.innerHTML = groups.filter(([, , vals]) => vals && vals.length).map(([key, title, vals]) =>
      `<div class="filter-group"><b>${title}</b>${vals.map((v) => `<button class="chip" type="button" data-key="${key}" data-value="${esc(v)}">${esc(pretty(v))}</button>`).join("")}</div>`).join("");
    host.querySelectorAll(".chip").forEach((chip) => chip.addEventListener("click", () => {
      const set = selected[chip.dataset.key], value = chip.dataset.value;
      set.has(value) ? set.delete(value) : set.add(value);
      chip.classList.toggle("on", set.has(value));
      load();
    }));
    filtersBuilt = true;
  }
  $("#clear-filters").addEventListener("click", () => {
    Object.values(selected).forEach((s) => s.clear());
    document.querySelectorAll("#filters .chip.on").forEach((c) => c.classList.remove("on"));
    load();
  });

  /* ------------------------------------------------------------ load + render */
  async function load() {
    const q = new URLSearchParams();
    Object.entries(selected).forEach(([key, set]) => set.forEach((v) => q.append(key === "waste" ? "waste" : key, v)));
    let stats;
    try {
      const res = await fetch(`/api/dashboard/stats?${q}`);
      if (res.status === 401) { location.assign("/login"); return; }
      stats = await res.json();
    } catch (_e) { return; }
    if (!filtersBuilt) buildFilters(stats.filters);
    countUp($("#kpi-scans"), stats.totals.scans);
    countUp($("#kpi-llm"), stats.totals.llm_calls);
    countUp($("#kpi-tokens"), stats.totals.tokens);
    const rates = stats.municipality.areas.map((a) => a.recycling_rate);
    $("#kpi-rate").textContent = `${Math.round(rates.reduce((a, b) => a + b, 0) / rates.length)}%`;
    donut("#donut-bins", "#legend-bins", stats.by_bin, (x) => pretty(x.label));
    bars(stats.by_bin);
    donut("#donut-source", "#legend-source", stats.by_source, (x) => (SOURCE_STYLE[x.label] || { name: x.label }).name);
    trend(stats.municipality.monthly);
    areas(stats.municipality.areas);
  }
  load();
})();
