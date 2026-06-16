"""
extractor.py
------------
Core NLP pipeline for extracting technical skills from interview transcripts.

Pipeline stages
---------------
1.  Text Cleaning          – remove noise, normalise whitespace
2.  Alias Normalisation    – replace known aliases with canonical names in-text
3.  Exact Skill Matching   – regex over the normalised text (case-insensitive)
4.  Tokenisation           – split into individual tokens for per-token passes
5.  Per-token Alias Lookup – catch aliases not caught by phrase substitution
6.  Fuzzy Matching         – RapidFuzz to handle misspellings
7.  Duplicate Removal      – preserve insertion order
8.  Categorisation + JSON  – build the final response dict
"""

import logging
import re
from typing import Dict, List, Set

from rapidfuzz import fuzz, process

from config import FUZZY_THRESHOLD, MIN_FUZZY_TOKEN_LENGTH, MAX_FUZZY_TOKEN_LENGTH
from normalizer import clean_text, normalize_aliases_in_text, resolve_alias, tokenize
from skill_database import ALL_SKILLS, SKILL_CATEGORIES

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pre-computed lookup structures
# ---------------------------------------------------------------------------

_LOWER_TO_CANONICAL: Dict[str, str] = {s.lower(): s for s in ALL_SKILLS}
_FUZZY_CORPUS: List[str] = ALL_SKILLS


# ---------------------------------------------------------------------------
# Stage 3 – Exact match
# ---------------------------------------------------------------------------

def _build_skill_pattern(skill: str) -> re.Pattern:
    """
    Build a word-boundary regex for *skill* that handles special chars in
    names like C++, C#, Next.js correctly.

    We use (?<![\\w]) / (?![\\w]) style boundaries but only exclude
    alphanumeric/underscore on each side, NOT dots or plus signs (which
    are part of some skill names themselves).
    """
    escaped = re.escape(skill)
    # Lookbehind: not preceded by a word-char or dot or # or +
    lb = r"(?<![A-Za-z0-9_])"
    # Lookahead: not followed by a word-char (allow punctuation after skill)
    la = r"(?![A-Za-z0-9_])"
    return re.compile(lb + escaped + la, re.IGNORECASE)


# Pre-compile all skill patterns once at import time for performance
_SKILL_PATTERNS: List[tuple] = [
    (skill, _build_skill_pattern(skill))
    for skill in sorted(ALL_SKILLS, key=len, reverse=True)
]


def _exact_match_in_text(text: str) -> List[str]:
    """
    Return all canonical skills found verbatim (case-insensitive) in *text*.
    Longer skill names are checked first to avoid partial matches.
    """
    found: List[str] = []
    for skill, pattern in _SKILL_PATTERNS:
        if pattern.search(text):
            found.append(skill)
            logger.debug("Exact match: %r", skill)
    return found


# ---------------------------------------------------------------------------
# Stage 6 – Fuzzy match
# ---------------------------------------------------------------------------

def _fuzzy_match_token(token: str, already_found: Set[str]) -> List[str]:
    """
    Fuzzy-match *token* against the skill corpus using RapidFuzz.

    Strategy: try fuzz.ratio first (strict).  For tokens that look like they
    could be a misspelling of a longer skill (e.g. 'Postgress' vs 'PostgreSQL')
    also try fuzz.partial_ratio which ignores length difference.  A candidate
    is accepted if EITHER scorer meets the threshold.
    """
    if len(token) < MIN_FUZZY_TOKEN_LENGTH or len(token) > MAX_FUZZY_TOKEN_LENGTH:
        return []

    corpus = [s for s in _FUZZY_CORPUS if s not in already_found]

    # Primary scorer: strict ratio
    ratio_results = process.extract(token, corpus, scorer=fuzz.ratio, limit=5)
    # Secondary scorer: partial ratio (better when skill name is longer than token)
    partial_results = process.extract(token, corpus, scorer=fuzz.partial_ratio, limit=5)

    # Merge: take the best score for each candidate across both scorers
    candidate_scores: Dict[str, float] = {}
    for candidate, score, _ in ratio_results:
        candidate_scores[candidate] = max(candidate_scores.get(candidate, 0), score)
    for candidate, score, _ in partial_results:
        candidate_scores[candidate] = max(candidate_scores.get(candidate, 0), score)

    matched: List[str] = []
    for candidate, score in sorted(candidate_scores.items(), key=lambda x: -x[1]):
        if score >= FUZZY_THRESHOLD:
            logger.debug("Fuzzy match: %r → %r (best_score=%d)", token, candidate, score)
            matched.append(candidate)
    return matched


# ---------------------------------------------------------------------------
# Public extraction function
# ---------------------------------------------------------------------------

def extract_skills(transcript: str) -> Dict:
    """
    Run the full NLP pipeline on *transcript* and return a structured dict.

    Parameters
    ----------
    transcript : str
        Raw interview transcript text.

    Returns
    -------
    dict with keys: skills, categories, total_found
    """
    if not transcript or not transcript.strip():
        logger.warning("Empty transcript received.")
        return _build_response([])

    # ── Stage 1: Text Cleaning ─────────────────────────────────────────────
    cleaned = clean_text(transcript)
    logger.debug("Stage 1 – Cleaned: %r", cleaned[:120])

    # ── Stage 2: Alias Normalisation ───────────────────────────────────────
    # normalize_aliases_in_text lowercases the text and replaces alias phrases
    # with their canonical names (preserving canonical casing).
    # e.g. "amazon web services" → "AWS", "reactjs" → "React"
    alias_normalised = normalize_aliases_in_text(cleaned)
    logger.debug("Stage 2 – Alias-normalised: %r", alias_normalised[:120])

    # ── Stage 3: Exact Skill Matching on full text ─────────────────────────
    # Works on both the original cleaned text AND the alias-normalised text
    # to maximise coverage.
    exact_matches: List[str] = _exact_match_in_text(cleaned)
    exact_matches += _exact_match_in_text(alias_normalised)
    logger.debug("Stage 3 – Exact matches: %s", exact_matches)

    # ── Stage 4: Tokenisation ──────────────────────────────────────────────
    tokens_original = tokenize(cleaned)
    tokens_normalised = tokenize(alias_normalised)
    # Combine both token sets
    all_tokens = list(dict.fromkeys(tokens_original + tokens_normalised))  # dedup order-preserved
    logger.debug("Stage 4 – Tokens (%d): %s", len(all_tokens), all_tokens[:30])

    # ── Stage 5: Per-token alias lookup ────────────────────────────────────
    alias_matches: List[str] = []
    for token in all_tokens:
        resolved = resolve_alias(token)
        if resolved:
            alias_matches.append(resolved)
            logger.debug("Stage 5 – Token alias: %r → %r", token, resolved)

    # ── Stage 6: Fuzzy Matching ────────────────────────────────────────────
    known_so_far: Set[str] = set(exact_matches + alias_matches)
    fuzzy_matches: List[str] = []

    for token in all_tokens:
        # Skip tokens we already know about
        if resolve_alias(token) or token in known_so_far:
            continue
        fuzz_hits = _fuzzy_match_token(token, known_so_far | set(fuzzy_matches))
        fuzzy_matches.extend(fuzz_hits)

    logger.debug("Stage 6 – Fuzzy matches: %s", fuzzy_matches)

    # ── Stage 7: Merge & Deduplicate ──────────────────────────────────────
    all_found: List[str] = exact_matches + alias_matches + fuzzy_matches
    seen: Set[str] = set()
    deduped: List[str] = []
    for skill in all_found:
        if skill not in seen:
            seen.add(skill)
            deduped.append(skill)

    logger.info("Extraction complete – %d unique skills found.", len(deduped))

    # ── Stages 8 & 9: Categorisation + JSON ──────────────────────────────
    return _build_response(deduped)


def _build_response(skills: List[str]) -> Dict:
    """Build the final structured response dict."""
    categories: Dict[str, List[str]] = {}
    for skill in skills:
        category = SKILL_CATEGORIES.get(skill, "other")
        categories.setdefault(category, []).append(skill)

    return {
        "skills": skills,
        "categories": categories,
        "total_found": len(skills),
    }
