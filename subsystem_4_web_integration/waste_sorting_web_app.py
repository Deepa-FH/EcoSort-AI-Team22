"""WasteSortingWebApp - the Flask application, written as a class.

All routes are small methods that (1) read the HTTP request, (2) call the
``IntegrationController`` or a service, and (3) return a page or JSON.
No business logic lives here ("Separate UI from business logic" - PPT).

Route overview
--------------
Pages  : /login  /signup  /  /dashboard  /history  /admin/rules
API    : /api/analyze  /api/chat  /api/review/<id>  /api/photo/<name>
         /api/dashboard/stats  /api/dashboard/export.csv  /api/admin/rules
         /api/tunnel/status|start|stop     /health
"""

from __future__ import annotations

import atexit
from datetime import timedelta
from typing import Any

from flask import (Flask, Response, jsonify, redirect, render_template, request,
                   send_from_directory, session, url_for)

from shared.error_handling import BaseErrorHandler, EcoSortError
from subsystem_1_dataset_preprocessing import DatasetErrorHandler, PreprocessingError
from subsystem_2_image_recognition import RecognitionError, RecognitionErrorHandler
from subsystem_3_recycling_ai import RecyclingAIError, RecyclingAIErrorHandler

from .app_config import AppConfig
from .exceptions import (AuthenticationError, PermissionDeniedError, ValidationFailedError,
                         WebDashboardErrorHandler)
from .integration_controller import IntegrationController
from .scan_service import is_valid_photo_name
from .tunnel_manager import TunnelManager
from .user_repository import AuthService

#: Roles allowed to see the dashboard (normal users may not).
DASHBOARD_ROLES = ("admin", "municipality")

#: Pages anybody may open without signing in.
PUBLIC_ENDPOINTS = {"login", "signup", "static", "health"}


class WasteSortingWebApp:
    """Builds and configures the Flask ``app`` object."""

    def __init__(self, config: AppConfig, controller: IntegrationController,
                 auth: AuthService, tunnel: TunnelManager):
        self._config = config
        self._controller = controller
        self._auth = auth
        self._tunnel = tunnel
        # Each subsystem owns an error handler; the web layer picks the right one by exception type.
        self._error_handlers: list[tuple[type[EcoSortError], BaseErrorHandler]] = [
            (PreprocessingError, DatasetErrorHandler()),
            (RecognitionError, RecognitionErrorHandler()),
            (RecyclingAIError, RecyclingAIErrorHandler()),
        ]
        self._fallback_handler = WebDashboardErrorHandler()
        self.flask_app = self._create_flask_app()
        atexit.register(self._tunnel.stop)       # never leave a tunnel running after exit

    # =====================================================================
    # Flask set-up
    # =====================================================================
    def _create_flask_app(self) -> Flask:
        cfg = self._config
        app = Flask(__name__, template_folder=str(cfg.template_dir), static_folder=str(cfg.static_dir))
        app.config.update(
            MAX_CONTENT_LENGTH=8 * 1024 * 1024,           # reject uploads over 8 MB
            SECRET_KEY=cfg.secret_key,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE="Lax",
            PERMANENT_SESSION_LIFETIME=timedelta(hours=12),
        )
        app.before_request(self._require_login)
        app.context_processor(self._template_context)
        app.register_error_handler(EcoSortError, self._on_ecosort_error)
        app.register_error_handler(413, self._on_too_large)

        def route(rule: str, endpoint: str, view, methods: tuple[str, ...] = ("GET",)) -> None:
            app.add_url_rule(rule, endpoint=endpoint, view_func=view, methods=list(methods))

        # pages
        route("/login", "login", self.login, ("GET", "POST"))
        route("/signup", "signup", self.signup, ("GET", "POST"))
        route("/logout", "logout", self.logout, ("POST",))
        route("/", "home", self.home)
        route("/dashboard", "dashboard", self.dashboard)
        route("/history", "history", self.history)
        route("/admin/rules", "admin_rules", self.admin_rules)
        # api
        route("/health", "health", self.health)
        route("/api/analyze", "analyze", self.analyze, ("POST",))
        route("/api/chat", "chat", self.chat, ("POST",))
        route("/api/review/<job_id>", "review", self.review)
        route("/api/photo/<name>", "photo", self.photo)
        route("/api/dashboard/stats", "dashboard_stats", self.dashboard_stats)
        route("/api/dashboard/export.csv", "export_csv", self.export_csv)
        route("/api/admin/rules", "save_rule", self.save_rule, ("POST",))
        route("/api/tunnel/status", "tunnel_status", self.tunnel_status)
        route("/api/tunnel/start", "tunnel_start", self.tunnel_start, ("POST",))
        route("/api/tunnel/stop", "tunnel_stop", self.tunnel_stop, ("POST",))
        return app

    # =====================================================================
    # Hooks
    # =====================================================================
    def _require_login(self):
        """Runs before every request: send anonymous visitors to /login."""
        if request.endpoint in PUBLIC_ENDPOINTS:
            return None
        if session.get("user_id"):
            return None
        if request.path.startswith("/api/"):
            return jsonify(error=AuthenticationError().safe_message, code="AUTH_REQUIRED"), 401
        return redirect(url_for("login"))

    def _template_context(self) -> dict[str, Any]:
        """Variables available in every HTML template."""
        return {"user": self.current_user(), "tunnel_enabled": self._tunnel.enabled,
                "ai_ready": self._controller.ai_available, "active_page": request.endpoint}

    def _on_ecosort_error(self, error: EcoSortError):
        """Turn any project exception into a safe JSON answer (no stack trace)."""
        handler = next((h for base, h in self._error_handlers if isinstance(error, base)), self._fallback_handler)
        response = handler.handle(error)
        return jsonify(error=response.message, code=response.code, recoverable=response.recoverable), response.http_status

    @staticmethod
    def _on_too_large(_error):
        return jsonify(error="Photo is too large. Please use an image under 8 MB.", code="IMAGE_TOO_LARGE"), 413

    # =====================================================================
    # Session helpers
    # =====================================================================
    @staticmethod
    def current_user() -> dict[str, Any] | None:
        """The signed-in user stored in the session cookie, or ``None``."""
        if not session.get("user_id"):
            return None
        return {"id": session["user_id"], "username": session.get("username", ""), "role": session.get("role", "user")}

    @staticmethod
    def _has_role(*roles: str) -> bool:
        return session.get("role") in roles

    def _require_role(self, *roles: str) -> None:
        """Raise ``PermissionDeniedError`` (-> HTTP 403) unless the user has one of ``roles``.

        Access matrix: admin = everything | municipality = assistant + dashboard |
        user = assistant + settings only.
        """
        if not self._has_role(*roles):
            raise PermissionDeniedError(f"role {session.get('role')!r} not in {roles}")

    def _user_id(self) -> int | None:
        user = self.current_user()
        return user["id"] if user else None

    # =====================================================================
    # Pages
    # =====================================================================
    def login(self):
        error = None
        if request.method == "POST":
            try:
                user = self._auth.login(request.form.get("username", ""), request.form.get("password", ""),
                                        request.form.get("role") or None)
            except AuthenticationError:
                error = "Incorrect username, password or role."
            else:
                session.clear()
                session.update(user_id=user["id"], username=user["username"], role=user["role"])
                session.permanent = True
                return redirect(url_for("home"))
        return render_template("login.html", error=error)

    def signup(self):
        error = None
        if request.method == "POST":
            try:
                self._auth.register(request.form.get("username", "").strip(), request.form.get("password", ""),
                                    request.form.get("role", "user"), request.form.get("signup_code", ""))
                return redirect(url_for("login", registered="1"))
            except ValidationFailedError as exc:        # includes UserExistsError
                error = exc.safe_message
        return render_template("signup.html", error=error)

    def logout(self):
        session.clear()
        return redirect(url_for("login"))

    def home(self):
        return render_template("index.html", threshold=round(self._config.default_threshold * 100),
                               rules=self._controller.rules.as_dicts())

    def dashboard(self):
        if not self._has_role(*DASHBOARD_ROLES):
            return redirect(url_for("home"))
        recent = self._controller.repository.history(limit=12) if self._has_role("admin") else []
        return render_template("dashboard.html", rules=self._controller.rules.as_dicts(), recent=recent)

    def history(self):
        if not self._has_role("admin"):               # scan history contains user names: admin only
            return redirect(url_for("home"))
        return render_template("history.html", scans=self._controller.repository.history())

    def admin_rules(self):
        if not self._has_role("admin"):
            return redirect(url_for("home"))
        return render_template("rules.html", rules=self._controller.rules.as_dicts())

    # =====================================================================
    # API
    # =====================================================================
    def health(self):
        """Used by Docker's health check; needs no login."""
        return jsonify(status="ok", ai_ready=self._controller.ai_available)

    def analyze(self):
        upload = request.files.get("photo")
        data = upload.read() if upload else None
        return jsonify(self._controller.analyze_photo(data, request.form.get("threshold"), self._user_id()))

    def chat(self):
        return jsonify(self._controller.chat(request.get_json(silent=True) or {}, self._user_id()))

    def review(self, job_id: str):
        return jsonify(self._controller.review_status(job_id))

    def photo(self, name: str):
        if not is_valid_photo_name(name):
            return jsonify(error="Photo not found."), 404
        return send_from_directory(self._controller.capture_dir, name)

    def dashboard_stats(self):
        self._require_role(*DASHBOARD_ROLES)
        def selected(name: str) -> list[str]:
            return [v.strip() for v in request.args.getlist(name) if v.strip()]

        filters = {"categories": selected("category"), "labels": selected("waste"),
                   "confidence": selected("confidence"), "cities": selected("city"), "months": selected("month")}
        return jsonify(self._controller.dashboard.get_statistics(filters))

    def export_csv(self):
        self._require_role("admin")
        csv_text = self._controller.dashboard.export_history_csv()
        return Response(csv_text, mimetype="text/csv",
                        headers={"Content-Disposition": "attachment; filename=ecosort_scans.csv"})

    def save_rule(self):
        self._require_role("admin")
        return jsonify(ok=True, rules=self._controller.update_rule(request.get_json(silent=True) or {}))

    # ---- tunnel (local Python only) ---------------------------------------
    def tunnel_status(self):
        self._require_role("admin")
        return jsonify(self._tunnel.state())

    def tunnel_start(self):
        self._require_role("admin")
        state, status = self._tunnel.start()
        return jsonify(state), status

    def tunnel_stop(self):
        self._require_role("admin")
        return jsonify(self._tunnel.stop())

    # =====================================================================
    # Running
    # =====================================================================
    def warm_up(self) -> None:
        """Load the YOLO model before the first request."""
        self._controller.warm_up()

    def run(self) -> None:
        """Start the built-in server (blocks until Ctrl+C)."""
        self.flask_app.run(host=self._config.host, port=self._config.port,
                           debug=False, use_reloader=False, threaded=True)
