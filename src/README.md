# src/ — Source Code Reference

Two Python modules support `master_segmentation.ipynb`. All transient data
(inputs, outputs, saved models) go to `src/io/`, which is **git-ignored** and
must be created locally before running.

## Notebook Execution Order

| # | Notebook | Location | Purpose |
|---|----------|----------|---------|
| 1 | `master_segmentation.ipynb` | root | **Canonical reproducible pipeline** — EDA → features → UMAP → GMM K=6 → CLV → ROI |

> `src/cleaning_data.ipynb` and `src/clusters.ipynb` are **exploratory
> development notebooks** used during iteration. They are superseded by
> `master_segmentation.ipynb` and do not need to be run for reproducibility
> or evaluation.

## Module Roles

| File | Purpose |
|------|---------|
| `data_processing.py` | Data loading, cleaning, negative-spend audit, feature engineering — outputs the 24-column normalised matrix |
| `clustering_model.py` | RobustScaler, UMAP reduction, GMM K=6, evaluation metrics (Silhouette / DB / CH), model persistence to `src/io/models/` |

## Placing the Input Data

Place the raw input file at:

```
src/io/master_transactions.csv
```

Create the directory structure before running:

```bash
mkdir -p src/io/models
cp /path/to/master_transactions.csv src/io/
```

## Running the Pipeline

```bash
pip install -r requirements.txt
jupyter lab master_segmentation.ipynb
```

Run all cells top-to-bottom (kernel: Python 3.13). Outputs are written to `src/io/`.

## Compiling the Technical Report

The report uses `fontspec` and requires **XeLaTeX** (or LuaLaTeX):

```bash
xelatex technical_report.tex
xelatex technical_report.tex   # second pass — resolves cross-references
```

Or with `latexmk`:

```bash
latexmk -xelatex technical_report.tex
```

Output: `technical_report.pdf` (max 15 pages per project rules).

## Compiling the Presentations

The Beamer skeletons use standard LaTeX (pdflatex or xelatex):

```bash
pdflatex checkpoint_presentation.tex
pdflatex pitch_presentation.tex
```

## src/io/ Layout (git-ignored — create locally)

```
src/io/
├── master_transactions.csv             ← input: place here before running
├── customer_segmentation_results.csv   ← output: written by notebook
└── models/
    ├── scaler.pkl                      ← RobustScaler (24 features)
    ├── reducer_umap3d.pkl              ← UMAP 3D reducer (clustering input)
    ├── reducer_umap2d.pkl              ← UMAP 2D reducer (visualisation only)
    └── gmm_k6.pkl                      ← GaussianMixture K=6
```

## Key Parameters

| Parameter | Value | Location |
|-----------|-------|----------|
| `FIXED_K` | 6 | `clustering_model.py` constant |
| UMAP `n_neighbors` | 30 | `reduce_umap()` default |
| UMAP `min_dist` | 0.1 | `reduce_umap()` default |
| Winsorize quantile | 0.99 | `winsorize()` default |
| WACC proxy (r) | 0.10 | notebook cell 31 |
| Random seed | 42 | notebook `SEED` constant |
