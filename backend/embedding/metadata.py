import os
import json
from dotenv import load_dotenv
# 
from langchain_text_splitters import RecursiveCharacterTextSplitter
# 
import vertexai
from vertexai.generative_models import GenerativeModel

load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"D:\AUPP\Project-Github\machine_learning_final_project\ocr-for-extraction-5f1d4479787d.json"

vertexai.init(project="ocr-for-extraction", location="us-central1")

def get_response(prompt):
    model = GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(
        prompt
    )
    return response.text

PROMPT = \
    """You are a medical information classifier specializing in sexually transmitted diseases (STDs) and sexually transmitted infections (STIs).

    Your task is to classify each piece of information provided and return a JSON object for every item in the list.

    Classification must be one of the following:
    - "general" - general awareness, statistics, overview, or public health information
    - "symptoms" - signs and symptoms of an STD/STI
    - "treatment" - medications, therapies, or medical procedures for an STD/STI
    - "prevention" - safe practices, vaccines, or methods to reduce transmission
    - "transmission" - how an STD/STI spreads between individuals
    - "diagnosis" - testing methods, screening, or diagnostic procedures
    - "complications" - long-term effects or health risks if untreated

    Disease must be one of the following:
    - "general" - if the information is not specific to one disease
    - "hiv" 
    - "syphilis"
    - "gonorrhea"
    - "chlamydia"
    - "herpes"
    - "hpv"
    - "hepatitis_b"
    - "hepatitis_c"
    - "trichomoniasis"
    - "mpox"

    Return ONLY a raw JSON array with no extra text, no markdown, and no code blocks.
    Each item in the array must follow this exact structure:
    [
        {
            "info": "<original text passed in>",
            "classification": "<one of the classification values above>",
            "disease": "<one of the disease values above>"
        },
        ...
    ]

    Here is the list of information to classify:
    """

def get_tagging(query : str):
    return get_response(
        f"Query from the user: {query}\nPrompt: {PROMPT}"
    )