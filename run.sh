#!/bin/bash
# Quick start script - runs the server with nohup

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GPU="${1:-0}"
PORT="${2:-8002}"
LOG_FILE="server.log"

echo "🚀 Starting KaniTTS server..."
echo "   GPU: $GPU"
echo "   Port: $PORT"
echo "   Log: $LOG_FILE"

export CUDA_VISIBLE_DEVICES=$GPU
nohup python server.py --port $PORT --gpu $GPU > "$LOG_FILE" 2>&1 &
PID=$!

echo "   PID: $PID"
echo ""
echo "✅ Server starting in background"
echo "   Check status: tail -f $LOG_FILE"
echo "   Test health:  curl http://localhost:$PORT/health"
