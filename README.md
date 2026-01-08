# KaniTTS Argentinian Spanish TTS

A finetuned Text-to-Speech model for Argentinian Spanish, packaged as a FastAPI server with OpenAI-compatible endpoints.

## Features

- 🇦🇷 **Argentinian Spanish** - Finetuned on native Argentinian speaker data
- 🎯 **Multiple Checkpoints** - Includes steps 7500, 11000, and 16480
- 🔌 **OpenAI Compatible** - Drop-in replacement for OpenAI TTS API
- ⚡ **Fast Inference** - GPU-accelerated generation
- 🐍 **Easy Setup** - Single conda environment setup

## Available Checkpoints

**Recommended Checkpoints:**
- **`checkpoint-7500`** - Balanced quality, good starting point
- **`checkpoint-11500`** - Enhanced training, refined output  
- **`checkpoint-16480`** - Final checkpoint, most trained (currently deployed)

<details>
<summary>All 33 Checkpoints (click to expand)</summary>

| Checkpoint | Training Steps | Notes |
|------------|----------------|-------|
| `checkpoint-500` | 500 | Early training |
| `checkpoint-1000` | 1000 | Early training |
| `checkpoint-1500` | 1500 | Early training |
| `checkpoint-2000` | 2000 | Early training |
| `checkpoint-2500` | 2500 | Early training |
| `checkpoint-3000` | 3000 | Early training |
| `checkpoint-3500` | 3500 | Early training |
| `checkpoint-4000` | 4000 | Mid training |
| `checkpoint-4500` | 4500 | Mid training |
| `checkpoint-5000` | 5000 | Mid training |
| `checkpoint-5500` | 5500 | Mid training |
| `checkpoint-6000` | 6000 | Mid training |
| `checkpoint-6500` | 6500 | Mid training |
| `checkpoint-7000` | 7000 | Mid training |
| `checkpoint-7500` | 7500 | **Recommended** |
| `checkpoint-8000` | 8000 | Refined |
| `checkpoint-8500` | 8500 | Refined |
| `checkpoint-9000` | 9000 | Refined |
| `checkpoint-9500` | 9500 | Refined |
| `checkpoint-10000` | 10000 | Refined |
| `checkpoint-10500` | 10500 | Refined |
| `checkpoint-11000` | 11000 | Enhanced |
| `checkpoint-11500` | 11500 | **Recommended** |
| `checkpoint-12000` | 12000 | Enhanced |
| `checkpoint-12500` | 12500 | Enhanced |
| `checkpoint-13000` | 13000 | More training |
| `checkpoint-13500` | 13500 | More training |
| `checkpoint-14000` | 14000 | More training |
| `checkpoint-14500` | 14500 | Advanced |
| `checkpoint-15000` | 15000 | Advanced |
| `checkpoint-15500` | 15500 | Advanced |
| `checkpoint-16000` | 16000 | Advanced |
| `checkpoint-16480` | 16480 | **Final - Recommended** |

</details>


## Quick Start

### 1. Setup Environment

```bash
# Run the setup script
chmod +x setup.sh
./setup.sh

# Or create manually:
conda create -n kanitts-arg python=3.10 -y
conda activate kanitts-arg
pip install -r requirements.txt
```

### 2. Start the Server

```bash
# Activate environment
conda activate kanitts-arg

# Start server (foreground)
python server.py

# Or use the run script (background with nohup)
chmod +x run.sh
./run.sh
```

### 3. Test the API

```bash
# Health check
curl http://localhost:8002/health

# Generate speech
curl -X POST http://localhost:8002/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input": "Hola, ¿cómo estás? Soy un modelo de síntesis de voz argentino."}' \
  --output test.wav
```

## API Endpoints

### Health Check
```
GET /health
```

### List Models (OpenAI compatible)
```
GET /v1/models
```

### Generate Speech (OpenAI compatible)
```
POST /v1/audio/speech
Content-Type: application/json

{
  "input": "Text to convert to speech",
  "voice": "ar4766",          // Speaker ID (optional)
  "response_format": "wav",   // wav or pcm
  "temperature": 0.7,         // 0.1-1.5
  "top_p": 0.9,              // 0.1-1.0
  "repetition_penalty": 1.2   // 1.0-2.0
}
```

### Simple Generate
```
POST /generate
Content-Type: application/json

{
  "text": "Text to convert",
  "speaker_id": "ar4766",
  "temperature": 0.7
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KANI_BASE_MODEL` | `nineninesix/kani-tts-400m-es` | Base model from HuggingFace |
| `KANI_CHECKPOINT` | `checkpoints/checkpoint-7500` | LoRA checkpoint path |
| `KANI_SPEAKER` | `ar4766` | Default speaker ID |

### Switching Checkpoints

```bash
# Use checkpoint 7500 (default)
python server.py

# Use checkpoint 11000
export KANI_CHECKPOINT=checkpoints/checkpoint-11000
python server.py

# Use checkpoint 16480 (final)
export KANI_CHECKPOINT=checkpoints/checkpoint-16480
python server.py
```

### Command Line Arguments

```bash
python server.py --port 8080 --host 0.0.0.0 --gpu 1
```

| Argument | Default | Description |
|----------|---------|-------------|
| `--port` | 8002 | Server port |
| `--host` | 0.0.0.0 | Host to bind |
| `--gpu` | 0 | GPU device ID |

## Project Structure

```
kani-tts-arg/
├── server.py           # FastAPI server
├── inference.py        # Model loading and inference
├── config_loader.py    # Configuration management
├── requirements.txt    # Python dependencies
├── setup.sh           # Environment setup script
├── run.sh             # Quick start script
├── config/            # Configuration files
│   ├── model_config.yaml
│   └── inference_config.yaml
└── checkpoints/       # Model checkpoints
    ├── checkpoint-7500/   # Default (21MB)
    ├── checkpoint-11000/  # Mid training (21MB)
    └── checkpoint-16480/  # Final (21MB)
```

## Technical Details

- **Base Model**: `nineninesix/kani-tts-400m-es` (400M parameters)
- **Finetuning**: LoRA adapters trained on Argentinian Spanish speakers
- **Checkpoint**: 7500 training steps
- **Audio Codec**: NVIDIA NeMo Nano Codec (22kHz, 0.6kbps)
- **Sample Rate**: 22050 Hz
- **Speaker ID**: `ar4766` (Argentinian female)

## Python Usage

```python
import requests

# Generate speech
response = requests.post(
    "http://localhost:8002/v1/audio/speech",
    json={
        "input": "¿Querés que te cuente un cuento?",
        "voice": "ar4766",
        "temperature": 0.7,
    }
)

with open("output.wav", "wb") as f:
    f.write(response.content)
```

## Troubleshooting

### CUDA not available
Make sure you have CUDA-compatible PyTorch installed:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### Model loading slow
First run downloads the base model from HuggingFace. Subsequent runs use cached model.

### Out of memory
Reduce `max_new_tokens` or use a GPU with more VRAM (minimum 4GB recommended).

## License

MIT License - See LICENSE file for details.
