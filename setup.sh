#!/bin/bash
# KaniTTS Argentinian Spanish TTS - Setup Script
# Creates conda environment and installs dependencies

set -e

ENV_NAME="${1:-kanitts-arg}"

echo "=============================================="
echo "🇦🇷 KaniTTS Argentinian Spanish TTS Setup"
echo "=============================================="
echo ""

# Check for conda
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda or Anaconda first."
    echo "   https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Create environment if it doesn't exist
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "📦 Environment '$ENV_NAME' already exists"
    read -p "   Recreate it? (y/N): " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing environment..."
        conda env remove -n "$ENV_NAME" -y
    else
        echo "✅ Using existing environment"
        echo ""
        echo "To activate: conda activate $ENV_NAME"
        echo "To run server: python server.py"
        exit 0
    fi
fi

echo ""
echo "📦 Creating conda environment '$ENV_NAME' with Python 3.10..."
conda create -n "$ENV_NAME" python=3.10 -y

echo ""
echo "📥 Installing dependencies..."
conda run -n "$ENV_NAME" pip install -r requirements.txt

echo ""
echo "=============================================="
echo "✅ Setup complete!"
echo "=============================================="
echo ""
echo "To use:"
echo "  1. Activate environment:"
echo "     conda activate $ENV_NAME"
echo ""
echo "  2. Start the server:"
echo "     python server.py"
echo ""
echo "  3. Test the API:"
echo "     curl http://localhost:8002/health"
echo ""
echo "  4. Generate speech:"
echo "     curl -X POST http://localhost:8002/v1/audio/speech \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"input\": \"Hola, ¿cómo estás?\"}' \\"
echo "       --output test.wav"
echo ""
