"""
skill_database.py
-----------------
Central registry of all known technical skills, their canonical names,
aliases, and category assignments.

This is the single source of truth that every other module references.
"""

from typing import Dict, List

# ---------------------------------------------------------------------------
# Canonical skill name  →  category
# ---------------------------------------------------------------------------
SKILL_CATEGORIES: Dict[str, str] = {
    # Programming Languages
    "Python": "languages",
    "Java": "languages",
    "JavaScript": "languages",
    "TypeScript": "languages",
    "C": "languages",
    "C++": "languages",
    "C#": "languages",
    "Go": "languages",
    "Rust": "languages",
    "PHP": "languages",
    "Ruby": "languages",
    "Swift": "languages",
    "Kotlin": "languages",
    # Frameworks & Libraries
    "Django": "frameworks",
    "Flask": "frameworks",
    "FastAPI": "frameworks",
    "React": "frameworks",
    "Angular": "frameworks",
    "Vue": "frameworks",
    "Next.js": "frameworks",
    "Express.js": "frameworks",
    "Node.js": "frameworks",
    "Spring Boot": "frameworks",
    "Laravel": "frameworks",
    "TensorFlow": "frameworks",
    "PyTorch": "frameworks",
    # Databases
    "MySQL": "databases",
    "PostgreSQL": "databases",
    "MongoDB": "databases",
    "SQLite": "databases",
    "Redis": "databases",
    "Oracle": "databases",
    "MariaDB": "databases",
    "Cassandra": "databases",
    # Cloud Platforms
    "AWS": "cloud",
    "Azure": "cloud",
    "GCP": "cloud",
    "Firebase": "cloud",
    "DigitalOcean": "cloud",
    # DevOps & Tools
    "Docker": "devops",
    "Kubernetes": "devops",
    "Git": "devops",
    "GitHub": "devops",
    "GitLab": "devops",
    "Jenkins": "devops",
    "Terraform": "devops",
    "Ansible": "devops",
    "Linux": "devops",
    "Nginx": "devops",
}

# All canonical skill names (convenience list)
ALL_SKILLS: List[str] = list(SKILL_CATEGORIES.keys())

# ---------------------------------------------------------------------------
# Alias map: lowercased alias  →  canonical name
# Covers abbreviations, alternate spellings, colloquial names, and expansions.
# ---------------------------------------------------------------------------
ALIAS_MAP: Dict[str, str] = {
    # JavaScript variants
    "js": "JavaScript",
    "javascript": "JavaScript",
    "java script": "JavaScript",
    # TypeScript variants
    "ts": "TypeScript",
    "typescript": "TypeScript",
    # Node.js variants
    "nodejs": "Node.js",
    "node js": "Node.js",
    "node.js": "Node.js",
    "node": "Node.js",
    # React variants
    "reactjs": "React",
    "react js": "React",
    "react.js": "React",
    "react native": "React",  # treat as React (closest canonical)
    # Next.js variants
    "nextjs": "Next.js",
    "next js": "Next.js",
    "next.js": "Next.js",
    # Express variants
    "expressjs": "Express.js",
    "express js": "Express.js",
    "express.js": "Express.js",
    "express": "Express.js",
    # Vue variants
    "vuejs": "Vue",
    "vue js": "Vue",
    "vue.js": "Vue",
    # Angular variants
    "angularjs": "Angular",
    "angular js": "Angular",
    # Django variants
    "django": "Django",
    # Flask variants
    "flask": "Flask",
    # FastAPI variants
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    # Spring Boot variants
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    # Laravel variants
    "laravel": "Laravel",
    # TensorFlow variants
    "tensorflow": "TensorFlow",
    "tensor flow": "TensorFlow",
    "tf": "TensorFlow",
    # PyTorch variants
    "pytorch": "PyTorch",
    "py torch": "PyTorch",
    "torch": "PyTorch",
    # AWS variants
    "aws": "AWS",
    "amazon web services": "AWS",
    "amazon aws": "AWS",
    # Azure variants
    "azure": "Azure",
    "microsoft azure": "Azure",
    # GCP variants
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "google cloud services": "GCP",
    # Firebase variants
    "firebase": "Firebase",
    # DigitalOcean variants
    "digitalocean": "DigitalOcean",
    "digital ocean": "DigitalOcean",
    "do": "DigitalOcean",
    # Docker variants
    "docker": "Docker",
    # Kubernetes variants
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "kube": "Kubernetes",
    # Git variants
    "git": "Git",
    # GitHub variants
    "github": "GitHub",
    "git hub": "GitHub",
    # GitLab variants
    "gitlab": "GitLab",
    "git lab": "GitLab",
    # Jenkins variants
    "jenkins": "Jenkins",
    # Terraform variants
    "terraform": "Terraform",
    "tf (infra)": "Terraform",
    # Ansible variants
    "ansible": "Ansible",
    # Linux variants
    "linux": "Linux",
    "ubuntu": "Linux",
    "centos": "Linux",
    "debian": "Linux",
    # Nginx variants
    "nginx": "Nginx",
    # Python variants
    "python": "Python",
    "python3": "Python",
    "py": "Python",
    # Java variants
    "java": "Java",
    # Go variants
    "go": "Go",
    "golang": "Go",
    "go lang": "Go",
    # Rust variants
    "rust": "Rust",
    "rustlang": "Rust",
    # C variants
    "c": "C",
    "c language": "C",
    # C++ variants
    "c++": "C++",
    "cpp": "C++",
    "c plus plus": "C++",
    # C# variants
    "c#": "C#",
    "csharp": "C#",
    "c sharp": "C#",
    # PHP variants
    "php": "PHP",
    # Ruby variants
    "ruby": "Ruby",
    # Swift variants
    "swift": "Swift",
    # Kotlin variants
    "kotlin": "Kotlin",
    # Database variants
    "mysql": "MySQL",
    "my sql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "post gres": "PostgreSQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "mongo db": "MongoDB",
    "sqlite": "SQLite",
    "sql lite": "SQLite",
    "redis": "Redis",
    "oracle": "Oracle",
    "oracle db": "Oracle",
    "mariadb": "MariaDB",
    "maria db": "MariaDB",
    "cassandra": "Cassandra",
    "apache cassandra": "Cassandra",
    # TypeScript
    "typescript": "TypeScript",
    "typescirpt": "TypeScript",
    "typscript": "TypeScript",
    "tyepscript": "TypeScript",
}
