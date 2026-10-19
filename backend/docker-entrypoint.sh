#!/bin/sh
# ^ tells the OS: "run this file using the sh shell"

set -e
# ^ if ANY command below fails, stop immediately (don't silently continue)

# ── GCP Credentials ────────────────────────────────────────────────────────
# Your GCP JSON key file can't be a Windows path (D:\AUPP\...) inside a Linux container.
# So instead, we store the JSON as a base64 string in the .env.prod file,
# then decode it back into a real file here at container startup.

if [ -n "$GCP_CREDENTIALS_BASE64" ]; then
    # -n means "if this variable is NOT empty"

    echo "$GCP_CREDENTIALS_BASE64" | base64 -d > /tmp/gcp-credentials.json
    # ^ decode the base64 string back into a real JSON file, save it to /tmp/

    export GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp-credentials.json
    # ^ set the env var that Google's SDK automatically looks for

    echo "GCP credentials loaded."
else
    echo "WARNING: GCP_CREDENTIALS_BASE64 not set — Vertex AI calls will fail."
fi

# ── Start your app ─────────────────────────────────────────────────────────
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2
# ^ actually start FastAPI. "exec" replaces this shell process with uvicorn,
#   which is important so Docker signals (stop/restart) reach uvicorn correctly.