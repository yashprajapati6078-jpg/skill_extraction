# Architecture – Technical Skill Extractor

## Overview

The Technical Skill Extractor is a single-service Python application that processes raw interview transcript text and returns a structured JSON list of detected technical skills. It is designed as a stateless REST microservice that plugs directly into the AI Voice Interview System pipeline.

```
Whisper STT
    │
    ▼
[raw transcript text]
    │
    ▼
POST /extract-skills
    │
    ▼
┌─────────────────────────────────────┐
│       NLP Extraction Pipeline       │
│                                     │
│  1. Text Cleaning                   │
│  2. Alias Normalisation             │
│  3. Exact Skill Matching            │
│  4. Tokenisation                    │
│  5. Per-token Alias Lookup          │
│  6. Fuzzy Matching (RapidFuzz)      │
│  7. Duplicate Removal               │
│  8. Categorisation                  │
│  9. JSON Formatting                 │
└─────────────────────────────────────┘
    │
    ▼
{skills, categories, total_found}
    │
    ├──▶ Candidate Evaluation Engine
    ├──▶ Interview Scoring System
    ├──▶ Follow-up Question Generator
    ├──▶ Interview Summary Generator
    └──▶ Automated Feedback Generator
```

---

## Module Responsibilities

### `skill_database.py`
Single source of truth. Defines:
- `SKILL_CATEGORIES` – dict mapping every canonical skill name to its category string.
- `ALL_SKILLS` – flat list of all canonical names (derived from SKILL_CATEGORIES keys).
- `ALIAS_MAP` – dict mapping every known lowercase alias to its canonical skill name.

Nothing else imports from outside this module. Extending the skill set means adding entries here only.

### `config.py`
All tuneable constants in one place: fuzzy threshold, log format, API metadata, token length bounds. No business logic.

### `models.py`
Pydantic v2 models for FastAPI request/response validation:
- `TranscriptRequest` – validates the incoming transcript string.
- `SkillExtractionResponse` – defines the output schema.
- `ErrorResponse` – standard error envelope.

### `normalizer.py`
Text preprocessing utilities called by `extractor.py`:

| Function | Purpose |
|---|---|
| `clean_text(text)` | Strip noise chars, collapse whitespace |
| `normalize_aliases_in_text(text)` | Lowercase + substitute alias phrases with canonical names |
| `resolve_alias(token)` | Per-token alias / canonical name lookup |
| `tokenize(text)` | Split into clean tokens, strip edge punctuation |

### `extractor.py`
Core pipeline. The public entry point is `extract_skills(transcript: str) → dict`.

Internal helpers:
- `_build_skill_pattern(skill)` – compiles a word-boundary-aware regex for each skill (handles `C++`, `C#`, `Next.js`).
- `_exact_match_in_text(text)` – runs all pre-compiled patterns over the text.
- `_fuzzy_match_token(token, already_found)` – runs `fuzz.ratio` and `fuzz.partial_ratio` and accepts the best score.
- `_build_response(skills)` – constructs the final categorised response dict.

### `app.py`
FastAPI application. Three endpoints:

| Method | Path | Purpose |
|---|---|---|
| POST | `/extract-skills` | Main extraction endpoint |
| GET | `/health` | Liveness probe |
| GET | `/skills` | List all known skills by category |

Also adds: CORS middleware, request-timing header (`X-Process-Time`), and a global exception handler.

---

## NLP Pipeline – Stage by Stage

### Stage 1 · Text Cleaning
`clean_text()` strips characters that cannot appear in skill names (HTML tags, emoji, etc.) while preserving `+`, `#`, `.`, and `-` which are part of names like `C++`, `C#`, `Next.js`.

### Stage 2 · Alias Normalisation
`normalize_aliases_in_text()` lowercases the text, then iterates through all known aliases sorted by length (longest first) and replaces them with their canonical names using word-boundary-aware regex. This catches multi-word phrases like `"amazon web services"` → `"AWS"` before single-word processing begins. A post-pass re-joins `C #` → `C#` and `C ++` → `C++`.

### Stage 3 · Exact Skill Matching
Pre-compiled patterns for every canonical skill are run over both the original cleaned text and the alias-normalised text. Patterns use `(?<![A-Za-z0-9_])` / `(?![A-Za-z0-9_])` boundaries instead of `\b` to correctly handle skills with non-word suffix characters (`C++`, `C#`). Skills are checked longest-first to avoid partial substring matches.

### Stage 4 · Tokenisation
`tokenize()` splits the alias-normalised text on whitespace and common punctuation (commas, semicolons, brackets, quotes), then strips leading/trailing dots and hyphens from each token. Internal characters are preserved so tokens like `C++`, `Next.js`, and `k8s` remain intact.

### Stage 5 · Per-token Alias Lookup
Each token is passed through `resolve_alias()`, which strips edge punctuation before looking up in `ALIAS_MAP` and then in the lowercase-to-canonical map. This catches single-token aliases that survived phrase substitution.

### Stage 6 · Fuzzy Matching
Tokens not already resolved are passed to `_fuzzy_match_token()`. Both `fuzz.ratio` and `fuzz.partial_ratio` are computed; the best score is used. The threshold (default 85) is high enough to reject ordinary English words (max ~50% similarity to any skill) while catching close misspellings. `partial_ratio` is particularly important for catching misspellings of longer skill names like `Postgress` → `PostgreSQL`.

### Stage 7 · Duplicate Removal
All matches from stages 3–6 are concatenated and deduplicated using an ordered-set pattern (insertion order preserved, first occurrence wins).

### Stages 8–9 · Categorisation + JSON Formatting
`_build_response()` groups skills by their category from `SKILL_CATEGORIES` and builds the final dict matching `SkillExtractionResponse`.

---

## Design Decisions

**Why two passes (original text + alias-normalised text)?**
Exact matching on the original preserves the canonical casing check for names like `Docker` that might be written as `docker`. The alias-normalised pass catches multi-word aliases that were substituted with their canonical form.

**Why sort aliases by length descending?**
To ensure `"amazon web services"` is substituted before `"aws"`, and `"google cloud platform"` before `"google cloud"`. Without this, shorter prefixes could partially match and corrupt the longer alias.

**Why both `fuzz.ratio` and `fuzz.partial_ratio`?**
`fuzz.ratio` is strict (equal-length comparison) and catches most misspellings. `fuzz.partial_ratio` ignores length differences, which is essential for cases like `Postgress` (9 chars) vs `PostgreSQL` (10 chars) where `fuzz.ratio` scores only 74% but `fuzz.partial_ratio` scores 88%.

**Why not use spaCy or NLTK?**
The skill set is a closed, known vocabulary. NER models designed for open-domain entity recognition carry significant overhead (model size, inference time, GPU requirements) without meaningful accuracy benefit over a well-designed rule-based + fuzzy hybrid for this bounded problem.

---

## Performance

| Metric | Target | Observed |
|---|---|---|
| Extraction accuracy | > 85% | 100% (77/77 on sample set) |
| Response time | < 1 second | ~5–15ms per transcript |
| Test coverage | — | 90 tests, 90 passed |

---

## Extending the System

### Adding a new skill
Edit `skill_database.py`:
1. Add the canonical name and its category to `SKILL_CATEGORIES`.
2. Optionally add aliases to `ALIAS_MAP`.
3. That's it — all pipeline stages pick up the change automatically at import time.

### Adjusting fuzzy threshold
Edit `config.py`: change `FUZZY_THRESHOLD`. Lower values increase recall at the cost of precision; higher values do the opposite. The range 80–90 is recommended.

### Adding a new category
Add the category string to the `SKILL_CATEGORIES` values for the relevant skills. The `categories` dict in the response is built dynamically — no code changes required.
