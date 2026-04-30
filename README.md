# Jakala × LUISS — Customer Segmentation Project

> **CRISP-DM end-to-end pipeline** · UMAP + Gaussian Mixture Model (K=6)
> Data Science in Action — LUISS / JAKALA · Academic Year 2025–2026

---

## Executive Summary

An Italian fashion retailer with **21,424 customers** and **€12,084,646** in observed
revenue over 24 months (March 2023 – February 2025) had no structured view of its
customer base. Every customer received the same marketing treatment regardless of value,
behaviour, or engagement pattern.

This project applied a rigorous **data-driven segmentation pipeline** to answer three
research questions:

1. Do behaviourally distinct customer groups exist in the data?
2. If distinct groups exist, what are their defining statistical signatures?
3. What is the quantified financial impact of targeted strategies relative to uniform treatment?

**Results:** 6 statistically validated customer segments. A targeted strategy roadmap
with **€140K/yr investment** projects a **€342K/yr revenue uplift** — a **2.4× gross
return multiple** on the strategy investment (scenario estimate; A/B validation required).

---

## Dataset

| Dimension | Value |
|-----------|-------|
| Customers | 21,424 (after removing 56 negative-spend anomalies from 21,480 raw) |
| Transaction rows | 102,655 raw lines |
| Observation window | 24 months — Mar 2023 → Feb 2025 |
| Observed revenue | €12,084,646 |
| Projected CLV (portfolio) | €16,187,953 |
| Clustering features | 24 behavioural signals per customer |

Place `master_transactions.csv` in `src/io/` before running the notebook.

---

## Methodology — CRISP-DM Pipeline (6 Phases + Financial Extension)

| Phase | Description | Key Decision |
|-------|-------------|--------------|
| **1 · Data Preparation** | Date parsing, NA handling, anomaly removal | 56 customers with return_value > gross_spend removed; Silhouette degrades from 0.42 → 0.33 if retained |
| **2 · Advanced EDA** | Seasonality, Pareto 80/20, email funnel, bivariate analysis | Top 20% of customers generate >70% of revenue |
| **3 · Feature Engineering** | 24 behavioural signals across 6 dimensions | RFM, discount propensity, email engagement, returns, category mix, channel/lifecycle |
| **4 · Dimensionality Reduction** | UMAP 24D→3D (clustering) / 2D (visualisation) | **Why UMAP:** preserves non-linear manifold structure; PCA insufficient (linear). **Why RobustScaler:** retail distributions are right-skewed; IQR-based scaling robust to extremes |
| **5 · Clustering** | GMM K=6, covariance_type='full', n_init=10 | **Why GMM:** fits ellipsoidal covariance envelopes, soft membership. **Why K=6:** (i) Silhouette per K, (ii) GMM posterior stability (96.5% >0.80), (iii) operational cap as tie-breaker |
| **6 · Profiling & Strategy** | Back-projection, persona naming, radar chart, geographic VIP index | Names derived from statistically dominant feature per segment |
| **Financial Extension** *(not a CRISP-DM phase)* | dCLV by segment, Revenue at Risk, ROI per strategy | dCLV = AOV × f_annual × r_ret/(1+r−r_ret), r=0.10 WACC proxy |

---

## 6 Customer Segments

| Segment | Size | % | Defining Signal | dCLV |
|---------|:----:|:-:|-----------------|:----:|
| **The Inner Circle** | 6,495 | 30.3% | Full-price loyal, AOV €192, 2.5×/yr, lowest discount rate | €1,545 |
| **Rising Stars** | 10,256 | 47.9% | Moderate frequency (1.4×/yr), AOV €177, no promo dependency | €545 |
| **Style Explorers** | 2,727 | 12.7% | Multi-category breadth, low AOV €97, cross-sell receptive | €85 |
| **Deal Chasers** | 768 | 3.6% | 74.6% discounted transactions, AOV €172, margin risk | €310 |
| **Dormant Potential** | 675 | 3.2% | 315-day avg recency, 76% one-timers, lapsed | €106 |
| **Quality Seekers** | 503 | 2.3% | ~33% return rate, above-avg basket, fit uncertainty | €95 |

---

## Business Impact

| Segment | Customers | Budget | Scenario Uplift | Gross ROI |
|---------|:---------:|:------:|:---------------:|:---------:|
| The Inner Circle | 6,495 | €45K | +€228K | **5.1×** |
| Rising Stars | 10,256 | €30K | +€95K | **3.2×** |
| Style Explorers | 2,727 | €20K | +€10K | 0.5× |
| Deal Chasers | 768 | €20K | +€4K | 0.2× |
| Dormant Potential | 675 | €10K | +€5K | 0.5× |
| Quality Seekers | 503 | €15K | +€1K | 0.1× |
| **TOTAL PORTFOLIO** | **21,424** | **€140K** | **+€342K** | **2.4×** |

> **ROI definition:** gross return multiple = Scenario Uplift / Annual Investment.
> Not an accounting ROI — uplifts are derived from untested behavioural assumptions
> and require A/B validation before operational adoption.
>
> **Break-even:** If Inner Circle churn reduction falls below **0.6 pp** (from the
> assumed 5 pp), the portfolio gross return multiple falls to ≤1×.

---

## Validation Metrics

| Metric | Result | Benchmark |
|--------|--------|-----------|
| Silhouette Score | 0.4188 | >0.35 = good |
| Davies-Bouldin Index | 0.7604 | <1.0 = good |
| Calinski-Harabasz | 10,975 | Higher = better |
| GMM Posterior Confidence | 0.983 avg; 96.5% >0.80 | >0.80 threshold |

---

## Repository Structure

```
├── technical_report.pdf            ← FINAL DELIVERABLE (PDF at repo root)
├── technical_report.tex            ← LaTeX source
├── master_segmentation.ipynb       ← MAIN NOTEBOOK (full CRISP-DM pipeline)
│
├── src/
│   ├── README.md                   # How-to for src/ modules
│   ├── data_processing.py          # Module: data loading and feature engineering
│   ├── clustering_model.py         # Module: scaling, UMAP, GMM, evaluation
│   └── io/                         # NOT tracked by git — place data here
│       ├── master_transactions.csv    ← input (copy here before running)
│       ├── customer_segmentation_results.csv  ← output
│       └── models/                    ← trained models (pkl)
│
├── assets/                         # Charts generated by the notebook
│   ├── bic_selection.png
│   ├── umap_space.png
│   ├── cluster_heatmap.png
│   ├── clv_analysis.png
│   ├── revenue_at_risk.png
│   ├── roi_framework.png
│   ├── ceo_pnl_heatmap.png
│   └── eda_*.png
│
├── requirements.txt                # Pinned exact dependencies
├── presentation_finale.html        # CEO briefing (interactive)
└── docs/
    └── Jakala_LUISS.pdf                   # Company brief (reference only, not committed)
```

---

## How to Run

### Setup

```bash
pip install -r requirements.txt
mkdir -p src/io/models
cp /path/to/master_transactions.csv src/io/
```

### Main Notebook

```bash
jupyter lab master_segmentation.ipynb
```

Run cells in order. The notebook imports from `src/` automatically.

### Compile the Report

```bash
tectonic technical_report.tex
# Output: technical_report.pdf (at repo root)
```

---

## Key Dependencies

| Library | Version | Usage |
|---------|:-------:|-------|
| pandas | 2.3.2 | Data manipulation |
| scikit-learn | 1.7.2 | Preprocessing, GMM, metrics |
| umap-learn | 0.5.12 | Dimensionality reduction |
| plotly | 6.7.0 | Interactive visualisations |
| seaborn / matplotlib | 0.13.2 / 3.10.6 | Static charts |
| jupyterlab | 4.4.7 | Notebook environment |

---

*JAKALA × LUISS · Data Science in Action · 2025–2026*
*21,424 customers · Mar 2023 – Feb 2025 · CRISP-DM 6 phases + Financial Extension · UMAP + GMM · K=6 · Python 3.13*
