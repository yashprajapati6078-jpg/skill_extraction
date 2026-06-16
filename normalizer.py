"""
normalizer.py
-------------
Text normalisation pipeline.

Responsibilities
----------------
1. Strip HTML / special characters (light cleaning).
2. Lowercase the text for alias and exact-match lookups.
3. Resolve known aliases to their canonical skill names.
4. Tokenise text into clean tokens (punctuation stripped from edges).
"""

import logging
import re
from typing import List, Optional, Set

from skill_database import ALIAS_MAP, ALL_SKILLS

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Phase 1 – Text cleaning
# ---------------------------------------------------------------------------

_WHITESPACE_PATTERN = re.compile(r"\s+")
# Remove characters that can't be part of any skill name except +, #, ., -
_NOISE_PATTERN = re.compile(r"[^a-zA-Z0-9\s\.\+\#\-]")


def clean_text(text: str) -> str:
    """
    Light cleaning: remove non-skill characters, normalise whitespace.
    Preserves original casing.
    """
    text = _NOISE_PATTERN.sub(" ", text)
    text = _WHITESPACE_PATTERN.sub(" ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Phase 2 – Alias normalisation
# ---------------------------------------------------------------------------

_SORTED_ALIASES: List[str] = sorted(ALIAS_MAP.keys(), key=len, reverse=True)
_LOWER_TO_CANONICAL = {s.lower(): s for s in ALL_SKILLS}


def resolve_alias(token: str) -> Optional[str]:
    """
    Return the canonical skill name for *token* (case-insensitive), or None.
    Strips trailing punctuation before looking up.
    """
    lower = token.lower().strip(" .-,;:")
    if lower in ALIAS_MAP:
        canonical = ALIAS_MAP[lower]
        logger.debug("Alias resolved: %r → %r", token, canonical)
        return canonical
    if lower in _LOWER_TO_CANONICAL:
        return _LOWER_TO_CANONICAL[lower]
    return None


def normalize_aliases_in_text(text: str) -> str:
    """
    Lowercase *text* and replace all alias phrases with their canonical names.
    Multi-word aliases ("amazon web services") are processed before shorter ones.

    Returns lowercased text with canonical skill names substituted in-place
    (e.g. "I used reactjs" → "i used React").
    """
    result = text.lower()

    for alias in _SORTED_ALIASES:
        canonical = ALIAS_MAP[alias]
        # Use \b-style boundaries but compatible with special alias chars.
        # Lookbehind: not preceded by alphanumeric or underscore.
        # Lookahead:  not followed by alphanumeric or underscore.
        # We deliberately do NOT exclude dots/+/# from the lookahead so that
        # aliases like "amazon web services" still match when followed by a period.
        pattern = r"(?<![A-Za-z0-9_])" + re.escape(alias) + r"(?![A-Za-z0-9_])"
        replacement = f" {canonical} "
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    result = _WHITESPACE_PATTERN.sub(" ", result).strip()
    # Re-join special canonical names that may have been split by the space padding:
    # "C #" → "C#", "C ++" → "C++"
    result = re.sub(r"(?<=\bC)\s+(?=#)", "", result)   # C # → C#
    result = re.sub(r"(?<=\bC)\s+(?=\+\+)", "", result)  # C ++ → C++
    return result


# ---------------------------------------------------------------------------
# Tokenisation
# ---------------------------------------------------------------------------

# Split on whitespace, commas, semicolons, brackets, quotes
_SPLIT_PATTERN = re.compile(r"[\s,;\"'\(\)\[\]\{\}|\\]+")
# Chars to strip from the edges of tokens (trailing/leading punctuation)
_EDGE_STRIP = re.compile(r"^[.\-:]+|[.\-:]+$")


def tokenize(text: str) -> List[str]:
    """
    Split *text* into tokens, stripping leading/trailing punctuation from each.
    Keeps internal chars like those in 'C++', 'C#', 'Next.js'.
    """
    raw = [t.strip() for t in _SPLIT_PATTERN.split(text) if t.strip()]
    tokens = []
    for tok in raw:
        cleaned = _EDGE_STRIP.sub("", tok).strip()
        if cleaned:
            tokens.append(cleaned)
    return tokens
