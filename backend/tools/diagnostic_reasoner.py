from backend.tools.symptom_checker import (
    detect_symptoms,
    get_symptom_details,
    get_overall_severity,
    get_confidence
)


# =========================================================
#  INTENT DETECTION
# =========================================================
def detect_intent(question: str):

    q = question.lower()

    if any(k in q for k in ["report", "test", "value"]):
        return "report"

    if any(k in q for k in ["pain", "fever", "cough", "breathing", "symptom"]):
        return "symptom"

    return "general"


# =========================================================
#  MAIN REASONING ENGINE (UPGRADED )
# =========================================================
# =========================================================
# MAIN REASONING ENGINE (DOCTOR STYLE )
# =========================================================
def reason(question):

    try:
        intent = detect_intent(question)

        #  skip general queries
        if intent == "general":
            return ""

        symptoms = detect_symptoms(question)

        if not symptoms:
            return ""

        details = get_symptom_details(question)
        severity = get_overall_severity(question)
        confidence = get_confidence(question)

        # ----------------------------
        #  PICK TOP CAUSES (IMPORTANT )
        # ----------------------------
        causes = []

        for d in details:
            for c in d.get("causes", []):
                if c not in causes:
                    causes.append(c)

        #  limit causes (doctor style)
        causes = causes[:3]

        # ----------------------------
        #  BUILD NATURAL REASONING
        # ----------------------------
        symptom_text = ", ".join(symptoms)

        reasoning = f"""
Possible clinical reasoning:

The symptoms ({symptom_text}) may be linked to a few likely conditions such as {", ".join(causes)}.

This pattern usually suggests how the body is responding to factors like infection, inflammation, or fatigue-related imbalance.

Severity appears to be {severity}, with a confidence level of {confidence}.
"""

        # ----------------------------
        #  SEVERE CASE
        # ----------------------------
        if severity == "severe":
            reasoning += """
This combination of symptoms could indicate a more serious condition and should not be ignored.
"""

        return reasoning.strip()

    except Exception as e:
        print("❌ REASONING ERROR:", e)
        return ""