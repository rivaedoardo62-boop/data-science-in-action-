# Pre-Submission Checklist

Run these checks before submitting. All items must be green.

---

## 1. Auto-checker requirements

```bash
# 1a. technical_report.pdf exists at repo root
ls technical_report.pdf

# 1b. Exactly 4 sections with correct titles
grep -n '\\section{' technical_report.tex
# Expected output (exactly these 4, no others):
#   \section{Introduction}
#   \section{Methods}
#   \section{Results and Discussion}
#   \section{Conclusions}

# 1c. Page count <= 15
mdls -name kMDItemNumberOfPages technical_report.pdf
# OR: open and count manually

# 1d. Appendix A and B present
grep -n '\\section{' technical_report.tex | grep -E 'Code Description|Author Contribution'
```

## 2. Fill in TODO placeholders

Search for all TODO items in the report:
```bash
grep -n 'TODO' technical_report.tex
```
Replace each `[TODO: Name Surname]` and `[TODO: Student ID]` with real data.

## 3. Data consistency — verify key numbers match notebook output

| Number | Source | Value |
|--------|--------|-------|
| Customers after cleaning | notebook cell 5 output | 21,424 |
| Observed revenue | notebook cell 31 output | €12,084,646 |
| Clustering features | `src/data_processing.py` `_CLUSTERING_EXCLUDE` | 24 |
| Silhouette Score | notebook cell 22 output | 0.4188 |
| Davies-Bouldin | notebook cell 22 output | 0.7604 |
| Calinski-Harabasz | notebook cell 22 output | 10,975 |
| GMM confidence avg | notebook cell 21 output | 0.983 |
| Portfolio CLV | notebook cell 31 output | €16,187,953 |
| Total investment | notebook cell 33 | €140,000 |
| Total uplift | notebook cell 33 | €342,000 |

## 4. src/io/ setup

```bash
# Check directory exists and is git-ignored
ls src/io/
git status src/io/    # should show nothing (ignored)

# Place input file
ls src/io/master_transactions.csv
```

## 5. Reproducibility check

```bash
# Re-run notebook from scratch and confirm output matches
jupyter nbconvert --to notebook --execute master_segmentation.ipynb \
  --output master_segmentation_executed.ipynb 2>&1 | tail -5

# Verify output CSV was written to src/io/
ls src/io/customer_segmentation_results.csv

# Verify models were saved to src/io/models/
ls src/io/models/
```

## 6. Final compilation

```bash
# Clean compile from scratch
rm -f technical_report.pdf
tectonic technical_report.tex
ls -lh technical_report.pdf
```

## 7. Repository state

```bash
git status
# Confirm:
#   - technical_report.pdf staged/committed
#   - technical_report.tex staged/committed
#   - README.md up to date
#   - src/README.md present
#   - src/io/ NOT committed (gitignored)
#   - No TODO placeholders left in committed files
```
