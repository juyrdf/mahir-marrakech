import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.main import app as fastapi_app
import gradio as gr

# Create a clean Gradio interface for Hugging Face Spaces
with gr.Blocks(title="Mahir Marrakech AI") as demo:
    gr.Markdown("# 🇲🇦 Mahir Marrakech AI Companion & PWA")
    gr.Markdown("Welcome! The Mahir Marrakech API and PWA application are active.")
    gr.Markdown("- 📱 **Open Mobile PWA Web App**: [Click Here to Launch App](/app)")
    gr.Markdown("- ⚙️ **API Documentation**: [View OpenAPI Docs](/docs)")

app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
