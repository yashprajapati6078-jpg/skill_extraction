# API Examples

## Base URL

```
http://localhost:8000
```

---

## POST /extract-skills

### Example 1 – Basic skill extraction

**Request**
```bash
curl -X POST http://localhost:8000/extract-skills \
  -H "Content-Type: application/json" \
  -d '{"transcript": "I have experience with Python, Django, MySQL, AWS and Docker."}'
```

**Response**
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

---

### Example 2 – Alias resolution

**Request**
```bash
curl -X POST http://localhost:8000/extract-skills \
  -H "Content-Type: application/json" \
  -d '{"transcript": "I use js, reactjs, and amazon web services."}'
```

**Response**
```json
{
  "skills": ["JavaScript", "React", "AWS"],
  "categories": {
    "languages": ["JavaScript"],
    "frameworks": ["React"],
    "cloud": ["AWS"]
  },
  "total_found": 3
}
```

---

### Example 3 – Misspelling correction

**Request**
```bash
curl -X POST http://localhost:8000/extract-skills \
  -H "Content-Type: application/json" \
  -d '{"transcript": "I work with Pythn and Dockerr daily."}'
```

**Response**
```json
{
  "skills": ["Python", "Docker"],
  "categories": {
    "languages": ["Python"],
    "devops": ["Docker"]
  },
  "total_found": 2
}
```

---

### Example 4 – Long interview answer

**Request**
```bash
curl -X POST http://localhost:8000/extract-skills \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Over my five years as a backend engineer I have worked primarily with Python and Go. I use FastAPI and Flask for building REST APIs, PostgreSQL and Redis for data persistence, Docker and Kubernetes for containerisation, and deploy everything on AWS using Terraform. All our CI/CD runs through Jenkins and GitHub Actions."
  }'
```

**Response**
```json
{
  "skills": ["Python", "Go", "FastAPI", "Flask", "PostgreSQL", "Redis", "Docker", "Kubernetes", "AWS", "Terraform", "Jenkins", "GitHub"],
  "categories": {
    "languages": ["Python", "Go"],
    "frameworks": ["FastAPI", "Flask"],
    "databases": ["PostgreSQL", "Redis"],
    "devops": ["Docker", "Kubernetes", "Terraform", "Jenkins", "GitHub"],
    "cloud": ["AWS"]
  },
  "total_found": 12
}
```

---

### Example 5 – Mixed casing and duplicates

**Request**
```bash
curl -X POST http://localhost:8000/extract-skills \
  -H "Content-Type: application/json" \
  -d '{"transcript": "PYTHON is my main language. I also use python for scripts. AWS and aws are my cloud platforms."}'
```

**Response**
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

---

## GET /health

**Request**
```bash
curl http://localhost:8000/health
```

**Response**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

## GET /skills

**Request**
```bash
curl http://localhost:8000/skills
```

**Response** (abbreviated)
```json
{
  "total": 58,
  "categories": {
    "languages": ["Python", "Java", "JavaScript", "TypeScript", "C", "C++", "C#", "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin"],
    "frameworks": ["Django", "Flask", "FastAPI", "React", "Angular", "Vue", "Next.js", "Express.js", "Node.js", "Spring Boot", "Laravel", "TensorFlow", "PyTorch"],
    "databases": ["MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Oracle", "MariaDB", "Cassandra"],
    "cloud": ["AWS", "Azure", "GCP", "Firebase", "DigitalOcean"],
    "devops": ["Docker", "Kubernetes", "Git", "GitHub", "GitLab", "Jenkins", "Terraform", "Ansible", "Linux", "Nginx"]
  }
}
```

---

## Python client example

```python
import httpx

client = httpx.Client(base_url="http://localhost:8000")

response = client.post("/extract-skills", json={
    "transcript": "I build microservices with Go and deploy them on Kubernetes using Helm charts. "
                  "Data lives in PostgreSQL and we cache with Redis. "
                  "Our CI/CD pipeline runs on GitLab."
})

data = response.json()
print("Skills found:", data["skills"])
print("Languages:", data["categories"].get("languages", []))
print("DevOps:", data["categories"].get("devops", []))
```

---

## Interactive docs

With the server running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
