# Smart Upgrade Ecosystem — Databricks Case Study

A hands-on data engineering / analytics case study, built on **Databricks** (Unity Catalog, Delta, AI/BI Dashboards, Genie, Databricks Apps).

**Scenario (fictional):** *Lumera* is a cloud accounting SaaS (*Lumera Books Online*) for SMBs. ~5% of Mid-Tier users are "Power Users" who have outgrown their plan and hit feature limits. The candidate builds the data foundation + analytics layer for a "Smart Upgrade Ecosystem" that detects this friction and surfaces a personalized upgrade offer.

## What's here

```
docs/
  Case_Study_Smart_Upgrade_Databricks_Handson.md   # Full case study (role, tiers, rubric)
  DATA_DICTIONARY.md                               # Schema + seeded patterns for the dataset
data/
  subscriptions.csv          # 10,000 businesses
  transactions.csv           # 60,000 monthly financial snapshots
  telemetry_events.csv.gz    # ~785,000 clickstream events (gzipped; ~93MB raw)
  generate_local.py          # Reproducible generator (pure Python stdlib, seed=42)
```

## The tiers (what the candidate delivers)

- **Tier 0 — Data Foundation (required):** Bronze→Silver→Gold medallion; dedupe, sessionize, quarantine bad records; Customer-360 + upgrade-funnel gold tables.
- **Tier 1 — AI/BI Dashboard (core):** Funnel, friction, engagement, and revenue KPIs on Unity Catalog Metric Views.
- **Tier 2 — Genie Space (intermediate):** Natural-language Q&A on the same semantic layer.
- **Tier 3 — Databricks App (advanced/bonus):** A "Smart Upgrade Offer Console" or friction-monitoring app.
- **Architecture write-up:** dual-velocity ingestion, sub-200ms serving, feature/metric contracts, drift & data-quality SLAs.

See [`docs/Case_Study_Smart_Upgrade_Databricks_Handson.md`](docs/Case_Study_Smart_Upgrade_Databricks_Handson.md) for full details and the evaluation rubric.

## Using the dataset

The data models three raw source streams and is **intentionally imperfect** (duplicates, nulls, malformed values, out-of-order events) — cleaning it is part of the exercise.

```bash
# Unzip the telemetry file
gunzip -k data/telemetry_events.csv.gz
```

Load into Databricks (e.g., upload to a Unity Catalog Volume and ingest with Auto Loader), or run the generator yourself:

```bash
python3 data/generate_local.py   # writes CSVs to /tmp/sds/out (edit paths as needed)
```

> **Grading note:** `subscriptions.csv` includes an `is_power_user_seed` column as ground truth. Candidates should **ignore it** — the friction cohort must be *derived* from telemetry + transactions, not read from this flag.

## Disclaimer

All data is **synthetic** and generated programmatically. "Lumera" is a fictional company; any resemblance to real companies or products is coincidental.
