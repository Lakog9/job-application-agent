"""
Document Generator module.

Takes:
  - the candidate's profile (from profile.json)
  - the structured JD analysis (from jd_analyzer.py)

Produces:
  - a structured JSON with tailored CV content + tailored cover letter content

The output is consumed by docx_writer.py to produce final .docx files.
"""
import json
from anthropic import Anthropic
from dotenv import load_dotenv

from src import config

load_dotenv()
client = Anthropic()


def load_prompt_template() -> str:
    """Load the document generator prompt from disk."""
    prompt_path = config.PROMPTS_DIR / "document_generator.txt"
    return prompt_path.read_text(encoding="utf-8")


def load_profile() -> dict:
    """Load the candidate profile from profile.json."""
    return json.loads(config.PROFILE_PATH.read_text(encoding="utf-8"))


def generate_documents(jd_analysis: dict, profile: dict | None = None) -> dict:
    """
    Generate tailored CV + cover letter content using Claude.

    Args:
        jd_analysis: The structured JD analysis dict (from jd_analyzer).
        profile: Optional candidate profile dict. If None, loads from profile.json.

    Returns:
        A dict with 'cv' and 'cover_letter' keys, ready for docx writing.
    """
    if profile is None:
        profile = load_profile()

    prompt_template = load_prompt_template()

    # Inject the two JSON inputs into the prompt template
    full_prompt = prompt_template.replace(
        "{profile_json}", json.dumps(profile, indent=2, ensure_ascii=False)
    ).replace(
        "{jd_analysis_json}", json.dumps(jd_analysis, indent=2, ensure_ascii=False)
    )

    print("Generating tailored CV + cover letter with Claude...")
    print("(this takes 15-30 seconds for a quality result)")

    message = client.messages.create(
        model=config.MODEL,
        max_tokens=config.MAX_TOKENS_DOCUMENT,
        temperature=config.TEMPERATURE_GENERATION,
        messages=[{"role": "user", "content": full_prompt}],
    )

    response_text = message.content[0].text.strip()

    # Defensive: strip markdown code fences if Claude added them
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError as e:
        print("❌ Failed to parse JSON response from Claude.")
        print(f"Raw response:\n{response_text[:500]}...")
        raise e

    print(f"✓ Documents generated. Tokens used: {message.usage.input_tokens} in / {message.usage.output_tokens} out")

    # Quick sanity checks on output structure
    if "cv" not in result or "cover_letter" not in result:
        raise ValueError(f"Output missing required keys. Got: {list(result.keys())}")

    return result


# ============= Standalone test =============
if __name__ == "__main__":
    from src.jd_analyzer import analyze_job_description

    # A realistic JD to test against (the actual EY one, abbreviated)
    sample_jd = """
    AI Consultant — EY Greece, Heraklion (Hybrid)

    As part of our AI & Data team of the Technology Consulting practice, you will work
    with multi-disciplinary teams to support clients in a wide range of data initiatives
    aiming to generate and present new, useful and actionable insights.

    Your Key Responsibilities:
    - Design and develop AI algorithms, models, and systems using tools like PyTorch and TensorFlow
    - Keep up with the latest advancements in AI technologies, including generative AI
    - Collaborate with cross-functional teams to understand requirements and develop AI solutions
    - Collect, clean, and preprocess data using appropriate tools and libraries
    - Train, test, and evaluate AI models employing appropriate evaluation metrics
    - Optimize and fine-tune models for performance, scalability and efficiency
    - Build applications and use appropriate prompting on generative AI models

    Skills required:
    - Bachelor's or Master's degree in computer science, data science, engineering, or related field
    - Strong background in AI, machine learning, deep learning, and statistical modeling
    - Hands-on experience with PyTorch, TensorFlow
    - Proficiency in Python, Java, or C++
    - Strong understanding of generative AI services e.g. OpenAI, Hugging Face, Claude, Gemini
    - Understanding of data structures, algorithms, and software development principles
    - Advanced technical writing skills in Greek and English
    """

    print("\n" + "="*60)
    print("STEP 1: Analyzing job description...")
    print("="*60)
    jd_analysis = analyze_job_description(sample_jd)

    print("\n" + "="*60)
    print("STEP 2: Generating tailored documents...")
    print("="*60)
    documents = generate_documents(jd_analysis)

    # Save outputs for inspection
    output_path = config.OUTPUTS_DIR / "test_generated_documents.json"
    output_path.write_text(
        json.dumps(documents, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\n✓ Output saved to: {output_path}")
    print("\n" + "="*60)
    print("PREVIEW — CV HEADLINE:")
    print("="*60)
    print(documents["cv"]["headline"])
    print("\nPREVIEW — CV SUMMARY:")
    print("="*60)
    print(documents["cv"]["summary"])
    print("\nPREVIEW — COVER LETTER HOOK (first paragraph):")
    print("="*60)
    print(documents["cover_letter"]["paragraphs"][0])