from backend.core.llm_model import generate_response


# =========================================================
#  CLEAN WEB DATA
# =========================================================
def clean_web_data(text: str):

    if not text:
        return ""

    #  LIMIT SIZE (IMPORTANT)
    return text.strip()[:800]


# =========================================================
#  RESEARCH AGENT (OPTIMIZED )
# =========================================================
def research_agent(question: str, web_data: str):

    print("\n🔬 RESEARCH AGENT START")

    if not question or not question.strip():
        return "Please provide a valid medical question."

    web_data = clean_web_data(web_data)

    # ❌ no web → fallback
    if not web_data:
        return "⚠️ No reliable external medical information found."

    # =====================================================
    #  CLEAN CONTEXT (SEPARATE DATA )
    # =====================================================
    context = f"Medical Evidence:\n{web_data}"

    # =====================================================
    #  SHORT + STRONG PROMPT
    # =====================================================
    prompt = f"""
You are a medical research assistant.

{context}

Question: {question}

RULES:
- Use ONLY the provided evidence
- Do NOT assume missing facts
- If incomplete → say "limited evidence available"

TASK:
- Answer clearly
- Explain reasoning based on data
- Keep it concise and professional
"""

    # =====================================================
    #  LLM CALL
    # =====================================================
    try:
        response = generate_response(
            user_input=prompt,
            mode="chat"
        )

        # =====================================================
        #  RETRY (SMART FIX )
        # =====================================================
        if not response or len(response.strip()) < 30:
            print("⚡ retry simplified research")

            response = generate_response(
                user_input=f"Based on this data:\n{web_data}\n\nAnswer: {question}",
                mode="chat"
            )

        if not response:
            return "⚠️ Unable to generate research response."

        return response.strip()

    except Exception as e:
        print("❌ RESEARCH ERROR:", e)
        return "⚠️ Research agent failed. Please try again."



