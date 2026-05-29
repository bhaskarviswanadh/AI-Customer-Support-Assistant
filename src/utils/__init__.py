"""Utility modules for the ticket resolution bot."""

from .exceptions import (
    TicketBotException,
    ConfigurationError,
    AIProcessingError,
    ExternalServiceError,
    DatabaseError,
    ValidationError,
    ProcessingError,
    FreshdeskAPIError,
    TicketNotFoundError,
    InvalidTicketDataError,
    InvalidWebhookDataError,
    InvalidQueryError,
)

from .validators import (
    TicketValidator,
    WebhookValidator,
    QueryValidator,
    DataValidator,
)

from .helpers import (
    generate_hash,
    truncate_text,
    extract_keywords,
    format_datetime,
    parse_datetime,
    time_ago,
    safe_json_loads,
    safe_json_dumps,
    merge_dicts,
    chunk_list,
    calculate_percentage,
    sanitize_filename,
    get_nested_value,
    set_nested_value,
)

__all__ = [
    # Exceptions
    "TicketBotException",
    "ConfigurationError",
    "AIProcessingError",
    "ExternalServiceError",
    "DatabaseError",
    "ValidationError",
    "ProcessingError",
    "FreshdeskAPIError",
    "TicketNotFoundError",
    "InvalidTicketDataError",
    "InvalidWebhookDataError",
    "InvalidQueryError",
    # Validators
    "TicketValidator",
    "WebhookValidator",
    "QueryValidator",
    "DataValidator",
    # Helpers
    "generate_hash",
    "truncate_text",
    "extract_keywords",
    "format_datetime",
    "parse_datetime",
    "time_ago",
    "safe_json_loads",
    "safe_json_dumps",
    "merge_dicts",
    "chunk_list",
    "calculate_percentage",
    "sanitize_filename",
    "get_nested_value",
    "set_nested_value",
]
