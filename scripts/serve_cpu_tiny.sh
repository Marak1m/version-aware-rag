#!/usr/bin/env bash
# Serve the cpu_tiny backend (configs/models.yaml) with llama.cpp on the CPU, for output-parsing
# checks only. Installs a prebuilt llama.cpp release under ~/.local/llama.cpp and lets llama-server
# fetch the pinned GGUF into ~/.cache/llama.cpp. Nothing is written inside the repository.
#
#   bash scripts/serve_cpu_tiny.sh          # start (idempotent)
#   bash scripts/serve_cpu_tiny.sh stop
set -uo pipefail
DEST="$HOME/.local/llama.cpp"
TAG="b11723"                                   # the release recorded in configs/models.yaml
HF="Qwen/Qwen2.5-Coder-0.5B-Instruct-GGUF:Q8_0" # revision ebb2015119c907b064c512bf053e945850b5875f
PORT=8080

if [ "${1:-}" = "stop" ]; then
  pkill -f "llama-server.*--port $PORT" && echo "stopped" || echo "not running"
  exit 0
fi
mkdir -p "$DEST"
SERVER=$(find "$DEST" -name llama-server -type f 2>/dev/null | head -1)
if [ -z "$SERVER" ]; then
  url="https://github.com/ggml-org/llama.cpp/releases/download/$TAG/llama-$TAG-bin-ubuntu-x64.tar.gz"
  echo "fetching $url"
  curl -sL "$url" -o /tmp/llama.tgz && tar -xzf /tmp/llama.tgz -C "$DEST" --strip-components=1 || { echo "download failed"; exit 1; }
  SERVER=$(find "$DEST" -name llama-server -type f | head -1)
fi
export LD_LIBRARY_PATH="$(dirname "$SERVER"):$DEST/lib:${LD_LIBRARY_PATH:-}"
"$SERVER" --version 2>&1 | head -1
if curl -s "http://localhost:$PORT/health" 2>/dev/null | grep -q '"ok"'; then
  echo "already running on :$PORT"; exit 0
fi
nohup "$SERVER" -hf "$HF" --alias cpu_tiny --port "$PORT" --ctx-size 8192 -t "$(nproc)" > "$DEST/server.log" 2>&1 &
for i in $(seq 1 120); do
  if curl -s "http://localhost:$PORT/health" 2>/dev/null | grep -q '"ok"'; then echo "ready on :$PORT after $((i * 5))s"; exit 0; fi
  sleep 5
done
echo "server did not come up; see $DEST/server.log"; tail -20 "$DEST/server.log"; exit 1
