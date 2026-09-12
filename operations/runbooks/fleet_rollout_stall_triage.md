# Operational Runbook: Fleet GitOps Staged Rollout Freeze & Desynchronization Triage

**Severity:** P1 / Fleet Delivery Stalled  
**Target Systems:** Argo CD ApplicationSet Controller, Target Kubernetes Clusters (50 Sites)

## Diagnostic Workflow

### 1. Check ApplicationSet Sync Status & Active Rolling Wave
```bash
kubectl -n argocd get applicationset fleet-lakehouse-platform -o yaml
argocd app list -l "ring=ring-0-canary"
```

### 2. Identify Failing Cluster in Current Delivery Ring
```bash
argocd app get lakehouse-cluster-prod-site02 --refresh
kubectl -n argocd get app lakehouse-cluster-prod-site02 -o jsonpath='{.status.conditions}' | jq .
```

### 3. Check Post-Upgrade Verification Gate Output
```bash
python delivery-cli/delivery_cli.py --site site02 --ring ring-0-canary --post-upgrade --json
```

### 4. Step-by-Step Remediation
1. **If Webhook Admission Timeout Occurs:**
   Inspect Kyverno or Gatekeeper logs on target cluster:
   ```bash
   kubectl -n kyverno logs -l app.kubernetes.io/name=kyverno --tail=100 | grep -i "timeout"
   ```
2. **If Staged Rollout Must Be Aborted:**
   Freeze rolling wave progression by setting ApplicationSet sync policy to suspended:
   ```bash
   kubectl -n argocd patch applicationset fleet-lakehouse-platform --type merge -p '{"spec":{"syncPolicy":{"automated":null}}}'
   ```
3. **Rollback Canary Cluster:**
   ```bash
   argocd app rollback lakehouse-cluster-prod-site02
   ```
