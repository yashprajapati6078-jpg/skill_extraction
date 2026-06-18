"""
tests/test_extraction.py
------------------------
Pytest test suite validating the core extraction pipeline.
Covers basic detection, case-insensitivity, duplicates, and categorised output.
"""

import json
import sys
from pathlib import Path

import pytest

# Make the project root importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from extractor import extract_skills


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def skills_set(result: dict) -> set:
    """Return the skills list as a set for order-insensitive comparison."""
    return set(result["skills"])


# ---------------------------------------------------------------------------
# Basic detection
# ---------------------------------------------------------------------------

class TestBasicExtraction:
    def test_single_language(self):
        result = extract_skills("I work with Python.")
        assert "Python" in result["skills"]

    def test_multiple_languages(self):
        result = extract_skills("I use Python, Java, and Go.")
        found = skills_set(result)
        assert {"Python", "Java", "Go"}.issubset(found)

    def test_framework_detection(self):
        result = extract_skills("The backend uses Django and FastAPI.")
        found = skills_set(result)
        assert {"Django", "FastAPI"}.issubset(found)

    def test_database_detection(self):
        result = extract_skills("We store data in PostgreSQL and Redis.")
        found = skills_set(result)
        assert {"PostgreSQL", "Redis"}.issubset(found)

    def test_cloud_detection(self):
        result = extract_skills("We deploy on AWS and Azure.")
        found = skills_set(result)
        assert {"AWS", "Azure"}.issubset(found)

    def test_devops_detection(self):
        result = extract_skills("We use Docker and Kubernetes for deployment.")
        found = skills_set(result)
        assert {"Docker", "Kubernetes"}.issubset(found)

    def test_no_skills(self):
        result = extract_skills("I enjoy long walks and cooking pasta.")
        assert result["skills"] == []
        assert result["total_found"] == 0

    def test_empty_transcript(self):
        result = extract_skills("")
        assert result["skills"] == []

    def test_whitespace_only(self):
        result = extract_skills("   \n\t  ")
        assert result["skills"] == []


# ---------------------------------------------------------------------------
# Case insensitivity
# ---------------------------------------------------------------------------

class TestCaseInsensitivity:
    def test_uppercase(self):
        result = extract_skills("I use PYTHON and DOCKER.")
        assert "Python" in result["skills"]
        assert "Docker" in result["skills"]

    def test_lowercase(self):
        result = extract_skills("I use python and docker.")
        assert "Python" in result["skills"]
        assert "Docker" in result["skills"]

    def test_mixed_case(self):
        result = extract_skills("PyThOn and DJANGO and mongoDB.")
        found = skills_set(result)
        assert "Python" in found
        assert "Django" in found
        assert "MongoDB" in found

    def test_returns_canonical_casing(self):
        """Ensure output always uses proper canonical capitalisation."""
        result = extract_skills("typescript and nextjs and postgresql")
        for skill in result["skills"]:
            # Skills should never be all-lowercase in the output
            assert skill[0].isupper() or skill in {"C", "C++", "C#", "Go"}


# ---------------------------------------------------------------------------
# Duplicate removal
# ---------------------------------------------------------------------------

class TestDuplicateRemoval:
    def test_duplicate_skills(self):
        result = extract_skills("Python Python AWS AWS Docker Docker")
        assert result["skills"].count("Python") == 1
        assert result["skills"].count("AWS") == 1
        assert result["skills"].count("Docker") == 1

    def test_alias_and_canonical_dedup(self):
        """Alias 'js' and 'JavaScript' in same sentence → only one entry."""
        result = extract_skills("I know js and also JavaScript very well.")
        assert result["skills"].count("JavaScript") == 1

    def test_total_found_matches_unique_skills(self):
        result = extract_skills("Python Python Python Java Java")
        assert result["total_found"] == len(result["skills"])


# ---------------------------------------------------------------------------
# Categorised output
# ---------------------------------------------------------------------------

class TestCategorisation:
    def test_language_category(self):
        result = extract_skills("I code in Python and Java.")
        assert "Python" in result["categories"].get("languages", [])
        assert "Java" in result["categories"].get("languages", [])

    def test_framework_category(self):
        result = extract_skills("I use Django and React.")
        assert "Django" in result["categories"].get("frameworks", [])
        assert "React" in result["categories"].get("frameworks", [])

    def test_database_category(self):
        result = extract_skills("I store data in MySQL and MongoDB.")
        assert "MySQL" in result["categories"].get("databases", [])
        assert "MongoDB" in result["categories"].get("databases", [])

    def test_cloud_category(self):
        result = extract_skills("Our cloud providers are AWS and GCP.")
        assert "AWS" in result["categories"].get("cloud", [])
        assert "GCP" in result["categories"].get("cloud", [])

    def test_devops_category(self):
        result = extract_skills("We use Docker, Kubernetes, and Terraform.")
        devops = result["categories"].get("devops", [])
        assert "Docker" in devops
        assert "Kubernetes" in devops
        assert "Terraform" in devops

    def test_multi_category_response(self):
        result = extract_skills("Python with Django on AWS using Docker.")
        cats = result["categories"]
        assert "languages" in cats
        assert "frameworks" in cats
        assert "cloud" in cats
        assert "devops" in cats


# ---------------------------------------------------------------------------
# Sample transcripts – batch accuracy test
# ---------------------------------------------------------------------------

class TestSampleTranscripts:
    """
    Load the 20 sample transcripts and verify that all expected skills
    are detected.  This gives an overall accuracy measurement.
    """

    @pytest.fixture(scope="class")
    def transcripts(self):
        path = Path(__file__).parent / "sample_transcripts.json"
        with open(path) as f:
            return json.load(f)

    def test_all_samples_pass_threshold(self, transcripts):
        total_expected = 0
        total_found = 0
        failures = []

        for sample in transcripts:
            result = extract_skills(sample["transcript"])
            found = set(result["skills"])
            expected = set(sample["expected_skills"])

            total_expected += len(expected)
            hits = expected & found
            total_found += len(hits)

            missing = expected - found
            if missing:
                failures.append(
                    f"[Sample {sample['id']}] {sample['description']}: "
                    f"Missing {missing}"
                )

        accuracy = total_found / total_expected if total_expected else 0
        print(f"\nOverall accuracy: {accuracy:.1%}  ({total_found}/{total_expected})")

        if failures:
            print("\nFailures:")
            for f in failures:
                print(" ", f)

        assert accuracy >= 0.85, (
            f"Accuracy {accuracy:.1%} is below the 85% target.\n"
            + "\n".join(failures)
        )

    def test_sample_1_basic_languages(self, transcripts):
        sample = next(s for s in transcripts if s["id"] == 1)
        result = extract_skills(sample["transcript"])
        assert "Python" in result["skills"]
        assert "Java" in result["skills"]

    def test_sample_8_duplicates(self, transcripts):
        sample = next(s for s in transcripts if s["id"] == 8)
        result = extract_skills(sample["transcript"])
        assert result["skills"].count("Python") == 1
        assert result["skills"].count("AWS") == 1

    def test_sample_9_long_answer(self, transcripts):
        sample = next(s for s in transcripts if s["id"] == 9)
        result = extract_skills(sample["transcript"])
        found = set(result["skills"])
        expected = set(sample["expected_skills"])
        # Allow one miss in a long transcript
        assert len(expected - found) <= 1
