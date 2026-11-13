/* common.js - helpers shared by all pages: HTML escaping, toast messages, theme toggle. */
window.EcoSort = (() => {
  const $ = (selector, root = document) => root.querySelector(selector);

  /** Escape text before putting it into innerHTML (prevents XSS). */
  function esc(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[c]);
  }

  /** Small message at the bottom of the screen. */
  let toastTimer;
  function toast(message) {
    const el = $("#toast");
    if (!el) return;
    el.textContent = message;
    el.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("show"), 2600);
  }

  /** Read the JSON blob the server embeds in <script id="boot-data">. */
  function bootData() {
    try { return JSON.parse($("#boot-data").textContent); } catch (_e) { return {}; }
  }

  // Light / dark toggle (the initial theme is set by a tiny inline script in <head>).
  const toggle = $("#theme-toggle");
  if (toggle) toggle.addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("ecosort-theme", next); } catch (_e) { /* private mode */ }
    document.dispatchEvent(new CustomEvent("themechange"));
  });

  return { $, esc, toast, bootData };
})();
