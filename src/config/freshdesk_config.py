"""
Freshdesk integration configuration.

This module contains all Freshdesk-specific settings.
"""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class FreshdeskConfig(BaseSettings):
    """
    Freshdesk API configuration settings.
    
    Configures connection to Freshdesk ticketing system.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="FRESHDESK_",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Credentials
    domain: str = Field(
        default="",
        description="Freshdesk domain (e.g., 'yourcompany')"
    )
    api_key: str = Field(
        default="",
        description="Freshdesk API key"
    )
    webhook_secret: str = Field(
        default="",
        description="Webhook secret for signature verification"
    )
    
    # API Configuration
    api_version: str = Field(
        default="v2",
        description="Freshdesk API version"
    )
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="API request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts"
    )
    retry_delay: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Delay between retries in seconds"
    )
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    rate_limit_calls: int = Field(
        default=100,
        ge=1,
        description="Maximum API calls per period"
    )
    rate_limit_period: int = Field(
        default=60,
        ge=1,
        description="Rate limit period in seconds"
    )
    
    # Connection Pooling
    pool_connections: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of connection pool connections"
    )
    pool_maxsize: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum size of connection pool"
    )
    
    # Circuit Breaker
    circuit_breaker_enabled: bool = Field(
        default=True,
        description="Enable circuit breaker pattern"
    )
    circuit_breaker_threshold: int = Field(
        default=5,
        ge=1,
        description="Number of failures before opening circuit"
    )
    circuit_breaker_timeout: int = Field(
        default=60,
        ge=1,
        description="Circuit breaker timeout in seconds"
    )
    
    # Status Codes
    status_open: int = Field(default=2, description="Open ticket status code")
    status_pending: int = Field(default=3, description="Pending ticket status code")
    status_resolved: int = Field(default=4, description="Resolved ticket status code")
    status_closed: int = Field(default=5, description="Closed ticket status code")
    
    # Priority Codes
    priority_low: int = Field(default=1, description="Low priority code")
    priority_medium: int = Field(default=2, description="Medium priority code")
    priority_high: int = Field(default=3, description="High priority code")
    priority_urgent: int = Field(default=4, description="Urgent priority code")
    
    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        """Validate Freshdesk domain."""
        if v and v.startswith("https://"):
            # Extract domain from full URL
            v = v.replace("https://", "").replace(".freshdesk.com", "")
        return v.strip()
    
    @property
    def base_url(self) -> str:
        """Get Freshdesk API base URL."""
        if not self.domain:
            return ""
        return f"https://{self.domain}.freshdesk.com/api/{self.api_version}"
    
    @property
    def is_configured(self) -> bool:
        """Check if Freshdesk is properly configured."""
        return bool(self.domain and self.api_key)
    
    def get_auth(self) -> tuple:
        """Get authentication tuple for requests."""
        return (self.api_key, "X")


# Global configuration instance
freshdesk_config = FreshdeskConfig()
