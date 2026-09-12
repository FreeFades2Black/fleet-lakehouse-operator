import os
import json
import pytest
import subprocess

def test_applicationset_structure():
    p = os.path.join(os.path.dirname(__file__), "..", "argocd", "applicationset-fleet-matrix.yaml")
    assert os.path.exists(p), "ApplicationSet manifest must exist"
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    assert "RollingSync" in content
    assert "ring-0-canary" in content
    assert "ring-1-core" in content
    assert "ring-2-airgap" in content
    assert "matrix:" in content

def test_50_cluster_inventory():
    clusters_dir = os.path.join(os.path.dirname(__file__), "..", "argocd", "clusters")
    files = [f for f in os.listdir(clusters_dir) if f.endswith(".json")]
    assert len(files) == 50, f"Expected 50 cluster manifests, found {len(files)}"
    
    rings = {"ring-0-canary": 0, "ring-1-core": 0, "ring-2-airgap": 0}
    for f in files:
        with open(os.path.join(clusters_dir, f), "r", encoding="utf-8") as jf:
            data = json.load(jf)
            assert "siteId" in data
            assert "server" in data
            ring = data["labels"]["ring"]
            assert ring in rings
            rings[ring] += 1
            
    assert rings["ring-0-canary"] == 2
    assert rings["ring-1-core"] == 23
    assert rings["ring-2-airgap"] == 25

def test_helm_chart_and_values():
    helm_dir = os.path.join(os.path.dirname(__file__), "..", "helm", "lakehouse-substrate")
    assert os.path.exists(os.path.join(helm_dir, "Chart.yaml"))
    assert os.path.exists(os.path.join(helm_dir, "values.yaml"))
    assert os.path.exists(os.path.join(helm_dir, "templates", "kafka", "kafka-cluster.yaml"))
    assert os.path.exists(os.path.join(helm_dir, "templates", "compute", "trino.yaml"))
    assert os.path.exists(os.path.join(helm_dir, "templates", "catalog", "nessie.yaml"))

def test_kyverno_ironbank_policies():
    p = os.path.join(os.path.dirname(__file__), "..", "security", "kyverno", "dod-ironbank-baseline.yaml")
    assert os.path.exists(p)
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    assert "require-run-as-non-root" in content
    assert "require-read-only-rootfs" in content
    assert "disallow-privilege-escalation" in content

def test_delivery_cli_harness():
    cli_path = os.path.join(os.path.dirname(__file__), "..", "delivery-cli", "delivery_cli.py")
    res = subprocess.run(["python", cli_path, "--cluster-context", "ring0-canary", "--verify-all", "--json"], capture_output=True, text=True)
    assert res.returncode == 0, f"Delivery CLI failed: {res.stderr}"
    data = json.loads(res.stdout)
    assert data["siteId"] == "ring0-canary"
    assert data["overallStatus"] == "PASSED"
    assert "pvc_bind_latency_ms" in data["metrics"]
    assert "synthetic_query_duration_s" in data["metrics"]

def test_kind_cluster_config():
    p = os.path.join(os.path.dirname(__file__), "kind-ring0-config.yaml")
    assert os.path.exists(p)
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    assert "name: ring0-canary" in content
    assert "role: control-plane" in content
    assert "role: worker" in content
    assert "ring=ring-0-canary" in content

def test_dockerfile_and_packaging():
    dockerfile = os.path.join(os.path.dirname(__file__), "..", "delivery-cli", "Dockerfile")
    requirements = os.path.join(os.path.dirname(__file__), "..", "delivery-cli", "requirements.txt")
    assert os.path.exists(dockerfile)
    assert os.path.exists(requirements)
    with open(dockerfile, "r", encoding="utf-8") as f:
        df_content = f.read()
    assert "FROM cgr.dev/chainguard/python:latest-dev AS builder" in df_content
    assert "USER 65532:65532" in df_content
    assert "ENTRYPOINT" in df_content

def test_ci_workflows():
    e2e = os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "e2e-canary.yml")
    pkg = os.path.join(os.path.dirname(__file__), "..", ".github", "workflows", "package-oci.yml")
    assert os.path.exists(e2e)
    assert os.path.exists(pkg)

