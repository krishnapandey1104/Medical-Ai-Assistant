from backend.core.llm_model import generate_response
from backend.core.image_ocr import extract_text


# =========================================================
#  REPORT ANALYSIS AGENT (FINAL UPGRADED )
# =========================================================
async def analyze_report_agent(file):

    print("\n📄 REPORT AGENT START")

    try:
        # =====================================================
        #  EXTRACT TEXT + TABLES
        # =====================================================
        data = await extract_text(file)

        text = data.get("text", "")
        tables = data.get("tables", [])
        formatted = data.get("formatted", "")
        trends = data.get("trends", {})

        # =====================================================
        # VALIDATION
        # =====================================================
        if not text or len(text.strip()) < 30:
            return "⚠️ Unable to extract readable content from the report."

        # limit size for LLM stability
        text = text[:1200]

        # =====================================================
        # STRUCTURED VALUES
        # =====================================================
        if tables:
            table_summary = "\n".join([
                f"{t['test']} = {t['value']} ({t['status']})"
                for t in tables[:10]
            ])
        else:
            table_summary = "No structured lab values detected"

        # =====================================================
        # ABNORMAL VALUES
        # =====================================================
        abnormal = [
            f"{t['test']} is {t['status']} ({t['value']})"
            for t in tables
            if t["status"] in ["HIGH", "LOW"]
        ]

        abnormal_text = "\n".join(abnormal[:5]) if abnormal else "No major abnormalities detected"

        # =====================================================
        #  TRENDS (OPTIONAL)
        # =====================================================
        trend_text = ""
        if trends:
            trend_text = "\n".join([
                f"{k}: {v}"
                for k, v in list(trends.items())[:5]
            ])

        # =====================================================
        # UNIVERSAL STRUCTURED PROMPT (FINAL)
        # =====================================================
        prompt = f"""
You are a highly accurate AI Medical Assistant.

Your task is to analyze ANY medical report (blood test, prescription, scan, discharge summary, etc.)
and explain EVERYTHING in simple, easy-to-understand language.

-------------------------------------

STRICT OUTPUT FORMAT (VERY IMPORTANT):

🧾 Summary:
Explain what this report is about in 2-3 simple lines.

📊 Key Findings:
Write each finding on a NEW LINE:
- Test / Observation → Value (Status if available)

📈 Interpretation:
Explain what these findings mean in simple language.
Write in SHORT LINES (not long paragraphs).

⚠️ Abnormalities / Concerns:
- List only abnormal or important issues
- If none → write: None

💊 Medicines (ONLY IF PRESENT OR NEEDED):
- If medicines are written in report → list them
- If report suggests condition where medicine may be needed → suggest common medicines (safe, general only)
- If not applicable → write: Not required

💡 Recommendations:
Write practical advice in POINTS (each on new line):
- Diet / lifestyle / precautions

👉 Next Steps:
Write clear next actions:
- Doctor visit / tests / monitoring

-------------------------------------

Report Text:
{text}

Extracted Values:
{table_summary}

Abnormal Findings:
{abnormal_text}

Trends:
{trend_text}

-------------------------------------

IMPORTANT RULES:

- Each heading MUST be followed by content on NEW LINES (no big paragraphs)
- Keep language SIMPLE (like explaining to a non-medical person)
- DO NOT leave any section empty
- If data missing → write "Not mentioned in report"
- DO NOT guess diseases
- DO NOT hallucinate values
- Medicines should be suggested ONLY when appropriate (not always)

-------------------------------------
"""
        # =====================================================
        #  LLM CALL
        # =====================================================
        response = generate_response(
            user_input=prompt,
            mode="report",
            report_context=text,
            messages=None
        )

        # =====================================================
        #  FAILURE HANDLING
        # =====================================================
        if not response or len(response.strip()) < 30:
            return "⚠️ Unable to generate report analysis."

        print("✅ REPORT ANALYSIS READY")

        return response.strip()

    except Exception as e:
        print("❌ REPORT AGENT ERROR:", e)
        return "⚠️ Report analysis failed. Please try again."





