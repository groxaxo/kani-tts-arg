#!/usr/bin/env python3
"""
KaniTTS Argentinian Spanish TTS Server
FastAPI server with OpenAI-compatible endpoints using checkpoint-7500

Usage:
    python server.py                  # Run on default port 8002
    python server.py --port 8080      # Run on custom port
    python server.py --gpu 1          # Use specific GPU
"""

import os
import io
import argparse
import torch
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from scipy.io.wavfile import write as wav_write

from inference import KaniModel, NemoAudioPlayer

# Configuration - can be overridden via environment variables
BASE_MODEL = os.environ.get("KANI_BASE_MODEL", "nineninesix/kani-tts-400m-es")
CHECKPOINT_PATH = os.environ.get("KANI_CHECKPOINT", "checkpoints/checkpoint-7500")
DEFAULT_SPEAKER = os.environ.get("KANI_SPEAKER", "ar4766")

app = FastAPI(
    title="KaniTTS Argentinian Spanish TTS API",
    description="Text-to-Speech API using KaniTTS finetuned on Argentinian Spanish",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instances
model = None
player = None


class SpeechRequest(BaseModel):
    """OpenAI-compatible speech request"""

    model: str = Field(default="tts-1", description="Model name (OpenAI compatible)")
    input: str = Field(..., description="Text to convert to speech (Spanish)")
    voice: str = Field(
        default="ar4766", description="Speaker ID (ar4766 for Argentinian)"
    )
    response_format: str = Field(default="wav", description="Audio format: wav or pcm")
    temperature: float = Field(
        default=0.7, ge=0.1, le=1.5, description="Generation temperature"
    )
    top_p: float = Field(default=0.9, ge=0.1, le=1.0, description="Top-p sampling")
    repetition_penalty: float = Field(
        default=1.2, ge=1.0, le=2.0, description="Repetition penalty"
    )
    max_new_tokens: int = Field(
        default=2000, ge=100, le=4000, description="Max new tokens"
    )

    class Config:
        extra = "ignore"


class GenerateRequest(BaseModel):
    """Simple generation request"""

    text: str = Field(..., description="Text to convert to speech")
    speaker_id: str = Field(default="ar4766", description="Speaker ID")
    temperature: float = Field(default=0.7)
    top_p: float = Field(default=0.9)
    repetition_penalty: float = Field(default=1.2)


@app.on_event("startup")
async def startup_event():
    global model, player
    print("=" * 60)
    print("🇦🇷 KaniTTS Argentinian Spanish TTS Server")
    print("=" * 60)
    print(f"  Base model: {BASE_MODEL}")
    print(f"  Checkpoint: {CHECKPOINT_PATH}")
    print(f"  Speaker: {DEFAULT_SPEAKER}")
    print("-" * 60)

    player = NemoAudioPlayer(text_tokenizer_name=BASE_MODEL)
    model = KaniModel(model_name=CHECKPOINT_PATH, player=player, base_model=BASE_MODEL)

    print("✅ Server ready!")
    print("=" * 60)


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "KaniTTS Argentinian Spanish TTS API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "models": "/v1/models",
            "speech": "POST /v1/audio/speech",
            "generate": "POST /generate",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "checkpoint": CHECKPOINT_PATH,
        "base_model": BASE_MODEL,
        "default_speaker": DEFAULT_SPEAKER,
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0)
        if torch.cuda.is_available()
        else None,
    }


@app.get("/v1/models")
async def list_models():
    """OpenAI-compatible models endpoint"""
    return {
        "object": "list",
        "data": [
            {
                "id": "tts-1",
                "object": "model",
                "created": 1736380800,
                "owned_by": "kani-tts-argentinian",
            }
        ],
    }


@app.post("/v1/audio/speech")
async def generate_speech(request: SpeechRequest):
    """OpenAI-compatible speech generation endpoint"""
    if not model or not player:
        raise HTTPException(status_code=503, detail="TTS not initialized")

    speaker = request.voice if request.voice else DEFAULT_SPEAKER

    try:
        input_ids, attention_mask = model.get_input_ids(request.input, speaker)

        with torch.no_grad():
            generated_ids = model.model.generate(
                input_ids=input_ids.to(model.device),
                attention_mask=attention_mask.to(model.device),
                eos_token_id=player.end_of_speech,
                do_sample=True,
                temperature=request.temperature,
                top_p=request.top_p,
                repetition_penalty=request.repetition_penalty,
                max_new_tokens=request.max_new_tokens,
            )

        audio, _ = player.get_waveform(generated_ids.to("cpu"))

        if request.response_format == "pcm":
            pcm_data = (audio * 32767).astype(np.int16)
            return Response(
                content=pcm_data.tobytes(),
                media_type="application/octet-stream",
                headers={
                    "Content-Type": "application/octet-stream",
                    "X-Sample-Rate": "22050",
                    "X-Channels": "1",
                    "X-Bit-Depth": "16",
                },
            )
        else:
            wav_buffer = io.BytesIO()
            wav_write(wav_buffer, 22050, audio)
            wav_buffer.seek(0)
            return Response(content=wav_buffer.read(), media_type="audio/wav")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
async def simple_generate(request: GenerateRequest):
    """Simple generation endpoint returning wav audio"""
    if not model or not player:
        raise HTTPException(status_code=503, detail="TTS not initialized")

    try:
        input_ids, attention_mask = model.get_input_ids(
            request.text, request.speaker_id
        )

        with torch.no_grad():
            generated_ids = model.model.generate(
                input_ids=input_ids.to(model.device),
                attention_mask=attention_mask.to(model.device),
                eos_token_id=player.end_of_speech,
                do_sample=True,
                temperature=request.temperature,
                top_p=request.top_p,
                repetition_penalty=request.repetition_penalty,
                max_new_tokens=2000,
            )

        audio, _ = player.get_waveform(generated_ids.to("cpu"))

        wav_buffer = io.BytesIO()
        wav_write(wav_buffer, 22050, audio)
        wav_buffer.seek(0)
        return Response(content=wav_buffer.read(), media_type="audio/wav")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def main():
    import uvicorn

    parser = argparse.ArgumentParser(description="KaniTTS Server")
    parser.add_argument("--port", type=int, default=8002, help="Port to run on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--gpu", type=int, default=0, help="GPU device ID")
    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)

    print(f"🚀 Starting server on {args.host}:{args.port} (GPU {args.gpu})")
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
