"""FastAPI application: the three interfaces plus the chat and appointment endpoints."""

import logging
from functools import lru_cache

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from . import config, database
from .llm import get_ai_response, get_gpt_oss_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Robust GPT-OSS-20B FCAP Platform")


class ChatMessage(BaseModel):
    message: str
    session_id: str = "default"


@lru_cache
def render(name: str) -> str:
    """Read an interface template from disk, cached after the first request."""
    return (config.TEMPLATE_DIR / f"{name}.html").read_text(encoding="utf-8")


database.init_database()


# PATIENT INTERFACE
@app.get("/", response_class=HTMLResponse)
async def patient_interface(request: Request):
    return render("patient")


@app.get("/clinic", response_class=HTMLResponse)
async def clinic_interface():
    return render("clinic")


@app.get("/admin", response_class=HTMLResponse)
async def admin_interface():
    return render("admin")


@app.post("/chat")
async def chat_endpoint(chat_data: ChatMessage):
    """Chat endpoint with GPT-OSS-20B integration - no fallbacks"""
    response = get_ai_response(chat_data.message)
    database.save_conversation(chat_data.session_id, chat_data.message, response)
    return {"response": response, "session_id": chat_data.session_id}


@app.get("/appointments")
async def get_appointments():
    """Get all appointments"""
    return database.list_appointments()


@app.post("/appointments")
async def create_appointment(
    patient_name: str = Form(...),
    patient_email: str = Form(...),
    appointment_date: str = Form(...),
    appointment_time: str = Form(...),
    doctor_name: str = Form("Dr. Smith")
):
    """Create a new appointment"""
    database.create_appointment(patient_name, patient_email, appointment_date,
                                appointment_time, doctor_name)
    return {"message": "Appointment created successfully"}


@app.get("/health/llm")
async def llm_health():
    """LLM health check endpoint"""
    try:
        response = get_gpt_oss_response("Say 'Hello from GPT-OSS-20B' in one sentence.")
        return {"ok": True, "sample": response[:40], "model": "gpt-oss-20b"}
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        return {"ok": False, "error": str(e), "model": "gpt-oss-20b"}
