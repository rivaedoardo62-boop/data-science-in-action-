# Jakala × LUISS — Customer Segmentation Project

Customer base segmentation for an Italian fashion retailer using advanced
unsupervised ML techniques (UMAP + Gaussian Mixture Model).
Developed for the Data Science in Action course — LUISS / JAKALA.

---

## Dataset

- **21,477 customers** · **24 months** of transactional data (Mar 2023 – Feb 2025)
- **€11.96M** observed revenue · **6 segments** identified
- CSV files are excluded from git tracking (`.gitignore`). Copy `master_transactions.csv` to the root before running the main notebook.

---

## Repository Structure

```
Idea-Factory/
│
│  ── NOTEBOOKS ─────────────────────────────────────────────────────────────
├── jakala_segmentation_advanced.ipynb  ← MAIN NOTEBOOK (full pipeline)
├── src/
│   ├── cleaning_data.ipynb             # Exploratory: data cleaning and initial EDA
│   ├── clusters.ipynb                  # Exploratory: algorithm comparison (KMeans, DBSCAN…)
│   ├── data_processing.py              # Support functions: loading and feature engineering
│   └── clustering_model.py             # Support functions: scaling, fitting, evaluation
│
│  ── IMAGES ──────────────────────────────────────────────────────────────
├── assets/
│   ├── jakala_project_pipeline.svg     # End-to-end pipeline diagram
│   ├── clv_analysis.png                # CLV by segment (Phase 7)
│   ├── revenue_at_risk.png             # Churn scenario analysis (Phase 7)
│   ├── roi_framework.png               # ROI by strategy (Phase 7)
│   ├── ceo_pnl_heatmap.png             # CEO P&L table (Phase 7)
│   └── eda_*.png                       # EDA charts (Phase 2)
│
│  ── OUTPUT & DOCS ─────────────────────────────────────────────────────────
├── customer_segmentation_results.csv   # 21,477 customers: assigned clusters + KPIs
├── presentation_finale.html            # CEO Briefing: strategy and ROI per segment
├── models/                             # Trained models (pickle)
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

### Main Notebook (full CRISP-DM pipeline)

```bash
jupyter notebook jakala_segmentation_advanced.ipynb
```

Run cells in order. The notebook is **self-contained**: it includes all phases
from data cleaning to final output with no external dependencies.

**Internal notebook structure (7 phases):**

| Phase | Content |
|-------|---------|
| 1 | Data Preparation & Quality (date parsing, NA handling, one-timer flag) |
| 2 | Advanced EDA (seasonality, Pareto 80/20, email funnel, bivariate analysis) |
| 3 | Feature Engineering (RFM, discount propensity, email engagement, returns) |
| 4 | Dimensionality Reduction with UMAP (2D + 3D, RobustScaler) |
| 5 | Clustering: DBSCAN (outlier isolation) + GMM (optimal K via BIC) |
| 6 | Profiling & Business Strategy (naming, radar chart, geographic VIP index) |
| 7 | Financial Modeling (CLV, Revenue at Risk, ROI per strategy, CEO P&L table) |

### Exploratory Notebooks (src/)

Contain the research and experimentation phase, run **before** the main notebook:

1. `src/cleaning_data.ipynb` — data cleaning, NA handling, initial features
2. `src/clusters.ipynb` — comparative test: KMeans / DBSCAN / OPTICS / GMM / HC

> **Note:** these notebooks require the data in `io/` or in the root. Paths
> are configurable in the first cell of each notebook.

---

## Output

| File | Description |
|------|-------------|
| `customer_segmentation_results.csv` | 21,477 rows: cluster_gmm, cluster_name, cluster_confidence, behavioral KPIs |
| `presentation_finale.html` | CEO document with strategy and ROI for all 6 segments |
| `assets/jakala_project_pipeline.svg` | Visual pipeline diagram |
| `assets/clv_analysis.png` | CLV by segment |
| `assets/revenue_at_risk.png` | Revenue at Risk — scenario analysis |
| `assets/ceo_pnl_heatmap.png` | CEO P&L heatmap |

---

## 6 Customer Segments

| Segment | Size | Description |
|---------|------|-------------|
| 💎 The Inner Circle | ~8% | High-value VIPs — frequent, high AOV, low discount dependency |
| 🔄 Quality Seekers | ~12% | High return rate (33%) — fit issues, need size tools |
| 🛍️ Style Explorers | ~18% | Multi-category browsers — upsell and bundle opportunity |
| 🏷️ Deal Chasers | ~22% | Discount-driven — protect margin, manage channel profitability |
| 🌱 Rising Stars | ~15% | Growing mid-tier — nurture toward VIP status |
| 👋 Dormant Potential | ~25% | One-timers and low-engagement — reactivation campaigns |

> **Cluster -1** (1 customer) is a statistical outlier isolated by DBSCAN — not a targetable segment.

---

## Key Dependencies

| Library | Min Version | Usage |
|---------|:-----------:|-------|
| pandas | 2.0.0 | Data manipulation |
| scikit-learn | 1.3.0 | Preprocessing, GMM, metrics |
| umap-learn | 0.5.5 | Dimensionality reduction |
| plotly | 5.15.0 | Radar chart, interactive scatter |
| seaborn / matplotlib | 0.12 / 3.7 | Static visualizations |

```bash
pip install -r requirements.txt
```
