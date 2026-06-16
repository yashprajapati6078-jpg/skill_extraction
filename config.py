"""
config.py
---------
Centralised configuration constants for the Technical Skill Extractor.
Adjust these values to tune extraction behaviour without touching business logic.
"""

# ---------------------------------------------------------------------------
# Fuzzy matching
# ---------------------------------------------------------------------------
# Minimum RapidFuzz similarity score (0–100) to accept a fuzzy match.
# 85 balances recall and precision well for technical vocabulary.
FUZZY_THRESHOLD: int = 85

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_LEVEL: str = "INFO"
LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
API_TITLE: str = "Technical Skill Extractor"
API_DESCRIPTION: str = (
    "Extracts technical skills from interview transcripts using "
    "alias normalisation, exact matching, and fuzzy matching."
)
API_VERSION: str = "1.0.0"
API_HOST: str = "0.0.0.0"
API_PORT: int = 8000

# ---------------------------------------------------------------------------
# Extraction pipeline
# ---------------------------------------------------------------------------
# Minimum token length to consider for fuzzy matching (avoids noise on
# short words like "a", "I", "go" — "Go" the language is handled via alias).
MIN_FUZZY_TOKEN_LENGTH: int = 4

# Maximum token length passed to the fuzzy matcher.  Very long tokens are
# unlikely to be skill names and skipping them keeps the pipeline fast.
MAX_FUZZY_TOKEN_LENGTH: int = 40
