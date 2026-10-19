import os
import base64
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from dotenv import load_dotenv
from auth import get_current_user

import vertexai
from vertexai.generative_models import GenerativeModel, Part

load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"D:\AUPP\Project-Github\machine_learning_final_project\ocr-for-extraction-5f1d4479787d.json"
vertexai.init(project="ocr-for-extraction", location="us-central1")

model = GenerativeModel("gemini-2.0-flash")  # one shared instance

router = APIRouter(prefix="/media", tags=["Media"])


# ── Image → text via Gemini Vision ────────────────────────────────────────────

async def _image_to_text(image_bytes: bytes, mime_type: str) -> str:
    image_part = Part.from_data(data=image_bytes, mime_type=mime_type)
    prompt_part = (
        "You are a medical assistant. "
        "Describe what you see in this image concisely and factually, "
        "focusing on any health-relevant details (symptoms, rashes, injuries, "
        "medical documents, test results, etc.). "
        "Your description will be appended to a user's health query. "
        "Do NOT diagnose — only describe objectively."
    )
    response = model.generate_content([image_part, prompt_part])
    return response.text.strip()


# ── Audio → text via Gemini ────────────────────────────────────────────────────

async def _audio_to_text(audio_bytes: bytes, mime_type: str) -> str:
    audio_part = Part.from_data(data=audio_bytes, mime_type=mime_type)
    prompt_part = (
        "Transcribe the following audio accurately. "
        "The speaker may be using Khmer or English. "
        "Return only the transcribed text, no commentary."
    )
    response = model.generate_content([audio_part, prompt_part])
    return response.text.strip()


# ── Unified endpoint (unchanged from before) ───────────────────────────────────

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/mp4", "audio/m4a",
                       "audio/wav", "audio/ogg", "audio/x-m4a"}
MAX_FILE_SIZE = 20 * 1024 * 1024


@router.post("/process")
async def process_media(
    image: UploadFile | None = File(default=None),
    audio: UploadFile | None = File(default=None),
    current_user: dict = Depends(get_current_user),
):
    if not image and not audio:
        raise HTTPException(status_code=400, detail="Provide at least one of: image, audio.")

    image_description: str | None = None
    transcript: str | None = None

    if image:
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=415, detail=f"Unsupported image type: {image.content_type}")
        image_bytes = await image.read()
        if len(image_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Image exceeds 20 MB limit.")
        try:
            image_description = await _image_to_text(image_bytes, image.content_type)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Image processing failed: {e}")

    if audio:
        if audio.content_type not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(status_code=415, detail=f"Unsupported audio type: {audio.content_type}")
        audio_bytes = await audio.read()
        if len(audio_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Audio exceeds 20 MB limit.")
        try:
            transcript = await _audio_to_text(audio_bytes, audio.content_type)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Audio transcription failed: {e}")

    parts = []
    if image_description:
        parts.append(f"[Image provided by user: {image_description}]")
    if transcript:
        parts.append(f"[User spoke: {transcript}]")

    return {
        "image_description": image_description,
        "transcript": transcript,
        "combined_context": "\n".join(parts),
    }