# Supply Chain Disruption Intelligence Dashboard

## Summary

This idea can be positioned as a focused **Genie Code + Databricks Free Edition dashboard POC** rather than a full production application. That framing makes it far more realistic for Builder Launchpad, because the current ask in the planner is whether the concept can be built in Genie Code within a Free Edition workspace, and the guidance already noted internally is to prefer a dashboard instead of an app for this setup.

The proposed POC will simulate a supply-chain intelligence workflow by combining a small slice of public vessel-movement data with weather enrichment, and surfacing the result in a dashboard that highlights vessel slowdown risk, weather overlap, and suggested next actions.

The GenAI angle should be both **behind the scenes** and **user-facing**:

- **Behind the scenes:** Genie Code helps generate the ingestion and transformation logic.
- **User-facing:** the final dashboard includes a conversational query layer where a user can ask questions such as which vessels are most at risk, why a specific port zone is flagged, what weather factors are driving delay, or what alternative action should be considered.

The dashboard can also present AI-generated natural-language summaries — likely cause of disruption, affected port zone, expected delay risk, and suggested mitigation or rerouting actions for operators. This keeps the build practical for a weekend event while still preserving the core value of the original idea and making the AI element explicit in the final experience.

## Why This Fits Databricks Free Edition

Databricks Free Edition includes access to **Genie, Genie Code, Lakeflow, and interactive data analysis** capabilities, which is enough for a lightweight prototype involving ingestion, transformation, and dashboard creation. Genie Code specifically supports generating and running code, building pipelines, and creating AI/BI dashboards across notebooks, SQL, and pipeline surfaces.

At the same time, Free Edition has constraints that make a smaller, dashboard-first build the right choice. It is:

- serverless-only,
- quota-limited,
- restricted to a limited set of trusted outbound internet domains,
- not intended for commercial or production use.

Because of those limits, the most defensible Builder Launchpad version is a **compact analytical prototype**, not a fully autonomous real-time logistics platform.

## Recommended POC Scope

The build should be reframed as a **Supply Chain Disruption Intelligence Dashboard** with the following scope:

- Ingest only **2–3 days of NOAA AIS vessel data** instead of the full archive. The NOAA 2024 AIS directory explicitly lists daily ZIP files and notes that the full set is 116.7 GB, so a very small sample is the practical path for the event.
- Use the AIS schema reference to map key fields such as **MMSI, SOG, and LAT/LON** for vessel identity, speed, and location tracking.
- Enrich vessel coordinates with **Open-Meteo weather data** to identify whether a vessel is operating in potentially disruptive weather conditions. Open-Meteo exposes a simple HTTP/JSON API, supports multiple locations in one request, and does not require authentication for basic use.
- Use **rule-based logic** to flag disruption risk — for example: *vessel slowdown near a busy port + high wind or marine severity = elevated delay risk.*
- Present results in a **dashboard** that shows high-risk vessels, likely disruption zones, and short recommended actions.

## Suggested Components by Layer

To make the POC more actionable for Builder Launchpad participants, the build can be broken into the following layers and components.

### 1. Data Ingestion Layer

- **Genie Code** in a notebook to generate Python code for downloading or loading a small sample of AIS files.
- **Python notebooks** for initial parsing and schema inspection.
- **Lakeflow** if the team wants a more pipeline-oriented implementation.
- **NOAA AIS daily ZIP files** as the raw historical vessel feed.

### 2. Storage and Data Modeling Layer

- **Delta tables** to store cleaned and transformed data.
- A simple **Bronze / Silver / Gold** structure.
- **Unity Catalog** tables where available in the workspace, for organizing the curated data used by dashboards and Genie.

**Suggested structure:**

| Layer | Contents |
|---|---|
| **Bronze** | Raw AIS records |
| **Silver** | Cleaned vessel positions with key fields — MMSI, timestamp, SOG, LAT, LON |
| **Gold** | Disruption-risk table — vessel, port zone, weather severity, delay score, recommended action |

### 3. Enrichment and Risk Logic Layer

- **Open-Meteo API** for weather enrichment.
- **PySpark or SQL** for joins and scoring logic.
- The **Marine Cadastre vessel traffic schema** reference to map AIS columns correctly.
- **Rule-based scoring** for the MVP — e.g. slowdown + severe weather + port proximity.

### 4. Dashboard and Visualization Layer

- **AI/BI dashboards** or **Databricks SQL dashboards** to display risk views.
- Tables and charts for high-risk vessels, disrupted zones, and vessel slowdown patterns.
- The **MarineCadastre AccessAIS UI** as a reference for how to think about vessel density and port-area layout.

### 5. GenAI and User Query Layer

This is the user-facing GenAI component of the POC.

- **Genie** on top of the curated Gold table or dashboard dataset.
- **Genie Code** to help prepare the semantic layer, SQL, and dashboard assets.
- A **conversational experience** where users ask natural-language questions against the curated disruption dataset.

**Example user questions:**

- Which vessels are currently at highest disruption risk?
- Why is the Port of Los Angeles zone flagged?
- Which weather factors are contributing most to delay risk?
- What action should operations consider for this vessel?

In this setup, the GenAI layer is not just helping developers build the solution; it is also part of the final end-user experience by answering questions and guiding users through the dashboard.

## Expected Deliverable

The final outcome for Builder Launchpad can be a **working dashboard prototype** with:

- a cleaned vessel-tracking table,
- a weather-enriched risk table,
- a few dashboard views such as **“High Risk Vessels,” “Port Zone Risk,”** and **“Suggested Action,”**
- a user-facing **GenAI assistant / conversational query layer** embedded in or alongside the dashboard,
- **Genie Code** used to accelerate pipeline creation, SQL logic, and dashboard generation.

The GenAI assistant should allow an operator to ask natural-language questions such as:

- which vessels are currently at highest disruption risk,
- why a given vessel or port zone is flagged,
- what weather or congestion factors are driving the risk,
- what mitigation or rerouting action should be considered.

This makes the AI component explicit in the final POC: not just data preparation in the backend, but an **interactive layer** that answers user queries and guides decisions through the dashboard.

This matches the internal direction that, in Free Edition, a dashboard is the easier and more feasible route than an app for this idea.

## Risks and Mitigation

The main technical risk is that Free Edition restricts outbound internet access to trusted domains, so direct runtime access to every public source may not be guaranteed. To reduce that risk, the team can:

- pre-download a few AIS files externally and upload them into the workspace,
- keep weather enrichment to a small batch of coordinates,
- focus on a batch prototype rather than real-time orchestration.

## Recommendation

This idea should be submitted as **feasible in Genie Code Free Edition**, provided it is scoped as a **dashboard-based disruption intelligence POC** and not as a production-grade, real-time autonomous routing platform. That version is realistic for the event, aligned with Free Edition constraints, and still strong enough to demonstrate business relevance and technical creativity.
