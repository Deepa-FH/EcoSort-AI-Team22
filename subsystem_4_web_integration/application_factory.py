"""Composition root: the ONE place where all objects are created and connected.

Reading this file top to bottom shows how the four subsystems fit together.
Tests call ``create_application`` with fake detectors / LLM clients (dependency injection).
"""

from __future__ import annotations

from subsystem_1_dataset_preprocessing import ImageValidator, PreprocessingPipeline
from subsystem_2_image_recognition import ImageRecognitionService, WasteDetector
from subsystem_3_recycling_ai import (DEFAULT_RULES, OpenAICompatibleClient, PromptBuilder,
                                      RecyclingRuleEngine, WasteAssistant)

from .app_config import AppConfig
from .dashboard_service import DashboardService
from .database import Database
from .integration_controller import IntegrationController
from .review_jobs import ReviewJobManager
from .scan_service import ScanService
from .tunnel_manager import TunnelManager
from .user_repository import AuthService, UserRepository
from .waste_repository import WasteRepository
from .waste_sorting_web_app import WasteSortingWebApp


def create_application(config: AppConfig, detector: WasteDetector | None = None,
                       llm_client: OpenAICompatibleClient | None = None,
                       run_reviews_in_background: bool = True) -> WasteSortingWebApp:
    """Build the full application.

    Args:
        config: settings (paths, API key ...).
        detector: pass a fake detector in tests; ``None`` builds the real YOLO detector.
        llm_client: pass a fake LLM in tests; ``None`` builds the real API client.
        run_reviews_in_background: tests set ``False`` so reviews finish immediately.
    """
    # --- Subsystem 4: storage ---------------------------------------------
    database = Database(config.db_path)
    database.initialize(config.admin_username, config.admin_password,
                        [rule.to_dict() for rule in DEFAULT_RULES])
    repository = WasteRepository(database)

    # --- Subsystem 3: rules + assistant -----------------------------------
    rules = RecyclingRuleEngine(repository)           # the repository acts as the RuleStore
    llm = llm_client or OpenAICompatibleClient(config.api_key, config.llm_model, config.llm_base_url)
    assistant = WasteAssistant(rules, llm, PromptBuilder())

    # --- Subsystem 2: recognition -----------------------------------------
    detector = detector or WasteDetector(config.model_path)
    recognition = ImageRecognitionService(detector, config.default_threshold)

    # --- Subsystem 1 + 4: scan workflow -----------------------------------
    scans = ScanService(ImageValidator(), PreprocessingPipeline.default(), recognition, rules,
                        repository, config.capture_dir)
    jobs = ReviewJobManager(assistant, repository, run_in_background=run_reviews_in_background)
    dashboard = DashboardService(repository, lambda: rules.all().keys())
    controller = IntegrationController(scans, assistant, rules, jobs, dashboard, repository,
                                       default_threshold_percent=config.default_threshold * 100)

    auth = AuthService(UserRepository(database), config.signup_code)
    tunnel = TunnelManager(config.local_url, enabled=config.tunnel_enabled, working_dir=config.root)
    return WasteSortingWebApp(config, controller, auth, tunnel)
