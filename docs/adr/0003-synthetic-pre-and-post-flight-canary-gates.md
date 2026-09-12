# ADR-0003: Synthetic Pre- and Post-Flight Automated Verification Gates

**Status:** Accepted  
**Date:** 2026-07-20  
**Lead Architect:** William Free Hall (Free) <whall4.wh@gmail.com>

## 1. Context & Operational Challenge
A cluster upgrade may successfully return `200 OK` on Pod status while underlying CSI storage drivers or admission webhooks are secretly degraded, causing runtime batch queries to fail hours later.

## 2. Options Considered
* **Option A: Rely Strictly on Kubernetes Readiness Probes**
  - *Evaluation:* Fails to detect real distributed storage latency, Ceph RBD mount timeouts, or query engine spill-to-disk failures.
* **Option B: Automated Synthetic Delivery Harness (`delivery-cli`)**
  - *Evaluation:* Automatically executes realistic synthetic workloads post-upgrade: measures real PVC bind times, commits an Iceberg record, executes a distributed Trino query, and validates admission webhook latency.

## 3. Decision & Trade-Off Accepted
We adopted **Option B (`delivery-cli` Synthetic Verification)**.  
**Trade-Off Accepted:** Adds ~90 seconds of automated verification per cluster rollout wave; guarantees 100% functional data engine readiness before declaring a wave healthy.
