"""
JD Analyzer module.
Reads a job description and extracts structured information using Claude.
"""
import json
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

from src import config

load_dotenv()
client = Anthropic()


def load_prompt_template() -> str:
    """Load the JD analyzer prompt from disk."""
    prompt_path = config.PROMPTS_DIR / "jd_analyzer.txt"
    return prompt_path.read_text(encoding="utf-8")


def analyze_job_description(jd_text: str) -> dict:
    """
    Send a job description to Claude and get back structured analysis.
    
    Args:
        jd_text: The raw job description text.
    
    Returns:
        A dictionary with structured info about the job.
    """
    prompt_template = load_prompt_template()
    full_prompt = prompt_template.replace("{job_description}", jd_text)
    
    print("Analyzing job description with Claude...")
    
    message = client.messages.create(
        model=config.MODEL,
        max_tokens=config.MAX_TOKENS_JD_ANALYSIS,
        temperature=config.TEMPERATURE_ANALYSIS,
        messages=[{"role": "user", "content": full_prompt}]
    )
    
    response_text = message.content[0].text.strip()
    
    # Sometimes the model wraps JSON in markdown code fences despite instructions.
    # Strip them defensively.
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])
    
    try:
        analysis = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response from Claude.")
        print(f"Raw response:\n{response_text}")
        raise e
    
    print(f"✓ Analysis complete. Tokens used: {message.usage.input_tokens} in / {message.usage.output_tokens} out")
    return analysis


# Quick standalone test when running this file directly
if __name__ == "__main__":
    sample_jd = """
    AI Consultant — EY Greece, Heraklion (Hybrid)
    
    We are looking for an AI Consultant to join our AI & Data team.
    Responsibilities: Design and develop AI algorithms using PyTorch and TensorFlow.
    Requirements: Bachelor's or Master's in computer science, data science, or related field.
    Strong background in AI, ML, deep learning. Proficiency in Python.
    Understanding of generative AI services (OpenAI, Hugging Face, Claude, Gemini).
    Greek and English required.
    """
    
    result = analyze_job_description(sample_jd)
    print("\n" + "="*60)
    print("STRUCTURED ANALYSIS:")
    print("="*60)
    print(json.dumps(result, indent=2, ensure_ascii=False))