
import os
from dotenv import load_dotenv

# #  Always load from ROOT 
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ENV_PATH = os.path.join(BASE_DIR, "..", ".env")

load_dotenv()


# =========================================================
#  MODEL CONFIG
# =========================================================
MODELS = {
    "qa": os.getenv("QA_MODEL", "llama3"),
    "tool": os.getenv("TOOL_MODEL", "phi3"),
    "report": os.getenv("REPORT_MODEL", "llama3"),
}


# =========================================================
#  GENERATION SETTINGS
# =========================================================
GEN_CONFIG = {
    "temperature": float(os.getenv("TEMPERATURE", 0.25)),
    "max_tokens": int(os.getenv("MAX_TOKENS", 600)),
    "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", 2)),
    "timeout": int(os.getenv("TIMEOUT", 120)),   # FIXED
}


# =========================================================
#  APP CONFIG
# =========================================================
APP_NAME = os.getenv("APP_NAME", "AI Medical Assistant")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# =========================================================
#  SAFETY CONFIG (CRITICAL)
# =========================================================
ENABLE_MEDICINE_SUGGESTION = os.getenv("ENABLE_MEDICINE", "False").lower() == "true"

STRICT_MEDICAL_MODE = os.getenv("STRICT_MEDICAL_MODE", "True").lower() == "true"

ALLOW_UNKNOWN_CONDITIONS = os.getenv("ALLOW_UNKNOWN", "False").lower() == "true"

ENABLE_VALIDATION = os.getenv("ENABLE_VALIDATION", "True").lower() == "true"

EMERGENCY_OVERRIDE = os.getenv("EMERGENCY_OVERRIDE", "True").lower() == "true"


# =========================================================
#  RAG CONFIG
# =========================================================
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "vector_db")
KNOWLEDGE_PATH = os.getenv("KNOWLEDGE_PATH", "medical_knowledge")

TOP_K = int(os.getenv("TOP_K", 3))
MIN_RELEVANCE_SCORE = int(os.getenv("MIN_RELEVANCE_SCORE", 2))


# =========================================================
# FEATURES
# =========================================================
ENABLE_OCR = os.getenv("ENABLE_OCR", "True").lower() == "true"

ENABLE_WEB_SEARCH = os.getenv("ENABLE_WEB_SEARCH", "True").lower() == "true"

ENABLE_RAG = os.getenv("ENABLE_RAG", "True").lower() == "true"


# =========================================================
#  PERFORMANCE
# =========================================================
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"

MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", 1200))


# =========================================================
#  TRUSTED SOURCES
# =========================================================
TRUSTED_SITES = [
    "who.int",
    "cdc.gov",
    "nih.gov",
    "nhs.uk",
    "mayoclinic.org",
    "medlineplus.gov",
    "clevelandclinic.org",
    "hopkinsmedicine.org",
    "health.harvard.edu",
    "ncbi.nlm.nih.gov",
    "pubmed.ncbi.nlm.nih.gov",
    "webmd.com",
    "healthline.com",
    "verywellhealth.com",
    "mountsinai.org",
    "stanfordhealthcare.org"
]


# =========================================================
#  OCR PATH
# =========================================================
TESSERACT_PATH = os.getenv("TESSERACT_PATH", None)


# =========================================================
#  VALIDATION
# =========================================================
def validate_config():

    if not MODELS["qa"]:
        raise ValueError("❌ QA_MODEL is not set")

    if GEN_CONFIG["max_tokens"] < 100:
        raise ValueError("❌ MAX_TOKENS too low")

    if GEN_CONFIG["timeout"] < 30:
        raise ValueError("❌ TIMEOUT too low")

    if TOP_K <= 0:
        raise ValueError("❌ TOP_K must be > 0")

    if MIN_RELEVANCE_SCORE < 1:
        raise ValueError("❌ MIN_RELEVANCE_SCORE must be >= 1")

    if GEN_CONFIG["retry_attempts"] <= 0:
        raise ValueError("❌ RETRY_ATTEMPTS must be > 0")

    print("✅ Config loaded successfully")


# =========================================================
#  RUN VALIDATION
# =========================================================
validate_config()



