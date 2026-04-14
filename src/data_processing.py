"""
data_processing.py
------------------
Funzioni di caricamento, pulizia e feature engineering per il progetto
Jakala × LUISS Customer Segmentation.

Usato da:
  - src/cleaning_data.ipynb
  - jakala_segmentation_advanced.ipynb (opzionale, il notebook è self-contained)
"""

from pathlib import Path
import numpy as np
import pandas as pd


# ── 1. Caricamento ────────────────────────────────────────────────────────────

def load_master(path: str | Path) -> pd.DataFrame:
    """Carica master_transactions.csv e converte le date."""
    df = pd.read_csv(path)
    df["Date"]              = pd.to_datetime(df["Date"], format="%d%b%Y", errors="coerce")
    df["Date_Of_Birth"]     = pd.to_datetime(df["Date_Of_Birth"], errors="coerce")
    df["subscription_date"] = pd.to_datetime(df["subscription_date"],
                                             format="%d%b%Y", errors="coerce")
    return df


# ── 2. Pulizia ────────────────────────────────────────────────────────────────

def clean_master(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pulizia base:
    - Riempie i rate newsletter mancanti con 0 (cliente senza iscrizione)
    - Rimuove righe con customer_id o Date nulli
    - Aggiunge flag is_return (1 se line_amount < 0)
    """
    df = df.copy()
    for col in ["nl_open_rate", "nl_click_rate", "nl_count", "nl_open_count", "nl_click_count"]:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    df = df.dropna(subset=["customer_id", "Date"])
    if "line_amount" in df.columns and "is_return" not in df.columns:
        df["is_return"] = (df["line_amount"] < 0).astype(int)
    return df


def flag_one_timers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggiunge colonna is_one_timer:
    1 se il cliente ha un solo giorno di acquisto distinto nel dataset.
    """
    df = df.copy()
    sessions = (
        df[df["is_return"] == 0]
        .groupby("customer_id")["Date"]
        .nunique()
        .reset_index(name="n_purchase_sessions")
    )
    one_timers = set(sessions.loc[sessions["n_purchase_sessions"] == 1, "customer_id"])
    df["is_one_timer"] = df["customer_id"].isin(one_timers).astype(int)
    return df


# ── 3. Feature Engineering ────────────────────────────────────────────────────

def compute_rfm(df: pd.DataFrame, ref_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """
    Calcola le feature RFM classiche a livello cliente.

    Returns
    -------
    DataFrame con colonne:
        customer_id, last_purchase, frequency, monetary,
        n_items_bought, avg_basket_value, recency_days
    """
    if ref_date is None:
        ref_date = df["Date"].max()
    purchases = df[df["is_return"] == 0].copy()
    rfm = purchases.groupby("customer_id").agg(
        last_purchase  = ("Date",        "max"),
        frequency      = ("Date",        "nunique"),
        monetary       = ("line_amount", "sum"),
        n_items_bought = ("Quantity",    "sum"),
    ).reset_index()
    rfm["recency_days"]     = (ref_date - rfm["last_purchase"]).dt.days
    rfm["avg_basket_value"] = (rfm["monetary"] / rfm["frequency"].clip(lower=1)).round(2)
    return rfm


def compute_discount_features(df: pd.DataFrame) -> pd.DataFrame:
    """Propensione allo sconto per cliente."""
    purchases = df[df["is_return"] == 0].copy()
    disc = purchases.groupby("customer_id").agg(
        avg_discount_pct     = ("discount_percentage", "mean"),
        pct_items_discounted = ("discount_percentage", lambda x: (x > 0).mean()),
        max_discount_applied = ("discount_percentage", "max"),
    ).reset_index()
    return disc


def compute_email_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engagement newsletter per cliente."""
    nl = df.groupby("customer_id").agg(
        nl_count      = ("nl_count",      "max"),
        nl_open_rate  = ("nl_open_rate",  "max"),
        nl_click_rate = ("nl_click_rate", "max"),
    ).reset_index()
    nl["has_newsletter"]   = (nl["nl_count"] > 0).astype(int)
    nl["engagement_score"] = (nl["nl_open_rate"] * 0.4 + nl["nl_click_rate"] * 0.6).round(4)
    return nl


def compute_return_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return rate per cliente."""
    ret = df.groupby("customer_id").agg(
        total_lines  = ("is_return", "count"),
        return_lines = ("is_return", "sum"),
    ).reset_index()
    ret["return_rate"] = (ret["return_lines"] / ret["total_lines"]).round(4)
    return ret[["customer_id", "return_rate"]]


def build_customer_matrix(df: pd.DataFrame, ref_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """
    Pipeline completa: aggrega tutte le feature a livello cliente.

    Returns
    -------
    customer_matrix : DataFrame (1 riga = 1 cliente)
    """
    if ref_date is None:
        ref_date = df["Date"].max()

    rfm   = compute_rfm(df, ref_date)
    disc  = compute_discount_features(df)
    nl    = compute_email_features(df)
    ret   = compute_return_features(df)

    demo = df.groupby("customer_id").agg(
        Gender            = ("Gender",            "first"),
        province          = ("province",          "first"),
        Date_Of_Birth     = ("Date_Of_Birth",     "first"),
        subscription_date = ("subscription_date", "first"),
        is_one_timer      = ("is_one_timer",      "max"),
    ).reset_index()
    demo["age_years"]   = ((ref_date - demo["Date_Of_Birth"]).dt.days / 365.25).round(1)
    demo["tenure_days"] = (ref_date - demo["subscription_date"]).dt.days

    cm = rfm.copy()
    for tbl in [disc, nl, ret, demo]:
        cm = cm.merge(tbl, on="customer_id", how="left")

    # Riempi NaN su feature numeriche con 0
    num_cols = cm.select_dtypes(include="number").columns.tolist()
    cm[num_cols] = cm[num_cols].fillna(0)

    return cm
