"""
Abstract interfaces for the ticket resolution bot.

These interfaces define contracts that implementations must follow,
enabling dependency injection and loose coupling.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class IAIEngine(ABC):
    """
    Interface for AI engine implementations.
    
    Defines the contract for AI-powered ticket classification and
    response generation capabilities.
    """
    
    @abstractmethod
    def categorize_ticket(
        self, 
        subject: str, 
        description: str
    ) -> Tuple[str, float, str]:
        """
        Categorize a ticket into tiers.
        
        Args:
            subject: Ticket subject line
            description: Ticket description/body
            
        Returns:
            Tuple of (tier, confidence_score, category)
            - tier: One of 'tier_1', 'tier_2', 'complex'
            - confidence_score: Float between 0 and 1
            - category: Specific category (e.g., 'billing', 'technical')
        """
        pass
    
    @abstractmethod
    def get_rag_response(self, query: str) -> Dict[str, any]:
        """
        Get response using Retrieval-Augmented Generation.
        
        Args:
            query: User query or ticket description
            
        Returns:
            Dictionary containing:
            - response: Generated response text
            - sources: List of source documents used
            - confidence: Confidence score
        """
        pass
    
    @abstractmethod
    def is_ready(self) -> bool:
        """
        Check if AI engine is initialized and ready.
        
        Returns:
            True if ready, False otherwise
        """
        pass


class IExternalClient(ABC):
    """
    Interface for external service clients (e.g., Freshdesk).
    
    Defines the contract for interacting with external ticketing systems.
    """
    
    @abstractmethod
    def get_ticket(self, ticket_id: int) -> Optional[Dict]:
        """
        Retrieve ticket details by ID.
        
        Args:
            ticket_id: External ticket ID
            
        Returns:
            Ticket data dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def update_ticket(self, ticket_id: int, data: Dict) -> Optional[Dict]:
        """
        Update ticket with new data.
        
        Args:
            ticket_id: External ticket ID
            data: Update data dictionary
            
        Returns:
            Updated ticket data or None if failed
        """
        pass
    
    @abstractmethod
    def add_note_to_ticket(
        self, 
        ticket_id: int, 
        note: str, 
        is_private: bool = False
    ) -> Optional[Dict]:
        """
        Add a note/comment to a ticket.
        
        Args:
            ticket_id: External ticket ID
            note: Note content
            is_private: Whether note is private
            
        Returns:
            Note data or None if failed
        """
        pass
    
    @abstractmethod
    def resolve_ticket(
        self, 
        ticket_id: int, 
        resolution_note: str = ""
    ) -> Optional[Dict]:
        """
        Mark ticket as resolved.
        
        Args:
            ticket_id: External ticket ID
            resolution_note: Optional resolution note
            
        Returns:
            Updated ticket data or None if failed
        """
        pass
    
    @abstractmethod
    def escalate_ticket(
        self, 
        ticket_id: int, 
        escalation_reason: str
    ) -> Optional[Dict]:
        """
        Escalate ticket to human agent.
        
        Args:
            ticket_id: External ticket ID
            escalation_reason: Reason for escalation
            
        Returns:
            Updated ticket data or None if failed
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test connection to external service.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass


class ITicketProcessor(ABC):
    """
    Interface for ticket processing implementations.
    
    Defines the contract for processing tickets through the AI pipeline.
    """
    
    @abstractmethod
    def process_new_ticket(self, ticket_data: Dict) -> Dict:
        """
        Process a new ticket through the AI pipeline.
        
        Args:
            ticket_data: Raw ticket data from webhook/API
            
        Returns:
            Processing result dictionary containing:
            - status: Processing status
            - tier: Assigned tier
            - action_taken: Action performed
            - details: Additional details
        """
        pass
    
    @abstractmethod
    def reprocess_ticket(self, ticket_id: int) -> Dict:
        """
        Reprocess an existing ticket.
        
        Args:
            ticket_id: Internal ticket ID
            
        Returns:
            Reprocessing result dictionary
        """
        pass
    
    @abstractmethod
    def get_ticket_stats(self) -> Dict:
        """
        Get ticket processing statistics.
        
        Returns:
            Statistics dictionary with counts and metrics
        """
        pass
    
    @abstractmethod
    def get_ticket_analytics(self) -> Dict:
        """
        Get detailed analytics about ticket processing.
        
        Returns:
            Analytics dictionary with detailed metrics
        """
        pass


class IRepository(ABC):
    """
    Base interface for repository implementations.
    
    Defines common CRUD operations for data access.
    """
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[any]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[any]:
        """Get all entities with pagination."""
        pass
    
    @abstractmethod
    def create(self, entity: any) -> any:
        """Create new entity."""
        pass
    
    @abstractmethod
    def update(self, id: int, entity: any) -> Optional[any]:
        """Update existing entity."""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        pass


class ITicketRepository(IRepository):
    """
    Interface for ticket repository.
    
    Extends base repository with ticket-specific operations.
    """
    
    @abstractmethod
    def get_by_freshdesk_id(self, freshdesk_id: int) -> Optional[any]:
        """Get ticket by Freshdesk ID."""
        pass
    
    @abstractmethod
    def get_by_status(self, status: str) -> List[any]:
        """Get tickets by status."""
        pass
    
    @abstractmethod
    def get_by_tier(self, tier: str) -> List[any]:
        """Get tickets by tier."""
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict:
        """Get ticket statistics."""
        pass


class ICacheService(ABC):
    """
    Interface for caching service.
    
    Defines contract for caching operations.
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(
        self, 
        key: str, 
        value: any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries."""
        pass
