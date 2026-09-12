# ADR-0002: Apache Iceberg REST Catalog (Project Nessie) vs Standalone Hive Metastore

**Status:** Accepted  
**Date:** 2026-07-02  
**Lead Architect:** William Free Hall (Free) <whall4.wh@gmail.com>

## 1. Context & Operational Challenge
Federal multi-cluster lakehouse query engines (Trino and Spark) require concurrent atomic metadata cataloging across classified and air-gapped boundaries without distributed database lockups.

## 2. Options Considered
* **Option A: Traditional Apache Hive Metastore (HMS) with Relational RDBMS**
  - *Evaluation:* High operational baggage; relational locking bottlenecks during concurrent PySpark write bursts; fragile RDBMS replication across disconnected networks.
* **Option B: Apache Iceberg REST Catalog Powered by Project Nessie**
  - *Evaluation:* Git-like version control for data tables (branches, tags, commits); lightweight container footprint; REST catalog API natively supported by both Trino 430+ and Apache Spark 3.5+.

## 3. Decision & Trade-Off Accepted
We adopted **Option B (Iceberg REST Catalog with Nessie)**.  
**Trade-Off Accepted:** Requires adopting the modern Iceberg REST catalog specification; eliminates relational metastore database administration and lock contention.
