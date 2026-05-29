"""
Response templates for ticket resolution.

This module provides templated responses for different ticket tiers
and scenarios.
"""

from typing import Dict
from string import Template


class ResponseTemplates:
    """
    Manages response templates for ticket resolution.
    
    Provides methods to generate formatted responses based on
    ticket tier and context.
    """
    
    # Tier 1 Templates (Auto-resolvable)
    TIER_1_GREETING = Template(
        "Hello! I can help you with this ${category} issue."
    )
    
    TIER_1_SOLUTION = Template(
        "Here's how to resolve this:\n\n${solution}\n\n"
        "This should address your concern."
    )
    
    TIER_1_CLOSING = Template(
        "This should resolve your issue. If you need further assistance, "
        "please don't hesitate to reach out!"
    )
    
    # Tier 2 Templates (Assisted resolution)
    TIER_2_GREETING = Template(
        "I understand your ${category} concern. Let me help you with this."
    )
    
    TIER_2_SOLUTION = Template(
        "Here's what you need to do:\n\n${solution}\n\n"
        "Please follow these steps carefully."
    )
    
    TIER_2_CLOSING = Template(
        "I've provided a solution above. If this doesn't resolve your issue, "
        "I'll escalate it to a human agent for further assistance."
    )
    
    # Complex Templates (Escalation required)
    COMPLEX_GREETING = Template(
        "I see this is a ${category} issue that requires specialized attention."
    )
    
    COMPLEX_ESCALATION = Template(
        "I'm escalating this ticket to our specialized team who will assist you shortly.\n\n"
        "Reason: ${reason}"
    )
    
    COMPLEX_CLOSING = Template(
        "A human agent will contact you within the next few hours to address your concern."
    )
    
    # Auto-resolution Template
    AUTO_RESOLUTION_NOTE = Template(
        "🤖 **AUTOMATED RESPONSE**\n\n"
        "${response}\n\n"
        "---\n"
        "This ticket has been automatically resolved by our AI assistant. "
        "If you need further help, please reply to this ticket."
    )
    
    # Escalation Template
    ESCALATION_NOTE = Template(
        "🚨 **ESCALATED TO HUMAN AGENT**\n\n"
        "**Reason:** ${reason}\n\n"
        "**Details:** ${details}\n\n"
        "---\n"
        "This ticket requires human intervention and has been assigned to our support team."
    )
    
    # Tier 2 Assistance Template
    TIER_2_NOTE = Template(
        "💡 **AI-ASSISTED RESPONSE**\n\n"
        "${response}\n\n"
        "---\n"
        "Please try the solution above. If it doesn't work, we'll escalate to a human agent."
    )
    
    @classmethod
    def get_tier_1_response(cls, category: str, solution: str) -> str:
        """
        Generate a complete Tier 1 response.
        
        Args:
            category: Ticket category
            solution: Solution text
            
        Returns:
            Formatted response string
        """
        greeting = cls.TIER_1_GREETING.substitute(category=category)
        solution_text = cls.TIER_1_SOLUTION.substitute(solution=solution)
        closing = cls.TIER_1_CLOSING.substitute()
        
        return f"{greeting}\n\n{solution_text}\n{closing}"
    
    @classmethod
    def get_tier_2_response(cls, category: str, solution: str) -> str:
        """
        Generate a complete Tier 2 response.
        
        Args:
            category: Ticket category
            solution: Solution text
            
        Returns:
            Formatted response string
        """
        greeting = cls.TIER_2_GREETING.substitute(category=category)
        solution_text = cls.TIER_2_SOLUTION.substitute(solution=solution)
        closing = cls.TIER_2_CLOSING.substitute()
        
        return f"{greeting}\n\n{solution_text}\n{closing}"
    
    @classmethod
    def get_complex_response(cls, category: str, reason: str) -> str:
        """
        Generate a complete complex ticket response.
        
        Args:
            category: Ticket category
            reason: Escalation reason
            
        Returns:
            Formatted response string
        """
        greeting = cls.COMPLEX_GREETING.substitute(category=category)
        escalation = cls.COMPLEX_ESCALATION.substitute(reason=reason)
        closing = cls.COMPLEX_CLOSING.substitute()
        
        return f"{greeting}\n\n{escalation}\n\n{closing}"
    
    @classmethod
    def get_auto_resolution_note(cls, response: str) -> str:
        """
        Generate auto-resolution note.
        
        Args:
            response: AI-generated response
            
        Returns:
            Formatted note string
        """
        return cls.AUTO_RESOLUTION_NOTE.substitute(response=response)
    
    @classmethod
    def get_escalation_note(cls, reason: str, details: str = "") -> str:
        """
        Generate escalation note.
        
        Args:
            reason: Escalation reason
            details: Additional details
            
        Returns:
            Formatted note string
        """
        return cls.ESCALATION_NOTE.substitute(
            reason=reason,
            details=details or "No additional details provided"
        )
    
    @classmethod
    def get_tier_2_note(cls, response: str) -> str:
        """
        Generate Tier 2 assistance note.
        
        Args:
            response: AI-generated response
            
        Returns:
            Formatted note string
        """
        return cls.TIER_2_NOTE.substitute(response=response)


# Template configuration dictionary (for backward compatibility)
RESPONSE_TEMPLATES: Dict[str, Dict[str, str]] = {
    "tier_1": {
        "greeting": "Hello! I can help you with this {category} issue.",
        "solution": "Here's how to resolve this: {solution}",
        "closing": "This should resolve your issue. Let me know if you need further assistance!"
    },
    "tier_2": {
        "greeting": "I understand your {category} concern. Let me help you with this.",
        "solution": "Here's what you need to do: {solution}",
        "closing": "I've provided a solution above. If this doesn't resolve your issue, I'll escalate it to a human agent."
    },
    "complex": {
        "greeting": "I see this is a complex {category} issue that requires specialized attention.",
        "escalation": "I'm escalating this ticket to our specialized team who will assist you shortly.",
        "closing": "A human agent will contact you within the next few hours."
    }
}
