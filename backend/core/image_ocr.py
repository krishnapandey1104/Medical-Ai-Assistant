import io
import re
import shutil
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

# =========================================================
#  SAFE IMPORT
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
#  TESSERACT SETUP
# =========================================================
TESSERACT_PATH = shutil.which("tesseract")

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
else:
    print("⚠️ Tesseract not found → OCR disabled")


SUPPORTED_TYPES = (".pdf", ".png", ".jpg", ".jpeg")


# =========================================================
#  TEXT CLEANING (IMPROVED)
# =========================================================
def clean_text(text):
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


# =========================================================
#  VALIDATION (IMPORTANT )
# =========================================================
def is_valid_medical_text(text):

    if not text or len(text.strip()) < 40:
        return False

    keywords = [
        "hb", "hemoglobin", "glucose", "cholesterol",
        "wbc", "rbc", "platelet", "test", "result"
    ]

    score = sum(1 for k in keywords if k in text.lower())

    return score >= 1


# =========================================================
#  IMAGE PREPROCESS ( MAJOR UPGRADE)
# =========================================================
def preprocess_image(img):
    img = img.convert("L")  # grayscale

    # increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)

    # sharpen
    img = img.filter(ImageFilter.SHARPEN)

    return img


# =========================================================
# OCR IMAGE (UPGRADED)
# =========================================================
def ocr_image(image_bytes):

    if not TESSERACT_PATH:
        return ""

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = preprocess_image(img)

        return pytesseract.image_to_string(
            img,
            config="--oem 3 --psm 6"
        )

    except Exception as e:
        print("❌ OCR ERROR:", e)
        return ""


# =========================================================
#  PDF PROCESS (IMPROVED)
# =========================================================
def extract_pdf_text(file_bytes):

    text = ""

    try:
        pdf = fitz.open(stream=file_bytes, filetype="pdf")

        for i in range(min(len(pdf), 10)):
            text += pdf[i].get_text()

        #  fallback OCR
        if len(text.strip()) < 50:
            print("🔄 OCR fallback activated")

            for i in range(min(len(pdf), 5)):
                pix = pdf[i].get_pixmap(matrix=fitz.Matrix(2, 2))
                text += ocr_image(pix.tobytes())

        pdf.close()

    except Exception as e:
        print("❌ PDF ERROR:", e)

    return text


# =========================================================
#  TABLE EXTRACTION (KEEP SIMPLE + STABLE)
# =========================================================
def extract_tables(text):

    results = []

    INVALID_WORDS = [
        "page", "may", "date", "positive", "negative",
        "test", "report", "lab", "method", "note"
    ]

    VALID_TESTS = [
        "hemoglobin", "rbc", "wbc", "platelet",
        "pcv", "mcv", "mch", "mchc", "rdw",
        "neutrophils", "lymphocytes", "monocytes", "eosinophils"
    ]

    pattern = re.compile(
        r"([A-Za-z][A-Za-z \(\)%]+)\s+"
        r"(\d+\.?\d*)\s*"
        r"([a-zA-Z/%µ]*)\s*"
        r"(\d+\.?\d*\s*[-–]\s*\d+\.?\d*)"
    )

    for line in text.split("\n"):
        line = line.strip()

        match = pattern.search(line)
        if not match:
            continue

        test = match.group(1).strip()
        value = match.group(2)
        unit = match.group(3) or ""
        range_text = match.group(4) or ""

        #  REMOVE NOISE
        if any(word in test.lower() for word in INVALID_WORDS):
            continue

        #  ONLY MEDICAL TESTS
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
            "status": detect_status(value, low, high)
        })

    return results


# =========================================================
#  RANGE + STATUS
# =========================================================
def extract_range(text):
    match = re.search(r"(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)", text or "")
    return (float(match.group(1)), float(match.group(2))) if match else (None, None)


def detect_status(value, low, high):
    try:
        v = float(value)

        if low is None or high is None:
            return "UNKNOWN"

        if v < low:
            return "LOW"
        elif v > high:
            return "HIGH"

        return "NORMAL"

    except:
        return "UNKNOWN"


# =========================================================
#  MAIN FUNCTION
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

    # -------------------------
    # EXTRACT
    # -------------------------
    if filename.endswith(".pdf"):
        text = extract_pdf_text(file_bytes)
    else:
        text = ocr_image(file_bytes)

    # -------------------------
    # VALIDATE
    # -------------------------
    if not text or len(text.strip()) < 30:
        return {
            "text": "",
            "tables": [],
            "trends": {},
            "formatted": ""
        }

    cleaned = clean_text(text)
    tables = extract_tables(cleaned)

    return {
        "text": cleaned[:2000],
        "tables": tables,
        "trends": {},
        "formatted": ""
    }

