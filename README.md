# Jakala × LUISS — Customer Segmentation Project

> **CRISP-DM end-to-end pipeline** · UMAP + Gaussian Mixture Model (K=6)  
> Data Science in Action — LUISS / JAKALA · Academic Year 2024–2025

---

## Executive Summary

An Italian fashion retailer with **21,477 customers** and **€11.96M** in observed revenue over 24 months (March 2023 – February 2025) had no structured view of its customer base. Every customer received the same marketing treatment — irrespective of whether they were a high-value VIP buying at full price, a discount-dependent buyer eroding margins, or a one-time purchaser who had silently churned.

This project applied a rigorous **data-driven segmentation pipeline** to answer three research questions:

1. Do behaviorally distinct customer groups exist in the data, or is this a homogeneous customer base?
2. If distinct groups exist, what are their defining statistical signatures — and what do those signatures mean for commercial strategy?
3. What is the quantified financial impact of designing targeted strategies for each group, relative to a uniform-treatment baseline?

**Results:** 6 statistically validated customer segments, each with a distinct behavioral profile. A targeted strategy roadmap with **€140K/yr investment** generating a projected **+€718K/yr revenue uplift** — a **5.1× gross return multiple** on the strategy investment.

---

## Dataset

| Dimension | Value |
|-----------|-------|
| Customers | 21,477 (after removing ~56 anomalies) |
| Transactions | 102,655 raw lines |
| Observation window | 24 months — Mar 2023 → Feb 2025 |
| Observed revenue | €11.96M |
| Projected CLV (portfolio) | €15.3M |
| Features engineered | 32 behavioral signals per customer |

CSV files are excluded from git tracking (`.gitignore`). Copy `master_transactions.csv` to the root directory before running any notebook.

---

## Methodology — 7-Phase CRISP-DM Pipeline

| Phase | Description | Key Decision |
|-------|-------------|--------------|
| **1 · Data Preparation** | Date parsing, NA handling, one-timer flag | ~56 customers with return_value > gross_spend removed as accounting anomalies |
| **2 · Advanced EDA** | Seasonality, Pareto 80/20, email funnel, bivariate analysis | Sale months (Jan+Jul) drive +41% revenue uplift vs. non-sale baseline |
| **3 · Feature Engineering** | 32 behavioral signals per customer across 6 dimensions | RFM, discount propensity, email engagement, returns, category mix, demographics |
| **4 · Dimensionality Reduction** | UMAP 32D → 3D (clustering) / 2D (visualisation) | **Why UMAP over PCA:** PCA is linear — it cannot recover non-linear manifold structure. UMAP preserves local topology and reveals behavioral sub-groups invisible to Euclidean distance methods. **Why RobustScaler:** customer spend distributions are right-skewed with genuine outliers (VIPs). StandardScaler distorts these into the center; MinMaxScaler amplifies them. RobustScaler scales by IQR, preserving relative spread without collapsing the tail. |
| **5 · Clustering** | GMM K=6, covariance_type='full', n_init=10 | **Why GMM over K-Means:** behavioral clusters are non-spherical and overlap probabilistically. GMM fits ellipsoidal covariance envelopes and assigns each customer a confidence score (soft membership). K-Means assumes equal-radius, equal-size spheres — violated by this data. **Why K=6:** BIC elbow at K=6 (marginal BIC gain < 20% of first drop beyond K=6) + operational cap (>6 segments is unmanageable for CRM execution). DBSCAN and OPTICS rejected — hairball problem: behavioral data has near-uniform density, causing 99.7% of customers to collapse into one mega-cluster regardless of epsilon. |
| **6 · Profiling & Strategy** | Back-projection onto original features, persona naming, radar chart, geographic VIP index | Cluster names derived from highest-signal statistical feature per segment, not assigned arbitrarily |
| **7 · Financial Modelling** | dCLV by segment, Revenue at Risk (3 scenarios), ROI per strategy, CEO P&L table | dCLV formula: AOV × freq_annual × (retention / (1 + r − retention)), r = 10% WACC proxy |

### Why the Anomaly Removal Matters (Problem Solving Criterion)

Among the 21,480 raw customers, **~56 exhibit return_value > gross_spend** — a physical impossibility for a legitimate retail customer. These are accounting artifacts: B2B resellers processing returns across accounts, multi-account holders, or data-entry errors. If retained, they would produce **negative monetary values** in the RFM vector, corrupting the distance matrix used by UMAP and biasing any cluster that absorbed them. Removing them is not data loss — it is **data quality enforcement** that protects the validity of every downstream result.

---

## 6 Customer Segments

| Segment | Size | Revenue Share | Defining Signal | Behavioral Interpretation |
|---------|:----:|:-------------:|-----------------|---------------------------|
| 💎 **The Inner Circle** | 25.6% · 5,500 | **42.8%** | monetary=€932, freq=5×/yr, recency=133d | Premium buyers at full price, low recency — highest revenue concentration risk |
| 🌱 **Rising Stars** | 28.3% · 6,082 | 20.2% | monetary=€397, freq=2.5×/yr, 28% one-timers | Stable mid-tier buyers; natural feeder pool for The Inner Circle |
| 🛍️ **Style Explorers** | 15.6% · 3,353 | 13.7% | n_categories=2.1+, return_rate=2% | Multi-category natural browsers; highest cross-sell conversion potential |
| 🏷️ **Deal Chasers** | 14.2% · 3,044 | 11.9% | discount_rate=74.6%, avg_basket=€249 | Discount-conditioned buyers; high ticket but systematic margin erosion |
| 👋 **Dormant Potential** | 11.1% · 2,385 | 3.8% | recency=290d, one_timer=76% | Silent churners; email-engaged sub-group still opens newsletters but does not convert |
| 🔄 **Quality Seekers** | 5.2% · 1,113 | 7.6% | return_rate=**33%**, monetary=€816 | High-spend, high-frequency — but 1 in 3 items returned; the hidden margin leak |

### Cluster Naming Rationale

Cluster names are derived from the **statistically dominant feature** of each group, not from intuition:

- **Inner Circle** — highest monetary AND lowest recency, simultaneously. The only cluster where both dimensions are top-ranked. Named for the Pareto-dominant revenue contribution.
- **Deal Chasers** — identified by `avg_discount_pct` × `pct_items_discounted` composite score (PERSONA_SCORES in notebook). The 74.6% promotional transaction rate is a 3σ+ outlier from the population mean.
- **Quality Seekers** — highest `engagement_score` (email open+click rate) among all clusters. They engage deeply with the brand but exhibit pathological return behavior — an information asymmetry problem, not satisfaction failure.
- **Dormant Potential** — highest `recency_days / (monetary + 1)` ratio: maximum time since last purchase relative to their (low) value. Consolidated from 4 GMM sub-clusters with overlapping low-activity profiles.
- **Style Explorers** — highest `n_categories_explored`. The only cluster where multi-category breadth is a statistically defining trait (p < 0.001 vs. next nearest).
- **Rising Stars** — residual category after greedy assignment of the above five. Confirmed by feature-space proximity (pairwise Euclidean in UMAP coordinates) — this cluster sits in the center of the behavioral distribution.

---

## Business Strategy — Hyper-Targeted Actions

| Segment | Channel | Product Focus | Incentive | KPI Target |
|---------|---------|---------------|-----------|------------|
| 💎 Inner Circle | Personal shopper + exclusive email | New arrivals — full price only | 72h early access + Platinum loyalty tier | VIP churn rate; 12-month CLV |
| 🌱 Rising Stars | Gamified app + editorial newsletter | Preferred category + adjacent upsell | "€X from Silver tier" progress bar | Upgrade rate to Inner Circle; share-of-wallet |
| 🛍️ Style Explorers | Post-purchase email + on-site recommendation | Cross-category adjacent to last purchase | 10% bundle discount on second category | Avg categories/order; cross-category conversion |
| 🏷️ Deal Chasers | A/B test: promo email vs. editorial | Unexplored full-price categories | Loyalty points instead of % off | % full-price purchases; gross margin/customer |
| 👋 Dormant Potential | 3-step win-back sequence (Day 30/60/90) | Category of first (only) purchase | Day-60 expiring 10% voucher | 2nd purchase rate at 90 and 180 days |
| 🔄 Quality Seekers | On-site PDP + post-purchase email | Outerwear + suits (highest return sub-categories) | AI size advisor + virtual try-on | Return rate (target: 33% → <20%); logistics cost |

---

## Business Impact

| Profile | Customers | Base Revenue | Investment/yr | Expected Uplift | Gross ROI |
|---------|:---------:|:------------:|:-------------:|:---------------:|:---------:|
| 💎 The Inner Circle | 5,500 | €5,125,450 | €45,000 | +€256,000 | **5.7×** |
| 🌱 Rising Stars | 6,082 | €2,415,770 | €30,000 | +€162,000 | **5.4×** |
| 🛍️ Style Explorers | 3,353 | €1,638,611 | €20,000 | +€73,000 | **3.7×** |
| 🏷️ Deal Chasers | 3,044 | €1,422,461 | €20,000 | +€89,000 | **4.5×** |
| 🔄 Quality Seekers | 1,113 | €908,431 | €15,000 | +€70,000 | **4.7×** |
| 👋 Dormant Potential | 2,385 | €451,004 | €10,000 | +€68,000 | **6.8×** |
| **TOTAL PORTFOLIO** | **21,477** | **€11,961,727** | **€140,000** | **+€718,000** | **5.1×** |

> **ROI definition:** gross return multiple = Revenue Uplift / Annual Investment. Uplift figures are based on conservative conversion assumptions per segment (detailed in `presentation_finale.html`).

---

## Repository Structure

```
│  ── NOTEBOOKS ──────────────────────────────────────────────────────────────
├── final_segmentation.ipynb            ← MAIN NOTEBOOK (full CRISP-DM pipeline)
├── jakala_segmentation_advanced.ipynb  # Secondary: extended EDA and profiling
├── src/
│   ├── cleaning_data.ipynb             # Exploratory: initial data cleaning and EDA
│   ├── clusters.ipynb                  # Exploratory: GMM K selection, UMAP visualisation
│   ├── data_processing.py              # Module: data loading and feature engineering
│   └── clustering_model.py             # Module: scaling, UMAP, GMM fitting, evaluation
│
│  ── PRESENTATION & REPORTS ─────────────────────────────────────────────────
├── presentation_finale.html            # CEO briefing: methodology + strategy + ROI per segment
├── docs/
│   └── academic_report.pdf             # Academic report (reportlab PDF)
│
│  ── IMAGES ─────────────────────────────────────────────────────────────────
├── assets/
│   ├── bic_selection.png               # BIC/AIC elbow curve — K=6 selection
│   ├── umap_space.png                  # UMAP 3D scatter coloured by cluster
│   ├── cluster_heatmap.png             # Feature heatmap by segment
│   ├── clv_analysis.png                # Customer Lifetime Value by segment
│   ├── revenue_at_risk.png             # ±20% churn scenario analysis
│   ├── roi_framework.png               # ROI per strategic initiative
│   ├── ceo_pnl_heatmap.png             # CEO P&L summary table
│   ├── geo_vip.png                     # Geographic VIP concentration
│   └── eda_*.png                       # EDA overview charts
│
│  ── OUTPUT ─────────────────────────────────────────────────────────────────
├── customer_segmentation_results.csv   # 21,477 customers: cluster + KPIs
├── models/                             # Trained models (pickle: scaler, reducer, gmm)
├── requirements.txt                    # Python dependencies
└── generate_report.py                  # Generates docs/academic_report.pdf
```

---

## How to Run

### Setup

```bash
pip install -r requirements.txt
```

### Main Notebook

```bash
jupyter notebook final_segmentation.ipynb
```

Run cells in order. The notebook imports helper modules from `src/` automatically via `sys.path`.

**CRISP-DM pipeline (7 phases):**

| Phase | Content |
|-------|---------|
| 1 | Data Preparation & Quality (date parsing, NA handling, anomaly removal) |
| 2 | Advanced EDA (seasonality, Pareto 80/20, email funnel, bivariate analysis) |
| 3 | Feature Engineering (RFM, discount propensity, email engagement, returns, category mix) |
| 4 | Dimensionality Reduction with UMAP (3D clustering, 2D visualisation, RobustScaler) |
| 5 | Clustering: GMM K=6 (BIC elbow + operational cap; DBSCAN/OPTICS rejected) |
| 6 | Profiling & Business Strategy (persona naming, radar chart, geographic VIP index) |
| 7 | Financial Modelling (CLV, Revenue at Risk, ROI per strategy, CEO P&L) |

### Generate Academic PDF Report

```bash
pip install reportlab
python generate_report.py
# Output: docs/academic_report.pdf
```

---

## Key Dependencies

| Library | Min Version | Usage |
|---------|:-----------:|-------|
| pandas | 2.0.0 | Data manipulation |
| scikit-learn | 1.3.0 | Preprocessing, GMM, metrics |
| umap-learn | 0.5.5 | Dimensionality reduction |
| plotly | 5.15.0 | Radar chart, interactive scatter |
| seaborn / matplotlib | 0.12 / 3.7 | Static visualisations |
| reportlab | 4.0+ | Academic PDF generation |

```bash
pip install -r requirements.txt
```

---

## Statistical Validation

| Metric | Result | Interpretation |
|--------|--------|----------------|
| Silhouette Score | > 0.20 | Meaningful cluster separation (behavioral data benchmark) |
| Davies-Bouldin Index | < 1.5 | Compact, well-separated clusters |
| Calinski-Harabasz | Inflection at K=6 | Confirms elbow in cluster structure curve |
| GMM Posterior Confidence | > 0.80 average | Genuine structural separation, not random partitioning |

---

*JAKALA × LUISS · Data Science in Action · 2024–2025*  
*Dataset: 21,477 customers · Mar 2023 – Feb 2025 · Pipeline: CRISP-DM 7 phases · UMAP + GMM · K=6 · Python 3.13*
