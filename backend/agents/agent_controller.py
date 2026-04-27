from backend.core.report_parser import parse_report
from backend.core.llm_model import generate_response
from backend.core.hybrid_retriever import hybrid_retrieve

from backend.tools.safety_guard import (
    allow_medicine,
    safety_message,
    is_medicine_query
)
from backend.tools.symptom_checker import get_overall_severity
from backend.tools.diagnostic_reasoner import reason
from backend.tools.drug_database import get_medicine


# =========================================================
# MEMORY SUMMARY (SAFE)
# =========================================================
def summarize_messages(messages):

    if not messages or len(messages) < 8:
        return "", messages

    old = messages[:-4]
    recent = messages[-4:]

    text = "\n".join([
        f"{m.get('role')}: {m.get('content')}"
        for m in old
    ])

    try:
        summary = generate_response(
            user_input=f"Summarize briefly:\n{text}",
            mode="chat",
            messages=None
        )
        return summary if summary else "", recent

    except:
        return "", recent


# =========================================================
# CONTEXT BUILDER (FIXED )
# =========================================================
def build_context(question, parsed, hybrid, reasoning, messages, summary, structured_data=None):

    parts = []

    # PRIORITY: STRUCTURED DATA (MAIN FIX)
    if structured_data:
        parts.append(f"Lab Results:\n{structured_data[:5]}")

        # CORRECT abnormal detection
        abnormal = [x for x in structured_data if x.get("status") in ["HIGH", "LOW"]]
        if abnormal:
            parts.append(f"Abnormal Findings:\n{abnormal[:3]}")

    #  REMOVE noisy parsed abnormal values (IMPORTANT FIX)
    # (Do NOT use parsed["abnormal_values"] anymore)

    # OPTIONAL: keep structured_data from parser if needed
    if parsed and parsed.get("structured_data"):
        structured = parsed["structured_data"][:5]
        parts.append(f"Report Values:\n{structured}")

    if hybrid:
        parts.append(f"Medical Knowledge:\n{hybrid[:400]}")

    if reasoning:
        parts.append(reasoning)

    if summary:
        parts.append(f"Summary:\n{summary[:200]}")

    if messages:
        recent = "\n".join([
            f"{m.get('role')}: {m.get('content')}"
            for m in messages[-2:]
        ])
        parts.append(f"Recent:\n{recent}")

    return "\n\n".join(parts)


# =========================================================
#  MAIN CONTROLLER (UPDATED MINIMALLY )
# =========================================================
def agent_controller(
    question,
    report_text,
    user_id,
    messages,
    user_level=None,
    manual_mode="Auto",
    structured_data=None   #  NEW PARAM
):

    try:
        print("\n🧠 AGENT START")

        if not question or not question.strip():
            question = "Analyze medical report"

        # =====================================================
        # SAFETY
        # =====================================================
        decision = allow_medicine(question)

        # =====================================================
        #  PARSE REPORT
        # =====================================================
        try:
            parsed = parse_report(report_text) if report_text else {}
        except:
            parsed = {}

        # =====================================================
        # MEMORY
        # =====================================================
        summary, messages = summarize_messages(messages)

        # =====================================================
        # RETRIEVAL
        # =====================================================
        try:
            hybrid = hybrid_retrieve(question)[:200]
        except:
            hybrid = ""

        # =====================================================
        #  REASONING
        # =====================================================
        reasoning = reason(question)[:150] if question else ""

        # =====================================================
        # SEVERITY
        # =====================================================
        severity = get_overall_severity(question)

        # =====================================================
        #  CONTEXT (FIXED)
        # =====================================================
        context_block = build_context(
            question,
            parsed,
            hybrid,
            reasoning,
            messages,
            summary,
            structured_data   #  PASS HERE
        )

        # =====================================================
        # 🤖 FINAL INPUT
        # =====================================================
        final_input = f"""
{context_block}

Question: {question}
"""

        mode = "report" if report_text else "chat"

        # =====================================================
        # LLM CALL
        # =====================================================
        response = generate_response(
            user_input=final_input,
            mode=mode,
            report_context=report_text[:2000],
            messages=messages
        )

        # =====================================================
        #  RETRY
        # =====================================================
        if not response or len(response.strip()) < 30:
            print("⚡ retry with simple prompt")

            response = generate_response(
                user_input=question,
                mode="chat",
                report_context="",
                messages=None
            )

        # =====================================================
        # MEDICINE
        # =====================================================
        if is_medicine_query(question):

            if decision["allowed"] and severity != "severe":
                meds = get_medicine(question)

                if meds:
                    response += f"""

Additional Guidance:
Common options: {", ".join(meds[:2])}.
Use only if appropriate.
"""

            else:
                warn = safety_message(decision)
                if warn:
                    response += "\n\n" + warn

        # =====================================================
        # EMERGENCY
        # =====================================================
        if severity == "severe" and "Emergency Warning" not in response:
            response = (
                "🚨 Emergency Warning:\n"
                "Seek immediate medical attention.\n\n"
                + response
            )

        # =====================================================
        # ❌ FINAL FAIL
        # =====================================================
        if not response or len(response.strip()) < 20:
            return "⚠️ Unable to generate response. Try again."

        print("✅ RESPONSE GENERATED")

        return response.strip()

    except Exception as e:
        print("❌ AGENT ERROR:", e)
        return "❌ Something went wrong"


