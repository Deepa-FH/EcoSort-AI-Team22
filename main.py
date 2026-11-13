"""EcoSort AI - application entry point.

Run (with your LLM API key):

    python main.py --api-key YOUR_KEY

or set the key once in the environment:

    PowerShell:  $env:LLM_API_KEY="YOUR_KEY"; python main.py
    bash/zsh  :  LLM_API_KEY=YOUR_KEY python main.py

Without a key the app still works: image recognition and the local recycling
rules run offline; only the AI chat / second opinion need the key.

Useful options:  --port 8000  --no-browser  --model path/to/best_model.pt  --help
"""

from __future__ import annotations

import threading
import webbrowser

from subsystem_4_web_integration import AppConfig, create_application


def main(argv: list[str] | None = None) -> None:
    """Read the settings, build the application and start the web server."""
    config = AppConfig.from_cli(argv)
    if not config.model_path.is_file():
        raise SystemExit(f"Trained model not found: {config.model_path}\n"
                         "Pass the weights with --model PATH or set WASTE_MODEL_PATH.")

    app = create_application(config)

    print("EcoSort AI starting with:", config.describe(), flush=True)
    if not config.api_key:
        print("NOTE: no API key supplied -> Ask AI falls back to local rules. "
              "Use --api-key or LLM_API_KEY to enable it.", flush=True)

    app.warm_up()        # load the model now: a broken model file fails here, not on the first scan
    print(f"Open {config.local_url}  (default sign-in: {config.admin_username} / admin)", flush=True)
    if config.open_browser:
        threading.Timer(1.2, lambda: webbrowser.open(config.local_url)).start()
    app.run()


if __name__ == "__main__":
    main()
