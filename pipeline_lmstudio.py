

# --------------------------
# Setup
# --------------------------


OUTPUT_IMAGE_DIR = "output_images"
os.makedirs(OUTPUT_IMAGE_DIR, exist_ok=True)



client = Client() if Client is not None else None

# --------------------------
# Helpers
# --------------------------
def clean_text(text):
    lines = text.splitlines()
    return "\n".join([line.strip() for line in lines if line.strip() and not re.match(r"^Page\s*\d+$", line, re.IGNORECASE)])

def extract_keywords_and_entities(text):
    if nlp is None:

    return list(set(keywords)), entities

# --------------------------
# PDF Extraction
# --------------------------
def extract_pdf_text(pdf_path):


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


    json_output_path = "pdf_questions.json"
    csv_output_path = "pdf_questions.csv"
    save_questions_json(questions, output_path=json_output_path)
    save_questions_csv(questions, output_path=csv_output_path)

    print(
        "📝 Generation complete. Questions saved to "
        f"JSON: {os.path.abspath(json_output_path)} | CSV: {os.path.abspath(csv_output_path)}"
    )
