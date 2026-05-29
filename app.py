import gradio as gr
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from main import app
from ai_engine import AIEngine
from config import settings
import uvicorn
import threading
import time
from loguru import logger

# Initialize AI engine
ai = None

def setup_ai():
    """Sets up the AI engine in background"""
    global ai
    try:
        logger.info("Loading AI engine...")
        ai = AIEngine()
        logger.info("AI engine ready")
    except Exception as err:
        logger.error(f"AI setup failed: {err}")

def test_classification(subject, description):
    """Tests ticket classification"""
    if not ai:
        return "AI engine not ready yet. Please wait..."
    
    try:
        tier, confidence, category = ai.categorize_ticket(subject, description)
        
        result = f"""
### Classification Results

**Tier:** {tier.upper()}
**Confidence:** {confidence:.0%}
**Category:** {category}

**What this means:**
"""
        
        if tier == "tier_1":
            result += "\n✅ Simple issue - can be auto-resolved"
        elif tier == "tier_2":
            result += "\n⚠️ Moderate complexity - bot will assist"
        else:
            result += "\n🚨 Complex issue - needs human agent"
        
        return result
        
    except Exception as err:
        logger.error(f"Classification test failed: {err}")
        return f"Error: {str(err)}"

def test_rag(query):
    """Tests RAG functionality"""
    if not ai:
        return "AI engine not ready yet. Please wait..."
    
    try:
        response = ai.get_rag_response(query)
        return f"### AI Response\n\n{response}"
    except Exception as err:
        logger.error(f"RAG test failed: {err}")
        return f"Error: {str(err)}"

def check_status():
    """Checks system status"""
    status = {
        "AI Engine": "✅ Ready" if ai else "❌ Not loaded",
        "Freshdesk Domain": settings.FRESHDESK_DOMAIN or "Not configured",
        "API Key": "✅ Set" if settings.FRESHDESK_API_KEY else "❌ Missing",
        "Database": settings.DATABASE_URL,
        "Log Level": settings.LOG_LEVEL
    }
    
    result = "### System Status\n\n"
    for key, value in status.items():
        result += f"**{key}:** {value}\n\n"
    
    return result

# Create the Gradio interface
with gr.Blocks(
    title="AI Ticket Bot",
    theme=gr.themes.Soft(),
    css="""
    .gradio-container {
        max-width: 1200px !important;
    }
    """
) as demo:
    
    gr.Markdown("""
    # 🤖 AI Customer Ticket Resolution Bot
    
    **Real-time AI-powered customer support automation**
    
    ---
    """)
    
    with gr.Tabs():
        
        # Ticket Classification Tab
        with gr.TabItem("🎯 Ticket Classification"):
            gr.Markdown("""
            ### Test Ticket Classification
            
            See how the AI categorizes different types of tickets.
            """)
            
            with gr.Row():
                with gr.Column():
                    subject_input = gr.Textbox(
                        label="Ticket Subject",
                        placeholder="e.g., Password reset not working"
                    )
                    desc_input = gr.Textbox(
                        label="Ticket Description",
                        placeholder="e.g., I clicked the reset link but nothing happened",
                        lines=5
                    )
                    classify_btn = gr.Button("Classify Ticket", variant="primary")
                
                with gr.Column():
                    classify_output = gr.Markdown(label="Results")
            
            classify_btn.click(
                fn=test_classification,
                inputs=[subject_input, desc_input],
                outputs=classify_output
            )
        
        # RAG Testing Tab
        with gr.TabItem("🔍 RAG Query Testing"):
            gr.Markdown("""
            ### Test Knowledge Base Retrieval
            
            Ask questions to see what the AI finds in the knowledge base.
            """)
            
            with gr.Row():
                with gr.Column():
                    rag_query = gr.Textbox(
                        label="Your Question",
                        placeholder="e.g., How do I reset my password?",
                        lines=3
                    )
                    rag_btn = gr.Button("Search Knowledge Base", variant="primary")
                
                with gr.Column():
                    rag_output = gr.Markdown(label="AI Response")
            
            rag_btn.click(
                fn=test_rag,
                inputs=[rag_query],
                outputs=rag_output
            )
        
        # System Status Tab
        with gr.TabItem("🏥 System Status"):
            gr.Markdown("""
            ### System Health Check
            
            Check if everything is configured properly.
            """)
            
            status_btn = gr.Button("Check Status", variant="primary")
            status_output = gr.Markdown()
            
            status_btn.click(
                fn=check_status,
                inputs=[],
                outputs=status_output
            )
        
        # Documentation Tab
        with gr.TabItem("📚 Documentation"):
            gr.Markdown("""
            ## 🚀 AI Customer Ticket Resolution Bot
            
            ### Features:
            - 🤖 **AI Classification:** Automatically categorizes tickets
            - 🔍 **Smart Search:** Retrieves relevant info from knowledge base
            - ⚡ **Auto-Resolution:** Resolves simple tickets automatically
            - 🚨 **Smart Escalation:** Routes complex issues to humans
            
            ### How It Works:
            1. **Ticket arrives** via Freshdesk webhook
            2. **AI analyzes** subject and description
            3. **Classifies** into Tier 1, 2, or Complex
            4. **Takes action** based on classification
            
            ### Tiers:
            - **Tier 1:** Simple issues (password resets, basic help)
            - **Tier 2:** Moderate issues (billing, account settings)
            - **Complex:** Technical issues, bugs, critical problems
            
            ### Tech Stack:
            - **Framework:** FastAPI + Gradio
            - **AI Models:** Sentence Transformers
            - **Database:** SQLite
            - **Integration:** Freshdesk API
            
            ---
            
            **Built for automated customer support** ❤️
            """)
    
    gr.Markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; margin: 20px 0;">
        <h3>🚀 Production Ready</h3>
        <p>This bot handles real customer tickets with AI automation.</p>
    </div>
    """)

# Start AI setup in background
threading.Thread(target=setup_ai, daemon=True).start()

# Launch the app
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )