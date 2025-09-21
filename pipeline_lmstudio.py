import os
import re
import json
import csv
try:
    import pdfplumber
except ModuleNotFoundError:  # pragma: no cover - handled during runtime
    pdfplumber = None
try:
    import spacy
except ModuleNotFoundError:  # pragma: no cover - optional dependency for tests
    spacy = None

try:
    from lmstudio import Client  # LM Studio 2025+ SDK
except ModuleNotFoundError:  # pragma: no cover - LM Studio is optional in tests
    Client = None
from typing import List, Dict, Any

# --------------------------
# Setup
# --------------------------
if spacy is not None:
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # Fall back to a blank English pipeline when the small model is unavailable.
        nlp = spacy.blank("en")
else:  # pragma: no cover - triggered only when spaCy is absent
    nlp = None
OUTPUT_IMAGE_DIR = "output_images"
os.makedirs(OUTPUT_IMAGE_DIR, exist_ok=True)

# Initialize LM Studio client
client = Client() if Client is not None else None

# --------------------------
# Helpers
# --------------------------
def clean_text(text):
    lines = text.splitlines()
    return "\n".join([line.strip() for line in lines if line.strip() and not re.match(r"^Page\s*\d+$", line, re.IGNORECASE)])

def extract_keywords_and_entities(text):
    if nlp is None:
        return [], []
    doc = nlp(text)
    entities = list(set([ent.text for ent in doc.ents]))
    keywords = [token.text for token in doc if token.pos_ in ("NOUN", "PROPN")]
    return list(set(keywords)), entities

# --------------------------
# PDF Extraction
# --------------------------
def extract_pdf_text(pdf_path):
    if pdfplumber is None:
        raise ImportError(
            "pdfplumber is required for PDF extraction but is not installed."
        )
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            text = clean_text(text)
            pages.append({"text": text})
    return pages

# --------------------------
# Chunking + metadata
# --------------------------
def chunk_and_summarize(pages, max_words=500):
    chunks=[]
    for page in pages:
        words = page["text"].split()
        for i in range(0, len(words), max_words):
            chunk_text = " ".join(words[i:i+max_words])
            keywords, entities = extract_keywords_and_entities(chunk_text)
            sentences = re.split(r'(?<=[.!?]) +', chunk_text)
            summary = " ".join(sentences[:3])
            chunks.append({
                "text": chunk_text,
                "summary": summary,
                "keywords": keywords,
                "entities": entities
            })
    return chunks

# --------------------------
# Question generation
# --------------------------
BLOOM_LEVELS = [
    "remember",
    "understand",
    "apply",
    "analyze",
    "evaluate",
    "create",
]


def _strip_code_fences(text: str) -> str:
    """Remove Markdown code fences that models sometimes include."""

    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # Drop the opening fence
        lines = lines[1:]
        # Drop the closing fence if present
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()


def _parse_structured_questions(raw_text: str, expected_levels: List[str]) -> List[Dict[str, Any]]:
    """Parse and validate the structured question response from the model."""

    cleaned = _strip_code_fences(raw_text)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("Model response is not valid JSON.") from exc

    if not isinstance(parsed, dict) or "questions" not in parsed:
        raise ValueError("Model response JSON must contain a 'questions' list.")

    questions = parsed["questions"]
    if not isinstance(questions, list):
        raise ValueError("'questions' must be a list of question objects.")

    normalized_expected = [level.lower() for level in expected_levels]
    seen_levels = []
    structured_questions: List[Dict[str, Any]] = []
    for item in questions:
        if not isinstance(item, dict):
            raise ValueError("Each question entry must be a JSON object.")

        question_text = item.get("question_text")
        bloom_level = item.get("bloom_level")
        difficulty_tag = item.get("difficulty_tag")

        if not isinstance(question_text, str) or not question_text.strip():
            raise ValueError("Each question must include non-empty 'question_text'.")
        if not isinstance(bloom_level, str):
            raise ValueError("Each question must include a 'bloom_level' string.")
        if not isinstance(difficulty_tag, str) or not difficulty_tag.strip():
            raise ValueError("Each question must include non-empty 'difficulty_tag'.")

        normalized_level = bloom_level.strip().lower()
        if normalized_level not in normalized_expected:
            raise ValueError(
                f"Bloom level '{bloom_level}' is not in the expected set: {expected_levels}."
            )
        if normalized_level in seen_levels:
            raise ValueError(
                f"Bloom level '{bloom_level}' appears more than once in the response."
            )
        seen_levels.append(normalized_level)

        structured_questions.append(
            {
                "question_text": question_text.strip(),
                "bloom_level": normalized_level,
                "difficulty_tag": difficulty_tag.strip(),
            }
        )

    missing_levels = set(normalized_expected) - set(seen_levels)
    if missing_levels:
        raise ValueError(
            "Model response is missing Bloom levels: " + ", ".join(sorted(missing_levels))
        )

    return structured_questions


def generate_questions_local(chunk, model, max_questions=3):
    prompt = f"""
You are an educational assistant generating assessment questions.
Chunk summary: {chunk.get('summary','')}

Text content:
{chunk.get('text','')}

Instructions:
- Produce exactly one question for each Bloom's taxonomy level: {', '.join(BLOOM_LEVELS)}.
- Provide a JSON object with a `questions` array.
- Each item must include `question_text`, `bloom_level`, and `difficulty_tag`.
- Use `difficulty_tag` to indicate relative challenge (e.g., easy, medium, hard).
- Do not include any additional commentary outside the JSON object.
"""
    response = model.generate(
        prompt=prompt,
        max_new_tokens=512,
        temperature=0.7
    )
    return _parse_structured_questions(response.output_text.strip(), BLOOM_LEVELS)

def generate_questions_for_pdf_local(chunks, model, max_questions_per_chunk=3):
    all_questions=[]
    for idx, chunk in enumerate(chunks, start=1):
        q_chunk = generate_questions_local(chunk, model, max_questions=max_questions_per_chunk)
        for q in q_chunk:
            question_text = q["question_text"]
            all_questions.append({
                "chunk_idx": idx,
                "question": question_text,
                "question_text": question_text,
                "bloom_level": q["bloom_level"],
                "difficulty_tag": q["difficulty_tag"],
                "summary": chunk.get("summary",""),
                "keywords": chunk.get("keywords",[]),
                "entities": chunk.get("entities",[])
            })
    return all_questions

# --------------------------
# Save JSON + CSV
# --------------------------
def save_questions_json(questions, output_path="pdf_questions.json"):
    with open(output_path,"w",encoding="utf-8") as f:
        json.dump(questions,f,indent=2,ensure_ascii=False)
    print(f"✅ Saved {len(questions)} questions to {output_path}")

def save_questions_csv(questions, output_path="pdf_questions.csv"):
    with open(output_path,"w",newline="",encoding="utf-8") as csvfile:
        fieldnames=[
            "chunk_idx",
            "question",
            "question_text",
            "bloom_level",
            "difficulty_tag",
            "summary",
            "keywords",
            "entities",
        ]
        writer=csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        for q in questions:
            writer.writerow({
                "chunk_idx":q["chunk_idx"],
                "question":q["question"],
                "question_text":q["question_text"],
                "bloom_level":q["bloom_level"],
                "difficulty_tag":q["difficulty_tag"],
                "summary":q["summary"],
                "keywords":"; ".join(q["keywords"]),
                "entities":"; ".join(q["entities"])
            })
    print(f"✅ Saved {len(questions)} questions to {output_path}")

# --------------------------
# Main
# --------------------------
if __name__=="__main__":
    pdf_path="sample.pdf"  # Replace with your PDF
    model_name="mistral-nemo-instruct-2407"

    print("📄 Extracting PDF content...")
    pages = extract_pdf_text(pdf_path)
    if not pages or all(not (page.get("text") or "").strip() for page in pages):
        print("⚠️ No extractable text found in the provided PDF. Exiting without generating questions.")
        raise SystemExit(1)

    print("✂️ Chunking and summarizing content...")
    chunks = chunk_and_summarize(pages)
    if not chunks:
        print("⚠️ No chunks were produced from the PDF content. Exiting without generating questions.")
        raise SystemExit(1)

    if client is None:
        raise ImportError(
            "LM Studio SDK is not installed. Install the 'lmstudio' package to generate questions."
        )

    print(f"🧠 Loading model '{model_name}' from LM Studio...")
    if hasattr(client, "load_model"):
        model = client.load_model(model_name)
    elif hasattr(client, "get_model"):
        model = client.get_model(model_name)
    elif hasattr(client, "models") and hasattr(client.models, "load"):
        model = client.models.load(model_name)
    else:
        raise AttributeError("LM Studio Client does not provide a recognized model-loading helper.")

    print("❓ Generating questions for each chunk...")
    questions = generate_questions_for_pdf_local(chunks, model=model)

    json_output_path = "pdf_questions.json"
    csv_output_path = "pdf_questions.csv"
    save_questions_json(questions, output_path=json_output_path)
    save_questions_csv(questions, output_path=csv_output_path)

    print(
        "📝 Generation complete. Questions saved to "
        f"JSON: {os.path.abspath(json_output_path)} | CSV: {os.path.abspath(csv_output_path)}"
    )
