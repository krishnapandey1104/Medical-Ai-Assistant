from backend.tools.symptom_checker import check_symptoms
from backend.tools.drug_database import lookup_drug
from backend.tools.diagnostic_reasoner import reason


# =========================================================
# SMART RULE ROUTER (UPGRADED )
# =========================================================
def rule_based_router(question: str):

    q = question.lower()

    # PRIORITY ORDER (IMPORTANT)

    # DRUG (highest priority)
    if any(k in q for k in ["medicine", "tablet", "drug", "dose", "dosage"]):
        return ["drug_database"]

    #  MIXED (symptom + why)
    if any(k in q for k in ["why", "cause", "reason"]) and \
       any(k in q for k in ["pain", "fever", "cough", "fatigue", "breathing"]):
        return ["diagnostic_reasoner", "symptom_checker"]

    #  SYMPTOM
    if any(k in q for k in ["pain", "fever", "cough", "fatigue", "symptom"]):
        return ["symptom_checker"]

    #  REASONING
    if any(k in q for k in ["why", "cause", "explain", "reason"]):
        return ["diagnostic_reasoner"]

    return []


# =========================================================
# 🛠 TOOL AGENT (FINAL OPTIMIZED )
# =========================================================
def tool_calling_agent(question: str):

    print("\n🛠 TOOL AGENT START")

    if not question or not question.strip():
        return ""

    # =====================================================
    #  SELECT TOOLS
    # =====================================================
    tools = rule_based_router(question)

    print("Selected Tools:", tools)

    if not tools:
        return ""

    responses = []

    # ====================================================
    #  EXECUTE MULTIPLE TOOLS (SMART )
    # =====================================================
    for tool in tools:
        try:
            if tool == "symptom_checker":
                res = check_symptoms(question)

            elif tool == "drug_database":
                res = lookup_drug(question)

            elif tool == "diagnostic_reasoner":
                res = reason(question)

            else:
                continue

            if res:
                responses.append(res)

        except Exception as e:
            print(f"❌ TOOL ERROR ({tool}):", e)

    # =====================================================
    #  MERGE RESPONSES (CLEAN )
    # =====================================================
    if responses:
        return "\n\n".join(responses)

    return ""


