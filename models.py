from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    freshdesk_id = Column(Integer, unique=True, index=True)
    subject = Column(String(500))
    description = Column(Text)
    customer_email = Column(String(255))
    priority = Column(Integer, default=1)
    status = Column(String(50), default="open")
    category = Column(String(100))
    tier = Column(String(50))
    confidence_score = Column(Float)
    auto_resolved = Column(Boolean, default=False)
    escalation_reason = Column(Text, nullable=True)
    bot_response = Column(Text)
    assigned_to = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to history
    history = relationship("TicketHistory", back_populates="ticket")

class TicketHistory(Base):
    __tablename__ = "ticket_history"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"))
    action = Column(String(100))
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship back to ticket
    ticket = relationship("Ticket", back_populates="history")

# Database setup
from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Creates all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Gets a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
