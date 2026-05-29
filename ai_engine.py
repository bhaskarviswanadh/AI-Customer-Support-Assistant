import os
import json
import numpy as np
from typing import List, Dict, Tuple
import torch
from loguru import logger
from config import settings

# Prevent tokenizer warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_CACHE"] = "/tmp/transformers_cache"

# Try loading AI libraries - fallback if they're not available
try:
    from transformers import AutoTokenizer, AutoModel
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    MODELS_AVAILABLE = True
except ImportError as err:
    logger.error(f"Couldn't load AI libraries: {err}")
    logger.warning("Running in basic mode without advanced models")
    MODELS_AVAILABLE = False

class AIEngine:
    def __init__(self):
        # Check if we can use GPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Running on: {self.device}")
        
        self._setup_models()
        self._load_docs()
        
    def _setup_models(self):
        """Sets up the AI models if available"""
        if not MODELS_AVAILABLE:
            logger.warning("No AI models - using keyword matching instead")
            self.embed_model = None
            self.classifier = None
            return
        
        try:
            logger.info("Loading embedding model...")
            self.embed_model = SentenceTransformer(settings.MODEL_NAME, device=self.device)
            
            logger.info("Loading classifier...")
            self.classifier = AutoModel.from_pretrained(settings.CLASSIFICATION_MODEL)
            
            logger.info("Models loaded successfully")
            
        except Exception as err:
            logger.error(f"Model loading failed: {err}")
            logger.warning("Switching to keyword-based mode")
            self.embed_model = None
            self.classifier = None
        
    def _load_docs(self):
        """Loads FAQ documents and creates embeddings"""
        self.docs = {}
        self.doc_embeddings = []
        self.doc_texts = []
        
        docs_dir = "docs"
        if not os.path.exists(docs_dir):
            logger.warning(f"No {docs_dir} folder found")
            return
        
        # Read all text files
        for filename in os.listdir(docs_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(docs_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.docs[filename] = content
                    self.doc_texts.append(content)
        
        # Create embeddings if we have the model
        if self.doc_texts and self.embed_model:
            logger.info("Creating document embeddings...")
            self.doc_embeddings = self.embed_model.encode(
                self.doc_texts, 
                convert_to_tensor=True,
                show_progress_bar=True
            )
            logger.info(f"Loaded {len(self.doc_texts)} documents")
        else:
            logger.warning("No documents or embedding model available")
        
    def categorize_ticket(self, subject: str, description: str) -> Tuple[str, float, str]:
        """
        Figures out what tier a ticket belongs to
        Returns: (tier, confidence, category)
        """
        # Combine the text
        full_text = f"{subject} {description}".lower()
        
        # Keywords for each tier
        simple_words = ["password", "reset", "login", "help", "how to"]
        moderate_words = ["billing", "payment", "subscription", "account", "upgrade"]
        complex_words = ["error", "bug", "crash", "system", "critical", "urgent"]
        
        # Count matches
        simple_count = sum(1 for word in simple_words if word in full_text)
        moderate_count = sum(1 for word in moderate_words if word in full_text)
        complex_count = sum(1 for word in complex_words if word in full_text)
        
        # Decide the tier
        if complex_count > 0:
            tier = "complex"
            confidence = min(0.9, 0.5 + (complex_count * 0.1))
        elif moderate_count > 0:
            tier = "tier_2"
            confidence = min(0.8, 0.6 + (moderate_count * 0.1))
        elif simple_count > 0:
            tier = "tier_1"
            confidence = min(0.7, 0.5 + (simple_count * 0.1))
        else:
            # When in doubt, mark as complex
            tier = "complex"
            confidence = 0.5
        
        category = self._find_category(full_text)
        
        logger.info(f"Classified as {tier} ({confidence:.0%} confident)")
        return tier, confidence, category
    
    def _find_category(self, text: str) -> str:
        """Figures out what category the ticket falls into"""
        categories = {
            "password_reset": ["password", "reset", "forgot", "login"],
            "billing": ["billing", "payment", "invoice", "charge"],
            "technical": ["error", "bug", "crash", "broken"],
            "account": ["account", "profile", "settings"],
            "general": ["help", "support", "question"]
        }
        
        for cat_name, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return cat_name
        
        return "general"
    
    def get_rag_response(self, query: str) -> str:
        """Gets an answer from the knowledge base"""
        if not self.doc_texts:
            return "Knowledge base isn't available right now. Please contact support."
        
        if not self.embed_model or not self.doc_embeddings:
            # Use simple matching instead
            return self._simple_search(query)
        
        try:
            # Encode the question
            query_vec = self.embed_model.encode([query], convert_to_tensor=True)
            
            # Find similar documents
            similarities = cosine_similarity(
                query_vec.cpu().numpy(), 
                self.doc_embeddings.cpu().numpy()
            )[0]
            
            # Get the best match
            best_idx = np.argmax(similarities)
            best_score = similarities[best_idx]
            
            if best_score > 0.3:
                doc = self.doc_texts[best_idx]
                return self._format_response(query, doc)
            else:
                return "Couldn't find anything relevant. Try contacting support."
                
        except Exception as err:
            logger.error(f"RAG search failed: {err}")
            return self._simple_search(query)
    
    def _simple_search(self, query: str) -> str:
        """Fallback search using keyword matching"""
        query_words = query.lower().split()
        
        best_doc = None
        best_score = 0
        
        for doc in self.doc_texts:
            doc_lower = doc.lower()
            score = sum(1 for word in query_words if word in doc_lower)
            if score > best_score:
                best_score = score
                best_doc = doc
        
        if best_doc and best_score > 0:
            return f"Found this in our docs:\n\n{best_doc[:500]}..."
        else:
            return "Couldn't find anything. Please contact support."
    
    def _format_response(self, query: str, doc: str) -> str:
        """Formats a response from a document"""
        lines = doc.split('\n')
        relevant = []
        
        query_words = query.lower().split()
        for line in lines:
            if any(word in line.lower() for word in query_words):
                relevant.append(line.strip())
        
        if relevant:
            response = "\n".join(relevant[:5])
            return f"Here's what I found:\n\n{response}"
        else:
            return f"From our knowledge base:\n\n{doc[:500]}..."