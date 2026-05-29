"""
Base settings configuration for the ticket resolution bot.

This module provides centralized configuration management with
environment variable support and validation.
"""

import os
from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Main application settings.
    
    All settings can be overridden via environment variables.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application Metadata
    app_name: str = Field(
        default="AI Customer Ticket Resolution Bot",
        description="Application name"
    )
    app_version: str = Field(
        default="2.0.0",
        description="Application version"
    )
    environment: str = Field(
        default="development",
        description="Environment: development, staging, production"
    )
    
    # Server Configuration
    host: str = Field(
        default="0.0.0.0",
        description="Server host address"
    )
    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Server port number"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    reload: bool = Field(
        default=False,
        description="Enable auto-reload on code changes"
    )
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./tickets.db",
        description="Database connection URL"
    )
    database_pool_size: int = Field(
        default=5,
        ge=1,
        description="Database connection pool size"
    )
    database_max_overflow: int = Field(
        default=10,
        ge=0,
        description="Maximum overflow connections"
    )
    database_echo: bool = Field(
        default=False,
        description="Enable SQL query logging"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    log_file: str = Field(
        default="bot.log",
        description="Log file path"
    )
    log_rotation: str = Field(
        default="10 MB",
        description="Log file rotation size"
    )
    log_retention: str = Field(
        default="30 days",
        description="Log file retention period"
    )
    log_format: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        description="Log message format"
    )
    
    # Security Configuration
    secret_key: str = Field(
        default="change-this-in-production",
        description="Secret key for signing tokens"
    )
    allowed_origins: list[str] = Field(
        default=["*"],
        description="CORS allowed origins"
    )
    
    # Performance Configuration
    enable_caching: bool = Field(
        default=True,
        description="Enable caching"
    )
    cache_ttl: int = Field(
        default=3600,
        ge=0,
        description="Default cache TTL in seconds"
    )
    max_workers: int = Field(
        default=4,
        ge=1,
        description="Maximum worker threads"
    )
    
    # Feature Flags
    enable_auto_resolution: bool = Field(
        default=True,
        description="Enable automatic ticket resolution"
    )
    enable_escalation: bool = Field(
        default=True,
        description="Enable ticket escalation"
    )
    enable_analytics: bool = Field(
        default=True,
        description="Enable analytics collection"
    )
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v.lower() not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v.lower()
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level value."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of: {allowed}")
        return v.upper()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


# Global settings instance
settings = Settings()
