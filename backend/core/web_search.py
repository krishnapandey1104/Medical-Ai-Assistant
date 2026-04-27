import requests
import time
import re

from backend.config import TRUSTED_SITES, ENABLE_WEB_SEARCH
from backend.tools.safety_guard import allow_medicine


# =========================================================
#  CACHE
# =========================================================
CACHE = {}
CACHE_TTL = 60 * 20  # 20 min


def normalize_key(key):
    return key.strip().lower()


def get_cache(key):
    key = normalize_key(key)

    if key in CACHE:
        value, timestamp = CACHE[key]

        if time.time() - timestamp < CACHE_TTL:
            return value

        del CACHE[key]

    return None


def set_cache(key, value):
    CACHE[normalize_key(key)] = (value, time.time())


# =========================================================
#  CLEAN
# =========================================================
def clean(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def deduplicate_sentences(text):
    seen = set()
    result = []

    for sentence in re.split(r"[.!?]", text):
        s = sentence.strip()

        if len(s) < 15:
            continue

        if s not in seen:
            seen.add(s)
            result.append(s)

    return ". ".join(result[:3])  #  tighter


# =========================================================
#  INTENT
# =========================================================
def detect_intent(query):

    q = query.lower()

    if any(k in q for k in ["pain", "fever", "cough", "breathing", "fatigue", "tired"]):
        return "symptom"

    if any(k in q for k in ["report", "value", "cholesterol", "hb", "sugar"]):
        return "report"

    return "general"


# =========================================================
#  FETCH WEB (IMPROVED )
# =========================================================
def search_trusted_web(query):

    cache_key = f"web:{query}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    try:
        #  smarter query expansion
        query = f"{query} causes symptoms treatment diagnosis"

        # better endpoint
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            },
            timeout=6
        )

        data = response.json()

        texts = []

        #  main abstract
        if data.get("AbstractText"):
            texts.append(clean(data["AbstractText"]))

        # related topics
        for topic in data.get("RelatedTopics", [])[:5]:
            if "Text" in topic:
                texts.append(clean(topic["Text"]))

        result = " ".join(texts)

        #  CLEAN
        result = deduplicate_sentences(result)

        # REMOVE HARD FILTER (IMPORTANT FIX)
        if not result:
            return ""

        set_cache(cache_key, result)
        return result

    except Exception as e:
        print("❌ WEB ERROR:", e)
        return ""


# =========================================================
#  SAFETY FILTER
# =========================================================
def enforce_web_safety(query, text):

    decision = allow_medicine(query)

    if not decision["allowed"]:
        if any(word in text.lower() for word in [
            "paracetamol", "ibuprofen", "dose", "tablet"
        ]):
            return "⚠️ Medicine-related advice is restricted."

    return text


# =========================================================
#  FORMAT RESPONSE (LLM-FRIENDLY )
# =========================================================
def format_web_response(query, text):

    intent = detect_intent(query)

    short_text = text[:250]  #  shorter

    if intent == "symptom":
        return f"Clinical reference:\n{short_text}"

    if intent == "report":
        return f"Medical reference:\n{short_text}"

    return short_text


# =========================================================
#  MAIN ROUTER
# =========================================================
def search_medical_web(query):

    if not ENABLE_WEB_SEARCH:
        return ""

    #  skip trivial queries
    if len(query.split()) < 4:
        return ""

    try:
        web_text = search_trusted_web(query)

        if not web_text:
            return ""

        safe_text = enforce_web_safety(query, web_text)

        return format_web_response(query, safe_text)

    except Exception as e:
        print("❌ WEB ROUTER ERROR:", e)
        return ""




