from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App basics
    APP_NAME: str = "AI Customer Ticket Resolution Bot"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server config
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Freshdesk credentials
    FRESHDESK_DOMAIN: str = ""
    FRESHDESK_API_KEY: str = ""
    FRESHDESK_WEBHOOK_SECRET: str = ""
    
    # AI model settings
    MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    CLASSIFICATION_MODEL: str = "facebook/bart-large-mnli"
    
    # Database
    DATABASE_URL: str = "sqlite:///./tickets.db"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "bot.log"
    
    # Keywords for classification
    TIER_1_KEYWORDS: List[str] = [
        "password", "reset", "login", "forgot", "access",
        "unlock", "username", "credentials", "sign in"
    ]
    
    TIER_2_KEYWORDS: List[str] = [
        "billing", "payment", "invoice", "subscription", "upgrade",
        "downgrade", "refund", "charge", "account", "settings"
    ]
    
    COMPLEX_KEYWORDS: List[str] = [
        "error", "bug", "crash", "broken", "not working", "issue",
        "problem", "critical", "urgent", "system", "technical"
    ]
    
    # Response templates
    AUTO_RESPONSE_TEMPLATES: dict = {
        "tier_1": {
            "greeting": "Hi there! I can help you with that.",
            "closing": "Let me know if you need anything else!"
        },
        "tier_2": {
            "greeting": "Thanks for reaching out.",
            "closing": "I've provided some info that should help."
        },
        "complex": {
            "greeting": "I've received your ticket.",
            "closing": "A human agent will get back to you soon."
        }
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()