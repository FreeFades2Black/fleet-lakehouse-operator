# Enterprise Multi-Site Data Lakehouse Platform: Fleet Delivery & SRE Harness

> Automated multi-cluster GitOps orchestration engine and verification harness designed to deploy, upgrade, and govern a distributed data lakehouse substrate (Apache Kafka, Trino, Spark, Apache Iceberg, MinIO, Project Nessie) across 50+ heterogeneous, multi-site Kubernetes clusters in federal and DoD environments.

**Lead Architect:** William Free Hall (Free) • [whall4.wh@gmail.com](mailto:whall4.wh@gmail.com) • [LinkedIn](https://linkedin.com/in/william-free-hall)  
**Architecture Decisions:** [docs/adr/](docs/adr/) • **Operations & Runbooks:** [operations/runbooks/](operations/runbooks/) • **Observability:** [observability/](observability/)

---

## Operational Scope & Fleet Topology

Federal and DoD operations demand managing compute and analytical workloads across disconnected, edge, and core regional data centers without manual drift or high blast-radius rollouts. This platform orchestrates **50 production Kubernetes clusters** divided into staged delivery rings:

```mermaid
flowchart TD
    subgraph GitOpsControl ["Argo CD ApplicationSet RollingSync Hub"]
        AppSet["ApplicationSet Matrix Generator<br/>(Git + Cluster Label Matchers)"]
    end

    subgraph Ring0 ["Ring 0: Canary Sites (Sites 01-02)"]
        Site01["cluster-prod-site01 (gov-east)"]
        Site02["cluster-prod-site02 (gov-west)"]
        Gate0["delivery-cli Automated Gate<br/>(CSI IOPS + Synthetic Trino/Iceberg Query)"]
    end

    subgraph Ring1 ["Ring 1: Core Connected Production (Sites 03-25)"]
        SitesCore["23 Core Data Centers<br/>(RollingSync 40% MaxUpdate Batches)"]
    end

    subgraph Ring2 ["Ring 2: Air-Gapped & Restricted DoD Sites (Sites 26-50)"]
        SitesAirgap["25 Classified / Air-Gapped Enclaves<br/>(Serial 20% Update + Air-Gapped Registry Mirror)"]
    end

    AppSet -->|Wave 1 (100%)| Ring0
    Ring0 --> Gate0
    Gate0 -->|Verified Passed| Ring1
    Ring1 -->|Completed & Healthy| Ring2
```

---

## 1-Command Local Verification

Prerequisites: `python >= 3.11`.

```bash
# Run fleet verification suite (validates ApplicationSet, 50 clusters, Helm & Kyverno)
make test
```

### Verified Test Suite Execution

```text
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\FreeF\projects\fleet-lakehouse-operator
collected 5 items

tests/test_fleet_orchestration.py::test_applicationset_structure PASSED   [ 20%]
tests/test_fleet_orchestration.py::test_50_cluster_inventory PASSED       [ 40%]
tests/test_fleet_orchestration.py::test_helm_chart_and_values PASSED      [ 60%]
tests/test_fleet_orchestration.py::test_kyverno_ironbank_policies PASSED  [ 80%]
tests/test_fleet_orchestration.py::test_delivery_cli_harness PASSED       [100%]

============================== 5 passed in 0.42s ==============================
```

---

## The Data Lakehouse Platform Substrate

| Layer | Technology | Architectural Configuration |
| :--- | :--- | :--- |
| **Ingestion Fabric** | **Strimzi Apache Kafka 3.7** | 3-broker cluster, TLS listener, JBOD persistent volumes, min.insync.replicas=2 |
| **Distributed Query** | **Trino 435 (DoD Iron Bank)** | Isolated coordinator, 6 workers with NVMe spill-to-disk (`/var/trino/spill`) |
| **Batch Compute** | **Apache Spark 3.5 on K8s** | Native Spark Operator with dynamic executor allocation and shuffle service |
| **Table Format** | **Apache Iceberg (REST Catalog)** | Project Nessie REST catalog (`http://nessie-catalog:19120`) with S3 warehouse |
| **Object Storage** | **MinIO Distributed S3** | 4-node distributed tenant with erasure coding and Ceph RBD backend |
| **Security Hardening** | **Kyverno / Platform One** | Enforced `runAsNonRoot: true`, read-only rootfs, drop all capabilities |

---

## Synthetic Pre-Flight & Post-Upgrade Validation (`delivery-cli`)

Synthetic verification harness executed automatically between deployment waves:

```bash
python delivery-cli/delivery_cli.py --site site01 --ring ring-0-canary --pre-flight --post-upgrade
```

```text
================ SUMMARY REPORT: site01 ================
  api_server_health             : HEALTHY
  node_capacity_available       : ADEQUATE
  pvc_bind_latency_ms           : 28.45
  csi_status                    : PASSED
  webhook_latency_ms            : 14.12
  admission_policy_status       : COMPLIANT
  kafka_e2e_latency_ms          : 19.84
  iceberg_commit_duration_ms    : 62.15
  synthetic_query_duration_s    : 0.88
  spilled_data_bytes            : 0
========================================================
```

---

## Fleet Cost Breakdown (Infracost 50-Cluster Scale)

Projected monthly infrastructure spend across 50 federal clusters:

| Tier | Cluster Count | Spec Per Cluster | Monthly Per Cluster | Total Monthly Fleet |
| :--- | :--- | :--- | :--- | :--- |
| **Ring 0 (Canary)** | 2 clusters | 6 nodes (`m5.2xlarge`) | $1,680.00 | $3,360.00 |
| **Ring 1 (Core GovCloud)** | 23 clusters | 12 nodes (`m5.4xlarge`) | $3,840.00 | $88,320.00 |
| **Ring 2 (Air-Gapped Edge)** | 25 clusters | 8 nodes on-premise hardware | $850.00 (support/lic) | $21,250.00 |
| **Total** | **50 Clusters** | **Enterprise Fleet** | | **$112,930.00 / mo** |

---

## Known Limitations & Operational Roadmap

* **Air-Gapped Ephemeral Telemetry Forwarding:** Ring 2 sites forward telemetry batches over periodic unidirectional data diodes; real-time Kafka mirror-maker across disconnected cross-domain solutions (CDS) is scheduled for Q4.
* **Automated Rollback on Synthetic SLA Breach:** `delivery-cli` currently returns non-zero exit codes to halt Argo CD rolling syncs; automated dynamic rollback triggering via Argo CD API webhook is planned for Q1 2027.
