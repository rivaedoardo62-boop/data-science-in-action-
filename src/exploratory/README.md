# `src/exploratory/` — Development Artefacts

These notebooks are **not part of the canonical pipeline** and are not required to
reproduce any figure or number in the technical report.

They are kept under version control as evidence of the exploratory work that
preceded the final consolidated `master_segmentation.ipynb`:

| File | What it explored |
|---|---|
| `cleaning_data.ipynb` | First-pass cleaning rules, anomaly detection, return-rate audit, schema validation. The conclusions (notably the 56-customer anomaly threshold) were carried over to `src/data_processing.py` and are now applied automatically by `build_customer_matrix()`. |
| `clusters.ipynb` | Comparative experiments across K-Means, DBSCAN, OPTICS, Agglomerative HC. The verdicts (UMAP+GMM with K=6 wins) drove the locked configuration in `src/clustering_model.py`. |

For reproducible execution of the final pipeline, run only
`master_segmentation.ipynb` at the repo root.
