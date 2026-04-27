from backend.core.llm_model import generate_response
from backend.core.rag_pipeline import retrieve
from backend.core.web_search import search_medical_web

from backend.tools.diagnostic_reasoner import reason
from backend.tools.symptom_checker import get_overall_severity
from backend.tools.safety_guard import allow_medicine, safety_message
from backend.tools.drug_database import get_medicine

from backend.config import ENABLE_WEB_SEARCH


# =========================================================
#  SAFE HISTORY (LIMITED)
# =========================================================
def format_history(messages):
    if not messages:
        return ""

    return "\n".join([
        f"{m.get('role')}: {m.get('content')}"
        for m in messages[-2:]  # 🔥 only last 2
    ])


# =========================================================
# EMERGENCY DETECTION
# =========================================================
def detect_emergency(text):
    flags = [
        "chest pain",
        "difficulty breathing",
        "unconscious",
        "severe bleeding",
        "stroke",
        "heart attack"
    ]
    return any(f in text.lower() for f in flags)


# =========================================================
#  MAIN AGENT (FINAL)
# =========================================================
# =========================================================
#  REACT AGENT (OPTIMIZED )
# =========================================================
def react_agent(
    question,
    report_text,
    parsed,
    user_id,
    messages,
    summary,
    mode,
    user_level
):

    print("\n🤖 REACT AGENT START")

    if not question or not question.strip():
        question = "Analyze this medical report"

    # =====================================================
    #  SAFETY
    # =====================================================
    decision = allow_medicine(question)

    # =====================================================
    #  SEVERITY
    # =====================================================
    severity = get_overall_severity(question)

    # =====================================================
    # LIGHT CONTEXT (CRITICAL FIX )
    # =====================================================
    context_parts = []

    #  ONLY MOST IMPORTANT DATA

    # 1️⃣ REPORT (LIMITED)
    if report_text:
        context_parts.append(f"Report: {report_text[:300]}")

    # 2️⃣ ABNORMAL VALUES ONLY
    if parsed and parsed.get("abnormal_values"):
        context_parts.append(f"Abnormal: {parsed['abnormal_values'][:3]}")

    # 3️⃣ RAG (SHORT)
    try:
        rag = retrieve(question)
        if rag:
            context_parts.append(f"Knowledge: {rag[:200]}")
    except:
        rag = ""

    # 4️⃣ WEB ONLY IF NEEDED
    if ENABLE_WEB_SEARCH and not rag:
        try:
            web = search_medical_web(question)
            if web:
                context_parts.append(f"Info: {web[:150]}")
        except:
            pass

    # 5️⃣ SHORT REASONING
    try:
        reasoning = reason(question)
        if reasoning:
            context_parts.append(reasoning[:120])
    except:
        pass

    context_block = "\n".join(context_parts)

    # =====================================================
    # FINAL INPUT (SHORT = FAST )
    # =====================================================
    final_input = f"""
{context_block}

Question: {question}
"""

    # =====================================================
    #  LLM CALL
    # =====================================================
    try:
        response = generate_response(
            user_input=final_input,
            mode="report" if report_text else "chat",
            report_context=report_text[:500],
            messages=None
        )

    except Exception as e:
        print("❌ LLM ERROR:", e)
        response = ""

    # =====================================================
    # 🔁 RETRY (VERY IMPORTANT )
    # =====================================================
    if not response or len(response.strip()) < 30:
        print("⚡ retry simple prompt")

        response = generate_response(
            user_input=question,
            mode="chat",
            report_context="",
            messages=None
        )

    if not response:
        return "⚠️ Unable to generate response. Please try again."

    # =====================================================
    # MEDICINE (ONLY IF USER ASKS )
    # =====================================================
    from backend.tools.safety_guard import is_medicine_query

    if is_medicine_query(question):

        if decision["allowed"] and severity != "severe":
            meds = get_medicine(question)

            if meds:
                response += f"""

Additional Guidance:
Common options: {", ".join(meds[:2])}
Use only if appropriate.
"""

        else:
            warn = safety_message(decision)
            if warn:
                response += "\n\n" + warn

    # =====================================================
    #  EMERGENCY
    # =====================================================
    if severity == "severe" and "Emergency Warning" not in response:
        response = (
            "🚨 Emergency Warning:\n"
            "Seek immediate medical attention.\n\n"
            + response
        )

    print("✅ RESPONSE READY")

    return response.strip()


