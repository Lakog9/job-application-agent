"""
Central configuration for the job application agent.
Change settings here in one place.
"""
from pathlib import Path

# ============= PATHS =============
ROOT_DIR = Path(__file__).parent.parent  # the project root
PROFILE_PATH = ROOT_DIR / "profile.json"
PROMPTS_DIR = ROOT_DIR / "prompts"
OUTPUTS_DIR = ROOT_DIR / "outputs"

# ============= MODEL SETTINGS =============
# Claude Sonnet 4.5 — strong balance of quality and cost
MODEL = "claude-sonnet-4-5-20250929"

# Max tokens for different tasks
MAX_TOKENS_JD_ANALYSIS = 2000
MAX_TOKENS_DOCUMENT = 4000

# Temperature: 0.0 = deterministic, 1.0 = creative
# We want consistent, structured output → low temperature
TEMPERATURE_ANALYSIS = 0.2
TEMPERATURE_GENERATION = 0.4