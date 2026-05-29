from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import json
import hmac
import hashlib
from datetime import datetime
from sqlalchemy import text
import time

from ticket_processor import TicketProcessor
from models import create_tables, get_db, Ticket
from config import settings
from loguru import logger

# Set up logging - keeps things organized
logger.add(settings.LOG_FILE, rotation="1 day", retention="7 days", level=settings.LOG_LEVEL)

# Initialize the FastAPI app
app = FastAPI(
    title="Customer Ticket Resolution Bot",
    description="AI-powered ticket resolution system with Freshdesk integration",
    version="1.0.0"
)

# CORS setup - allows requests from anywhere for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global processor instance
processor = None

# Request/Response models
class TicketWebhook(BaseModel):
    id: int
    subject: str
    description: str
    requester_id: int
    priority: int = 1
    status: int = 2
    created_at: str
    updated_at: str

class TestTicketRequest(BaseModel):
    subject: str
    description: str
    priority: int = 1

class ReprocessRequest(BaseModel):
    ticket_id: int

@app.on_event("startup")
async def startup_event():
    """Gets everything ready when the app starts"""
    global processor
    
    try:
        create_tables()
        logger.info("Database tables ready")
        
        processor = TicketProcessor()
        logger.info("Ticket processor is up and running")
        
    except Exception as err:
        logger.error(f"Startup failed: {err}")
        raise

@app.get("/")
async def root():
    """Basic info endpoint"""
    return {
        "message": "Customer Ticket Resolution Bot",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Checks if everything is working properly"""
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        
        freshdesk_ok = processor.freshdesk_client.test_connection()
        
        return {
            "status": "healthy",
            "database": "connected",
            "freshdesk": "connected" if freshdesk_ok else "disconnected",
            "ai_models": "loaded",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as err:
        logger.error(f"Health check failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))

@app.post("/webhook/freshdesk")
async def freshdesk_webhook(request: Request, background_tasks: BackgroundTasks):
    """Handles incoming webhooks from Freshdesk"""
    try:
        raw_body = await request.body()
        logger.info(f"Got webhook, body size: {len(raw_body)} bytes")
        
        # Verify the webhook is legit
        if settings.FRESHDESK_WEBHOOK_SECRET:
            secret_header = request.headers.get("x-webhook-secret")
            if secret_header:
                expected = "ai-customer-ticket-resolution-bot"
                if secret_header != expected:
                    logger.warning(f"Secret mismatch: got {secret_header}")
                    raise HTTPException(status_code=401, detail="Invalid webhook secret")
                logger.info("Webhook verified")
            else:
                # Try signature verification as fallback
                sig = request.headers.get("X-Freshdesk-Signature") or \
                      request.headers.get("X-Webhook-Signature") or \
                      request.headers.get("X-Signature")
                
                if sig:
                    expected_sig = hmac.new(
                        settings.FRESHDESK_WEBHOOK_SECRET.encode(),
                        raw_body,
                        hashlib.sha256
                    ).hexdigest()
                    
                    if not hmac.compare_digest(sig, expected_sig):
                        raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse the JSON payload
        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError as err:
            logger.error(f"Bad JSON: {err}")
            raise HTTPException(status_code=400, detail="Invalid JSON")
        
        # Figure out what kind of webhook this is
        ticket_info = None
        
        if data.get("freshdesk_webhook") and data["freshdesk_webhook"].get("ticket_id"):
            # It's a webhook notification - fetch the full ticket
            tid = data["freshdesk_webhook"]["ticket_id"]
            logger.info(f"Fetching ticket {tid} from Freshdesk")
            
            try:
                ticket_info = processor.freshdesk_client.get_ticket(tid)
                if not ticket_info:
                    logger.error(f"Couldn't get ticket {tid}")
                    return {"status": "error", "reason": "Failed to fetch ticket"}
            except Exception as err:
                logger.error(f"Error fetching ticket {tid}: {err}")
                return {"status": "error", "reason": str(err)}
        
        elif data.get("ticket"):
            # Direct ticket data from Freshdesk
            ticket_info = data["ticket"]
        
        elif data.get("id") and data.get("subject"):
            # Test format
            ticket_info = data
        
        else:
            logger.warning("Webhook doesn't contain valid ticket data")
            return {"status": "ignored", "reason": "Not a ticket event"}
        
        if ticket_info:
            logger.info(f"Processing ticket {ticket_info.get('id')}")
            background_tasks.add_task(process_in_background, ticket_info)
            return {"status": "processing", "ticket_id": ticket_info.get("id")}
        else:
            return {"status": "ignored", "reason": "No ticket data"}
            
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Webhook error: {err}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(err))

async def process_in_background(ticket_data: Dict):
    """Handles ticket processing without blocking the webhook response"""
    try:
        logger.info(f"Background task started for ticket {ticket_data.get('id')}")
        result = processor.process_new_ticket(ticket_data)
        logger.info(f"Processing done: {result}")
    except Exception as err:
        logger.error(f"Background processing failed: {err}")
        import traceback
        logger.error(traceback.format_exc())

@app.post("/test-ticket")
async def test_ticket(request: TestTicketRequest):
    """Test endpoint - simulates a real ticket"""
    try:
        # Generate a unique ID using timestamp
        unique_id = int(time.time() * 1000) % 1000000
        
        mock_data = {
            "id": unique_id,
            "subject": request.subject,
            "description": request.description,
            "requester_id": 12345,
            "priority": request.priority,
            "status": 2,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = processor.process_new_ticket(mock_data)
        
        return {
            "success": True,
            "test_ticket": mock_data,
            "processing_result": result
        }
        
    except Exception as err:
        logger.error(f"Test ticket failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))

@app.post("/reprocess-ticket")
async def reprocess_ticket(request: ReprocessRequest):
    """Reprocesses a ticket that was already handled"""
    try:
        result = processor.reprocess_ticket(request.ticket_id)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Reprocessing failed"))
            
    except Exception as err:
        logger.error(f"Reprocess failed: {err}")
        raise HTTPException(status_code=500, detail=str(err))

@app.get("/stats")
async def get_stats():
    """Returns processing statistics"""
    try:
        return processor.get_ticket_stats()
    except Exception as err:
        logger.error(f"Stats error: {err}")
        raise HTTPException(status_code=500, detail=str(err))

@app.get("/analytics")
async def get_analytics():
    """Returns detailed analytics"""
    try:
        return processor.get_ticket_analytics()
    except Exception as err:
        logger.error(f"Analytics error: {err}")
        raise HTTPException(status_code=500, detail=str(err))

@app.get("/tickets")
async def get_tickets(limit: int = 50, offset: int = 0):
    """Lists processed tickets with pagination"""
    try:
        db = next(get_db())
        tickets = db.query(Ticket).offset(offset).limit(limit).all()
        
        return {
            "tickets": [
                {
                    "id": t.id,
                    "freshdesk_id": t.freshdesk_id,
                    "subject": t.subject,
                    "category": t.category,
                    "tier": t.tier,
                    "confidence_score": t.confidence_score,
                    "auto_resolved": t.auto_resolved,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "updated_at": t.updated_at.isoformat() if t.updated_at else None
                }
                for t in tickets
            ],
            "total": len(tickets),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as err:
        logger.error(f"Get tickets error: {err}")
        raise HTTPException(status_code=500, detail=str(err))

@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: int):
    """Gets details for a specific ticket"""
    try:
        db = next(get_db())
        t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not t:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return {
            "id": t.id,
            "freshdesk_id": t.freshdesk_id,
            "subject": t.subject,
            "description": t.description,
            "category": t.category,
            "tier": t.tier,
            "confidence_score": t.confidence_score,
            "auto_resolved": t.auto_resolved,
            "escalation_reason": t.escalation_reason,
            "bot_response": t.bot_response,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None
        }
        
    except Exception as err:
        logger.error(f"Get ticket error: {err}")
        raise HTTPException(status_code=500, detail=str(err))

@app.get("/docs")
async def get_docs():
    """API documentation"""
    return {
        "endpoints": {
            "GET /": "Root endpoint with basic info",
            "GET /health": "Health check",
            "POST /webhook/freshdesk": "Freshdesk webhook endpoint",
            "POST /test-ticket": "Test ticket processing",
            "GET /stats": "Processing statistics",
            "GET /analytics": "Detailed analytics",
            "GET /tickets": "List processed tickets",
            "GET /tickets/{id}": "Get specific ticket",
            "GET /docs": "This documentation"
        },
        "webhook_format": {
            "description": "Freshdesk webhook should send ticket data",
            "example": {
                "ticket": {
                    "id": 123,
                    "subject": "Test ticket",
                    "description": "Ticket description",
                    "requester_id": 456,
                    "priority": 1,
                    "status": 2
                }
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )