import io
import re
import shutil
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

from backend.config import TESSERACT_PATH as ENV_TESSERACT_PATH

# =========================================================
# SAFE IMPORT
# =========================================================
try:
    import fitz  # PyMuPDF
    assert hasattr(fitz, "open")
except Exception:
    raise RuntimeError(
        "❌ PyMuPDF not installed correctly.\n"
        "Run: pip uninstall fitz -y && pip install PyMuPDF"
    )


# =========================================================
# TESSERACT SETUP (FIXED)
# =========================================================
TESSERACT_PATH = ENV_TESSERACT_PATH or shutil.which("tesseract")

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    print(f"✅ Tesseract loaded: {TESSERACT_PATH}")
else:
    print("⚠️ Tesseract not found → OCR disabled")


SUPPORTED_TYPES = (".pdf", ".png", ".jpg", ".jpeg")


# =========================================================
# TEXT CLEANING
# =========================================================
def clean_text(text):
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


# =========================================================
# VALIDATION
# =========================================================
def is_valid_medical_text(text):
    keywords = [
        "hemoglobin", "glucose", "cholesterol", "wbc",
        "rbc", "platelet", "creatinine", "urea",
        "test", "report", "result"
    ]
    score = sum(1 for k in keywords if k in text.lower())
    return score >= 1


# =========================================================
# IMAGE PREPROCESS (IMPROVED)
# =========================================================
def preprocess_image(img):
    img = img.convert("L")

    img = ImageEnhance.Contrast(img).enhance(2.5)
    img = ImageEnhance.Sharpness(img).enhance(2)

    img = img.filter(ImageFilter.MedianFilter())

    return img


# =========================================================
# OCR IMAGE
# =========================================================
def ocr_image(image_bytes):

    if not TESSERACT_PATH:
        return ""

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = preprocess_image(img)

        text = pytesseract.image_to_string(
            img,
            config="--oem 3 --psm 6"
        )

        return text

    except Exception as e:
        print("❌ OCR ERROR:", e)
        return ""


# =========================================================
# PDF PROCESS
# =========================================================
def extract_pdf_text(file_bytes):

    text = ""

    try:
        pdf = fitz.open(stream=file_bytes, filetype="pdf")

        for i in range(min(len(pdf), 10)):
            text += pdf[i].get_text()

        # OCR fallback
        if len(text.strip()) < 50:
            print("🔄 OCR fallback activated")

            for i in range(min(len(pdf), 5)):
                pix = pdf[i].get_pixmap(matrix=fitz.Matrix(3, 3))
                img_bytes = pix.tobytes()
                text += ocr_image(img_bytes)

        pdf.close()

    except Exception as e:
        print("❌ PDF ERROR:", e)

    return text


# =========================================================
# TABLE EXTRACTION (IMPROVED)
# =========================================================
def extract_tables(text):

    results = []

    VALID_TESTS = [
        "hemoglobin", "rbc", "wbc", "platelet",
        "pcv", "mcv", "mch", "mchc", "rdw",
        "glucose", "cholesterol", "triglycerides",
        "creatinine", "urea", "bilirubin",
        "neutrophils", "lymphocytes", "monocytes", "eosinophils"
    ]

    pattern = re.compile(
        r"([A-Za-z][A-Za-z \(\)%]+)\s+"
        r"(\d+\.?\d*)\s*"
        r"([a-zA-Z/%µ]*)\s*"
        r"(\d+\.?\d*\s*[-–]\s*\d+\.?\d*)"
    )

    for line in text.split("\n"):

        match = pattern.search(line)
        if not match:
            continue

        test = match.group(1).strip()
        value = match.group(2)
        unit = match.group(3) or ""
        range_text = match.group(4) or ""

        if not any(v in test.lower() for v in VALID_TESTS):
            continue

        try:
            value_float = float(value)
        except:
            continue

        low, high = extract_range(range_text)

        results.append({
            "test": test,
            "value": value_float,
            "unit": unit,
            "range": f"{low}-{high}" if low else "N/A",
            "status": detect_status(value_float, low, high)
        })

    print(f"📊 Extracted {len(results)} lab values")

    return results


# =========================================================
# RANGE + STATUS
# =========================================================
def extract_range(text):
    match = re.search(r"(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)", text or "")
    return (float(match.group(1)), float(match.group(2))) if match else (None, None)


def detect_status(value, low, high):
    if low is None or high is None:
        return "UNKNOWN"

    if value < low:
        return "LOW"
    elif value > high:
        return "HIGH"
    return "NORMAL"


# =========================================================
# MAIN FUNCTION
# =========================================================
async def extract_text(file):

    if not file:
        return {"text": "", "tables": [], "trends": {}, "formatted": ""}

    try:
        file_bytes = await file.read()
        await file.seek(0)
    except Exception as e:
        print("❌ FILE ERROR:", e)
        return {"text": "", "tables": [], "trends": {}, "formatted": ""}

    filename = file.filename.lower()

    if not filename.endswith(SUPPORTED_TYPES):
        return {"text": "Unsupported file type", "tables": [], "trends": {}, "formatted": ""}

    if filename.endswith(".pdf"):
        text = extract_pdf_text(file_bytes)
    else:
        text = ocr_image(file_bytes)

    if not text or len(text.strip()) < 30:
        return {"text": "", "tables": [], "trends": {}, "formatted": ""}

    cleaned = clean_text(text)
    tables = extract_tables(cleaned)

    return {
        "text": cleaned[:2000],
        "tables": tables,
        "trends": {},
        "formatted": ""
    }

















# import os
# from dotenv import load_dotenv

# # #  Always load from ROOT (safe way)
# # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# # ENV_PATH = os.path.join(BASE_DIR, "..", ".env")

# load_dotenv()


# # =========================================================
# #  MODEL CONFIG
# # =========================================================
# MODELS = {
#     "qa": os.getenv("QA_MODEL", "llama3"),
#     "tool": os.getenv("TOOL_MODEL", "phi3"),
#     "report": os.getenv("REPORT_MODEL", "llama3"),
# }


# # =========================================================
# #  GENERATION SETTINGS
# # =========================================================
# GEN_CONFIG = {
#     "temperature": float(os.getenv("TEMPERATURE", 3)),
#     "max_tokens": int(os.getenv("MAX_TOKENS", 600)),
#     "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", 2)),
#     "timeout": int(os.getenv("TIMEOUT", 120)),   # FIXED
# }


# # =========================================================
# #  APP CONFIG
# # =========================================================
# APP_NAME = os.getenv("APP_NAME", "AI Medical Assistant")

# DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# # =========================================================
# #  SAFETY CONFIG (CRITICAL)
# # =========================================================
# ENABLE_MEDICINE_SUGGESTION = os.getenv("ENABLE_MEDICINE", "False").lower() == "true"

# STRICT_MEDICAL_MODE = os.getenv("STRICT_MEDICAL_MODE", "True").lower() == "true"

# ALLOW_UNKNOWN_CONDITIONS = os.getenv("ALLOW_UNKNOWN", "False").lower() == "true"

# ENABLE_VALIDATION = os.getenv("ENABLE_VALIDATION", "True").lower() == "true"

# EMERGENCY_OVERRIDE = os.getenv("EMERGENCY_OVERRIDE", "True").lower() == "true"


# # =========================================================
# #  RAG CONFIG
# # =========================================================
# VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "vector_db")
# KNOWLEDGE_PATH = os.getenv("KNOWLEDGE_PATH", "medical_knowledge")

# TOP_K = int(os.getenv("TOP_K", 3))
# MIN_RELEVANCE_SCORE = int(os.getenv("MIN_RELEVANCE_SCORE", 2))


# # =========================================================
# # FEATURES
# # =========================================================
# ENABLE_OCR = os.getenv("ENABLE_OCR", "True").lower() == "true"

# ENABLE_WEB_SEARCH = os.getenv("ENABLE_WEB_SEARCH", "True").lower() == "true"

# ENABLE_RAG = os.getenv("ENABLE_RAG", "True").lower() == "true"


# # =========================================================
# #  PERFORMANCE
# # =========================================================
# CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"

# MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", 1200))


# # =========================================================
# #  TRUSTED SOURCES
# # =========================================================
# TRUSTED_SITES = [
#     "who.int",
#     "cdc.gov",
#     "nih.gov",
#     "nhs.uk",
#     "mayoclinic.org",
#     "medlineplus.gov",
#     "clevelandclinic.org",
#     "hopkinsmedicine.org",
#     "health.harvard.edu",
#     "ncbi.nlm.nih.gov",
#     "pubmed.ncbi.nlm.nih.gov",
#     "webmd.com",
#     "healthline.com",
#     "verywellhealth.com",
#     "mountsinai.org",
#     "stanfordhealthcare.org"
# ]


# # =========================================================
# #  OCR PATH
# # =========================================================
# TESSERACT_PATH = os.getenv("TESSERACT_PATH", None)


# # =========================================================
# #  VALIDATION
# # =========================================================
# def validate_config():

#     if not MODELS["qa"]:
#         raise ValueError("❌ QA_MODEL is not set")

#     if GEN_CONFIG["max_tokens"] < 100:
#         raise ValueError("❌ MAX_TOKENS too low")

#     if GEN_CONFIG["timeout"] < 30:
#         raise ValueError("❌ TIMEOUT too low")

#     if TOP_K <= 0:
#         raise ValueError("❌ TOP_K must be > 0")

#     if MIN_RELEVANCE_SCORE < 1:
#         raise ValueError("❌ MIN_RELEVANCE_SCORE must be >= 1")

#     if GEN_CONFIG["retry_attempts"] <= 0:
#         raise ValueError("❌ RETRY_ATTEMPTS must be > 0")

#     print("✅ Config loaded successfully")


# # =========================================================
# #  RUN VALIDATION
# # =========================================================
# validate_config()



