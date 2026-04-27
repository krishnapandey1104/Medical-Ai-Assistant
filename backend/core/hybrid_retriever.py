from backend.core.rag_pipeline import retrieve as rag_retrieve
from backend.core.web_search import search_medical_web


# =========================================================
#  INTENT DETECTION
# =========================================================
def detect_intent(query):

    q = query.lower()

    if any(k in q for k in ["report", "test", "value", "hb", "cholesterol", "sugar"]):
        return "report"

    if any(k in q for k in [
        "pain", "fever", "cough", "breathing",
        "fatigue", "tired", "symptom"
    ]):
        return "symptom"

    return "general"


# =========================================================
#  HYBRID RETRIEVE (OPTIMIZED)
# =========================================================
def hybrid_retrieve(query, report_context=""):

    print("\n HYBRID RETRIEVE:", query)

    intent = detect_intent(query)

    # ----------------------------
    # STEP 1: RAG
    # ----------------------------
    rag_context = rag_retrieve(query, report_context)

    #  LIMIT RAG SIZE (CRITICAL FIX)
    if rag_context:
        rag_context = rag_context[:400]

    # ----------------------------
    # STEP 2: DECIDE WEB
    # ----------------------------
    use_web = should_use_web(query, rag_context, intent)

    web_context = ""
    if use_web:
        web_context = search_medical_web(query)

        #  LIMIT WEB SIZE
        if web_context:
            web_context = web_context[:250]

    # ----------------------------
    # STEP 3: FUSION
    # ----------------------------
    final_context = fuse_context(rag_context, web_context, intent)

    return final_context


# =========================================================
#  WEB DECISION LOGIC (SMARTER)
# =========================================================
def should_use_web(query, rag_context, intent):

    q = query.lower()

    #  report → never web
    if intent == "report":
        return False

    #  strong rag → skip web
    if rag_context and len(rag_context) > 150:
        return False

    #  research queries
    if any(k in q for k in [
        "latest", "research", "study",
        "new treatment", "recent"
    ]):
        return True

    # no rag → use web
    if not rag_context:
        return True

    return False


# =========================================================
#  SMART FUSION (CLEAN + SHORT )
# =========================================================
def fuse_context(rag, web, intent):

    # ----------------------------
    # REPORT → ONLY RAG
    # ----------------------------
    if intent == "report":
        return rag or ""

    # ----------------------------
    # STRONG RAG → USE ONLY RAG
    # ----------------------------
    if rag and len(rag) > 150:
        return rag

    # ----------------------------
    # COMBINE (SHORT FORMAT)
    # ----------------------------
    parts = []

    if rag:
        parts.append(f"Medical info: {rag}")

    if web:
        parts.append(f"Extra context: {web}")

    final = " ".join(parts)

    #  FINAL HARD LIMIT (MOST IMPORTANT)
    return final[:500]