"""TunnelManager - optional "Go live" feature (Cloudflare quick tunnel).

Only used when the app runs directly with Python on a PC that has the
``cloudflared`` program installed. In Docker it is switched off
(``SORTLY_ENABLE_TUNNEL=0``) and the UI hides the panel.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

TUNNEL_URL_PATTERN = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com", re.IGNORECASE)


class TunnelManager:
    """Starts / stops ``cloudflared`` and reports the public URL."""

    def __init__(self, local_url: str, enabled: bool = True, working_dir: Path | None = None):
        self._local_url = local_url
        self._enabled = enabled
        self._working_dir = working_dir
        self._process: subprocess.Popen | None = None
        self._lock = threading.Lock()
        self._state = self._idle_state()

    @property
    def enabled(self) -> bool:
        return self._enabled

    @staticmethod
    def _idle_state() -> dict:
        return {"status": "stopped", "url": None, "message": "The public tunnel is off.", "started_at": None}

    # ---- locating the program -------------------------------------------
    def find_executable(self) -> str | None:
        """Find ``cloudflared`` on PATH or in the usual Windows install folders."""
        found = shutil.which("cloudflared")
        if found:
            return found
        home = Path.home()
        candidates = [
            home / "AppData" / "Local" / "Microsoft" / "WinGet" / "Links" / "cloudflared.exe",
            Path(r"C:\Program Files\cloudflared\cloudflared.exe"),
            Path(r"C:\Program Files (x86)\cloudflared\cloudflared.exe"),
        ]
        if self._working_dir:
            candidates.insert(0, self._working_dir / "cloudflared.exe")
        packages = home / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
        if packages.exists():
            candidates.extend(packages.glob("Cloudflare.cloudflared_*/*cloudflared.exe"))
        return next((str(p) for p in candidates if p.exists()), None)

    # ---- state -----------------------------------------------------------
    def state(self) -> dict:
        """Current tunnel status (copied dict, safe to return as JSON)."""
        if not self._enabled:
            return {"status": "disabled", "url": None, "enabled": False, "cloudflared_available": False,
                    "message": "The public tunnel is not available in this deployment."}
        with self._lock:
            state = dict(self._state)
            process = self._process
        if process is not None and process.poll() is not None and state["status"] in {"starting", "online"}:
            state.update(status="error", url=None, message="The Cloudflare tunnel process stopped unexpectedly.")
            with self._lock:
                self._state.update(state)
        state["enabled"] = True
        state["cloudflared_available"] = self.find_executable() is not None
        return state

    def start(self) -> tuple[dict, int]:
        """Launch the tunnel. Returns ``(state, http_status)``."""
        if not self._enabled:
            return self.state(), 503
        executable = self.find_executable()
        if not executable:
            return ({"status": "unavailable", "enabled": True, "url": None,
                     "error": "cloudflared is not installed. Install it, restart this app, and try again."}, 503)
        with self._lock:
            if self._process is not None and self._process.poll() is None:
                return dict(self._state), 200
            flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            try:
                self._process = subprocess.Popen(
                    [executable, "tunnel", "--url", self._local_url], cwd=self._working_dir,
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace", bufsize=1, creationflags=flags)
            except Exception as error:
                self._process = None
                self._state.update(status="error", url=None, message=f"Could not start cloudflared: {error}")
                return {**self._state, "error": self._state["message"]}, 500
            self._state.update(status="starting", url=None, started_at=int(time.time()),
                               message="Cloudflare is creating a secure public URL…")
            process = self._process
        threading.Thread(target=self._read_output, args=(process,), daemon=True).start()
        return self.state(), 202

    def stop(self) -> dict:
        """Close the tunnel (also called automatically when the app exits)."""
        with self._lock:
            process = self._process
            if process is None or process.poll() is not None:
                self._process = None
                self._state.update(self._idle_state())
                return self.state()
            self._state.update(status="stopping", message="Closing the public tunnel…")
        process.terminate()
        try:
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)
        with self._lock:
            if self._process is process:
                self._process = None
                self._state.update(self._idle_state())
        return self.state()

    def _read_output(self, process: subprocess.Popen) -> None:
        """Background thread: watch cloudflared's output for the public URL."""
        try:
            assert process.stdout is not None
            for raw_line in iter(process.stdout.readline, ""):
                match = TUNNEL_URL_PATTERN.search(raw_line.strip())
                if match:
                    with self._lock:
                        if self._process is process:
                            self._state.update(status="online", url=match.group(0),
                                               message="Your protected public link is live.")
            code = process.wait()
            with self._lock:
                if self._process is process and self._state["status"] != "stopping":
                    self._state.update(status="error", url=None, message=f"Cloudflare tunnel stopped (exit code {code}).")
        except Exception as error:
            with self._lock:
                if self._process is process:
                    self._state.update(status="error", url=None, message=f"Tunnel error: {error}")
