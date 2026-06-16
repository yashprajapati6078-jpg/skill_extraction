# Technical Skill Extractor

A production-ready Python microservice that extracts technical skills from interview transcripts using a multi-stage NLP pipeline: alias normalisation, exact matching, and fuzzy matching (RapidFuzz).

Part of the **AI Voice Interview System** — receives Whisper STT output and feeds structured skill data to the Evaluation Engine, Scoring System, Follow-up Question Generator, Summary Generator, and Feedback Generator.

---

## Features

- **58 canonical skills** across 5 categories (languages, frameworks, databases, cloud, DevOps)
- **Alias resolution** — `js` → `JavaScript`, `reactjs` → `React`, `amazon web services` → `AWS`, `k8s` → `Kubernetes`, and 80+ more
- **Fuzzy matching** — catches misspellings like `Pythn`, `Dockerr`, `Kuberenetes`, `Postgress` using RapidFuzz with dual-scorer strategy
- **Case-insensitive** — `PYTHON`, `python`, `Python` all return `Python`
- **Duplicate removal** — preserves insertion order, emits each skill once
- **Categorised output** — groups by `languages`, `frameworks`, `databases`, `cloud`, `devops`
- **FastAPI REST API** — interactive docs at `/docs`
- **100% test accuracy** on 20 realistic sample transcripts (77/77 expected skills found)
- **90 automated tests** across extraction, aliases, and fuzzy matching

---

## Quick Start

### 1. Clone and install

```bash
git clone <repo-url>
cd technical-skill-extractor
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the API server

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Extract skills

```bash
curl -X POST http://localhost:8000/extract-skills \
  -H "Content-Type: application/json" \
  -d '{"transcript": "I worked with Python, Django, MySQL, AWS and Docker."}'
```

**Response:**
```json
{
  "skills": ["Python", "Django", "MySQL", "AWS", "Docker"],
  "categories": {
    "languages": ["Python"],
    "frameworks": ["Django"],
    "databases": ["MySQL"],
    "cloud": ["AWS"],
    "devops": ["Docker"]
  },
  "total_found": 5
}
```

### 4. Run tests

```bash
python -m pytest tests/ -v
```

---

## API Reference

### `POST /extract-skills`

Extract technical skills from a transcript.

**Request body:**
```json
{ "transcript": "string (1–50,000 chars)" }
```

**Response:**
```json
{
  "skills": ["Python", "AWS"],
  "categories": {
    "languages": ["Python"],
    "cloud": ["AWS"]
  },
  "total_found": 2
}
```

| Field | Type | Description |
|---|---|---|
| `skills` | `string[]` | Deduplicated canonical skill names, insertion-order preserved |
| `categories` | `object` | Skills grouped by category |
| `total_found` | `integer` | Count of unique skills detected |

---

### `GET /health`

Liveness probe.

```json
{ "status": "ok", "version": "1.0.0" }
```

---

### `GET /skills`

List all 58 canonical skills grouped by category.

---

## Supported Skills

### Programming Languages (13)
Python, Java, JavaScript, TypeScript, C, C++, C#, Go, Rust, PHP, Ruby, Swift, Kotlin

### Frameworks & Libraries (13)
Django, Flask, FastAPI, React, Angular, Vue, Next.js, Express.js, Node.js, Spring Boot, Laravel, TensorFlow, PyTorch

### Databases (8)
MySQL, PostgreSQL, MongoDB, SQLite, Redis, Oracle, MariaDB, Cassandra

### Cloud Platforms (5)
AWS, Azure, GCP, Firebase, DigitalOcean

### DevOps & Tools (10)
Docker, Kubernetes, Git, GitHub, GitLab, Jenkins, Terraform, Ansible, Linux, Nginx

---

## Alias Examples

| Input | Resolved To |
|---|---|
| `js` | JavaScript |
| `javascript` | JavaScript |
| `reactjs` | React |
| `react js` | React |
| `nodejs` | Node.js |
| `node js` | Node.js |
| `amazon web services` | AWS |
| `google cloud` | GCP |
| `google cloud platform` | GCP |
| `k8s` | Kubernetes |
| `golang` | Go |
| `csharp` | C# |
| `c sharp` | C# |
| `cpp` | C++ |
| `postgres` | PostgreSQL |
| `mongo` | MongoDB |
| `tf` | TensorFlow |

---

## Misspelling Examples

| Input | Detected As |
|---|---|
| `Pythn` | Python |
| `Dockerr` | Docker |
| `Kuberenetes` | Kubernetes |
| `Postgress` | PostgreSQL |
| `Jangoo` | Django |
| `Ansibel` | Ansible |
| `Terrafrom` | Terraform |
| `Jenskins` | Jenkins |
| `Typescirpt` | TypeScript |

---

## Project Structure

```
technical-skill-extractor/
│
├── app.py               # FastAPI application, endpoints, middleware
├── extractor.py         # Core NLP pipeline (8-stage extraction engine)
├── normalizer.py        # Text cleaning, alias resolution, tokenisation
├── skill_database.py    # All canonical skills, categories, and alias map
├── models.py            # Pydantic request/response models
├── config.py            # Tunable constants (fuzzy threshold, log level, etc.)
├── requirements.txt     # Python dependencies
├── .gitignore
│
├── tests/
│   ├── test_extraction.py      # Core extraction, casing, dedup, categorisation
│   ├── test_aliases.py         # All alias resolution cases
│   ├── test_fuzzy_matching.py  # All misspelling detection cases
│   └── sample_transcripts.json # 20 realistic interview transcripts
│
├── docs/
│   └── architecture.md  # Pipeline design and module responsibilities
│
└── examples/
    └── api_examples.md  # curl and Python client examples
```

---

## Configuration

All tuneable values are in `config.py`:

| Setting | Default | Description |
|---|---|---|
| `FUZZY_THRESHOLD` | `85` | RapidFuzz minimum score (0–100) to accept a match |
| `MIN_FUZZY_TOKEN_LENGTH` | `4` | Minimum token length to attempt fuzzy matching |
| `MAX_FUZZY_TOKEN_LENGTH` | `40` | Maximum token length for fuzzy matching |
| `LOG_LEVEL` | `"INFO"` | Python logging level |
| `API_PORT` | `8000` | Server port |

---

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t skill-extractor .
docker run -p 8000:8000 skill-extractor
```

### Production (Gunicorn + Uvicorn workers)

```bash
pip install gunicorn
gunicorn app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | Override logging verbosity |

---

## Extending the Skill Set

To add a new skill, edit `skill_database.py` only:

```python
# 1. Add to SKILL_CATEGORIES
SKILL_CATEGORIES = {
    ...
    "Svelte": "frameworks",   # new skill
}

# 2. (Optional) Add aliases
ALIAS_MAP = {
    ...
    "sveltejs": "Svelte",
    "svelte js": "Svelte",
}
```

No other changes needed. The pipeline picks up new entries automatically at startup.

---

## Future Improvements

1. **Contextual extraction** — use a lightweight language model to distinguish skill mentions from false positives ("I worked on the Java team" vs "I use Java").
2. **Proficiency estimation** — parse surrounding words ("expert in", "beginner with", "5 years of") to estimate skill level.
3. **Version detection** — extract specific versions ("Python 3.11", "React 18").
4. **Custom skill lists** — accept a `custom_skills` array in the request body for domain-specific vocabularies.
5. **Confidence scores** — return a score for each detected skill indicating match type (exact / alias / fuzzy) and fuzzy similarity.
6. **Streaming transcripts** — WebSocket endpoint for real-time extraction as Whisper outputs chunks.
7. **Batch endpoint** — `POST /extract-skills/batch` accepting an array of transcripts.

---

## License

MIT
