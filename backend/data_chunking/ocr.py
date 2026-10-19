import io
import os
import json
# 
from pathlib import Path
from dotenv import load_dotenv
# 
from google.cloud import vision
# 
import pymupdf
from PIL import Image

load_dotenv(path = Path(__file__).parent.parent / '.env')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv('OCR_KEY')

DATA_DIR = ""
PATH_TO_FILE = ""

client = vision.ImageAnnotatorClient() 

def extract_text(file_path):
    doc = pymupdf.open(file_path)
    full_text = ""

    for page in doc:
        pix = page.get_pixmap(dpi = 300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        response = client.text_detection(image=vision.Image(content=buf.getvalue()))
        full_text += response.text_annotations[0].description if response.text_annotations else ""
    
    doc.close()
    return full_text

info = {
    "full_text": extract_text(PATH_TO_FILE)
}

with open(DATA_DIR, "w", encoding="utf-8") as f:
    json.dump(info, f, ensure_ascii=False, indent = 4)