from backend.core.llm_model import generate_response

# SAFETY + TOOLS
from backend.tools.safety_guard import allow_medicine, safety_message, is_medicine_query
from backend.tools.drug_database import get_medicine
from backend.tools.symptom_checker import get_overall_severity
from backend.tools.diagnostic_reasoner import reason


# =========================================================
#  MEDICAL QA AGENT (OPTIMIZED )
# =========================================================
def medical_qa_agent(question: str, report_text: str, context: str):

    try:
        print("\n🧠 QA AGENT START")

        if not question or not question.strip():
            return "Please ask a valid medical question."

        # =====================================================
        # SAFETY
        # =====================================================
        decision = allow_medicine(question)

        # =====================================================
        #  REASONING (SHORT )
        # =====================================================
        reasoning = reason(question)
        reasoning = reasoning[:150] if reasoning else ""

        # =====================================================
        # ⚠️ SEVERITY
        # =====================================================
        severity = get_overall_severity(question)

        # =====================================================
        #  LIGHT CONTEXT (VERY IMPORTANT )
        # =====================================================
        context_parts = []

        if context:
            context_parts.append(f"Knowledge: {context[:200]}")

        if report_text:
            context_parts.append(f"Report: {report_text[:300]}")

        if reasoning:
            context_parts.append(f"Reasoning: {reasoning}")

        context_block = "\n".join(context_parts)

        # =====================================================
        #  FINAL INPUT (SHORT = FAST 🔥)
        # =====================================================
        final_input = f"""
{context_block}

Question: {question}
"""

        # =====================================================
        #  LLM CALL
        # =====================================================
        response = generate_response(
            user_input=final_input,
            mode="report" if report_text else "chat",
            report_context=report_text[:500] if report_text else "",
            messages=None
        )

        # =====================================================
        # 🔁 RETRY (SMART FIX )
        # =====================================================
        if not response or len(response.strip()) < 30:
            print("⚡ retry simple mode")

            response = generate_response(
                user_input=question,
                mode="chat",
                report_context="",
                messages=None
            )

        if not response:
            return "⚠️ Unable to generate response. Please try again."

        # =====================================================
        #  MEDICINE (ONLY IF USER ASKS )
        # =====================================================
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
        if severity == "severe":
            response = (
                "🚨 Emergency Warning:\n"
                "Seek immediate medical attention.\n\n"
                + response
            )

        # =====================================================
        # FINAL CHECK
        # =====================================================
        if len(response.strip()) < 20:
            return "⚠️ Unable to generate response. Try again."

        print("✅ QA RESPONSE READY")

        return response.strip()

    except Exception as e:
        print("❌ QA AGENT ERROR:", e)
        return "❌ Something went wrong while processing your request"



