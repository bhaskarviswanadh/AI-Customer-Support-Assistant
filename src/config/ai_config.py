"""
AI-specific configuration settings.

This module contains all AI model and processing configurations.
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIConfig(BaseSettings):
    """
    AI Engine configuration settings.
    
    Configures AI models, embeddings, and classification parameters.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AI_",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Model Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model for semantic search"
    )
    classification_model: str = Field(
        default="facebook/bart-large-mnli",
        description="Model for ticket classification"
    )
    max_sequence_length: int = Field(
        default=512,
        ge=128,
        le=2048,
        description="Maximum sequence length for models"
    )
    
    # Device Configuration
    device: str = Field(
        default="auto",
        description="Device to use: 'auto', 'cpu', 'cuda', 'mps'"
    )
    use_gpu: bool = Field(
        default=True,
        description="Use GPU if available"
    )
    
    # Processing Configuration
    batch_size: int = Field(
        default=8,
        ge=1,
        le=128,
        description="Batch size for model inference"
    )
    confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for classifications"
    )
    
    # RAG Configuration
    rag_top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of documents to retrieve for RAG"
    )
    rag_similarity_threshold: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score for RAG retrieval"
    )
    knowledge_base_path: str = Field(
        default="docs",
        description="Path to knowledge base documents"
    )
    vector_db_path: str = Field(
        default="faiss_index",
        description="Path to vector database index"
    )
    
    # Caching Configuration
    cache_embeddings: bool = Field(
        default=True,
        description="Cache generated embeddings"
    )
    cache_classifications: bool = Field(
        default=True,
        description="Cache classification results"
    )
    embedding_cache_ttl: int = Field(
        default=86400,  # 24 hours
        ge=0,
        description="Embedding cache TTL in seconds"
    )
    
    # Fallback Configuration
    enable_fallback: bool = Field(
        default=True,
        description="Enable fallback to keyword-based classification"
    )
    
    @property
    def should_use_gpu(self) -> bool:
        """Determine if GPU should be used."""
        if self.device == "cuda":
            return True
        if self.device == "cpu":
            return False
        # Auto-detect
        return self.use_gpu


class ClassificationConfig(BaseSettings):
    """
    Ticket classification configuration.
    
    Defines keywords and rules for ticket categorization.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CLASSIFICATION_",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Tier 1 Keywords (Simple, auto-resolvable)
    tier_1_keywords: List[str] = Field(
        default=[
            "password reset",
            "forgot password",
            "login issue",
            "account access",
            "basic setup",
            "simple configuration",
            "download",
            "installation guide",
            "how to",
            "tutorial",
        ],
        description="Keywords indicating Tier 1 tickets"
    )
    
    # Tier 2 Keywords (Moderate complexity)
    tier_2_keywords: List[str] = Field(
        default=[
            "billing",
            "payment",
            "subscription",
            "upgrade",
            "downgrade",
            "feature request",
            "bug report",
            "performance issue",
            "slow",
            "not working",
        ],
        description="Keywords indicating Tier 2 tickets"
    )
    
    # Complex Keywords (Requires human intervention)
    complex_keywords: List[str] = Field(
        default=[
            "critical",
            "urgent",
            "emergency",
            "system down",
            "data loss",
            "security",
            "breach",
            "custom integration",
            "api",
            "advanced configuration",
            "enterprise",
        ],
        description="Keywords indicating complex tickets"
    )
    
    # Category Mappings
    category_keywords: dict = Field(
        default={
            "billing": ["billing", "payment", "invoice", "charge", "subscription"],
            "technical": ["error", "bug", "crash", "not working", "broken"],
            "account": ["login", "password", "access", "account", "authentication"],
            "feature": ["feature", "request", "enhancement", "suggestion"],
            "performance": ["slow", "performance", "lag", "timeout"],
            "security": ["security", "breach", "hack", "unauthorized"],
        },
        description="Category keyword mappings"
    )
    
    # Confidence Thresholds
    tier_1_confidence_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Confidence threshold for Tier 1 classification"
    )
    tier_2_confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Confidence threshold for Tier 2 classification"
    )


# Global configuration instances
ai_config = AIConfig()
classification_config = ClassificationConfig()
