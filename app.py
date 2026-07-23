import gradio as gr
import uvicorn
import os
import sys

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.app.main import app as fastapi_app

# Mount FastAPI inside Gradio
demo = gr.Blocks(title="Mahir Marrakech")

app = gr.mount_gradio_app(fastapi_app, demo, path="/gradio")

if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="0.0.0.0", port=7860)
