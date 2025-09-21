import json
import pathlib
import sys

import pytest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline_lmstudio import (  # noqa: E402
    BLOOM_LEVELS,
    generate_questions_for_pdf_local,
)


class StubModel:
    def __init__(self, response_payload):
        self._response_payload = response_payload

    def generate(self, prompt, max_new_tokens, temperature):  # noqa: D401
        class Response:
            def __init__(self, text):
                self.output_text = text

        return Response(self._response_payload)


def _make_response(excluded_level=None):
    questions = []
    for level in BLOOM_LEVELS:
        if level == excluded_level:
            continue
        questions.append(
            {
                "question_text": f"What is an example of {level}?",
                "bloom_level": level,
                "difficulty_tag": "medium",
            }
        )
    return json.dumps({"questions": questions})


def test_generate_questions_for_pdf_local_requires_all_levels():
    chunk = {"text": "Example text", "summary": "Summary"}
    model = StubModel(_make_response(excluded_level=BLOOM_LEVELS[-1]))

    with pytest.raises(ValueError) as exc:
        generate_questions_for_pdf_local([chunk], model=model)

    assert BLOOM_LEVELS[-1] in str(exc.value)


def test_generate_questions_for_pdf_local_returns_structured_questions():
    chunk = {
        "text": "Example text",
        "summary": "Summary",
        "keywords": ["example"],
        "entities": ["Entity"],
    }
    model = StubModel(_make_response())

    questions = generate_questions_for_pdf_local([chunk], model=model)

    assert len(questions) == len(BLOOM_LEVELS)
    first_question = questions[0]

    assert first_question["chunk_idx"] == 1
    assert first_question["question"] == first_question["question_text"]
    assert first_question["bloom_level"] in BLOOM_LEVELS
    assert first_question["difficulty_tag"] == "medium"
    assert first_question["summary"] == "Summary"
    assert first_question["keywords"] == ["example"]
    assert first_question["entities"] == ["Entity"]
