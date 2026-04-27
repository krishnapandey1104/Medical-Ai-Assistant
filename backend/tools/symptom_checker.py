# =========================================================
# ADVANCED SYMPTOM DATABASE (ENHANCED )
# =========================================================
SYMPTOMS_DB = {
    "fever": {
        "aliases": ["high temperature", "temperature", "feverish"],
        "causes": ["viral infection", "bacterial infection", "inflammation"],
        "severity": "mild"
    },
    "fatigue": {
        "aliases": ["tired", "weakness", "low energy", "exhausted"],
        "causes": ["poor sleep", "stress", "anemia", "thyroid imbalance"],
        "severity": "mild"
    },
    "headache": {
        "aliases": ["head pain", "migraine", "pressure in head"],
        "causes": ["stress", "migraine", "dehydration"],
        "severity": "mild"
    },
    "chest pain": {
        "aliases": ["chest discomfort", "pressure in chest", "tight chest"],
        "causes": ["heart-related issue", "muscle strain", "acid reflux"],
        "severity": "severe"
    },
    "breathing difficulty": {
        "aliases": ["shortness of breath", "difficulty breathing", "dyspnea"],
        "causes": ["asthma", "lung infection", "allergy"],
        "severity": "severe"
    }
}


# =========================================================
#  NORMALIZE TEXT
# =========================================================
def normalize(text: str):
    return text.lower().strip()


# =========================================================
#  SMART MATCH (FUZZY )
# =========================================================
def match_phrase(text, phrase):
    return phrase in text or any(word in text for word in phrase.split())


# =========================================================
#  DETECT SYMPTOMS (IMPROVED )
# =========================================================
def detect_symptoms(text: str):

    text = normalize(text)
    detected = []

    for symptom, data in SYMPTOMS_DB.items():

        # check main symptom
        if match_phrase(text, symptom):
            detected.append(symptom)
            continue

        # check aliases
        for alias in data["aliases"]:
            if match_phrase(text, alias):
                detected.append(symptom)
                break

    return list(set(detected))


# =========================================================
#  GET DETAILS (LIMITED + PRIORITIZED )
# =========================================================
def get_symptom_details(text: str):

    detected = detect_symptoms(text)
    results = []

    for s in detected:
        data = SYMPTOMS_DB[s]

        results.append({
            "symptom": s,
            "causes": data["causes"][:3],  #  limit
            "severity": data["severity"]
        })

    return results


# =========================================================
#  SEVERITY (SMART )
# =========================================================
def get_overall_severity(text: str):

    detected = detect_symptoms(text)

    if not detected:
        return "unknown"

    if any(SYMPTOMS_DB[s]["severity"] == "severe" for s in detected):
        return "severe"

    if len(detected) >= 2:
        return "moderate"

    return "mild"


# =========================================================
#  CONFIDENCE (IMPROVED )
# =========================================================
def get_confidence(text: str):

    detected = detect_symptoms(text)

    if not detected:
        return "low"

    if len(detected) >= 2:
        return "high"

    return "medium"


# =========================================================
#  OUTPUT (CLEAN )
# =========================================================
def check_symptoms(text: str):

    details = get_symptom_details(text)

    if not details:
        return ""

    output = []

    for item in details:
        causes = ", ".join(item["causes"])
        output.append(f"{item['symptom']} → {causes}")

    return "\n".join(output)





