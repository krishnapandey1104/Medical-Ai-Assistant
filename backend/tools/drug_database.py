# =========================================================
#  SYMPTOM → SAFE MEDICAL OPTIONS
# =========================================================
SYMPTOM_DRUGS = {
    "fever": ["Paracetamol", "Ibuprofen"],
    "headache": ["Ibuprofen", "Paracetamol"],
    "cold": ["Cetirizine", "Paracetamol"],
    "cough": ["Dextromethorphan", "Ambroxol"],
    "body pain": ["Ibuprofen", "Diclofenac"],
    "sore throat": ["Lozenges", "Paracetamol"],
    "fatigue": ["Multivitamins", "Iron supplements"]  #  added
}


# =========================================================
#  NORMALIZE TEXT (BETTER MATCH )
# =========================================================
def normalize(text):
    return text.lower().strip()


# =========================================================
#  SAFETY FILTER (IMPROVED )
# =========================================================
def is_safe_query(text):

    text = normalize(text)

    unsafe_keywords = [
        "dose", "dosage", "how much",
        "prescribe", "mg", "tablet",
        "exact medicine", "which medicine exactly"
    ]

    return not any(k in text for k in unsafe_keywords)


# =========================================================
#  SMART SYMPTOM DETECTION
# =========================================================
def detect_symptom(text):

    text = normalize(text)

    for symptom in SYMPTOM_DRUGS.keys():
        if symptom in text:
            return symptom

    #  extra mapping
    if "tired" in text or "weak" in text:
        return "fatigue"

    return None


# ========================================================
#  SAFE MEDICINE SUGGESTION (FINAL )
# =========================================================
def get_medicine(text: str):

    text = normalize(text)

    # ----------------------------
    #  BLOCK UNSAFE
    # ----------------------------
    if not is_safe_query(text):
        return {
            "allowed": False,
            "message": "⚠️ Specific dosage or prescription advice is not provided."
        }

    # ----------------------------
    #  DETECT SYMPTOM
    # ----------------------------
    symptom = detect_symptom(text)

    if not symptom:
        return {
            "allowed": False,
            "message": ""
        }

    drugs = SYMPTOM_DRUGS.get(symptom, [])

    if not drugs:
        return {
            "allowed": False,
            "message": ""
        }

    # ----------------------------
    #  SAFE RESPONSE
    # ----------------------------
    return {
        "allowed": True,
        "meds": drugs[:2],
        "message": f"""
Additional guidance:
Some common over-the-counter options may include {drugs[0]} or {drugs[1]}.

⚠️ Avoid self-medication if symptoms are severe, persistent, or unclear.
"""
    }





