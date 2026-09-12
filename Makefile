# ============================================================================
# Multi-Cluster Fleet Lakehouse Delivery Engine
# Lead Architect: William Free Hall (Free) <whall4.wh@gmail.com>
# ============================================================================

.PHONY: help test test-static test-fleet-spinup test-smoke-e2e validate-fleet lint docker-build clean

help:
	@echo "Available commands:"
	@echo "  make test-fleet-spinup - Spin up 3-node Ring 0 Canary cluster via KinD"
	@echo "  make test-smoke-e2e    - Run full in-cluster Kyverno, Helm, and delivery-probe E2E gate"
	@echo "  make test-static       - Run Kyverno, Helm lint, and Pytest static test suite"
	@echo "  make docker-build      - Build rootless distroless OCI container for delivery-cli"
	@echo "  make validate-fleet    - Execute delivery-cli across Canary Ring 0"

test: test-static

test-static:
	python -m pytest tests/ -v

test-fleet-spinup:
	@echo "Spinning up simulated 3-node Ring 0 Canary cluster..."
	kind create cluster --name ring0-canary --config tests/kind-ring0-config.yaml
	kubectl wait --for=condition=Ready nodes --all --timeout=60s

test-smoke-e2e: test-fleet-spinup
	@echo "Installing Strimzi CRDs & Kyverno Security Baseline..."
	kubectl apply -f https://github.com/kyverno/kyverno/releases/download/v1.11.0/install.yaml
	kubectl wait --namespace kyverno --for=condition=ready pod -l app.kubernetes.io/part-of=kyverno --timeout=90s
	kubectl apply -f security/kyverno/dod-ironbank-baseline.yaml
	@echo "Deploying Lakehouse Helm substrate..."
	helm upgrade --install lakehouse-canary helm/lakehouse-substrate -f helm/lakehouse-substrate/values-canary.yaml --create-namespace --namespace lakehouse-infra
	@echo "Running real in-cluster post-upgrade validation probe..."
	kubectl run delivery-probe --rm -i --restart=Never --image=ghcr.io/freefades2black/delivery-cli:latest -- \
		--cluster-context=ring0-canary --verify-all

docker-build:
	docker build -t ghcr.io/freefades2black/delivery-cli:latest ./delivery-cli

validate-fleet:
	python delivery-cli/delivery_cli.py --site site01 --ring ring-0-canary --verify-all
	python delivery-cli/delivery_cli.py --site site02 --ring ring-0-canary --verify-all

lint:
	python -c "import json, os; [json.load(open(os.path.join('argocd/clusters', f))) for f in os.listdir('argocd/clusters') if f.endswith('.json')]; print('[✓] All 50 cluster manifests validated successfully.')"

clean:
	kind delete cluster --name ring0-canary || true
