# Incident Post-Mortem: Ring 0 Canary Admission Webhook Lockout Stalling Fleet Rollout

**Incident Date:** 2026-07-29  
**Impact Duration:** 42 minutes (Fleet rollout safely paused at Ring 0)  
**Severity:** SEV-2  
**Root Cause:** A Kyverno policy update introduced a regex constraint asserting container registry domains. The validating webhook timed out on un-cached air-gapped DNS lookups in Canary Site 02, causing Kubernetes API server to reject Trino worker pods.

## Timeline
* **10:00 UTC:** Argo CD ApplicationSet initiated Ring 0 Canary deployment to Site 01 and Site 02.
* **10:03 UTC:** Site 01 upgraded cleanly; Site 02 halted with `Internal error occurred: failed calling webhook "validate.kyverno.svc-fail"`.
* **10:05 UTC:** Argo CD RollingSync strategy automatically blocked progression to Ring 1 (23 core sites protected).
* **10:18 UTC:** Delivery CLI synthetic health check flagged admission latency spike (p99 > 3,500ms).
* **10:32 UTC:** Hotfix deployed tuning webhook failure policy to `Ignore` for internal system pods and caching DNS resolvers.
* **10:42 UTC:** Site 02 smoke test passed; wave progression to Ring 1 resumed.

## Corrective Actions & Architectural Safeguards
1. Enforced `delivery-cli` pre-flight admission webhook latency assertion (< 50ms threshold).
2. Proved value of Ring 0 Canary design: 48 operational federal clusters experienced zero downtime.
