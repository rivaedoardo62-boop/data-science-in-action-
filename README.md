# Jakala × LUISS — Customer Segmentation Project

Customer base segmentation for an Italian fashion retailer using UMAP + Gaussian Mixture Model (K=6).
Developed for the Data Science in Action course — LUISS / JAKALA.

---

## Dataset

- **21,477 customers** · **24 months** of transactional data (Mar 2023 – Feb 2025)
- **€11.96M** observed revenue · **€15.3M** projected CLV · **6 segments** identified
- CSV files are excluded from git tracking (`.gitignore`). Copy `master_transactions.csv` to the root before running.

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
│  ── OUTPUT & DOCS ──────────────────────────────────────────────────────────
├── customer_segmentation_results.csv   # 21,477 customers: cluster + KPIs
├── presentation_finale.html            # CEO briefing: strategy and ROI per segment
├── models/                             # Trained models (pickle: scaler, reducer, gmm)
├── docs/
│   └── Jakala_LUISS.pdf                # Original project brief
└── requirements.txt                    # Python dependencies
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
| 1 | Data Preparation & Quality (date parsing, NA handling, one-timer flag) |
| 2 | Advanced EDA (seasonality, Pareto 80/20, email funnel, bivariate analysis) |
| 3 | Feature Engineering (RFM, discount propensity, email engagement, returns) |
| 4 | Dimensionality Reduction with UMAP (2D + 3D, RobustScaler) |
| 5 | Clustering: GMM with K=6 (optimal validated by BIC elbow) |
| 6 | Profiling & Business Strategy (persona naming, radar chart, geographic VIP index) |
| 7 | Financial Modelling (CLV, Revenue at Risk, ROI per strategy, CEO P&L table) |

### Exploratory Notebooks (src/)

1. `src/cleaning_data.ipynb` — data cleaning, NA handling, initial feature checks
2. `src/clusters.ipynb` — BIC/AIC K selection, UMAP 2D/3D visualisation, GMM fit

---

## Output

| File | Description |
|------|-------------|
| `customer_segmentation_results.csv` | 21,477 rows: cluster_gmm, cluster_name, cluster_confidence, behavioural KPIs |
| `presentation_finale.html` | CEO document: strategy, ROI, and P&L for all 6 segments |
| `assets/bic_selection.png` | BIC/AIC elbow confirming K=6 |
| `assets/umap_space.png` | UMAP 3D cluster scatter |
| `assets/cluster_heatmap.png` | Segment feature heatmap |
| `assets/clv_analysis.png` | CLV by segment |
| `assets/revenue_at_risk.png` | Revenue at Risk — churn scenario analysis |
| `assets/ceo_pnl_heatmap.png` | CEO P&L heatmap |

---

## 6 Customer Segments

| Segment | Size | Revenue share | Key insight |
|---------|:----:|:-------------:|-------------|
| 💎 The Inner Circle | 25.6% | 42.8% | High-value VIPs — 5,500 customers drive nearly half of revenue |
| 🌱 Rising Stars | 28.3% | 20.2% | Largest segment — natural feeder pool toward The Inner Circle |
| 🛍️ Style Explorers | 15.6% | 13.7% | Multi-category browsers — upsell and bundle opportunity |
| 🏷️ Deal Chasers | 14.2% | 11.9% | Discount-driven (74.6% promo rate) — margin protection priority |
| 👋 Dormant Potential | 11.1% | 3.8% | Low engagement — reactivation campaigns |
| 🔄 Quality Seekers | 5.2% | 7.6% | High return rate (29.1%) — fit issues, need sizing tools |

**Financial summary:** €140K/yr investment · +€376K/yr projected uplift · **2.7× ROI**

---

## Key Dependencies

| Library | Min Version | Usage |
|---------|:-----------:|-------|
| pandas | 2.0.0 | Data manipulation |
| scikit-learn | 1.3.0 | Preprocessing, GMM, metrics |
| umap-learn | 0.5.5 | Dimensionality reduction |
| plotly | 5.15.0 | Radar chart, interactive scatter |
| seaborn / matplotlib | 0.12 / 3.7 | Static visualisations |

```bash
pip install -r requirements.txt
```
