"""Optional minimal JSON API for the script engine.

This API is not required for the Streamlit app. Run locally with:
    uvicorn api:app --host 0.0.0.0 --port 8000
"""
from engine.core import generate_script

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
    app = FastAPI(title="Akansha AI Video Studio API", version="1.0.0")

    class ScriptRequest(BaseModel):
        topic: str
        audience: str = "General audience"
        presenter: str = "Akansha"
        style: str = "Educational"
        tone: str = "Simple and conversational"
        duration: int = 2
        extra_context: str = ""
        include_example: bool = True
        include_cta: bool = True

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/generate-script")
    def script(request: ScriptRequest):
        if not request.topic.strip():
            return {"error": "topic is required"}
        result = generate_script(
            topic=request.topic,
            audience=request.audience,
            presenter=request.presenter,
            style=request.style,
            tone=request.tone,
            duration=request.duration,
            extra_context=request.extra_context,
            include_example=request.include_example,
            include_cta=request.include_cta,
        )
        return {"script": result}
except ImportError:
    app = None
