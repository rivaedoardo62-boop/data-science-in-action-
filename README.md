# Jakala – Customer Segmentation Project

Analisi di segmentazione clienti sviluppata nell'ambito del progetto Jakala / LUISS.

## Obiettivo

Pulire, integrare e analizzare dati di clienti, prodotti e transazioni per identificare cluster di clienti significativi tramite tecniche di machine learning non supervisionato.

## Struttura del repository

```
project jakala/
├── src/
│   ├── cleaning_data.ipynb   # Pulizia e preprocessing dei dati
│   └── clusters.ipynb        # Clustering e analisi dei segmenti
├── docs/
│   └── Jakala_LUISS.pdf      # Brief e documentazione del progetto
├── ROW DATA/                 # Dati grezzi originali (gitignored)
├── MERGERED DATA/            # Dati integrati (gitignored)
└── io/                       # Dataset aziendali (gitignored)
```

## Come eseguire i notebook

1. Assicurarsi di avere Python 3 e Jupyter installati:
   ```bash
   pip install jupyter pandas numpy scikit-learn matplotlib seaborn
   ```

2. Avviare Jupyter:
   ```bash
   jupyter notebook
   ```

3. Eseguire i notebook nell'ordine:
   - Prima `src/cleaning_data.ipynb` — produce i dati puliti
   - Poi `src/clusters.ipynb` — esegue il clustering sui dati puliti

## Note

I file di dati (CSV, TXT, XLSX) sono esclusi dal tracking git tramite `.gitignore`. Inserire i dataset nella cartella `io/` prima di eseguire i notebook.
