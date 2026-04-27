import os
import re
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


# =========================================================
#  PATH
# =========================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_PATH = os.path.join(BASE_DIR, "medical_knowledge")


# =========================================================
#  LIGHT EMBEDDING MODEL (FAST )
# =========================================================
print("🔄 Loading embedding model...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  #  FAST


# =========================================================
#  VECTOR DB
# =========================================================
client = chromadb.Client(Settings(persist_directory="vector_db"))
collection = client.get_or_create_collection("medical")


# =========================================================
#  CLEAN
# =========================================================
def clean(text):
    return re.sub(r"\s+", " ", text).strip()


# =========================================================
#  INTENT
# =========================================================
def detect_intent(query):
    q = query.lower()

    if any(k in q for k in ["report", "test", "value", "cholesterol", "hb", "sugar"]):
        return "report"

    if any(k in q for k in ["pain", "fever", "symptom", "cough", "breathing"]):
        return "symptom"

    return "general"


# =========================================================
#  QUERY IMPROVE
# =========================================================
def improve_query(query):

    q = query.lower()

    expansions = {
        "sugar": "blood glucose diabetes",
        "bp": "blood pressure hypertension",
        "chest pain": "cardiac angina heart",
        "breathing": "respiratory lung oxygen",
        "fever": "infection inflammation",
    }

    for key, val in expansions.items():
        if key in q:
            q += " " + val

    return q


# =========================================================
#  CHUNKING
# =========================================================
def chunk_text(text, chunk_size=200, overlap=50):  # smaller chunks

    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])

        if len(chunk.strip()) > 50:
            chunks.append(chunk)

    return chunks


# =========================================================
#  LOAD KNOWLEDGE
# =========================================================
def load_knowledge():

    try:
        if collection.count() > 0:
            print("✅ RAG already loaded")
            return

        if not os.path.exists(KNOWLEDGE_PATH):
            print("❌ Knowledge folder missing")
            return

        docs, ids, embeds, metas = [], [], [], []
        i = 0

        for file in os.listdir(KNOWLEDGE_PATH):

            if not file.endswith(".txt"):
                continue

            path = os.path.join(KNOWLEDGE_PATH, file)

            try:
                with open(path, encoding="utf-8") as f:
                    text = f.read()
            except:
                continue

            chunks = chunk_text(text)

            for chunk in chunks:
                emb = embedding_model.encode(chunk).tolist()

                docs.append(chunk)
                ids.append(f"id_{i}")
                metas.append({"source": file})
                embeds.append(emb)
                i += 1

        if docs:
            collection.add(
                documents=docs,
                ids=ids,
                embeddings=embeds,
                metadatas=metas
            )
            print(f"✅ Loaded {len(docs)} chunks")

    except Exception as e:
        print("❌ LOAD ERROR:", e)


# =========================================================
#  RETRIEVE (OPTIMIZED )
# =========================================================
def retrieve(query, report_context=""):

    if not query:
        return ""

    try:
        print("\n🔍 RAG QUERY:", query)

        intent = detect_intent(query)

        # skip simple queries
        if intent == "general" and len(query.split()) < 4:
            return ""

        improved_query = improve_query(query)

        emb = embedding_model.encode(improved_query).tolist()

        results = collection.query(
            query_embeddings=[emb],
            n_results=5   # reduced
        )

        docs = results.get("documents", [[]])[0]

        if not docs:
            return ""

        # -------------------------
        # LIGHT FILTER
        # -------------------------
        final = []

        for doc in docs[:3]:  #  top 3 only

            if len(doc.strip()) < 50:
                continue

            final.append(clean(doc[:180]))

        if not final:
            return ""

        print("✅ RAG READY")

        return "\n\n".join(final)

    except Exception as e:
        print("❌ RAG ERROR:", e)
        return ""




