# backend/tools/safety_guard.py

from backend.tools.symptom_checker import (
    detect_symptoms,
    get_overall_severity
)

from backend.config import ENABLE_MEDICINE_SUGGESTION


# =========================================================
#  KEYWORDS
# =========================================================
RISKY_KEYWORDS = [
    "pregnant", "pregnancy",
    "baby", "infant", "child",
    "breastfeeding"
]

EMERGENCY_KEYWORDS = [
    "chest pain",
    "heart attack",
    "stroke",
    "severe bleeding",
    "unconscious",
    "difficulty breathing"
]

MEDICINE_KEYWORDS = [
    "medicine", "tablet", "drug",
    "treatment", "what should i take",
    "what can i take", "suggest"
]

DOSAGE_KEYWORDS = [
    "dose", "dosage", "mg",
    "how much", "how many"
]


# =========================================================
#  DETECTORS
# =========================================================
def is_medicine_query(query: str) -> bool:
    return any(k in query.lower() for k in MEDICINE_KEYWORDS)


def is_dosage_query(query: str) -> bool:
    return any(k in query.lower() for k in DOSAGE_KEYWORDS)


def is_risky(query: str) -> bool:
    return any(k in query.lower() for k in RISKY_KEYWORDS)


def is_emergency(query: str) -> bool:
    return any(k in query.lower() for k in EMERGENCY_KEYWORDS)


# =========================================================
#  MAIN SAFETY LOGIC (BALANCED )
# =========================================================
def allow_medicine(query: str) -> dict:

    try:
        q = query.lower()

        symptoms = detect_symptoms(q)
        severity = get_overall_severity(q)

        # ----------------------------
        #  EMERGENCY → HARD BLOCK
        # ----------------------------
        if is_emergency(q) or severity == "severe":
            return block("Emergency condition", "severe", symptoms)

        # ----------------------------
        #  DOSAGE → HARD BLOCK
        # ----------------------------
        if is_dosage_query(q):
            return block("Dosage advice not allowed", severity, symptoms)

        # ----------------------------
        # RISKY CASE
        # ---------------------------
        if is_risky(q):
            return block("Special population (pregnancy/child)", "high", symptoms)

        # ----------------------------
        #  GLOBAL DISABLE
        # ----------------------------
        if not ENABLE_MEDICINE_SUGGESTION:
            return soft_block("Medicine suggestions disabled", severity, symptoms)

        # ----------------------------
        #  NORMAL QUERY (IMPORTANT FIX )
        # ----------------------------
        # allow general symptom help even if not explicit medicine query
        return {
            "allowed": True,
            "type": "safe",
            "severity": severity,
            "symptoms": symptoms
        }

    except Exception as e:
        print("❌ SAFETY ERROR:", e)
        return block("System safety fallback")


# =========================================================
#  HARD BLOCK
# =========================================================
def block(reason, severity="unknown", symptoms=None):

    return {
        "allowed": False,
        "type": "hard",
        "reason": reason,
        "severity": severity,
        "symptoms": symptoms or []
    }


# =========================================================
#  SOFT BLOCK (NEW )
# =========================================================
def soft_block(reason, severity="unknown", symptoms=None):

    return {
        "allowed": False,
        "type": "soft",
        "reason": reason,
        "severity": severity,
        "symptoms": symptoms or []
    }


# =========================================================
#  USER MESSAGE (SMART UX )
# =========================================================
def safety_message(result):

    if result.get("allowed"):
        return ""

    reason = result.get("reason", "")

    # ----------------------------
    # HARD BLOCK → STRONG WARNING
    # ----------------------------
    if result.get("type") == "hard":
        return f"""
⚠️ For your safety, this request is restricted.

Reason: {reason}

👉 Please consult a doctor immediately.
"""

    # ----------------------------
    # SOFT BLOCK → LIGHT MESSAGE
    # ----------------------------
    return f"""
Note:
{reason}

General guidance can still be provided.
"""





