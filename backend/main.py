from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from contextlib import asynccontextmanager

from backend.core.image_ocr import extract_text
from backend.agents.agent_controller import agent_controller
from backend.core.memory import (
    init_db,
    create_session,
    add_message,
    get_messages,
    save_report,
    get_latest_report,
    get_sessions
)

# ===============================
# LIFESPAN
# ===============================
@asynccontextmanager
async def lifespan(app):
    print("🚀 Starting server...")
    init_db()
    yield
    print("🛑 Shutting down...")

# ===============================
# INIT APP
# ===============================
app = FastAPI(
    title="AI Medical Assistant",
    lifespan=lifespan
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_path = os.path.join(BASE_DIR, "frontend")

app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# ===============================
# CORS
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# MODELS
# ===============================
class ChatRequest(BaseModel):
    message: str
    session_id: int | None = None


# ===============================
# VALIDATION
# ===============================
def validate_session(session_id: int):
    if not session_id or session_id <= 0:
        raise HTTPException(400, "Invalid session ID")

    sessions = get_sessions("user1")
    valid_ids = [s["id"] for s in sessions]

    if session_id not in valid_ids:
        raise HTTPException(404, "Session not found")


def validate_message(message: str):
    if not message or len(message.strip()) < 2:
        raise HTTPException(400, "Message too short")


def validate_file(filename: str):
    if not filename.lower().endswith((".pdf", ".png", ".jpg", ".jpeg")):
        raise HTTPException(400, "Unsupported file type")


# ===============================
# ROUTES
# ===============================

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def home():
    return FileResponse(os.path.join(frontend_path, "dashboard.html"))


@app.get("/session")
def new_session():
    session_id = create_session("user1")
    print("🆕 New session:", session_id)
    return {"session_id": session_id}


# ===============================
# CHAT (FIXED)
# ===============================
@app.post("/chat")
async def chat(data: ChatRequest):

    try:
        # ✅ FIXED SESSION HANDLING
        if not data.session_id:
            session_id = create_session("user1")
        else:
            session_id = int(data.session_id)

        validate_session(session_id)
        validate_message(data.message)

        print("\n💬 USER:", data.message)

        add_message(session_id, "user", data.message)

        history = get_messages(session_id)
        report_text = get_latest_report(session_id) or ""

        # 🤖 AI CALL
        response = agent_controller(
            question=data.message,
            report_text=report_text,
            user_id="user1",
            messages=history,
            structured_data=[]
        )

        # fallback
        if not response or len(response.strip()) < 10:
            print("⚡ fallback triggered")

            response = agent_controller(
                question=data.message,
                report_text="",
                user_id="user1",
                messages=[],
                structured_data=[]
            )

            if not response:
                response = "⚠️ AI couldn't generate a response. Try again."

        add_message(session_id, "assistant", response)

        print(f"✅ RESPONSE READY (session {session_id})")

        return {
            "response": response,
            "session_id": session_id
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        print("❌ CHAT ERROR:", e)
        return {
            "response": f"⚠️ Error: {str(e)}",
            "session_id": data.session_id
        }


# ===============================
# HISTORY
# ===============================
@app.get("/history/{session_id}")
def get_history(session_id: int):

    try:
        validate_session(session_id)
        history = get_messages(session_id)
        return {"history": history}

    except HTTPException as e:
        raise e

    except Exception as e:
        print("❌ HISTORY ERROR:", e)
        return {"history": []}


# ===============================
# UPLOAD
# ===============================
@app.post("/upload")
async def upload_auto(
    file: UploadFile = File(...),
    session_id: int = Form(None)
):

    try:
        validate_file(file.filename)

        file_bytes = await file.read()
        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(400, "File too large (max 10MB)")
        await file.seek(0)

        # AUTO SESSION
        if session_id is None:
            session_id = create_session("user1")

        print(f"\n📄 UPLOAD: {file.filename} (session {session_id})")

        result = await extract_text(file)

        text = result.get("text", "")
        tables = result.get("tables", [])
        trends = result.get("trends", {})
        formatted = result.get("formatted", "")

        if not text.strip() and not tables:
            raise HTTPException(400, "⚠️ Could not read report")

        save_report(session_id, text)

        # 🤖 AI ANALYSIS
        summary = agent_controller(
            question="Analyze medical report",
            report_text=text,
            user_id="user1",
            messages=[],
            structured_data=tables
        )

        return {
            "session_id": session_id,
            "summary": summary,
            "tables": tables,
            "trends": trends,
            "formatted": formatted
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        print("❌ UPLOAD ERROR:", e)
        raise HTTPException(500, f"Report analysis failed: {str(e)}")


# ===============================
# OPTIONAL FEATURES
# ===============================
cart = []

@app.post("/cart/add")
def add_cart(item: dict):
    cart.append(item)
    return {"message": "Added", "cart": cart}


@app.get("/cart")
def get_cart():
    return cart


appointments = []

@app.post("/doctor/book")
def book(doc: dict):
    appointments.append(doc)
    return {"message": "Booked", "appointments": appointments}


@app.get("/doctor")
def get_doc():
    return appointments