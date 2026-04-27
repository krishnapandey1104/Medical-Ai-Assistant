#!/bin/bash

echo "🚀 Setting up Medical AI Assistant..."

# ----------------------------
# Create Virtual Environment
# ----------------------------
python3 -m venv venv
source venv/bin/activate

# ----------------------------
# Install Python Dependencies
# ----------------------------
pip install --upgrade pip
pip install -r requirements.txt

# ----------------------------
# Install Tesseract (Linux only)
# ----------------------------
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt update
    sudo apt install -y tesseract-ocr poppler-utils
fi

# ----------------------------
# Install Ollama
# ----------------------------
curl -fsSL https://ollama.com/install.sh | sh

# ----------------------------
# Pull Models
# ----------------------------
ollama pull phi3
ollama pull llama3

echo "✅ Setup complete!"
echo "Run: streamlit run app.py"