"""Configuration modules for the ticket resolution bot."""

from .settings import settings, Settings
from .ai_config import ai_config, classification_config, AIConfig, ClassificationConfig
from .freshdesk_config import freshdesk_config, FreshdeskConfig
from .templates import ResponseTemplates, RESPONSE_TEMPLATES

__all__ = [
    "settings",
    "Settings",
    "ai_config",
    "classification_config",
    "AIConfig",
    "ClassificationConfig",
    "freshdesk_config",
    "FreshdeskConfig",
    "ResponseTemplates",
    "RESPONSE_TEMPLATES",
]
