"""
tests/test_aliases.py
---------------------
Pytest test suite for alias normalisation.
Verifies that every defined alias returns its canonical skill name.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from extractor import extract_skills


class TestJavaScriptAliases:
    def test_js(self):
        assert "JavaScript" in extract_skills("I use js for the frontend.")["skills"]

    def test_javascript_lowercase(self):
        assert "JavaScript" in extract_skills("javascript is my primary language.")["skills"]

    def test_java_script_spaced(self):
        assert "JavaScript" in extract_skills("I love java script.")["skills"]


class TestNodejsAliases:
    def test_nodejs_no_dot(self):
        assert "Node.js" in extract_skills("nodejs powers our API.")["skills"]

    def test_node_js_spaced(self):
        assert "Node.js" in extract_skills("I use node js for microservices.")["skills"]

    def test_node_bare(self):
        assert "Node.js" in extract_skills("I run the server on node.")["skills"]


class TestReactAliases:
    def test_reactjs(self):
        assert "React" in extract_skills("Our SPA is built in reactjs.")["skills"]

    def test_react_js_spaced(self):
        assert "React" in extract_skills("I chose react js for this project.")["skills"]


class TestAWSAliases:
    def test_amazon_web_services(self):
        assert "AWS" in extract_skills("We run workloads on amazon web services.")["skills"]

    def test_aws_uppercase(self):
        assert "AWS" in extract_skills("AWS Lambda handles our events.")["skills"]

    def test_amazon_aws(self):
        assert "AWS" in extract_skills("amazon aws is our primary cloud.")["skills"]


class TestGCPAliases:
    def test_google_cloud(self):
        assert "GCP" in extract_skills("We migrated to google cloud.")["skills"]

    def test_google_cloud_platform(self):
        assert "GCP" in extract_skills("google cloud platform hosts our GKE clusters.")["skills"]

    def test_gcp_bare(self):
        assert "GCP" in extract_skills("gcp bills by the second.")["skills"]


class TestGoAliases:
    def test_golang(self):
        assert "Go" in extract_skills("I write backend services in golang.")["skills"]

    def test_go_lang_spaced(self):
        assert "Go" in extract_skills("I prefer go lang over Rust for CLIs.")["skills"]


class TestKubernetesAliases:
    def test_k8s(self):
        assert "Kubernetes" in extract_skills("We scale pods on k8s.")["skills"]

    def test_kube(self):
        assert "Kubernetes" in extract_skills("kube manages our cluster autoscaling.")["skills"]


class TestCSharpAliases:
    def test_csharp(self):
        assert "C#" in extract_skills("I build .NET apps in csharp.")["skills"]

    def test_c_sharp_spaced(self):
        assert "C#" in extract_skills("c sharp is used for Unity development.")["skills"]


class TestCppAliases:
    def test_cpp(self):
        assert "C++" in extract_skills("Low-level code is written in cpp.")["skills"]

    def test_c_plus_plus(self):
        assert "C++" in extract_skills("c plus plus for game engine internals.")["skills"]


class TestPythonAliases:
    def test_python3(self):
        assert "Python" in extract_skills("All scripts run on python3.")["skills"]

    def test_py_alias(self):
        # "py" is short; ensure it maps correctly
        assert "Python" in extract_skills("I script in py.")["skills"]


class TestAzureAliases:
    def test_microsoft_azure(self):
        assert "Azure" in extract_skills("We use microsoft azure for hosting.")["skills"]


class TestDockerAliases:
    def test_docker_canonical(self):
        assert "Docker" in extract_skills("Containers are built with Docker.")["skills"]


class TestPostgreSQLAliases:
    def test_postgres(self):
        assert "PostgreSQL" in extract_skills("We use postgres as our primary DB.")["skills"]

    def test_post_gres_spaced(self):
        assert "PostgreSQL" in extract_skills("post gres handles relational data.")["skills"]


class TestMongoAliases:
    def test_mongo(self):
        assert "MongoDB" in extract_skills("mongo stores our documents.")["skills"]

    def test_mongo_db_spaced(self):
        assert "MongoDB" in extract_skills("I prefer mongo db for flexible schemas.")["skills"]


class TestTensorFlowAliases:
    def test_tf(self):
        assert "TensorFlow" in extract_skills("I train models with tf.")["skills"]

    def test_tensor_flow_spaced(self):
        assert "TensorFlow" in extract_skills("tensor flow is excellent for production ML.")["skills"]


class TestNextjsAliases:
    def test_nextjs_no_dot(self):
        assert "Next.js" in extract_skills("SSR is handled by nextjs.")["skills"]

    def test_next_js_spaced(self):
        assert "Next.js" in extract_skills("I use next js for SEO-optimised pages.")["skills"]


class TestExpressAliases:
    def test_expressjs(self):
        assert "Express.js" in extract_skills("The API is built with expressjs.")["skills"]

    def test_express_bare(self):
        assert "Express.js" in extract_skills("express handles routing in our backend.")["skills"]
