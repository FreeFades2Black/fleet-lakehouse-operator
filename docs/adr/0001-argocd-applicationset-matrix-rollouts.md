# ADR-0001: Progressive Delivery Rings with Argo CD ApplicationSet Matrix Generator

**Status:** Accepted  
**Date:** 2026-06-15  
**Lead Architect:** William Free Hall (Free) <whall4.wh@gmail.com>

## 1. Context & Operational Challenge
Deploying and upgrading a complex data lakehouse platform (Kafka, Trino, Spark, Apache Iceberg) across 50 heterogeneous federal/DoD Kubernetes clusters creates high blast-radius risk. Upgrading all clusters simultaneously or maintaining 50 separate Application manifests creates configuration drift and operational burnout.

## 2. Options Considered
* **Option A: Monolithic Multi-Cluster GitOps Application with Global Sync**
  - *Evaluation:* A single faulty Helm chart or breaking CRD upgrade immediately impacts all 50 sites simultaneously; zero canary verification.
* **Option B: Staged Delivery Rings (Ring 0, 1, 2) via ApplicationSet Matrix Generator**
  - *Evaluation:* Automates wave progression: Ring 0 (Canary, Sites 01-02, 100% update with synthetic smoke test gate), Ring 1 (Core Connected, Sites 03-25, 40% rolling batches), and Ring 2 (Air-Gapped & Restricted, Sites 26-50, 20% strict serial update).

## 3. Decision & Trade-Off Accepted
We adopted **Option B (Staged Delivery Rings)**.  
**Trade-Off Accepted:** Total fleet deployment duration extends to ~4.5 hours; however, blast radius is constrained to 2 canary sites, protecting 48 mission-critical operational sites from regressions.
