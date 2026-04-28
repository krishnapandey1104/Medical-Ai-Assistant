# 🧠 AI Medical Assistant (RAG + OCR + LLM)

An intelligent medical assistant that analyzes reports (PDF/images), extracts key values using OCR, and generates structured insights using LLMs (Ollama) and Retrieval-Augmented Generation (RAG).

---

## 🚀 Features

- 📄 Upload medical reports (PDF, images)
- 🔍 OCR-based text extraction (Tesseract)
- 📊 Automatic lab value extraction (Hb, RBC, etc.)
- 🧠 AI-powered analysis using LLM (Llama3, Phi3 via Ollama)
- 📚 RAG-based medical knowledge retrieval
- 💬 Chat with memory (session-based)
- ⚠️ Abnormality detection & safe recommendations

---

## 🏗️ Architecture

User → Frontend → FastAPI Backend │ ├── OCR (Tesseract) ├── Parser (Lab extraction) ├── RAG (ChromaDB) └── LLM (Ollama)

---

## 🧰 Tech Stack

- **Backend:** FastAPI
- **LLM:** Ollama (Llama3, Phi3)
- **RAG:** ChromaDB + Sentence Transformers
- **OCR:** Tesseract + PyMuPDF
- **Database:** SQLite
- **Containerization:** Docker + Docker Compose

---

## 📁 Project Structure

MEDICAL_AI_ASSISTANT/
 ├── backend/  
 ├── frontend/  
 ├── tests/
 ├── docker/
        ├── Dockerfile
        │--docker-compose.yml
 ├── requirements.txt
 ├── requirements-dev.txt
├── .env

---

# Clone the Repository

```bash
git clone https://github.com/Suryansh2301/Medical-Ai-Assistant.git


# Environment Setup

Create a .env file in root:

QA_MODEL=llama3:latest
TOOL_MODEL=phi3:latest
REPORT_MODEL=llama3:latest

OLLAMA_BASE_URL=http://ollama:11434
TESSERACT_PATH=/usr/bin/tesseract 

# Start Containers
Bash
cd docker
docker-compose up -d --build
docker exec -it ollama ollama pull llama3
docker exec -it ollama ollama pull phi3
#check ollama
docker exec -it ollama ollama list

# check images and container
docker ps

# run
docker logs medical_ai_system


# Open App

http://localhost:8000/static/upload.html
