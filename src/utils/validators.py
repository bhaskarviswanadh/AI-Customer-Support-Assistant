"""
Input validation utilities.

This module provides validation functions for ticket data,
webhook payloads, and other inputs.
"""

import re
from typing import Dict, List, Optional, Any
from email.utils import parseaddr

from .exceptions import (
    InvalidTicketDataError,
    InvalidWebhookDataError,
    InvalidQueryError,
    ValidationError
)


class TicketValidator:
    """Validates ticket data."""
    
    # Validation constants
    MIN_SUBJECT_LENGTH = 3
    MAX_SUBJECT_LENGTH = 500
    MIN_DESCRIPTION_LENGTH = 10
    MAX_DESCRIPTION_LENGTH = 10000
    
    @classmethod
    def validate_ticket_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate ticket data from webhook or API.
        
        Args:
            data: Ticket data dictionary
            
        Returns:
            Validated and sanitized ticket data
            
        Raises:
            InvalidTicketDataError: If validation fails
        """
        errors = []
        
        # Validate required fields
        required_fields = ['subject', 'description']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            raise InvalidTicketDataError(
                "Ticket data validation failed",
                details={"errors": errors}
            )
        
        # Validate subject
        subject = str(data['subject']).strip()
        if len(subject) < cls.MIN_SUBJECT_LENGTH:
            errors.append(
                f"Subject too short (minimum {cls.MIN_SUBJECT_LENGTH} characters)"
            )
        if len(subject) > cls.MAX_SUBJECT_LENGTH:
            errors.append(
                f"Subject too long (maximum {cls.MAX_SUBJECT_LENGTH} characters)"
            )
        
        # Validate description
        description = str(data['description']).strip()
        if len(description) < cls.MIN_DESCRIPTION_LENGTH:
            errors.append(
                f"Description too short (minimum {cls.MIN_DESCRIPTION_LENGTH} characters)"
            )
        if len(description) > cls.MAX_DESCRIPTION_LENGTH:
            errors.append(
                f"Description too long (maximum {cls.MAX_DESCRIPTION_LENGTH} characters)"
            )
        
        # Validate email if provided
        if 'customer_email' in data and data['customer_email']:
            if not cls.is_valid_email(data['customer_email']):
                errors.append(f"Invalid email address: {data['customer_email']}")
        
        # Validate priority if provided
        if 'priority' in data:
            try:
                priority = int(data['priority'])
                if priority not in [1, 2, 3, 4]:
                    errors.append("Priority must be 1, 2, 3, or 4")
            except (ValueError, TypeError):
                errors.append("Priority must be an integer")
        
        if errors:
            raise InvalidTicketDataError(
                "Ticket data validation failed",
                details={"errors": errors}
            )
        
        # Return sanitized data
        return {
            'subject': subject,
            'description': description,
            'customer_email': data.get('customer_email', '').strip(),
            'priority': int(data.get('priority', 1)),
            'freshdesk_id': data.get('id') or data.get('freshdesk_id'),
        }
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not email:
            return False
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize text input by removing potentially harmful content.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text


class WebhookValidator:
    """Validates webhook payloads."""
    
    @staticmethod
    def validate_freshdesk_webhook(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Freshdesk webhook payload.
        
        Args:
            data: Webhook payload
            
        Returns:
            Validated webhook data
            
        Raises:
            InvalidWebhookDataError: If validation fails
        """
        if not data:
            raise InvalidWebhookDataError("Empty webhook payload")
        
        # Check for Freshdesk webhook structure
        if 'freshdesk_webhook' not in data:
            raise InvalidWebhookDataError(
                "Invalid webhook structure: missing 'freshdesk_webhook' key"
            )
        
        webhook_data = data['freshdesk_webhook']
        
        # Validate ticket_id
        if 'ticket_id' not in webhook_data:
            raise InvalidWebhookDataError(
                "Invalid webhook: missing 'ticket_id'"
            )
        
        try:
            ticket_id = int(webhook_data['ticket_id'])
            if ticket_id <= 0:
                raise ValueError("Ticket ID must be positive")
        except (ValueError, TypeError) as e:
            raise InvalidWebhookDataError(
                f"Invalid ticket_id: {webhook_data.get('ticket_id')}",
                original_exception=e
            )
        
        return {
            'ticket_id': ticket_id,
            'event_type': webhook_data.get('event_type', 'ticket_created'),
            'triggered_at': webhook_data.get('triggered_at'),
        }
    
    @staticmethod
    def verify_webhook_signature(
        payload: bytes,
        signature: str,
        secret: str
    ) -> bool:
        """
        Verify webhook signature for security.
        
        Args:
            payload: Raw webhook payload bytes
            signature: Signature from webhook header
            secret: Webhook secret
            
        Returns:
            True if signature is valid, False otherwise
        """
        import hmac
        import hashlib
        
        if not signature or not secret:
            return False
        
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)


class QueryValidator:
    """Validates search queries and RAG inputs."""
    
    MIN_QUERY_LENGTH = 3
    MAX_QUERY_LENGTH = 1000
    
    @classmethod
    def validate_query(cls, query: str) -> str:
        """
        Validate and sanitize search query.
        
        Args:
            query: Search query string
            
        Returns:
            Sanitized query
            
        Raises:
            InvalidQueryError: If validation fails
        """
        if not query or not query.strip():
            raise InvalidQueryError("Query cannot be empty")
        
        query = query.strip()
        
        if len(query) < cls.MIN_QUERY_LENGTH:
            raise InvalidQueryError(
                f"Query too short (minimum {cls.MIN_QUERY_LENGTH} characters)"
            )
        
        if len(query) > cls.MAX_QUERY_LENGTH:
            raise InvalidQueryError(
                f"Query too long (maximum {cls.MAX_QUERY_LENGTH} characters)"
            )
        
        # Remove potentially harmful characters
        query = TicketValidator.sanitize_text(query)
        
        return query


class DataValidator:
    """General data validation utilities."""
    
    @staticmethod
    def validate_id(id_value: Any, field_name: str = "ID") -> int:
        """
        Validate ID field.
        
        Args:
            id_value: ID value to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated integer ID
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            id_int = int(id_value)
            if id_int <= 0:
                raise ValueError(f"{field_name} must be positive")
            return id_int
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Invalid {field_name}: {id_value}",
                original_exception=e
            )
    
    @staticmethod
    def validate_tier(tier: str) -> str:
        """
        Validate ticket tier value.
        
        Args:
            tier: Tier value to validate
            
        Returns:
            Validated tier
            
        Raises:
            ValidationError: If validation fails
        """
        valid_tiers = ['tier_1', 'tier_2', 'complex']
        tier = tier.lower().strip()
        
        if tier not in valid_tiers:
            raise ValidationError(
                f"Invalid tier: {tier}. Must be one of: {valid_tiers}"
            )
        
        return tier
    
    @staticmethod
    def validate_confidence(confidence: float) -> float:
        """
        Validate confidence score.
        
        Args:
            confidence: Confidence score to validate
            
        Returns:
            Validated confidence score
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            conf = float(confidence)
            if not 0.0 <= conf <= 1.0:
                raise ValueError("Confidence must be between 0 and 1")
            return conf
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Invalid confidence score: {confidence}",
                original_exception=e
            )
