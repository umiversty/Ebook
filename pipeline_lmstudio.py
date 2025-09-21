import importlib
import os
import re
import json
import csv
from typing import Any, Dict, List, Optional

LMSTUDIO_AVAILABLE = importlib.util.find_spec("lmstudio") is not None
if LMSTUDIO_AVAILABLE:
    from lmstudio import Client  # LM Studio 2025+ SDK
else:
    Client = None

# --------------------------
# Setup
# --------------------------
PDFPLUMBER_AVAILABLE = importlib.util.find_spec("pdfplumber") is not None
SPACY_AVAILABLE = importlib.util.find_spec("spacy") is not None

if SPACY_AVAILABLE:
    import spacy

    if importlib.util.find_spec("en_core_web_sm") is not None:
        nlp = spacy.load("en_core_web_sm")
    else:
        nlp = spacy.blank("en")
else:
    nlp = None
OUTPUT_IMAGE_DIR = "output_images"
os.makedirs(OUTPUT_IMAGE_DIR, exist_ok=True)

# Initialize LM Studio client when available
client = Client() if Client is not None else None

# --------------------------
# Helpers
# --------------------------
def clean_text(text):
    lines = text.splitlines()
    return "\n".join([line.strip() for line in lines if line.strip() and not re.match(r"^Page\s*\d+$", line, re.IGNORECASE)])

def extract_keywords_and_entities(text):
    if nlp is None:
        words = re.findall(r"[A-Za-z][A-Za-z\-]+", text)
        keywords = sorted(set(word for word in words if word[0].isupper()))
        return keywords, []

    doc = nlp(text)
    entities = list({ent.text for ent in doc.ents})
    keywords = [token.text for token in doc if token.pos_ in ("NOUN", "PROPN")]
    return list(set(keywords)), entities

# --------------------------
# PDF Extraction
# --------------------------
def extract_pdf_text(pdf_path):
    if not PDFPLUMBER_AVAILABLE:
        raise ModuleNotFoundError("pdfplumber is required for PDF extraction but is not installed.")
    import pdfplumber
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
def _build_question_prompt(chunk: Dict[str, Any], max_questions: int) -> str:
    return f"""
You are an educational assistant generating study questions.
Chunk summary: {chunk.get('summary','')}

Text content:
{chunk.get('text','')}

Respond ONLY with valid JSON formatted as:
{{
  "questions": [
    {{
      "question": "",
      "answer": "",
      "explanation": "",
      "source_span": {{"text": "", "start": 0, "end": 0}}
    }}
  ]
}}

Requirements:
- Include up to {max_questions} questions.
- Provide a concise correct answer for each question.
- Explain the reasoning for each answer in the "explanation" field.
- Populate "source_span" with the verbatim supporting text and the character start/end offsets relative to the provided chunk. Use -1 for unknown offsets.
- Do not include any additional commentary outside of the JSON.
"""


def _extract_json_block(text: str) -> Optional[str]:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    return match.group(0)


def _parse_question_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw_questions = payload.get("questions")
    if not isinstance(raw_questions, list):
        raise ValueError("Model response did not include a 'questions' list.")

    normalized: List[Dict[str, Any]] = []
    for item in raw_questions:
        if not isinstance(item, dict):
            continue
        question_text = item.get("question", "").strip()
        answer_text = item.get("answer", "").strip()
        explanation_text = item.get("explanation", "").strip()
        source_span = item.get("source_span") or {}
        source_text = ""
        start_offset: Optional[int] = None
        end_offset: Optional[int] = None
        if isinstance(source_span, dict):
            source_text = str(source_span.get("text", "")).strip()
            start_offset = source_span.get("start")
            end_offset = source_span.get("end")
        normalized.append(
            {
                "question": question_text,
                "answer": answer_text,
                "explanation": explanation_text,
                "source_span": {
                    "text": source_text,
                    "start": int(start_offset) if isinstance(start_offset, int) else -1,
                    "end": int(end_offset) if isinstance(end_offset, int) else -1,
                },
            }
        )
    return [q for q in normalized if q["question"] and q["answer"]]


def parse_model_response(text: str) -> List[Dict[str, Any]]:
    """Parse the LM Studio response text into structured question payloads."""

    json_block = _extract_json_block(text)
    if not json_block:
        raise ValueError("Model response did not contain JSON payload.")

    payload = json.loads(json_block)
    questions = _parse_question_payload(payload)
    if not questions:
        raise ValueError("No valid questions parsed from model response.")
    return questions


def generate_questions_local(chunk: Dict[str, Any], model, max_questions: int = 3) -> List[Dict[str, Any]]:
    prompt = _build_question_prompt(chunk, max_questions)
    response = model.generate(
        prompt=prompt,
        max_new_tokens=768,
        temperature=0.7
    )
    return parse_model_response(response.output_text.strip())

def generate_questions_for_pdf_local(chunks, model, max_questions_per_chunk=3):
    all_questions=[]
    for idx, chunk in enumerate(chunks, start=1):
        q_chunk = generate_questions_local(chunk, model, max_questions=max_questions_per_chunk)
        for question_idx, q in enumerate(q_chunk, start=1):
            all_questions.append({
                "id": f"{idx}-{question_idx}",
                "chunk_idx": idx,
                "question": q["question"],
                "answer": q["answer"],
                "explanation": q.get("explanation", ""),
                "source_span": q.get("source_span", {}),
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
            "id",
            "chunk_idx",
            "question",
            "answer",
            "explanation",
            "source_span",
            "summary",
            "keywords",
            "entities",
        ]
        writer=csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        for q in questions:
            writer.writerow({
                "id": q.get("id"),
                "chunk_idx":q["chunk_idx"],
                "question":q["question"],
                "answer":q.get("answer",""),
                "explanation":q.get("explanation",""),
                "source_span":json.dumps(q.get("source_span",{}), ensure_ascii=False),
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
        raise ModuleNotFoundError(
            "lmstudio SDK is required to load models. Install the package to use the generation pipeline."
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
