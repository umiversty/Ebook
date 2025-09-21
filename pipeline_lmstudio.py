"""Pipeline utilities for generating educator questions via LM Studio."""
from __future__ import annotations

import csv
import json
import os
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

try:  # pragma: no cover - optional dependency
    from lmstudio import Client  # type: ignore
except ImportError:  # pragma: no cover - LM Studio SDK is optional for tests
    Client = None  # type: ignore

try:  # pragma: no cover - spaCy is optional at runtime
    import spacy

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # When the model is not available locally we lazily create a blank model.
        nlp = spacy.blank("en")
except Exception:  # pragma: no cover - failure means we fall back to heuristics
    spacy = None  # type: ignore
    nlp = None

try:  # pragma: no cover - depending on environment
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    try:
        from PyPDF2 import PdfReader  # type: ignore
    except ImportError:  # pragma: no cover
        PdfReader = None  # type: ignore


OUTPUT_IMAGE_DIR = "output_images"
DEFAULT_MODEL_NAME = "mistral-nemo-instruct-2407"

Path(OUTPUT_IMAGE_DIR).mkdir(parents=True, exist_ok=True)


@dataclass
class PDFPage:
    """Represents a single extracted PDF page."""

    index: int
    text: str


QuestionDict = Dict[str, Any]
ChunkDict = Dict[str, Any]


if Client is not None:  # pragma: no cover - dependency not present in tests
    client = Client()
else:  # pragma: no cover
    client = None


# --------------------------
# Helpers
# --------------------------
def clean_text(text: str) -> str:
    """Normalise whitespace and remove bare page markers from PDF text."""

    lines = text.splitlines()
    cleaned_lines = [
        line.strip()
        for line in lines
        if line.strip() and not re.match(r"^Page\s*\d+$", line, re.IGNORECASE)
    ]
    return "\n".join(cleaned_lines)


def extract_keywords_and_entities(text: str) -> Tuple[List[str], List[Dict[str, str]]]:
    """Extract keywords and named entities from ``text``.

    The pipeline supports both spaCy-based extraction and a heuristic fallback so
    the code continues to operate in lightweight environments (such as CI).
    """

    if not text.strip():
        return [], []

    if nlp is not None:
        doc = nlp(text)
        keywords = sorted(
            {
                token.lemma_.lower()
                for token in doc
                if token.is_alpha and not token.is_stop and len(token) > 3
            }
        )
        entities = [
            {"text": ent.text, "label": ent.label_}
            for ent in doc.ents
            if ent.text.strip()
        ]
        return keywords, entities

    # Fallback: use simple token frequency heuristics.
    tokens = [
        token.lower()
        for token in re.findall(r"[A-Za-z][A-Za-z\-']+", text)
        if len(token) > 3
    ]
    counter = Counter(tokens)
    keywords = [token for token, _ in counter.most_common(10)]
    return keywords, []


# --------------------------
# PDF Extraction
# --------------------------
def extract_pdf_text(pdf_path: str) -> List[PDFPage]:
    """Extracts text from ``pdf_path`` and returns a list of :class:`PDFPage`."""

    if PdfReader is None:  # pragma: no cover - exercised only when dependency missing
        raise RuntimeError(
            "PyPDF2/pypdf is not installed. Install it to extract PDF text."
        )

    reader = PdfReader(pdf_path)
    pages: List[PDFPage] = []
    for idx, page in enumerate(reader.pages):
        raw_text = page.extract_text() or ""
        pages.append(PDFPage(index=idx + 1, text=clean_text(raw_text)))
    return pages


# --------------------------
# Chunking + metadata
# --------------------------
def chunk_and_summarize(
    pages: Sequence[PDFPage], max_words: int = 500
) -> List[ChunkDict]:
    """Split pages into roughly ``max_words`` sized chunks with metadata."""

    chunks: List[ChunkDict] = []
    for page in pages:
        if not page.text:
            continue
        words = page.text.split()
        if not words:
            continue
        for i in range(0, len(words), max_words):
            chunk_words = words[i : i + max_words]
            chunk_text = " ".join(chunk_words)
            keywords, entities = extract_keywords_and_entities(chunk_text)
            sentences = re.split(r"(?<=[.!?]) +", chunk_text)
            summary = " ".join(sentences[:3]).strip()
            chunks.append(
                {
                    "text": chunk_text,
                    "summary": summary,
                    "keywords": keywords,
                    "entities": entities,
                    "page_start": page.index,
                    "page_end": page.index,
                }
            )
    return chunks


# --------------------------
# Model interaction
# --------------------------
def _prepare_prompt(chunk: ChunkDict, questions_per_chunk: int) -> str:
    """Build a prompt instructing LM Studio to return structured JSON."""

    return (
        "You are an educational content assistant. Generate multiple choice "
        "questions that help teachers assess comprehension. Use the provided "
        "context to craft insightful questions. Return strictly valid JSON "
        "matching this schema:\n"
        "{\n"
        "  \"questions\": [\n"
        "    {\n"
        "      \"question\": string,\n"
        "      \"answer\": string,\n"
        "      \"explanation\": string,\n"
        "      \"source_span\": {\n"
        "        \"text\": string,\n"
        "        \"start\": integer,\n"
        "        \"end\": integer\n"
        "      }\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        f"Limit the output to {questions_per_chunk} high quality question(s).\n"
        "Context:\n"
        f"{chunk['text']}\n"
    )


def _invoke_model(model: Any, prompt: str) -> str:
    """Attempt to invoke a loaded LM Studio model and return the raw response."""

    if model is None:  # pragma: no cover - runtime safeguard
        raise RuntimeError("A loaded LM Studio model is required to generate questions.")

    # The LM Studio client exposes slightly different helpers depending on the
    # version. We try common variations while keeping the interface lenient.
    if hasattr(model, "complete"):
        result = model.complete(prompt=prompt)
    elif hasattr(model, "generate"):
        result = model.generate(prompt=prompt)
    elif callable(model):
        result = model(prompt)
    else:  # pragma: no cover - defensive fallback
        raise AttributeError("The provided LM Studio model cannot be invoked.")

    if isinstance(result, str):
        return result

    if isinstance(result, dict):
        for key in ("text", "completion", "output", "response"):
            value = result.get(key)
            if isinstance(value, str):
                return value
        # Some SDKs nest the text deeper.
        choices = result.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0]
            if isinstance(message, dict):
                for key in ("text", "message"):
                    nested = message.get(key)
                    if isinstance(nested, str):
                        return nested
                    if isinstance(nested, dict):
                        content = nested.get("content")
                        if isinstance(content, str):
                            return content
        raise ValueError("Unable to determine text output from model response.")

    # Some SDKs return objects with an ``output_text`` attribute.
    if hasattr(result, "output_text"):
        return getattr(result, "output_text")

    raise ValueError("Unsupported model response type: {type(result)!r}")


def parse_model_response(raw_response: str) -> List[QuestionDict]:
    """Parse the LM Studio response and normalise question payloads.

    Parameters
    ----------
    raw_response:
        The raw string returned by the model invocation. The function extracts
        the JSON body containing the ``questions`` array and returns a cleaned
        list ready for downstream processing.
    """

    if not raw_response or not raw_response.strip():
        raise ValueError("Model response was empty.")

    # Remove common Markdown fences to improve JSON parsing reliability.
    cleaned = re.sub(r"```(?:json)?", "", raw_response).strip()

    # Attempt to locate the JSON object containing the questions payload.
    json_match = re.search(
        r"\{[^{}]*\"questions\"\s*:\s*\[[\s\S]*?\]\s*\}", cleaned
    )
    if not json_match:
        raise ValueError("Model response did not contain a questions payload.")

    try:
        payload = json.loads(json_match.group(0))
    except json.JSONDecodeError as exc:  # pragma: no cover - depends on model output
        raise ValueError("Unable to decode model JSON payload.") from exc

    questions = payload.get("questions")
    if not isinstance(questions, list):
        raise ValueError("Model payload is missing a valid 'questions' array.")

    normalised: List[QuestionDict] = []
    for item in questions:
        if not isinstance(item, dict):
            continue
        question_text = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        explanation = str(item.get("explanation", "")).strip()
        source_span = _normalise_source_span(item.get("source_span"))

        normalised.append(
            {
                "question": question_text,
                "answer": answer,
                "explanation": explanation,
                "source_span": source_span,
            }
        )

    if not normalised:
        raise ValueError("No valid questions were parsed from the model response.")

    return normalised


def _normalise_source_span(raw_span: Any) -> Dict[str, Any]:
    """Ensure ``source_span`` has the expected shape."""

    default_span = {"text": "", "start": 0, "end": 0}
    if not raw_span:
        return default_span

    if isinstance(raw_span, dict):
        text = str(raw_span.get("text", "")).strip()
        start = raw_span.get("start")
        end = raw_span.get("end")
        try:
            start_int = int(start) if start is not None else 0
        except (TypeError, ValueError):
            start_int = 0
        try:
            end_int = int(end) if end is not None else 0
        except (TypeError, ValueError):
            end_int = 0
        return {"text": text, "start": start_int, "end": end_int}

    # If the model only returned text, capture it and leave offsets empty.
    if isinstance(raw_span, str):
        return {"text": raw_span.strip(), "start": 0, "end": 0}

    return default_span


def generate_questions_for_chunks(
    model: Any, chunks: Sequence[ChunkDict], questions_per_chunk: int = 3
) -> List[QuestionDict]:
    """Invoke ``model`` for each chunk and aggregate question metadata."""

    all_questions: List[QuestionDict] = []
    for chunk in chunks:
        prompt = _prepare_prompt(chunk, questions_per_chunk)
        raw_response = _invoke_model(model, prompt)
        parsed_questions = parse_model_response(raw_response)
        for question in parsed_questions:
            enriched_question = {
                **question,
                "summary": chunk.get("summary", ""),
                "keywords": chunk.get("keywords", []),
                "entities": chunk.get("entities", []),
                "page_start": chunk.get("page_start"),
                "page_end": chunk.get("page_end"),
            }
            all_questions.append(enriched_question)
    return all_questions


# --------------------------
# Save JSON + CSV
# --------------------------
def save_questions_json(
    questions: Sequence[QuestionDict], output_path: str = "pdf_questions.json"
) -> None:
    questions_list = list(questions)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(questions_list, file, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(questions_list)} questions to {output_path}")


def save_questions_csv(
    questions: Sequence[QuestionDict], output_path: str = "pdf_questions.csv"
) -> None:
    questions_list = list(questions)
    fieldnames = [
        "question",
        "answer",
        "explanation",
        "source_span",
        "summary",
        "keywords",
        "entities",
        "page_start",
        "page_end",
    ]
    with open(output_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for question in questions_list:
            row = dict(question)
            row["keywords"] = "; ".join(question.get("keywords", []))
            entities = question.get("entities", [])
            if entities and isinstance(entities, list):
                row["entities"] = "; ".join(
                    [
                        f"{entity.get('text')} ({entity.get('label')})"
                        if isinstance(entity, dict)
                        else str(entity)
                        for entity in entities
                    ]
                )
            else:
                row["entities"] = ""
            row["source_span"] = json.dumps(question.get("source_span", {}), ensure_ascii=False)
            writer.writerow(row)
    print(f"✅ Saved {len(questions_list)} questions to {output_path}")


# --------------------------
# Main
# --------------------------
def main(pdf_path: str = "sample.pdf", model_name: str = DEFAULT_MODEL_NAME) -> None:
    print("📄 Extracting PDF content...")
    pages = extract_pdf_text(pdf_path)
    if not pages or all(not page.text.strip() for page in pages):
        print(
            "⚠️ No extractable text found in the provided PDF. Exiting without generating questions."
        )
        raise SystemExit(1)

    print("✂️ Chunking and summarizing content...")
    chunks = chunk_and_summarize(pages)
    if not chunks:
        print("⚠️ No chunks were produced from the PDF content. Exiting without generating questions.")
        raise SystemExit(1)

    if client is None:
        raise RuntimeError(
            "LM Studio client is unavailable. Ensure the lmstudio package is installed and configured."
        )

    print(f"🧠 Loading model '{model_name}' from LM Studio...")
    if hasattr(client, "load_model"):
        model = client.load_model(model_name)
    elif hasattr(client, "get_model"):
        model = client.get_model(model_name)
    elif hasattr(client, "models") and hasattr(client.models, "load"):
        model = client.models.load(model_name)
    else:  # pragma: no cover - defensive fallback
        raise AttributeError("LM Studio Client does not provide a recognized model-loading helper.")

    print("❓ Generating questions for each chunk...")
    questions = generate_questions_for_chunks(model, chunks)

    json_output_path = "pdf_questions.json"
    csv_output_path = "pdf_questions.csv"
    save_questions_json(questions, output_path=json_output_path)
    save_questions_csv(questions, output_path=csv_output_path)

    print(
        "📝 Generation complete. Questions saved to "
        f"JSON: {os.path.abspath(json_output_path)} | CSV: {os.path.abspath(csv_output_path)}"
    )


if __name__ == "__main__":
    main()
