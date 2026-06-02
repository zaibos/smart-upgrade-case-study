# Case Study: The "Smart Upgrade" Ecosystem — Databricks Hands-On Edition

**Role:** Data Engineer / Solutions Architect 
**Domain:** Lumera (Lumera Books Online – LBO)
**Scale:** 5 Million Active Users (sample dataset provided)
**Platform:** Databricks (Unity Catalog, Delta, AI/BI Dashboards, Genie, Databricks Apps)

---

## About Lumera

**Lumera** is a cloud-based financial software company serving small and medium-sized businesses (SMBs). Its flagship product, **Lumera Books Online (LBO)**, is a SaaS accounting and business-management platform that lets businesses manage invoicing, payments, payroll, expenses, and financial reporting from a single web and mobile application.

Lumera operates on a **tiered subscription (freemium-to-premium) model** — customers start on entry or mid-tier plans and upgrade as their needs grow. With **5 million active businesses**, growth-driven monetization (converting users to higher-value plans at the right moment) is central to Lumera's business. The **Growth Data Platform** team owns the data and analytics infrastructure that powers these monetization and personalization initiatives.

---

## 1. The Scenario

You are a Data Engineer / Architect on the **Growth Data Platform** team. The business has identified that **5% of Mid-Tier users (~250k businesses)** are "Power Users" who have outgrown their current plan. They are hitting feature limits and experiencing friction.

**The Goal:** Build the data foundation and analytics layer for a **"Smart Upgrade Ecosystem"** that detects friction points and surfaces a personalized, AI-driven upgrade offer (e.g., *"Upgrade now for 50% off"*) at the moment of need.

Three teams collaborate on this initiative:

1. **Data Engineering (You):** Owner of the pipeline, data quality, the semantic layer, and the analytics/serving surfaces.
2. **Data Science (DS):** Owns business logic (defining "Friction") and A/B test analysis — they consume *your* semantic layer.
3. **AI/ML Science:** Owns the Propensity Model (who is likely to buy) and Dynamic Pricing Model (how much discount) — they consume *your* features.

> **Your focus in this exercise:** the **Data Engineering + Analytics surfaces**. You will build the lakehouse foundation and then expose it to the business and to other teams through **three Databricks products**, scaling in difficulty.

---

## 2. The Data Landscape

You are provided with (or will generate — see Appendix) sample data approximating three production streams:

| Source | Production reality | Sample provided | Key fields |
|---|---|---|---|
| **Telemetry** | Kafka, ~2B events/day (clicks, errors, page loads) | Clickstream event files (JSON/CSV) | `user_id`, `event_type`, `event_ts`, `page`, `error_code`, `session_id`, `device` |
| **Transaction Ledger** | Postgres CDC (financial) | Daily transaction snapshots | `user_id`, `invoice_count`, `payroll_runs`, `revenue`, `txn_date` |
| **Subscription Data** | Postgres CDC | Subscription table | `user_id`, `plan_tier`, `seats`, `renewal_date`, `mrr`, `signup_date` |

**Data is intentionally imperfect:** out-of-order events, duplicates, late-arriving records, and some malformed/missing fields. Handling this is part of the evaluation.

**Latency tiers (for design discussion):** Inference < 200ms · Reporting T+1.

---

## 3. The Challenge — Your Deliverables (Tiered)

Deliverables are layered. **Tier 0 is the required foundation; Tiers 1–3 escalate in difficulty.** Complete as many as your time and the target level allow.

### Tier 0 — Data Foundation (Required for everything else)

Build a **medallion (Bronze → Silver → Gold)** pipeline in Unity Catalog.

1. **Ingestion & cleansing:** Load all three sources to Bronze. In Silver, dedupe, handle late/out-of-order events, fix/quarantine malformed records, and **sessionize** the clickstream (stitch events into sessions; define a session-timeout rule).
2. **Customer-360 Gold model:** Build the dimensional marts the business needs:
   - `dim_customer`, `dim_subscription`, `dim_date`, `dim_feature`
   - `fact_feature_usage_daily` / `_monthly`
   - `fact_monthly_financials`
   - A **`customer_360`** gold table combining real-time signals (e.g., *errors in last hour*) and batch signals (e.g., *YoY revenue growth*).
3. **Friction & funnel facts:** Produce a gold table powering **Upgrade Funnel** reporting: `intervention_trigger`, `nudge_sent`, `propensity_score` (a placeholder/mock score is fine), `outcome` (converted / dismissed / ignored).

**Deliverable:** notebooks/SQL + a short README of assumptions, sessionization logic, and data-quality strategy.

---

### Tier 1 — AI/BI Dashboard *(Core — required)*

Build a **Databricks AI/BI (Lakeview) Dashboard** on top of the gold layer that the Growth/DS team would use to monitor the funnel. It must answer at minimum:

- How many **Power Users** are flagged as "in friction" over time? By plan tier / segment?
- **Upgrade-funnel conversion:** triggers → nudges sent → offers viewed → upgrades, with drop-off at each stage.
- **Session & engagement KPIs:** active users, avg session duration, error rate trend.
- **Revenue impact:** MRR uplift from converted users; discount cost vs. uplift.
- At least one **interactive filter** (date range, plan tier, or segment).

**Evaluation:** correct metric logic, sound use of **Unity Catalog Metric Views** as the semantic layer behind the dashboard, clarity of visualizations, and whether the KPIs actually answer the business question.

---

### Tier 2 — Genie Space *(Intermediate — required)*

Create a **Databricks Genie Space** on the same gold/Metric-View semantic layer so a non-technical PM can ask questions in natural language.

1. Curate the tables/metric views exposed to Genie.
2. Add **instructions, sample SQL, and synonyms** so Genie answers reliably.
3. Demonstrate it correctly answering at least 5 representative questions, e.g.:
   - *"How many power users hit a feature limit last week?"*
   - *"What's the upgrade conversion rate by plan tier this month?"*
   - *"Which features have the highest usage among users who upgraded?"*
   - *"What was the MRR uplift from the discount campaign?"*

**Evaluation:** quality of the **semantic modeling for NL** (this is the real test — did they model/annotate the gold layer well enough that Genie is accurate?), the curation/instructions, and handling of ambiguous questions. This is the practical realization of the **"DS metric contract"** — DS defines metrics declaratively (Metric Views) instead of writing Spark code in your pipeline.

---

### Tier 3 — Databricks App *(Advanced — bonus / for senior candidates)*

Build a **Databricks App** that operationalizes the "Smart Upgrade" experience — i.e., the surface the application UI (or a growth analyst) would interact with.

Choose **one**:
- **A) "Smart Upgrade Offer Console"** — given a `user_id`, display their Customer-360 (friction signals, usage, financials), their (mock) propensity score, and the recommended offer. Simulates the **<200ms serving / inference request** the app UI would make.
- **B) "Friction Monitoring & Intervention" app** — an interactive console for the growth team to view at-risk power users, filter/segment, and trigger/preview a nudge.

Requirements: query the gold layer / a SQL warehouse (or a served model endpoint) from the app, handle a user-supplied input, and render results interactively (Streamlit/Dash or FastAPI+React).

**Evaluation:** app-dev competence, latency-aware data access (warehouse vs. online table vs. model serving), auth/resource config, and how cleanly it reuses the gold layer rather than re-deriving logic.

---

## 4. Design & Discussion Questions (write-up — all candidates)

Even if you don't build Tier 3, address these in your write-up:

1. **Dual-velocity ingestion:** How would you handle 2B clickstream events/day vs. strict financial CDC in production? (e.g., Structured Streaming/Auto Loader + Lakeflow Declarative Pipelines; CDC via `APPLY CHANGES`.)
2. **State & serving for <200ms inference:** How do you store and serve the Customer-360 state for real-time scoring? (Feature Store / Online Tables / Lakebase, model serving.)
3. **The AI feature contract:** When the AI scientist says *"I need avg session time over the last 7 days,"* what's the workflow, and how do you guarantee **train/serve parity**?
4. **The feedback loop:** Model performance is degrading and AI blames "bad data." How do you prove it automatically? What **SLAs / data-quality contracts** do you expose? (e.g., Lakehouse Monitoring, expectations, freshness SLAs.)

---


## 5. Submission

- A Databricks workspace (or exported notebooks/DAB project) containing the pipeline, Metric Views, dashboard, and Genie Space config.
- A README covering assumptions, design decisions, trade-offs, and what you'd do with more time.
- A 15–20 min walkthrough (live or recorded).

---

## Appendix — Sample Data

If a dataset is not pre-provided, generate synthetic data approximating the three streams above (5M users can be down-sampled to ~10k–50k for the exercise), including **seeded imperfections** (duplicates, out-of-order events, missing logouts/fields) and **seeded "power-user friction" patterns** so the funnel and anomalies are discoverable. Provide the generation script with your submission.
