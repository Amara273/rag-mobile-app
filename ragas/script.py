import json
import os
import logging
import ollama
from datasets import Dataset
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel
from khmerns import tokenize, normalize
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_utilization
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.run_config import RunConfig
from langchain_google_vertexai import VertexAI, VertexAIEmbeddings
from database import get_db, get_similarity
from metadata import get_tagging

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ── Environment ───────────────────────────────────────────────────────────────
load_dotenv()
os.environ["OPENAI_API_KEY"] = "dummy-not-used"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"D:\AUPP\Project-Github\machine_learning_final_project\ocr-for-extraction-5f1d4479787d.json"
vertexai.init(project="ocr-for-extraction", location="us-central1")

# ── System prompt ─────────────────────────────────────────────────────────────
PROMPT = '''
You are a medical assistant specializing in sexually transmitted diseases (STD/STI) in the context of Cambodia. You must only use the information explicitly provided to you, including disease descriptions, tags, and structured data. Do not introduce outside knowledge, assumptions, or general medical advice beyond the provided content. Before answering, verify whether the available information is sufficient. If it is not sufficient, respond with a brief apology and state that there is not enough information to provide a reliable response, then advise the user to seek professional medical care.

Your tone must be polite, calm, supportive, and empathetic, as users may be asking questions during stressful or sensitive situations. Avoid sounding blunt, robotic, or alarming. Responses must be short, concise, and written with correct grammar and formal spelling. Only include information that is directly relevant to the disease and tags provided, and avoid adding unrelated explanations or educational content.

If the user writes in Khmer, respond in Khmer. Medical terms should remain in English if no Khmer translation has been provided. Maintain formal and clear wording in both English and Khmer. You must never diagnose users, never conclude that they have a disease, and never estimate probability or confirm infection. Always use neutral phrasing and encourage users to consult a healthcare professional for proper evaluation. Each response should remain brief, ideally within three to five short sentences, with no speculation, no assumptions, and no unnecessary elaboration. Your goal is to provide supportive, accurate, and concise STD/STI-related guidance strictly within the provided Cambodia-focused information while prioritizing user safety and professional medical consultation.
'''

# ── RAGAS: Gemini via Vertex AI as judge (supports Khmer) ────────────────────
_gemini_llm = LangchainLLMWrapper(VertexAI(
    model_name="gemini-2.0-flash",
    project="ocr-for-extraction",
    location="us-central1",
    temperature=0.0,
))
_gemini_embeddings = LangchainEmbeddingsWrapper(VertexAIEmbeddings(
    model_name="text-multilingual-embedding-002",  # multilingual — handles Khmer
    project="ocr-for-extraction",
    location="us-central1",
))

faithfulness.llm            = _gemini_llm
context_utilization.llm     = _gemini_llm
answer_relevancy.llm        = _gemini_llm
answer_relevancy.embeddings = _gemini_embeddings

# ── Column name auto-detection ────────────────────────────────────────────────
# Candidate column names to try, in priority order.
# If you get an AttributeError, check the printed keys and add the correct one here.
_CANDIDATE_COLUMNS = ["content", "text", "chunk", "document", "page_content", "body", "chunk_text"]

def _extract_text_from_row(row) -> str:
    """
    Attempt to extract text from a DB row by trying known column names.
    Falls back to printing available keys so you can update _CANDIDATE_COLUMNS.
    """
    try:
        keys = list(row._mapping.keys())
    except AttributeError:
        try:
            keys = list(vars(row).keys())
            keys = [k for k in keys if not k.startswith("_")]
        except TypeError:
            keys = []

    for col in _CANDIDATE_COLUMNS:
        if col in keys:
            return str(getattr(row, col) if hasattr(row, col) else row._mapping[col])

    logger.error(
        f"Could not find a text column in DB row. Available columns: {keys}. "
        f"Add the correct name to _CANDIDATE_COLUMNS at the top of this file."
    )
    raise AttributeError(
        f"No text column found in DB row. Available columns: {keys}. "
        f"Add the correct one to _CANDIDATE_COLUMNS in eval.py."
    )

# ── Helpers ───────────────────────────────────────────────────────────────────
def segment_text(text: str) -> str:
    return " ".join(tokenize(normalize(text)))

def retrieve_contexts(
    question: str,
    db,
    static_contexts: list[str] | None = None,
    top_k: int = 5,
) -> list[str]:
    """
    Use pre-written contexts from data.json if available (reproducible eval).
    Falls back to live DB retrieval if contexts are missing from the JSON.
    """
    if static_contexts:
        return [" ".join(tokenize(normalize(ctx))) for ctx in static_contexts]

    segmented = segment_text(question)
    embedded = ollama.embed(model="bge-m3", input=segmented)
    results = get_similarity(db, embedded.embeddings, k=top_k)

    if not results:
        return ["No relevant information found."]

    return [_extract_text_from_row(row) for row in results]

def get_answer(question: str, contexts: list[str]) -> str:
    """Mirror the chat endpoint's generation step exactly."""
    segmented_query = segment_text(question)
    tags = get_tagging(segmented_query)
    context_text = "\n\n".join(contexts)

    full_prompt = f"""
{PROMPT}

Context (retrieved from database):
{context_text}

Tags: {tags}

User Query: {segmented_query}
"""
    model = GenerativeModel("gemini-2.0-flash")
    return model.generate_content(full_prompt).text.strip()

def load_test_data(data_file: str) -> list[dict]:
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# ── Evaluation ────────────────────────────────────────────────────────────────
def evaluate_ragas(data_file: str = "data.json"):
    test_cases = load_test_data(data_file)
    logger.info(f"Loaded {len(test_cases)} test cases from {data_file}")

    db = next(get_db())

    questions, answers, contexts_list = [], [], []
    try:
        for i, case in enumerate(test_cases):
            question = case["question"]
            static_contexts = case.get("contexts")

            contexts = retrieve_contexts(question, db, static_contexts=static_contexts)
            answer = get_answer(question, contexts)

            questions.append(question)
            answers.append(answer)
            contexts_list.append(contexts)
            logger.info(f"[{i+1}/{len(test_cases)}] Processed: {question[:60]}...")
    finally:
        db.close()

    dataset = Dataset.from_dict({
        "question": questions,
        "answer":   answers,
        "contexts": contexts_list,
    })

    run_config = RunConfig(
        timeout=600,
        max_retries=3,
        max_workers=1,
    )

    logger.info("Running RAGAS evaluation...")
    results = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_utilization],
        run_config=run_config,
    )

    print("\n── RAGAS Evaluation Results ──")
    print(results)
    return results

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    evaluate_ragas("data.json")