from typing import Dict
from datetime import datetime
from loguru import logger

from ai_engine import AIEngine
from freshdesk_client import FreshdeskClient
from models import Ticket, TicketHistory, get_db
from config import settings

class TicketProcessor:
    def __init__(self):
        self.ai = AIEngine()
        self.freshdesk = FreshdeskClient()
        self.db = next(get_db())
        logger.info("Ticket processor ready")
    
    def process_new_ticket(self, ticket_data: Dict) -> Dict:
        """Processes a new ticket from Freshdesk"""
        try:
            logger.info(f"Processing ticket {ticket_data.get('id')}")
            
            # Pull out the important bits
            tid = ticket_data.get('id')
            subject = ticket_data.get('subject', '')
            desc = ticket_data.get('description', '')
            email = ticket_data.get('requester_id')
            priority = ticket_data.get('priority', 1)
            
            # Let AI figure out what to do with it
            tier, confidence, category = self.ai.categorize_ticket(subject, desc)
            
            # Decide how to handle it
            auto_resolve = tier == "tier_1" and confidence > 0.6
            needs_escalation = tier == "complex" or confidence < 0.5
            
            # Get a response from the knowledge base
            response = self.ai.get_rag_response(f"{subject} {desc}")
            
            ai_result = {
                'tier': tier,
                'confidence': confidence,
                'category': category,
                'auto_resolvable': auto_resolve,
                'escalation_needed': needs_escalation,
                'response': response,
                'escalation_reason': 'Complex issue' if needs_escalation else None
            }
            
            # Save it to the database
            ticket = self._save_ticket(tid, subject, desc, email, priority, ai_result)
            
            # Take action based on classification
            if auto_resolve:
                self._auto_resolve(tid, ai_result)
            elif needs_escalation:
                self._escalate(tid, ai_result)
            else:
                self._handle_tier_2(tid, ai_result)
            
            # Log what happened
            self._log_action(ticket.id, "processed", 
                           f"Classified as {tier} with {confidence:.0%} confidence")
            
            return {
                "success": True,
                "ticket_id": tid,
                "tier": tier,
                "confidence": confidence,
                "category": category,
                "auto_resolved": auto_resolve,
                "escalated": needs_escalation,
                "response": response
            }
            
        except Exception as err:
            logger.error(f"Processing failed: {err}")
            return {"success": False, "error": str(err)}
    
    def _save_ticket(self, tid, subject, desc, email, priority, ai_result):
        """Saves ticket to database"""
        try:
            ticket = Ticket(
                freshdesk_id=tid,
                subject=subject,
                description=desc,
                customer_email=str(email),
                priority=priority,
                category=ai_result['category'],
                tier=ai_result['tier'],
                confidence_score=ai_result['confidence'],
                auto_resolved=ai_result['auto_resolvable'],
                escalation_reason=ai_result.get('escalation_reason'),
                bot_response=ai_result['response']
            )
            
            self.db.add(ticket)
            self.db.commit()
            self.db.refresh(ticket)
            
            logger.info(f"Saved ticket {tid} to database")
            return ticket
            
        except Exception as err:
            logger.error(f"Save failed: {err}")
            self.db.rollback()
            raise
    
    def _auto_resolve(self, tid, ai_result):
        """Automatically resolves simple tickets"""
        try:
            logger.info(f"Auto-resolving ticket {tid}")
            
            # Post the bot's response
            self.freshdesk.add_note_to_ticket(tid, ai_result['response'], is_private=False)
            
            # Mark it as resolved
            self.freshdesk.auto_resolve_ticket(tid, ai_result['response'])
            
            # Update our database
            ticket = self.db.query(Ticket).filter(Ticket.freshdesk_id == tid).first()
            if ticket:
                ticket.status = "resolved"
                ticket.auto_resolved = True
                self.db.commit()
            
            logger.info(f"Ticket {tid} auto-resolved")
            
        except Exception as err:
            logger.error(f"Auto-resolve failed for {tid}: {err}")
    
    def _escalate(self, tid, ai_result):
        """Escalates complex tickets to humans"""
        try:
            logger.info(f"Escalating ticket {tid}")
            
            # Create escalation note
            reason = ai_result.get('escalation_reason', 'Needs human attention')
            note = f"🚨 ESCALATED\n\nReason: {reason}\n\nTier: {ai_result['tier']}\nConfidence: {ai_result['confidence']:.0%}\n\n{ai_result['response']}"
            
            self.freshdesk.add_note_to_ticket(tid, note, is_private=True)
            self.freshdesk.escalate_ticket(tid, reason)
            
            # Update database
            ticket = self.db.query(Ticket).filter(Ticket.freshdesk_id == tid).first()
            if ticket:
                ticket.status = "escalated"
                ticket.assigned_to = "human_agent"
                self.db.commit()
            
            logger.info(f"Ticket {tid} escalated")
            
        except Exception as err:
            logger.error(f"Escalation failed for {tid}: {err}")
    
    def _handle_tier_2(self, tid, ai_result):
        """Handles moderate complexity tickets"""
        try:
            logger.info(f"Handling tier 2 ticket {tid}")
            
            # Add bot's suggestion
            self.freshdesk.add_note_to_ticket(tid, ai_result['response'], is_private=False)
            
            # Set to pending
            self.freshdesk.update_ticket_status(tid, 3)
            
            # Update database
            ticket = self.db.query(Ticket).filter(Ticket.freshdesk_id == tid).first()
            if ticket:
                ticket.status = "pending"
                self.db.commit()
            
            logger.info(f"Tier 2 ticket {tid} handled")
            
        except Exception as err:
            logger.error(f"Tier 2 handling failed for {tid}: {err}")
    
    def _log_action(self, ticket_id, action, details):
        """Logs what happened to a ticket"""
        try:
            history = TicketHistory(
                ticket_id=ticket_id,
                action=action,
                details=details
            )
            self.db.add(history)
            self.db.commit()
        except Exception as err:
            logger.error(f"Logging failed: {err}")
    
    def get_ticket_stats(self) -> Dict:
        """Returns statistics about processed tickets"""
        try:
            total = self.db.query(Ticket).count()
            auto_resolved = self.db.query(Ticket).filter(Ticket.auto_resolved == True).count()
            escalated = self.db.query(Ticket).filter(Ticket.status == "escalated").count()
            pending = self.db.query(Ticket).filter(Ticket.status == "pending").count()
            
            return {
                "total_tickets": total,
                "auto_resolved": auto_resolved,
                "escalated": escalated,
                "pending": pending,
                "auto_resolution_rate": (auto_resolved / total * 100) if total > 0 else 0
            }
            
        except Exception as err:
            logger.error(f"Stats error: {err}")
            return {}
    
    def reprocess_ticket(self, ticket_id: int) -> Dict:
        """Reprocesses a ticket"""
        try:
            # Fetch from Freshdesk
            ticket_data = self.freshdesk.get_ticket(ticket_id)
            if not ticket_data:
                return {"success": False, "error": "Ticket not found"}
            
            # Process it again
            return self.process_new_ticket(ticket_data)
            
        except Exception as err:
            logger.error(f"Reprocess failed for {ticket_id}: {err}")
            return {"success": False, "error": str(err)}
    
    def get_ticket_analytics(self) -> Dict:
        """Returns detailed analytics"""
        try:
            # Count by tier
            tier1 = self.db.query(Ticket).filter(Ticket.tier == "tier_1").count()
            tier2 = self.db.query(Ticket).filter(Ticket.tier == "tier_2").count()
            complex_tickets = self.db.query(Ticket).filter(Ticket.tier == "complex").count()
            
            # Average confidence
            scores = self.db.query(Ticket.confidence_score).filter(
                Ticket.confidence_score.isnot(None)
            ).all()
            avg_conf = sum([s[0] for s in scores]) / len(scores) if scores else 0
            
            # Recent tickets
            recent = self.db.query(Ticket).order_by(Ticket.created_at.desc()).limit(10).all()
            
            return {
                "tier_distribution": {
                    "tier_1": tier1,
                    "tier_2": tier2,
                    "complex": complex_tickets
                },
                "average_confidence": avg_conf,
                "recent_tickets": [
                    {
                        "id": t.freshdesk_id,
                        "subject": t.subject,
                        "tier": t.tier,
                        "status": t.status,
                        "created_at": t.created_at.isoformat()
                    }
                    for t in recent
                ]
            }
            
        except Exception as err:
            logger.error(f"Analytics error: {err}")
            return {}