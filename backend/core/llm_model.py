import requests
import os
from backend.config import MODELS, GEN_CONFIG

if os.getenv("DOCKER_ENV"):
    OLLAMA_URL = "http://ollama:11434"
else:
    OLLAMA_URL = "http://localhost:11434"

print(f"🔗 Ollama URL: {OLLAMA_URL}")


# =========================================================
#  MODEL SELECTION (LLAMA FIRST )
# =========================================================
def choose_model(prompt: str, report_context: str):

    if report_context and len(report_context) > 50:
        return MODELS.get("report", "llama3:latest")

    return MODELS.get("qa", "llama3:latest")


# =========================================================
#  EMERGENCY DETECTION
# =========================================================
def detect_emergency(text):
    red_flags = [
        "chest pain",
        "difficulty breathing",
        "heart attack",
        "stroke",
        "unconscious",
        "severe bleeding"
    ]
    return any(flag in text.lower() for flag in red_flags)


# =========================================================
#  OLLAMA CALL (OPTIMIZED )
# =========================================================
def call_ollama(model, prompt, timeout=300):
    try:

    #=======================
    # dynamic token
    #=======================
        if len(prompt)>2000: # report / long input
            num_predict = 1500
            num_ctx = 8192
        else: # normal chat
            num_predict = 500
            num_ctx = 2048
        #===============
        # call
        #==============

        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful and safe medical assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False,
                "options": {
                    "temperature": GEN_CONFIG["temperature"],
                    "num_predict": num_predict,             #400,
                    "num_ctx": num_ctx       #2048
                }
            },
            timeout=timeout
        )

        if response.status_code != 200:
            print(f"❌ HTTP ERROR: {response.status_code}", response.text)
            return ""

        data = response.json()

        return data.get("message", {}).get("content", "").strip()

    except Exception as e:
        print(f"❌ {model} ERROR:", e)
        return ""


# =========================================================
#  MEMORY (LIGHT)
# =========================================================
def build_memory_context(messages, query):

    if not messages:
        return ""

    return "\n".join([
        f"{m.get('role')}: {m.get('content')}"
        for m in messages[-2:]
    ])


# =========================================================
#  INTENT DETECTION
# =========================================================
def detect_intent(query):

    q = query.lower()

    if any(k in q for k in [
        "pain", "fever", "cough", "fatigue",
        "tired", "weak", "dizziness",
        "breathing"
    ]):
        return "symptom"

    if any(k in q for k in [
        "report", "test", "value", "hb",
        "cholesterol", "sugar"
    ]):
        return "report"

    return "general"


# =========================================================
#  PROMPT BUILDER (ANTI-HALLUCINATION )
# =========================================================
def build_prompt(memory, query, mode, report_context):

    intent = detect_intent(query)

    base = f"""
You are a careful and practical medical assistant.

{memory}

SAFETY RULES:
- Use ONLY the given information (query + report + context)
- Do NOT invent medical facts
- If unsure → say "information is limited"
- Focus on COMMON causes first
- Avoid rare or dangerous conditions unless strong warning signs exist
- Do NOT scare the user

NO MARKDOWN:
- Do NOT use **, *, ##, or any markdown formatting
- Use plain text only

STYLE:
- Simple
- Human-like
- Clear reasoning
- Practical advice
"""

    # ================= REPORT =================
    if report_context:
        return base + f"""

TASK:
1. Explain report in simple terms
2. Highlight abnormal values (only if present)
3. Explain what it may indicate
4. If unclear → say "information is limited"

FORMAT:

Summary:
Key Findings:
What it may indicate:
Next steps:

User Question:
{query}

Report:
{report_context[:1000]}
"""

    # ================= SYMPTOM =================
    if intent == "symptom":
        return base + f"""

TASK:

1. Identify 2–3 MOST LIKELY causes (common first)
2. Explain briefly in simple words WHY 
3. Suggest practical steps
4. Ask 2–3 SMART follow-up questions

FORMAT:

Most likely causes:
- cause + simple reasoning

What you can do:
- practical steps

When to worry:
- only real warning signs

Follow-up questions:
- Q1
- Q2
- Q3

User Question:
{query}
"""

    # ================= GENERAL =================
    return base + f"""

TASK:
- Answer clearly
- If unsure → say "information is limited"
- Add 1–2 useful follow-up questions

FORMAT:

Answer:
Follow-up questions:

User Question:
{query}
"""


# =========================================================
#  CLEAN RESPONSE
# =========================================================
def clean_response(text):

    if not text:
        return ""

    remove = [
        "I'm sorry",
        "Based on your symptoms",
        "here are the most likely causes",
        "as a clinical assistant",
        "classic combo",
        "strong contender",
        "I would suspect",
        "rare but serious",
        "please let me know",
        "would you like"
        "**",   #  REMOVE MARKDOWN
        "*",    #  REMOVE MARKDOWN
        "##"
    ]

    for r in remove:
        text = text.replace(r, "")

    return text.strip()


# =========================================================
#  ANTI-HALLUCINATION GUARD
# =========================================================
def enforce_uncertainty(output):

    if not output or len(output.split()) < 20:
        return "Information is limited. Please provide more details."

    return output


# =========================================================
#  MAIN FUNCTION
# =========================================================
def generate_response(
    user_input: str,
    mode: str = "chat",
    report_context: str = "",
    messages=None
):

    try:
        # MEMORY
        memory = build_memory_context(messages, user_input)

        # PROMPT
        prompt = build_prompt(memory, user_input, mode, report_context)

        # MODEL
        model = choose_model(user_input, report_context)
        print(f"🧠 Using model: {model}")

        # TRY LLAMA (2 attempts)
        output = call_ollama(model, prompt)

        if not output:
            print("🔁 retry llama...")
            output = call_ollama(model, prompt)

        # FALLBACK
        if not output:
            print("⚡ fallback → phi3")
            output = call_ollama("phi3:latest", prompt)

        if not output:
            return "⚠️ Unable to generate response. Please try again."

        # CLEAN + VALIDATE
        output = clean_response(output)
        output = enforce_uncertainty(output)

        # EMERGENCY
        if detect_emergency(user_input):
            output = (
                "🚨 Emergency Warning:\n"
                "Seek immediate medical attention.\n\n"
                + output
            )

        return output.strip()

    except Exception as e:
        print("❌ ERROR:", e)
        return "⚠️ AI system error. Please try again."

