"""AppConfig - every setting of the application in ONE place.

Priority (highest first):  command-line option  >  environment variable  >  default.
That is why ``python main.py --api-key KEY`` and ``docker run -e LLM_API_KEY=KEY``
both work.
"""

from __future__ import annotations

import argparse
import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _env_flag(name: str, default: bool) -> bool:
    """Read a true/false environment variable (``1``, ``true``, ``yes`` = True)."""
    value = os.environ.get(name)
    return default if value is None else value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class AppConfig:
    """Plain settings object (a dataclass: attributes + generated ``__init__``)."""

    root: Path = PROJECT_ROOT
    model_path: Path = field(default_factory=lambda: Path(
        os.environ.get("WASTE_MODEL_PATH", PROJECT_ROOT / "models" / "best_model.pt")))
    data_dir: Path = field(default_factory=lambda: Path(os.environ.get("SORTLY_DATA_DIR", PROJECT_ROOT / "data")))
    db_path: Path | None = None                 # default: <data_dir>/sortly.sqlite3
    host: str = field(default_factory=lambda: os.environ.get("SORTLY_HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: int(os.environ.get("SORTLY_PORT", "5000")))
    open_browser: bool = field(default_factory=lambda: not _env_flag("SORTLY_NO_BROWSER", False))
    tunnel_enabled: bool = field(default_factory=lambda: _env_flag("SORTLY_ENABLE_TUNNEL", True))
    # --- LLM (Ask AI) ---
    api_key: str | None = field(default_factory=lambda: os.environ.get("LLM_API_KEY") or None)
    llm_model: str = field(default_factory=lambda: os.environ.get("LLM_MODEL", "mistralai-mistral-small-4"))
    llm_base_url: str = field(default_factory=lambda: os.environ.get("LLM_BASE_URL", "https://chat.kiconnect.nrw/api/v1"))
    # --- accounts / security ---
    admin_username: str = field(default_factory=lambda: os.environ.get("SORTLY_USERNAME", "admin"))
    admin_password: str = field(default_factory=lambda: os.environ.get("SORTLY_PASSWORD", "admin"))
    signup_code: str = field(default_factory=lambda: os.environ.get("SORTLY_SIGNUP_CODE", "pythonai"))
    secret_key: str = field(default_factory=lambda: os.environ.get("SORTLY_SECRET_KEY") or secrets.token_hex(32))
    # --- behaviour ---
    default_threshold: float = 0.65

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self.model_path = Path(self.model_path)
        self.data_dir = Path(self.data_dir)
        self.db_path = Path(self.db_path) if self.db_path else Path(
            os.environ.get("SORTLY_DB_PATH", self.data_dir / "sortly.sqlite3"))

    # ---- derived paths ---------------------------------------------------
    @property
    def capture_dir(self) -> Path:
        """Folder where uploaded/captured photos are stored."""
        return self.data_dir / "camera_captures"

    @property
    def template_dir(self) -> Path:
        return self.root / "templates"

    @property
    def static_dir(self) -> Path:
        return self.root / "static"

    @property
    def local_url(self) -> str:
        """URL the Cloudflare tunnel forwards to (always loopback)."""
        return f"http://127.0.0.1:{self.port}"

    # ---- factory: command line -------------------------------------------
    @classmethod
    def from_cli(cls, argv: list[str] | None = None) -> "AppConfig":
        """Build the configuration from command-line arguments.

        Example:  ``python main.py --api-key KEY --port 8000 --no-browser``
        """
        defaults = cls()
        parser = argparse.ArgumentParser(
            description="EcoSort AI - waste sorting and recycling assistant (Flask web app).")
        parser.add_argument("--api-key", default=defaults.api_key,
                            help="LLM API key (or set the LLM_API_KEY environment variable)")
        parser.add_argument("--model", type=Path, default=defaults.model_path, help="path to the YOLO weights")
        parser.add_argument("--llm-model", default=defaults.llm_model, help="LLM model name")
        parser.add_argument("--llm-base-url", default=defaults.llm_base_url, help="OpenAI-compatible API URL")
        parser.add_argument("--host", default=defaults.host, help="use 0.0.0.0 inside Docker")
        parser.add_argument("--port", type=int, default=defaults.port)
        parser.add_argument("--data-dir", type=Path, default=defaults.data_dir,
                            help="where the database and photos are stored")
        parser.add_argument("--no-browser", action="store_true", help="do not open a browser window")
        parser.add_argument("--no-tunnel", action="store_true", help="hide/disable the Cloudflare 'Go live' feature")
        args = parser.parse_args(argv)
        config = cls(
            model_path=args.model, data_dir=args.data_dir, host=args.host, port=args.port,
            api_key=args.api_key, llm_model=args.llm_model, llm_base_url=args.llm_base_url,
            open_browser=defaults.open_browser and not args.no_browser,
            tunnel_enabled=defaults.tunnel_enabled and not args.no_tunnel,
        )
        return config

    def describe(self) -> dict:
        """Settings safe to print (the API key is NOT included, only whether it exists)."""
        return {"model": str(self.model_path), "data_dir": str(self.data_dir), "host": self.host,
                "port": self.port, "llm_model": self.llm_model, "llm_base_url": self.llm_base_url,
                "api_key": "set" if self.api_key else "missing", "tunnel": self.tunnel_enabled}
