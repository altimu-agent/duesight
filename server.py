"""DueSight web server — FastAPI + Server-Sent Events.

Run locally:
    .venv/bin/uvicorn server:app --reload --port 8000

Production:
    uvicorn server:app --host 0.0.0.0 --port $PORT
"""

import json
import os
import sys

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from agent import run_agent_stream  # noqa: E402

load_dotenv()

app = FastAPI(title="DueSight", description="Elite B2B intelligence in minutes.")
app.mount("/static", StaticFiles(directory="static"), name="static")


class AnalyzeRequest(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    website: str | None = None
    industry: str | None = None
    country: str | None = None
    contract_value: int | None = None
    competitors: list[str] | None = None


@app.get("/")
def index() -> FileResponse:
    return FileResponse("static/index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model": os.getenv("MODEL", "claude-sonnet-4-6")}


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest) -> StreamingResponse:
    if not os.getenv("TOKENROUTER_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="TOKENROUTER_API_KEY not configured on the server.",
        )

    def event_stream():
        try:
            for event in run_agent_stream(
                company=req.company,
                website=req.website,
                industry=req.industry,
                country=req.country,
                contract_value=req.contract_value,
                competitors=req.competitors,
            ):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            err = {"type": "error", "message": f"{type(e).__name__}: {e}"}
            yield f"data: {json.dumps(err)}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
