import importlib
import sys
import types
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="module")
def pipeline_module():
    dummy_lmstudio = types.ModuleType("lmstudio")

    class DummyModel:
        def generate(self, *args, **kwargs):  # pragma: no cover - unused in tests
            class Response:
                output_text = "1. Define energy."

            return Response()

    class DummyClient:
        def load_model(self, name):
            return DummyModel()

    dummy_lmstudio.Client = DummyClient
    sys.modules.setdefault("lmstudio", dummy_lmstudio)

    dummy_spacy = types.ModuleType("spacy")

    class DummyDoc:
        def __init__(self, text):
            self.ents = []
            self._text = text

        def __iter__(self):
            return iter([])

    class DummyNLP:
        def __call__(self, text):
            return DummyDoc(text)

    dummy_spacy.load = lambda name: DummyNLP()
    sys.modules.setdefault("spacy", dummy_spacy)

    if "pipeline_lmstudio" in sys.modules:
        del sys.modules["pipeline_lmstudio"]
    return importlib.import_module("pipeline_lmstudio")


def test_student_profile_target_difficulty_band_shifts_with_metrics(pipeline_module):
    StudentProfile = pipeline_module.StudentProfile

    struggling = StudentProfile(accuracy=0.35, average_response_time=55.0, mastery_score=0.3)
    developing = StudentProfile(accuracy=0.6, average_response_time=35.0, mastery_score=0.55)
    excelling = StudentProfile(accuracy=0.9, average_response_time=15.0, mastery_score=0.85)

    assert struggling.target_difficulty_band() == "foundational"
    assert developing.target_difficulty_band() == "intermediate"
    assert excelling.target_difficulty_band() == "advanced"


@pytest.mark.parametrize(
    "profile_kwargs,expected_band",
    [
        ({"accuracy": 0.4, "average_response_time": 50.0, "mastery_score": 0.35}, "foundational"),
        ({"accuracy": 0.65, "average_response_time": 30.0, "mastery_score": 0.55}, "intermediate"),
        ({"accuracy": 0.9, "average_response_time": 20.0, "mastery_score": 0.8}, "advanced"),
    ],
)
def test_generate_questions_for_pdf_local_applies_difficulty_filtering(
    pipeline_module, monkeypatch, profile_kwargs, expected_band
):
    module = pipeline_module

    candidates = [
        {"question": "Define kinetic energy.", "bloom_level": "remember"},
        {"question": "Explain the law of conservation of energy.", "bloom_level": "understand"},
        {"question": "Apply conservation of energy to a pendulum.", "bloom_level": "apply"},
        {"question": "Analyze energy transfer in a roller coaster.", "bloom_level": "analyze"},
        {"question": "Evaluate the efficiency of a power plant.", "bloom_level": "evaluate"},
        {"question": "Design an experiment about energy conversion.", "bloom_level": "create"},
    ]

    def fake_generate(chunk, model, max_questions):
        return [dict(item) for item in candidates[:max_questions]]

    monkeypatch.setattr(module, "generate_questions_local", fake_generate)

    profile = module.StudentProfile(**profile_kwargs)
    results = module.generate_questions_for_pdf_local(
        chunks=[{"summary": "", "keywords": [], "entities": []}],
        model=object(),
        max_questions_per_chunk=len(candidates),
        student_profile=profile,
    )

    assert results, "Expected filtered questions for the provided profile"
    desired_levels = module.DIFFICULTY_BANDS[expected_band]
    for question in results:
        assert question["difficulty_band"] == expected_band
        assert question["bloom_level"] in desired_levels
