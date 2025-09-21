import pytest

from pipeline_lmstudio import parse_model_response


def test_parse_model_response_extracts_expected_fields():
    response = """
    Some header text that might precede JSON.
    {"questions": [
        {
            "question": "What is the main idea?",
            "answer": "Photosynthesis converts light to energy.",
            "explanation": "The text explains that plants create energy through photosynthesis.",
            "source_span": {"text": "plants create energy through photosynthesis", "start": 102, "end": 150}
        }
    ]}
    """

    parsed = parse_model_response(response)

    assert len(parsed) == 1
    question = parsed[0]
    assert question["question"] == "What is the main idea?"
    assert question["answer"] == "Photosynthesis converts light to energy."
    assert question["explanation"].startswith("The text explains")
    assert question["source_span"]["start"] == 102
    assert question["source_span"]["end"] == 150


def test_parse_model_response_raises_for_missing_payload():
    with pytest.raises(ValueError):
        parse_model_response("No JSON here")
