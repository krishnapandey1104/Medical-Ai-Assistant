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
        You are an advanced AI Medical Assistant.

        Analyze ANY type of medical report (lab report, prescription, scan, etc.)

        STRICT FORMAT:

        🧾 Summary:
        (1–3 line summary)

        📊 Key Findings:
        - Parameter / Observation: Value
        - Include all important values dynamically

        📈 Interpretation:
        (Simple explanation in plain language)

        ⚠️ Abnormalities / Concerns:
        (List abnormal findings, or "None identified")

        💊 Medications:
        (List medicines if present, otherwise "Not mentioned")

        💡 Recommendations:
        (General safe advice only)

        👉 Next Steps:
        (Doctor consultation or next actions)

        -------------------------------------

        Report Text:
        {text}

        Extracted Values:
        {table_summary}

        Abnormal Findings:
        {abnormal_text}

        Trends:
        {trend_text}

        IMPORTANT RULES:
        - Do NOT leave any section empty
        - If missing → "Not mentioned in report"
        - Do NOT hallucinate
        - Keep output clean and structured
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





