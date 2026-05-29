"""
Custom exception hierarchy for the ticket resolution bot.

This module defines a comprehensive exception hierarchy that provides
clear, specific error types for different failure scenarios.
"""

from typing import Optional, Dict, Any


class TicketBotException(Exception):
    """Base exception for all ticket bot errors."""
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.original_exception = original_exception
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


# Configuration Exceptions
class ConfigurationError(TicketBotException):
    """Raised when there's a configuration issue."""
    pass


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing."""
    pass


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration values are invalid."""
    pass


# AI Processing Exceptions
class AIProcessingError(TicketBotException):
    """Base exception for AI-related errors."""
    pass


class ModelLoadError(AIProcessingError):
    """Raised when AI model fails to load."""
    pass


class ClassificationError(AIProcessingError):
    """Raised when ticket classification fails."""
    pass


class EmbeddingError(AIProcessingError):
    """Raised when embedding generation fails."""
    pass


class RAGError(AIProcessingError):
    """Raised when RAG processing fails."""
    pass


# External Service Exceptions
class ExternalServiceError(TicketBotException):
    """Base exception for external service errors."""
    pass


class FreshdeskAPIError(ExternalServiceError):
    """Raised when Freshdesk API call fails."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_body = response_body
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["status_code"] = self.status_code
        data["response_body"] = self.response_body
        return data


class FreshdeskAuthenticationError(FreshdeskAPIError):
    """Raised when Freshdesk authentication fails."""
    pass


class FreshdeskRateLimitError(FreshdeskAPIError):
    """Raised when Freshdesk rate limit is exceeded."""
    pass


class FreshdeskConnectionError(FreshdeskAPIError):
    """Raised when connection to Freshdesk fails."""
    pass


# Database Exceptions
class DatabaseError(TicketBotException):
    """Base exception for database errors."""
    pass


class TicketNotFoundError(DatabaseError):
    """Raised when a ticket is not found in the database."""
    
    def __init__(self, ticket_id: int, **kwargs):
        message = f"Ticket with ID {ticket_id} not found"
        super().__init__(message, details={"ticket_id": ticket_id}, **kwargs)
        self.ticket_id = ticket_id


class DuplicateTicketError(DatabaseError):
    """Raised when attempting to create a duplicate ticket."""
    
    def __init__(self, freshdesk_id: int, **kwargs):
        message = f"Ticket with Freshdesk ID {freshdesk_id} already exists"
        super().__init__(message, details={"freshdesk_id": freshdesk_id}, **kwargs)
        self.freshdesk_id = freshdesk_id


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass


# Validation Exceptions
class ValidationError(TicketBotException):
    """Base exception for validation errors."""
    pass


class InvalidTicketDataError(ValidationError):
    """Raised when ticket data is invalid."""
    pass


class InvalidWebhookDataError(ValidationError):
    """Raised when webhook data is invalid."""
    pass


class InvalidQueryError(ValidationError):
    """Raised when a query is invalid."""
    pass


# Processing Exceptions
class ProcessingError(TicketBotException):
    """Base exception for ticket processing errors."""
    pass


class TicketProcessingError(ProcessingError):
    """Raised when ticket processing fails."""
    
    def __init__(self, ticket_id: int, stage: str, **kwargs):
        message = f"Failed to process ticket {ticket_id} at stage: {stage}"
        super().__init__(
            message, 
            details={"ticket_id": ticket_id, "stage": stage}, 
            **kwargs
        )
        self.ticket_id = ticket_id
        self.stage = stage


class EscalationError(ProcessingError):
    """Raised when ticket escalation fails."""
    pass


class ResolutionError(ProcessingError):
    """Raised when ticket resolution fails."""
    pass


# Cache Exceptions
class CacheError(TicketBotException):
    """Base exception for cache-related errors."""
    pass


class CacheConnectionError(CacheError):
    """Raised when cache connection fails."""
    pass


class CacheKeyError(CacheError):
    """Raised when cache key is invalid or not found."""
    pass
