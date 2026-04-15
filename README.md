# Jakala × LUISS — Customer Segmentation Project

Segmentazione della customer base di un fashion retailer italiano tramite
tecniche avanzate di ML non supervisionato (UMAP + Gaussian Mixture Model).
Progetto sviluppato per il corso Data Science in Action — LUISS / JAKALA.

---

## Dataset

- **21,477 clienti** · **24 mesi** di dati transazionali (Mar 2023 – Feb 2025)
- **€11.96M** di revenue osservata · **6 segmenti** identificati
- I file CSV sono esclusi dal tracking git (`.gitignore`). Copiare `master_transactions.csv` nella root prima di eseguire il notebook principale.

---

## Struttura del repository

```
Idea-Factory/
│
│  ── NOTEBOOK ──────────────────────────────────────────────────────────────
├── jakala_segmentation_advanced.ipynb  ← NOTEBOOK PRINCIPALE (pipeline completa)
├── src/
│   ├── cleaning_data.ipynb             # Fase esplorativa: pulizia e EDA iniziale
│   ├── clusters.ipynb                  # Fase esplorativa: test algoritmi (KMeans, DBSCAN…)
│   ├── data_processing.py              # Funzioni di supporto: caricamento e feature engineering
│   └── clustering_model.py             # Funzioni di supporto: scaling, fitting, valutazione
│
│  ── IMMAGINI ──────────────────────────────────────────────────────────────
├── assets/
│   ├── jakala_project_pipeline.svg     # Diagramma pipeline end-to-end
│   ├── clv_analysis.png                # CLV per segmento (Fase 7)
│   ├── revenue_at_risk.png             # Scenario analysis churn (Fase 7)
│   ├── roi_framework.png               # ROI per strategia (Fase 7)
│   ├── ceo_pnl_heatmap.png             # CEO P&L table (Fase 7)
│   └── eda_*.png                       # Grafici EDA (Fase 2)
│
│  ── OUTPUT & DOCS ─────────────────────────────────────────────────────────
├── customer_segmentation_results.csv   # 21,477 clienti: cluster assegnati + KPI
├── strategic_action_plan_v2.html       # CEO Briefing: strategia e ROI per segmento
├── models/                             # Modelli addestrati (pickle)
├── docs/
│   └── Jakala_LUISS.pdf                # Brief originale del progetto
└── requirements.txt                    # Dipendenze Python
```

---

## Come eseguire il progetto

### Setup

```bash
pip install -r requirements.txt
```

### Notebook principale (pipeline completa CRISP-DM)

```bash
jupyter notebook jakala_segmentation_advanced.ipynb
```

Eseguire le celle in ordine. Il notebook è **self-contained**: include tutte le fasi
dalla pulizia dati all'output finale senza dipendenze esterne.

**Struttura interna del notebook (7 fasi):**

| Fase | Contenuto |
|------|-----------|
| 1 | Data Preparation & Quality (parsing date, NA, one-timer flag) |
| 2 | EDA Avanzata (stagionalità, Pareto 80/20, funnel email, bivariata) |
| 3 | Feature Engineering (RFM, discount propensity, email engagement, resi) |
| 4 | Dimensionality Reduction con UMAP (2D + 3D, RobustScaler) |
| 5 | Clustering: DBSCAN (outlier isolation) + GMM (K ottimale via BIC) |
| 6 | Profiling & Business Strategy (naming, radar chart, VIP index geografico) |
| 7 | Financial Modeling (CLV, Revenue at Risk, ROI per strategia, CEO P&L table) |

### Notebook esplorativi (src/)

Contengono la fase di ricerca e sperimentazione, eseguiti **prima** del notebook principale:

1. `src/cleaning_data.ipynb` — pulizia dati, gestione NA, feature iniziali
2. `src/clusters.ipynb` — test comparativo KMeans / DBSCAN / OPTICS / GMM / HC

> **Nota:** questi notebook richiedono i dati in `io/` o nella root. I percorsi
> sono configurabili nella prima cella di ciascun notebook.

---

## Output

| File | Descrizione |
|------|-------------|
| `customer_segmentation_results.csv` | 21,477 righe: cluster_gmm, cluster_name, cluster_confidence, KPI comportamentali |
| `strategic_action_plan_v2.html` | Documento CEO con strategia e ROI per tutti e 6 i segmenti |
| `assets/jakala_project_pipeline.svg` | Diagramma visivo della pipeline |
| `assets/clv_analysis.png` | CLV per segmento |
| `assets/revenue_at_risk.png` | Revenue at Risk — scenario analysis |
| `assets/ceo_pnl_heatmap.png` | CEO P&L heatmap |

---

## Dipendenze principali

| Libreria | Versione minima | Utilizzo |
|----------|:--------------:|---------|
| pandas | 2.0.0 | Data manipulation |
| scikit-learn | 1.3.0 | Preprocessing, GMM, metriche |
| umap-learn | 0.5.5 | Dimensionality reduction |
| plotly | 5.15.0 | Radar chart, scatter interattivi |
| seaborn / matplotlib | 0.12 / 3.7 | Visualizzazioni statiche |

```bash
pip install -r requirements.txt
```
