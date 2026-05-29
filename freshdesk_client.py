import requests
from typing import Dict, List, Optional
from loguru import logger
from config import settings

class FreshdeskClient:
    def __init__(self):
        self.domain = settings.FRESHDESK_DOMAIN
        self.api_key = settings.FRESHDESK_API_KEY
        self.base_url = f"https://{self.domain}.freshdesk.com/api/v2"
        self.auth = (self.api_key, "X")
        
        if not self.domain or not self.api_key:
            logger.warning("Freshdesk not configured properly")
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Makes a request to Freshdesk API"""
        try:
            url = f"{self.base_url}/{endpoint}"
            headers = {"Content-Type": "application/json"}
            
            response = requests.request(
                method=method,
                url=url,
                auth=self.auth,
                headers=headers,
                json=data
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Freshdesk API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as err:
            logger.error(f"Request failed: {err}")
            return None
    
    def get_ticket(self, ticket_id: int) -> Optional[Dict]:
        """Gets ticket details"""
        return self._request("GET", f"tickets/{ticket_id}")
    
    def update_ticket(self, ticket_id: int, data: Dict) -> Optional[Dict]:
        """Updates a ticket"""
        return self._request("PUT", f"tickets/{ticket_id}", data)
    
    def add_note_to_ticket(self, ticket_id: int, note: str, is_private: bool = False) -> Optional[Dict]:
        """Adds a note to a ticket"""
        data = {"body": note, "private": is_private}
        return self._request("POST", f"tickets/{ticket_id}/notes", data)
    
    def assign_ticket(self, ticket_id: int, agent_id: int) -> Optional[Dict]:
        """Assigns ticket to an agent"""
        data = {"responder_id": agent_id}
        return self._request("PUT", f"tickets/{ticket_id}", data)
    
    def update_ticket_status(self, ticket_id: int, status: int) -> Optional[Dict]:
        """Updates ticket status"""
        data = {"status": status}
        return self._request("PUT", f"tickets/{ticket_id}", data)
    
    def get_agents(self) -> List[Dict]:
        """Gets list of agents"""
        result = self._request("GET", "agents")
        return result if result else []
    
    def get_agent_by_email(self, email: str) -> Optional[Dict]:
        """Finds an agent by email"""
        agents = self.get_agents()
        for agent in agents:
            if agent.get("email") == email:
                return agent
        return None
    
    def resolve_ticket(self, ticket_id: int, resolution_note: str = "") -> Optional[Dict]:
        """Marks ticket as resolved"""
        data = {"status": 5, "resolution": resolution_note}
        return self._request("PUT", f"tickets/{ticket_id}", data)
    
    def close_ticket(self, ticket_id: int) -> Optional[Dict]:
        """Closes a ticket"""
        data = {"status": 6}
        return self._request("PUT", f"tickets/{ticket_id}", data)
    
    def escalate_ticket(self, ticket_id: int, escalation_reason: str) -> Optional[Dict]:
        """Escalates ticket to human"""
        note = f"🚨 ESCALATED\n\nReason: {escalation_reason}\n\nNeeds human intervention."
        self.add_note_to_ticket(ticket_id, note, is_private=True)
        data = {"priority": 3}
        return self._request("PUT", f"tickets/{ticket_id}", data)
    
    def auto_resolve_ticket(self, ticket_id: int, bot_response: str) -> Optional[Dict]:
        """Auto-resolves with bot response"""
        note = f"🤖 AUTO-RESOLVED\n\n{bot_response}\n\nResolved by AI assistant."
        self.add_note_to_ticket(ticket_id, note, is_private=False)
        return self.resolve_ticket(ticket_id, "Resolved by AI")
    
    def get_ticket_conversations(self, ticket_id: int) -> List[Dict]:
        """Gets ticket conversation history"""
        result = self._request("GET", f"tickets/{ticket_id}/conversations")
        return result if result else []
    
    def create_ticket(self, data: Dict) -> Optional[Dict]:
        """Creates a new ticket"""
        return self._request("POST", "tickets", data)
    
    def search_tickets(self, query: str) -> List[Dict]:
        """Searches tickets"""
        endpoint = f'search/tickets?query="{query}"'
        result = self._request("GET", endpoint)
        return result.get("results", []) if result else []
    
    def get_ticket_fields(self) -> List[Dict]:
        """Gets custom ticket fields"""
        result = self._request("GET", "ticket_fields")
        return result if result else []
    
    def update_custom_field(self, ticket_id: int, field_name: str, value: str) -> Optional[Dict]:
        """Updates a custom field"""
        data = {"custom_fields": {field_name: value}}
        return self._request("PUT", f"tickets/{ticket_id}", data)
    
    def get_ticket_stats(self, ticket_id: int) -> Optional[Dict]:
        """Gets ticket stats"""
        return self._request("GET", f"tickets/{ticket_id}/time_entries")
    
    def add_time_entry(self, ticket_id: int, time_spent: int, note: str = "") -> Optional[Dict]:
        """Adds time entry"""
        data = {"time_entry": {"time_spent": time_spent, "note": note}}
        return self._request("POST", f"tickets/{ticket_id}/time_entries", data)
    
    def get_satisfaction_ratings(self, ticket_id: int) -> Optional[Dict]:
        """Gets satisfaction ratings"""
        return self._request("GET", f"tickets/{ticket_id}/satisfaction_ratings")
    
    def test_connection(self) -> bool:
        """Tests if Freshdesk connection works"""
        try:
            result = self._request("GET", "tickets")
            return result is not None
        except Exception as err:
            logger.error(f"Connection test failed: {err}")
            return False
