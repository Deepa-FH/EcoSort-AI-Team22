"""Run the full local EcoSort dashboard with a local YOLO model and API LLM."""

from __future__ import annotations

import atexit
import argparse
import hmac
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
from datetime import timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
MODEL_PATH = Path(os.environ.get("WASTE_MODEL_PATH", str(ROOT / "models" / "best_model.pt")))
DATA_DIR = Path(os.environ.get("SORTLY_DATA_DIR", str(ROOT)))
CAPTURE_DIR = DATA_DIR / "camera_captures"
TRAINING_PYTHON = Path(
    r"C:\Users\asus\Documents\ChatGPT\AI Powered waste sorting and recycling assistance\.venv-training\Scripts\python.exe"
)
DEFAULT_THRESHOLD = 0.50
MIN_THRESHOLD = 0.10
MAX_THRESHOLD = 0.95
APP_USERNAME = os.environ.get("SORTLY_USERNAME", "admin")
APP_PASSWORD = os.environ.get("SORTLY_PASSWORD", "admin")
SIGNUP_CODE = "pythonai"
DB_PATH = Path(os.environ.get("SORTLY_DB_PATH", str(DATA_DIR / "sortly.sqlite3")))
APP_PORT = int(os.environ.get("SORTLY_PORT", "5000"))
LOCAL_APP_URL = f"http://127.0.0.1:{APP_PORT}"
TUNNEL_URL_PATTERN = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com", re.IGNORECASE)


def switch_to_training_python() -> None:
    if TRAINING_PYTHON.exists() and Path(sys.executable).resolve() != TRAINING_PYTHON.resolve():
        raise SystemExit(subprocess.call([str(TRAINING_PYTHON), "-u", str(Path(__file__).resolve()), *sys.argv[1:]]))


switch_to_training_python()

import cv2  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, session, url_for  # noqa: E402
from ultralytics import YOLO  # noqa: E402
from database import Database  # noqa: E402
from recycling_ai.llm_client import OpenAICompatibleClient  # noqa: E402

app = Flask(__name__, template_folder="waste_web/templates", static_folder="waste_web/static")
app.config.update(
    MAX_CONTENT_LENGTH=8 * 1024 * 1024,
    SECRET_KEY=secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
)
database = Database(DB_PATH)
database.init(APP_USERNAME, APP_PASSWORD)
model = None
model_lock = threading.Lock()
jobs: dict[str, dict] = {}
jobs_lock = threading.Lock()
tunnel_process: subprocess.Popen | None = None
tunnel_lock = threading.Lock()
tunnel_state = {
    "status": "stopped",
    "url": None,
    "message": "The public tunnel is off.",
    "started_at": None,
}
llm_client = OpenAICompatibleClient(
    api_key=os.environ.get("LLM_API_KEY"),
    model=os.environ.get("LLM_MODEL", "gpt-4o-mini"),
    base_url=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
)


ROUTES = {
    "Biomuell": {
        "category": "Organic waste", "bin": "Brown organic bin", "bin_de": "Biotonne",
        "color": "Brown", "hex": "#8B5E3C", "theme": "organic", "symbol": "leaf",
        "note": "Food scraps and accepted garden waste belong here. Check local rules for cooked food and compostable liners.",
    },
    "Glass": {
        "category": "Glass", "bin": "Deposit return or glass container", "bin_de": "Pfandautomat / Altglascontainer",
        "color": "Green / white / brown", "hex": "#4F8A67", "theme": "glass", "symbol": "bottle",
        "note": "Return deposit bottles first. Put non-deposit container glass into the matching white, green or brown container.",
    },
    "Metal": {
        "category": "Metal", "bin": "Yellow bin or recycling centre", "bin_de": "Gelbe Tonne / Wertstoffhof",
        "color": "Yellow", "hex": "#F4C542", "theme": "metal", "symbol": "can",
        "note": "Metal packaging usually belongs in the yellow bin. Other metal objects normally go to a recycling centre.",
    },
    "Papier": {
        "category": "Paper & cardboard", "bin": "Blue paper bin", "bin_de": "Papiertonne",
        "color": "Blue", "hex": "#3178C6", "theme": "paper", "symbol": "paper",
        "note": "Use for clean paper and flattened cardboard. Heavily soiled or coated paper may need residual waste.",
    },
    "Plastic": {
        "category": "Plastic", "bin": "Deposit return or yellow bin", "bin_de": "Pfandautomat / Gelbe Tonne",
        "color": "Yellow", "hex": "#F4C542", "theme": "plastic", "symbol": "bottle",
        "note": "Return bottles carrying a deposit symbol. Empty plastic packaging without a deposit usually goes in the yellow bin.",
    },
    "Sondermuell": {
        "category": "Special waste", "bin": "Special collection point", "bin_de": "Schadstoffmobil / Sammelstelle",
        "color": "Red", "hex": "#D94B4B", "theme": "special", "symbol": "battery",
        "note": "Batteries, chemicals and hazardous items must go to a designated collection point, never a household bin.",
    },
    "Textile_Trash": {
        "category": "Textiles", "bin": "Reuse or textile collection", "bin_de": "Altkleidercontainer / Spende",
        "color": "Orange", "hex": "#D9822B", "theme": "textile", "symbol": "shirt",
        "note": "Donate clean, wearable textiles or use a textile collection point. Wet or contaminated textiles follow local rules.",
    },
}


@app.before_request
def require_login():
    if request.endpoint in {"login", "signup", "static"}:
        return None
    if session.get("user_id"):
        return None
    if request.path.startswith("/api/"):
        return jsonify(error="Authentication required. Please sign in again."), 401
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = database.authenticate(username, password)
        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session.permanent = True
            return redirect(url_for("home"))
        error = "Incorrect username or password."
    return render_template("login.html", error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "user")
        code = request.form.get("signup_code", "")
        if not hmac.compare_digest(code, SIGNUP_CODE):
            error = "The invitation code is incorrect."
        elif len(username) < 3 or len(password) < 6:
            error = "Use a username with at least 3 characters and a password with at least 6 characters."
        elif role not in {"user", "municipality", "admin"}:
            error = "Choose a valid account type."
        else:
            try:
                database.create_user(username, password, role)
                return redirect(url_for("login", registered="1"))
            except Exception:
                error = "That username is already registered."
    return render_template("signup.html", error=error)


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def current_user() -> dict[str, Any] | None:
    if not session.get("user_id"):
        return None
    return {"id": session["user_id"], "username": session.get("username", ""), "role": session.get("role", "user")}


def is_admin() -> bool:
    return session.get("role") == "admin"


def admin_required():
    if not is_admin():
        return jsonify(error="Administrator access required."), 403
    return None


def routes() -> dict[str, dict[str, Any]]:
    return database.rules()


def route_label_from_text(answer: str, rule_set: dict[str, dict[str, Any]]) -> str | None:
    text = answer.lower()
    for label, rule in rule_set.items():
        if label.lower() in text or rule["bin"].lower() in text or rule["bin_de"].lower() in text:
            return label
    return None


def find_cloudflared() -> str | None:
    executable = shutil.which("cloudflared")
    if executable:
        return executable
    candidates = [
        ROOT / "cloudflared.exe",
        Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Links" / "cloudflared.exe",
        Path(r"C:\Program Files\cloudflared\cloudflared.exe"),
        Path(r"C:\Program Files (x86)\cloudflared\cloudflared.exe"),
    ]
    package_root = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    if package_root.exists():
        candidates.extend(package_root.glob("Cloudflare.cloudflared_*/*cloudflared.exe"))
    return next((str(path) for path in candidates if path.exists()), None)


def public_tunnel_state() -> dict:
    with tunnel_lock:
        state = dict(tunnel_state)
        process = tunnel_process
    if process is not None and process.poll() is not None and state["status"] in {"starting", "online"}:
        state.update(status="error", url=None, message="The Cloudflare tunnel process stopped unexpectedly.")
        with tunnel_lock:
            tunnel_state.update(state)
    state["cloudflared_available"] = find_cloudflared() is not None
    return state


def read_tunnel_output(process: subprocess.Popen) -> None:
    global tunnel_process
    try:
        assert process.stdout is not None
        for raw_line in iter(process.stdout.readline, ""):
            line = raw_line.strip()
            match = TUNNEL_URL_PATTERN.search(line)
            if match:
                with tunnel_lock:
                    if tunnel_process is process:
                        tunnel_state.update(
                            status="online", url=match.group(0),
                            message="Your protected public link is live.",
                        )
        return_code = process.wait()
        with tunnel_lock:
            if tunnel_process is process and tunnel_state["status"] != "stopping":
                tunnel_state.update(
                    status="error", url=None,
                    message=f"Cloudflare tunnel stopped (exit code {return_code}).",
                )
    except Exception as exc:
        with tunnel_lock:
            if tunnel_process is process:
                tunnel_state.update(status="error", url=None, message=f"Tunnel error: {exc}")


def stop_tunnel_process() -> None:
    global tunnel_process
    with tunnel_lock:
        process = tunnel_process
        if process is None or process.poll() is not None:
            tunnel_process = None
            tunnel_state.update(status="stopped", url=None, message="The public tunnel is off.", started_at=None)
            return
        tunnel_state.update(status="stopping", message="Closing the public tunnel…")
    process.terminate()
    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3)
    with tunnel_lock:
        if tunnel_process is process:
            tunnel_process = None
            tunnel_state.update(status="stopped", url=None, message="The public tunnel is off.", started_at=None)


atexit.register(stop_tunnel_process)


def get_model():
    global model
    if model is None:
        model = YOLO(str(MODEL_PATH))
    return model


def run_llm(prompt: str, image_path: Path | None = None) -> tuple[str, int]:
    """Ask the configured API LLM and return an approximate usage count."""
    answer = llm_client.ask(prompt)
    estimated_tokens = max(1, (len(prompt) + len(answer)) // 4)
    return answer, estimated_tokens


def llm_review(job_id: str, scan_id: int, user_id: int | None, image_path: Path, detections: list[dict]) -> None:
    with jobs_lock:
        jobs[job_id] = {"status": "working"}
    try:
        summary = ", ".join(f"{d['label']} ({d['confidence']:.0%})" for d in detections) or "No object detected"
        rule_set = routes()
        rules_text = "\n".join(
            f"- {label}: {rule['bin']} ({rule['bin_de']}). {rule['note']}" for label, rule in rule_set.items()
        )
        prompt = (
            "Answer entirely in English. You are helping sort one waste item in Germany. "
            f"The local model predictions are: {summary}. Treat these as hints, not facts. "
            "Identify the visible object and recommend the correct German disposal route, "
            "including a deposit return if applicable. Do not guess if the photo is unclear. "
            "Use exactly these five English lines:\n"
            "Object: ...\nBin: ...\nReason: ...\nConfidence: high/medium/low\n"
            "Note: ...\n"
            "Mention when local municipal rules or a deposit symbol should be checked. "
            "Use the following administrator-maintained local rules as guidance:\n"
            f"{rules_text}\n"
            "Respond in English only."
        )
        answer, tokens = run_llm(prompt, image_path)
        label = route_label_from_text(answer, rule_set)
        database.update_scan_review(scan_id, "llm", tokens, label)
        database.add_usage(user_id, "review", tokens)
        with jobs_lock:
            jobs[job_id] = {"status": "done", "answer": answer}
    except Exception as exc:
        with jobs_lock:
            jobs[job_id] = {"status": "error", "message": str(exc)}


@app.get("/")
def home():
    return render_template("index.html", threshold=int(DEFAULT_THRESHOLD * 100), user=current_user())


@app.get("/dashboard")
def dashboard():
    return render_template("dashboard.html", user=current_user())


@app.get("/history")
def history():
    return render_template("history.html", scans=database.history(), user=current_user())


@app.get("/admin/rules")
def admin_rules():
    denied = admin_required()
    if denied:
        return denied
    return render_template("rules.html", rules=routes(), user=current_user())


@app.get("/api/dashboard/stats")
def dashboard_stats():
    def selected(name: str) -> list[str]:
        values = request.args.getlist(name)
        return [value.strip() for value in values if value.strip()]

    stats = database.stats({
        "categories": selected("category"),
        "labels": selected("waste"),
        "confidence": selected("confidence"),
        "cities": selected("city"),
        "months": selected("month"),
    })
    stats["filters"]["waste"] = sorted(routes().keys())
    stats["municipality"] = {
        "areas": [
            {"name": "Dortmund-Mitte", "street": "Kampstraße", "recycling_rate": 68, "monthly_tons": 124},
            {"name": "Hörde", "street": "Hörder Bahnhofstraße", "recycling_rate": 74, "monthly_tons": 91},
            {"name": "Hombruch", "street": "Harkortstraße", "recycling_rate": 71, "monthly_tons": 83},
            {"name": "Aplerbeck", "street": "Köln-Berliner-Straße", "recycling_rate": 77, "monthly_tons": 76},
            {"name": "Bochum", "street": "Kortumstraße", "recycling_rate": 64, "monthly_tons": 118},
            {"name": "Lünen", "street": "Lange Straße", "recycling_rate": 61, "monthly_tons": 69},
        ],
        "monthly": [62, 64, 66, 65, 69, 72, 70, 74, 76, 75, 78, 80],
    }
    return jsonify(stats)


@app.post("/api/admin/rules")
def save_rule():
    denied = admin_required()
    if denied:
        return denied
    payload = request.get_json(silent=True) or {}
    label = str(payload.get("label", ""))
    if label not in routes():
        return jsonify(error="Unknown waste label."), 404
    fields = {key: str(payload.get(key, "")).strip() for key in
              ("category", "bin", "bin_de", "color", "hex", "theme", "symbol", "note")}
    if not all(fields.values()):
        return jsonify(error="All rule fields are required."), 400
    database.update_rule(label, fields)
    return jsonify(ok=True, rules=routes())


@app.post("/api/analyze")
def analyze():
    if "photo" not in request.files:
        return jsonify(error="Please take or upload a photo first."), 400
    try:
        threshold_percent = float(request.form.get("threshold", DEFAULT_THRESHOLD * 100))
    except (TypeError, ValueError):
        threshold_percent = DEFAULT_THRESHOLD * 100
    threshold = max(MIN_THRESHOLD, min(MAX_THRESHOLD, threshold_percent / 100))

    encoded = request.files["photo"].read()
    frame = cv2.imdecode(np.frombuffer(encoded, dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        return jsonify(error="The image could not be read. Please take another photo."), 400
    height, width = frame.shape[:2]
    if height < 80 or width < 80:
        return jsonify(error="The image is too small. Please take another photo."), 400

    # The local model inspects the normalized image; the API LLM provides explanations.
    if max(height, width) > 2000:
        scale = 2000 / max(height, width)
        frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    photo_id = uuid.uuid4().hex
    image_path = CAPTURE_DIR / f"web_{photo_id}.jpg"
    if not cv2.imwrite(str(image_path), frame):
        return jsonify(error="The photo could not be saved."), 500

    try:
        with model_lock:
            result = get_model().predict(frame, conf=0.10, imgsz=640,
                                         device=0 if torch.cuda.is_available() else "cpu", verbose=False)[0]
    except Exception as exc:
        return jsonify(error=f"Model prediction failed: {exc}"), 500

    detections = []
    for box in result.boxes:
        detections.append({
            "label": result.names[int(box.cls[0])],
            "confidence": round(float(box.conf[0]), 4),
            "box": [round(float(x), 1) for x in box.xyxy[0].tolist()],
        })
    detections.sort(key=lambda item: item["confidence"], reverse=True)
    top = detections[0] if detections else None
    needs_review = top is None or top["confidence"] < threshold
    rule_set = routes()
    route = rule_set.get(top["label"]) if top else None
    user = current_user()
    scan_id = database.add_scan(
        user["id"] if user else None, f"camera_captures/{image_path.name}", top["label"] if top else None,
        top["confidence"] if top else None, top["label"] if top else None,
        source="local", llm_used=0, llm_tokens=0,
    )
    response = {
        "photo_url": f"/api/photo/{image_path.name}",
        "image_size": [frame.shape[1], frame.shape[0]],
        "detections": detections,
        "top": top,
        "needs_review": needs_review,
        "threshold": round(threshold, 2),
        "route": route,
        "scan_id": scan_id,
    }
    if needs_review:
        job_id = uuid.uuid4().hex
        response["job_id"] = job_id
        threading.Thread(target=llm_review, args=(job_id, scan_id, user["id"] if user else None, image_path, detections), daemon=True).start()
    return jsonify(response)


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()
    if not message:
        return jsonify(error="Please enter a question."), 400
    if len(message) > 1200:
        return jsonify(error="Please keep the question under 1,200 characters."), 400

    image_path = None
    image_name = str(payload.get("image_name", ""))
    if image_name.startswith("web_") and image_name.endswith(".jpg"):
        candidate = CAPTURE_DIR / Path(image_name).name
        if candidate.exists():
            image_path = candidate
    prediction = str(payload.get("prediction", "No current model prediction"))[:300]
    prompt = (
        "Answer entirely in English as a friendly German waste-sorting assistant. "
        "Give practical, concise guidance and mention Pfand or local municipal differences when relevant. "
        f"Current custom YOLO context: {prediction}. "
        f"User question: {message}"
    )
    try:
        answer, tokens = run_llm(prompt, image_path)
        user = current_user()
        database.add_usage(user["id"] if user else None, "chat", tokens)
        return jsonify(answer=answer, estimated_tokens=tokens)
    except Exception as exc:
        return jsonify(error=str(exc)), 502


@app.get("/api/review/<job_id>")
def review(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
    if job is None:
        return jsonify(error="Review not found."), 404
    return jsonify(job)


@app.get("/api/photo/<name>")
def photo(name: str):
    if not name.startswith("web_") or not name.endswith(".jpg"):
        return jsonify(error="Photo not found."), 404
    return send_from_directory(CAPTURE_DIR, name)


@app.get("/api/tunnel/status")
def tunnel_status():
    return jsonify(public_tunnel_state())


@app.post("/api/tunnel/start")
def tunnel_start():
    global tunnel_process
    executable = find_cloudflared()
    if not executable:
        return jsonify(
            error="cloudflared is not installed. Install it, restart this app, and try again.",
            status="unavailable",
        ), 503
    with tunnel_lock:
        if tunnel_process is not None and tunnel_process.poll() is None:
            return jsonify(dict(tunnel_state))
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        try:
            tunnel_process = subprocess.Popen(
                [executable, "tunnel", "--url", LOCAL_APP_URL],
                cwd=ROOT,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                creationflags=creation_flags,
            )
        except Exception as exc:
            tunnel_process = None
            tunnel_state.update(status="error", url=None, message=f"Could not start cloudflared: {exc}")
            return jsonify(error=tunnel_state["message"], **tunnel_state), 500
        tunnel_state.update(
            status="starting", url=None,
            message="Cloudflare is creating a secure public URL…",
            started_at=int(time.time()),
        )
        process = tunnel_process
    threading.Thread(target=read_tunnel_output, args=(process,), daemon=True).start()
    return jsonify(public_tunnel_state()), 202


@app.post("/api/tunnel/stop")
def tunnel_stop():
    stop_tunnel_process()
    return jsonify(public_tunnel_state())


@app.errorhandler(413)
def too_large(_error):
    return jsonify(error="Photo is too large. Please use an image under 8 MB."), 413


def main() -> None:
    global MODEL_PATH, LOCAL_APP_URL, APP_PORT
    parser = argparse.ArgumentParser(description="Run the EcoSort AI waste-sorting dashboard.")
    parser.add_argument("--api-key", default=os.environ.get("LLM_API_KEY"), help="LLM API key; prefer LLM_API_KEY")
    parser.add_argument("--model", type=Path, default=MODEL_PATH)
    parser.add_argument("--llm-model", default=os.environ.get("LLM_MODEL", "gpt-4o-mini"))
    parser.add_argument("--llm-base-url", default=os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"))
    parser.add_argument("--host", default=os.environ.get("SORTLY_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=APP_PORT)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    MODEL_PATH = args.model
    APP_PORT = args.port
    LOCAL_APP_URL = f"http://127.0.0.1:{APP_PORT}"
    llm_client.api_key = args.api_key
    llm_client.model = args.llm_model
    llm_client.base_url = args.llm_base_url.rstrip("/")
    if not MODEL_PATH.exists():
        raise SystemExit(f"Trained model not found: {MODEL_PATH}")
    url = LOCAL_APP_URL
    print(f"Opening {url}", flush=True)
    if not args.no_browser:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    app.run(host=args.host, port=APP_PORT, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
