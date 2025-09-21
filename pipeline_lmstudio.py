

# --------------------------
# Setup
# --------------------------

OUTPUT_IMAGE_DIR = "output_images"
os.makedirs(OUTPUT_IMAGE_DIR, exist_ok=True)


# --------------------------
# Student profile modelling
# --------------------------
DIFFICULTY_BANDS = {
    "foundational": {"remember", "understand"},
    "intermediate": {"apply", "analyze"},
    "advanced": {"evaluate", "create"},
}


@dataclass
class StudentProfile:
    accuracy: float
    average_response_time: float
    mastery_score: float = 0.5
    growth_trend: float = 0.0

    @classmethod
    def from_dict(cls, payload: Dict[str, float]) -> "StudentProfile":
        return cls(
            accuracy=float(payload.get("accuracy", 0.6)),
            average_response_time=float(payload.get("average_response_time", 35.0)),
            mastery_score=float(payload.get("mastery_score", payload.get("mastery", 0.5))),
            growth_trend=float(payload.get("growth_trend", payload.get("growth", 0.0))),
        )

    @classmethod
    def default(cls) -> "StudentProfile":
        return cls(accuracy=0.65, average_response_time=35.0)

    def target_difficulty_band(self) -> str:
        """Return a Bloom difficulty band derived from performance signals."""

        # Normalise metrics to a 0-1 scale and clamp to avoid runaway inputs.
        accuracy_score = max(0.0, min(1.0, self.accuracy))
        mastery_score = max(0.0, min(1.0, self.mastery_score))
        speed_score = 1.0 - max(0.0, min(1.0, self.average_response_time / 60.0))
        growth_score = max(-1.0, min(1.0, self.growth_trend))

        composite = (
            0.45 * accuracy_score
            + 0.25 * mastery_score
            + 0.2 * speed_score
            + 0.1 * ((growth_score + 1.0) / 2.0)
        )

        if composite >= 0.7:
            return "advanced"
        if composite >= 0.5:
            return "intermediate"
        return "foundational"


def load_student_profile(profile_path: Optional[str] = None) -> StudentProfile:
    """Load a student profile from JSON, falling back to defaults when missing."""

    if profile_path and os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
            return StudentProfile.from_dict(payload)

    env_payload = os.environ.get("STUDENT_PROFILE")
    if env_payload:
        try:
            payload = json.loads(env_payload)
            return StudentProfile.from_dict(payload)
        except json.JSONDecodeError:
            pass

    return StudentProfile.default()

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

    return list(set(keywords)), entities

# --------------------------
# PDF Extraction
# --------------------------
def extract_pdf_text(pdf_path):
    if pdfplumber is None:
        raise ImportError(
            "pdfplumber is required for PDF extraction but is not installed."
        )


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


            "summary",
            "keywords",
            "entities",
        ]

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

    profile_path = os.environ.get("STUDENT_PROFILE_PATH", "student_profile.json")
    student_profile = load_student_profile(profile_path)
    print(
        "🎯 Loaded student profile → accuracy: "
        f"{student_profile.accuracy:.2f}, avg response: {student_profile.average_response_time:.1f}s, "
        f"target band: {student_profile.target_difficulty_band()}"
    )

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
    questions = generate_questions_for_pdf_local(
        chunks,
        model=model,
        student_profile=student_profile,
    )

    json_output_path = "pdf_questions.json"
    csv_output_path = "pdf_questions.csv"
    save_questions_json(questions, output_path=json_output_path)
    save_questions_csv(questions, output_path=csv_output_path)

    print(
        "📝 Generation complete. Questions saved to "
        f"JSON: {os.path.abspath(json_output_path)} | CSV: {os.path.abspath(csv_output_path)}"
    )
