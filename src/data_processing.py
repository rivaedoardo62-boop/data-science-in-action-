"""
data_processing.py
──────────────────
Single source of truth for all data loading, cleaning, and feature engineering
for the Jakala × LUISS Customer Segmentation project (Team: The Hexagon).

Consumed by: master_segmentation.ipynb

Data source
-----------
master_transactions.csv  —  102,655 transaction lines · 21,480 unique customers
                             24 months: March 2023 – February 2025
                             24 columns (already pre-joined: transactions +
                             customer demographics + product + email campaign)

Pipeline output
---------------
build_customer_matrix()  →  1 row per customer · ~37-column matrix
get_clustering_features() →  24 clustering features, numpy array ready for
                              RobustScaler → UMAP → GMM (cells 13–22 in the
                              master notebook).
"""

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


# ── Module-level constants ─────────────────────────────────────────────────────

# Months that correspond to seasonal sale campaigns (Jan = winter, Jul = summer)
SALE_MONTHS: tuple[int, ...] = (1, 7)

# Top-level product categories present in the dataset
CATEGORIES: list[str] = [
    "Outerwear",
    "Tops",
    "Bottoms",
    "Accessories",
    "Underwear & Nightwear",
    "Sportswear",
    "Child",
]

# Numeric columns excluded from the clustering feature vector.
# Either identifiers, datetime proxies already encoded elsewhere, or
# variables collinear with features we keep.
_CLUSTERING_EXCLUDE: set[str] = {
    "customer_id",
    "last_purchase",        # datetime — encoded as recency_days
    "return_value",         # derivable from monetary × return_rate
    "gross_spend",          # alias of monetary
    "net_spend",            # derivable from gross_spend − return_value
    "n_items_bought",       # collinear with frequency × avg_basket_value
    "avg_ticket",           # collinear with avg_basket_value
    "nl_count",             # raw count — superseded by nl_open_rate / nl_click_rate
    "nl_open_count",
    "nl_click_count",
    "has_newsletter",       # binary collinear with nl_open_rate > 0
}


# ── 1. Loading ─────────────────────────────────────────────────────────────────

def load_master(path: str | Path) -> pd.DataFrame:
    """
    Load master_transactions.csv and parse all date columns.

    The file is a pre-joined dataset: each row is one transaction line item
    with customer demographics and email campaign metrics attached.

    Date formats in the raw file:
      - Date, subscription_date : "DDMONYYYY" (e.g. "03OCT2023")
      - Date_Of_Birth            : ISO "YYYY-MM-DD"
    """
    df = pd.read_csv(path)
    df["Date"]              = pd.to_datetime(df["Date"],              format="%d%b%Y", errors="coerce")
    df["Date_Of_Birth"]     = pd.to_datetime(df["Date_Of_Birth"],     errors="coerce")
    df["subscription_date"] = pd.to_datetime(df["subscription_date"], format="%d%b%Y", errors="coerce")
    return df


# ── 2. Cleaning ────────────────────────────────────────────────────────────────

def clean_master(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply basic data quality rules to the raw transaction DataFrame.

    Rules applied
    -------------
    1. Newsletter metrics (nl_*): fill NaN with 0.
       Rationale: a missing rate means the customer never received a newsletter,
       so zero engagement is the correct imputation.
    2. Drop rows where customer_id or Date is null.
       These rows cannot be attributed to any customer or time window.
    3. Ensure is_return flag exists.
       In the raw data it is already present; this is a safety fallback.
    """
    df = df.copy()
    for col in ["nl_open_rate", "nl_click_rate", "nl_count",
                "nl_open_count", "nl_click_count"]:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    df = df.dropna(subset=["customer_id", "Date"])

    if "is_return" not in df.columns:
        df["is_return"] = (df["line_amount"] < 0).astype(int)

    return df


def remove_negative_spend_anomalies(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Index]:
    """
    Remove customers whose total return value exceeds their total gross spend.

    These are accounting anomalies — typically B2B resellers, multi-account
    holders, or data-entry errors — that would produce negative monetary
    features and distort any distance-based algorithm.

    The HTML presentation references ~52 such customers; this function
    identifies 56 in the raw file (minor version drift between analysis runs).

    Returns
    -------
    df_clean    : transaction DataFrame with anomalous customers removed
    anomaly_ids : pandas Index of removed customer_ids (for audit trail)
    """
    gross = (
        df[df["is_return"] == 0]
        .groupby("customer_id")["line_amount"]
        .sum()
        .rename("gross_spend")
    )
    returns = (
        df[df["is_return"] == 1]
        .groupby("customer_id")["line_amount"]
        .sum()
        .abs()
        .rename("return_value")
    )
    combined    = pd.concat([gross, returns], axis=1).fillna(0)
    anomaly_ids = combined.index[combined["return_value"] > combined["gross_spend"]]
    df_clean    = df[~df["customer_id"].isin(anomaly_ids)].copy()
    return df_clean, anomaly_ids


def flag_one_timers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add is_one_timer column: 1 if the customer had exactly one distinct
    purchase day across the full observation window.

    One-timers represent a structurally different behavioral regime:
    they have no repeat-purchase signal, so their recency reflects a
    single event rather than a pattern. Flagging them allows the model
    to separate them from multi-visit customers without dropping them.
    """
    df = df.copy()
    sessions = (
        df[df["is_return"] == 0]
        .groupby("customer_id")["Date"]
        .nunique()
        .reset_index(name="n_purchase_sessions")
    )
    one_timers = set(
        sessions.loc[sessions["n_purchase_sessions"] == 1, "customer_id"]
    )
    df["is_one_timer"] = df["customer_id"].isin(one_timers).astype(int)
    return df


# ── 3. Feature Engineering ─────────────────────────────────────────────────────

def compute_rfm(
    df: pd.DataFrame,
    ref_date: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """
    RFM + extended monetary features at customer level.

    All aggregations are computed on purchase lines only (is_return == 0).

    Features produced
    -----------------
    recency_days     : days elapsed since last purchase at ref_date
    frequency        : number of distinct purchase days (proxy for visit count)
    monetary         : sum of line_amount on purchase lines (gross spend)
    n_items_bought   : total units purchased (Quantity sum)
    avg_basket_value : monetary / frequency — average spend per visit
    avg_ticket       : mean line_amount per purchase line
    gross_spend      : alias of monetary (kept for profiling clarity)
    return_value     : absolute sum of return line amounts
    net_spend        : gross_spend − return_value
    """
    if ref_date is None:
        ref_date = df["Date"].max()

    purchases = df[df["is_return"] == 0].copy()
    returns   = df[df["is_return"] == 1].copy()

    rfm = purchases.groupby("customer_id").agg(
        last_purchase  = ("Date",        "max"),
        frequency      = ("Date",        "nunique"),
        monetary       = ("line_amount", "sum"),
        n_items_bought = ("Quantity",    "sum"),
        avg_ticket     = ("line_amount", "mean"),
    ).reset_index()

    rfm["recency_days"]     = (ref_date - rfm["last_purchase"]).dt.days
    rfm["avg_basket_value"] = (rfm["monetary"] / rfm["frequency"].clip(lower=1)).round(2)
    rfm["gross_spend"]      = rfm["monetary"]

    return_totals = (
        returns.groupby("customer_id")["line_amount"]
        .sum()
        .abs()
        .reset_index()
        .rename(columns={"line_amount": "return_value"})
    )
    rfm = rfm.merge(return_totals, on="customer_id", how="left")
    rfm["return_value"] = rfm["return_value"].fillna(0)
    rfm["net_spend"]    = rfm["gross_spend"] - rfm["return_value"]

    return rfm


def compute_discount_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Price-sensitivity and discount-propensity features per customer.

    Features produced
    -----------------
    avg_discount_pct         : mean discount_percentage across purchase lines
    pct_items_discounted     : share of purchase lines that carried any discount
    pct_spend_in_sale_season : share of gross spend in sale months (Jan + Jul)

    A high pct_spend_in_sale_season combined with a high avg_discount_pct
    identifies the "Deal Chaser" behavioral profile — customers who shop
    almost exclusively during promotions.
    """
    purchases = df[df["is_return"] == 0].copy()

    disc = purchases.groupby("customer_id").agg(
        avg_discount_pct     = ("discount_percentage", "mean"),
        pct_items_discounted = ("discount_percentage", lambda x: (x > 0).mean()),
    ).reset_index()

    purchases = purchases.copy()
    purchases["_is_sale"]    = purchases["Date"].dt.month.isin(SALE_MONTHS).astype(int)
    purchases["_sale_amt"]   = purchases["line_amount"] * purchases["_is_sale"]

    sale_agg = purchases.groupby("customer_id").agg(
        _total = ("line_amount", "sum"),
        _sale  = ("_sale_amt",  "sum"),
    ).reset_index()
    sale_agg["pct_spend_in_sale_season"] = (
        sale_agg["_sale"] / sale_agg["_total"].replace(0, np.nan)
    ).fillna(0).clip(0, 1)

    disc = disc.merge(
        sale_agg[["customer_id", "pct_spend_in_sale_season"]],
        on="customer_id", how="left",
    )
    disc["pct_spend_in_sale_season"] = disc["pct_spend_in_sale_season"].fillna(0)
    return disc


def compute_email_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Newsletter engagement features per customer.

    The nl_* columns in the raw data are transaction-level constants:
    every row for the same customer carries the same value. max() is
    therefore the correct (identity) aggregation.

    Features produced
    -----------------
    nl_count       : total newsletters received by the customer
    nl_open_rate   : share of newsletters opened (0–1)
    nl_click_rate  : share of newsletters clicked (0–1)
    has_newsletter : 1 if customer is subscribed to the newsletter
    engagement_score : composite index = 0.4 × open_rate + 0.6 × click_rate
                       (click weighted higher — stronger purchase intent signal)
    """
    nl = df.groupby("customer_id").agg(
        nl_count      = ("nl_count",      "max"),
        nl_open_rate  = ("nl_open_rate",  "max"),
        nl_click_rate = ("nl_click_rate", "max"),
    ).reset_index()
    nl["has_newsletter"]   = (nl["nl_count"] > 0).astype(int)
    nl["engagement_score"] = (
        nl["nl_open_rate"] * 0.4 + nl["nl_click_rate"] * 0.6
    ).round(4)
    return nl


def compute_return_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return rate per customer (computed at transaction-line level).

    return_rate = return lines / total lines ∈ [0, 1]

    This is distinct from a quantity-based return rate. A customer who
    returns every other full outfit (line_amount = -€286) contributes
    equally to return_rate regardless of how many units were in the order.
    """
    ret = df.groupby("customer_id").agg(
        total_lines  = ("is_return", "count"),
        return_lines = ("is_return", "sum"),
    ).reset_index()
    ret["return_rate"] = (ret["return_lines"] / ret["total_lines"]).round(4)
    return ret[["customer_id", "return_rate"]]


def compute_category_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Category breadth, category mix, and channel mix per customer.

    Computed on purchase lines only (is_return == 0).

    Features produced
    -----------------
    n_categories_explored : number of distinct top-level categories purchased
                            High value → Style Explorer behavioral profile
    pct_<Category>        : share of purchase lines in each of the 7 categories
                            (column names are normalised to snake_case)
    ecommerce_share       : share of purchases via E-commerce channel
    outlet_share          : share of purchases via Outlet channel
    """
    purchases = df[df["is_return"] == 0].copy()

    breadth = (
        purchases.groupby("customer_id")["category"]
        .nunique()
        .reset_index(name="n_categories_explored")
    )

    # Category mix: one-hot encode → aggregate → normalise by total lines
    total_lines = (
        purchases.groupby("customer_id")
        .size()
        .reset_index(name="_total_lines")
    )

    cat_wide = (
        purchases.assign(_one=1)
        .pivot_table(
            index="customer_id",
            columns="category",
            values="_one",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )
    # Normalise raw counts → percentages
    cat_wide = cat_wide.merge(total_lines, on="customer_id", how="left")
    cat_cols = [c for c in cat_wide.columns if c not in ("customer_id", "_total_lines")]
    for col in cat_cols:
        safe_name = "pct_" + col.lower().replace(" ", "_").replace("&", "and")
        cat_wide[safe_name] = (cat_wide[col] / cat_wide["_total_lines"]).fillna(0).round(4)
        cat_wide = cat_wide.drop(columns=[col])
    cat_wide = cat_wide.drop(columns=["_total_lines"])

    # Channel mix
    if "store_channel" in purchases.columns:
        purchases = purchases.copy()
        purchases["_is_ecom"]   = (purchases["store_channel"] == "E-commerce").astype(int)
        purchases["_is_outlet"] = (purchases["store_channel"] == "Outlet").astype(int)
        channel = purchases.groupby("customer_id").agg(
            ecommerce_share = ("_is_ecom",   "mean"),
            outlet_share    = ("_is_outlet", "mean"),
        ).reset_index()
    else:
        channel = purchases[["customer_id"]].drop_duplicates().copy()
        channel["ecommerce_share"] = 0.0
        channel["outlet_share"]    = 0.0

    result = breadth.merge(cat_wide, on="customer_id", how="left")
    result = result.merge(channel,   on="customer_id", how="left")
    return result


def compute_demographics(
    df: pd.DataFrame,
    ref_date: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """
    Demographic and account-tenure features per customer.

    Features produced
    -----------------
    Gender        : biological sex (categorical — used for profiling, not clustering)
    province      : Italian province (categorical — geographic profiling only)
    age_years     : customer age at ref_date (from Date_Of_Birth)
    tenure_days   : days since subscription_date at ref_date
    is_one_timer  : flag added upstream by flag_one_timers()
    """
    if ref_date is None:
        ref_date = df["Date"].max()

    demo = df.groupby("customer_id").agg(
        Gender            = ("Gender",            "first"),
        province          = ("province",          "first"),
        Date_Of_Birth     = ("Date_Of_Birth",     "first"),
        subscription_date = ("subscription_date", "first"),
        is_one_timer      = ("is_one_timer",      "max"),
    ).reset_index()

    demo["age_years"]   = (
        (ref_date - demo["Date_Of_Birth"]).dt.days / 365.25
    ).round(1)
    demo["tenure_days"] = (
        (ref_date - demo["subscription_date"]).dt.days
    ).clip(lower=0)

    return demo


# ── 4. Master Pipeline ─────────────────────────────────────────────────────────

def build_customer_matrix(
    df: pd.DataFrame,
    ref_date: Optional[pd.Timestamp] = None,
    remove_anomalies: bool = True,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    End-to-end pipeline: raw transactions → 1-row-per-customer feature matrix.

    Execution order
    ---------------
    1. clean_master()                  — fill NaN, drop bad rows, ensure flags
    2. remove_negative_spend_anomalies() — remove ~56 accounting anomalies
    3. flag_one_timers()               — mark single-visit customers
    4. compute_rfm()                   — recency, frequency, monetary, basket
    5. compute_discount_features()     — discount propensity + sale seasonality
    6. compute_email_features()        — newsletter engagement + composite score
    7. compute_return_features()       — return rate
    8. compute_category_features()     — breadth + category mix + channel mix
    9. compute_demographics()          — age, tenure, gender, province
    10. Merge all tables on customer_id (left join from RFM base)
    11. Fill NaN on numeric columns with 0

    Parameters
    ----------
    df               : raw DataFrame from load_master()
    ref_date         : reference date for recency/age/tenure; defaults to max(Date)
    remove_anomalies : if True, removes customers where return_value > gross_spend
    verbose          : if True, prints row/column counts at key steps

    Returns
    -------
    customer_matrix : DataFrame · 1 row per customer · ~35 columns
    """
    if verbose:
        print(f"[build_customer_matrix] Input: {df.shape[0]:,} transaction rows")

    df = clean_master(df)

    if remove_anomalies:
        df, removed = remove_negative_spend_anomalies(df)
        if verbose:
            print(f"  Anomalies removed : {len(removed)} customers "
                  f"(return_value > gross_spend)")

    df = flag_one_timers(df)

    if ref_date is None:
        ref_date = df["Date"].max()

    if verbose:
        print(f"  Reference date    : {ref_date.date()}")

    rfm  = compute_rfm(df, ref_date)
    disc = compute_discount_features(df)
    nl   = compute_email_features(df)
    ret  = compute_return_features(df)
    cat  = compute_category_features(df)
    demo = compute_demographics(df, ref_date)

    cm = rfm.copy()
    for tbl in [disc, nl, ret, cat, demo]:
        cm = cm.merge(tbl, on="customer_id", how="left")

    # Fill NaN on numeric columns only — preserve Gender and province as strings
    num_cols = cm.select_dtypes(include="number").columns
    cm[num_cols] = cm[num_cols].fillna(0)

    if verbose:
        print(f"  Customer matrix   : {cm.shape[0]:,} customers "
              f"× {cm.shape[1]} features")

    return cm


def get_clustering_features(
    customer_matrix: pd.DataFrame,
) -> tuple[np.ndarray, list[str]]:
    """
    Extract the numeric feature matrix passed to RobustScaler → UMAP → GMM.

    Drops identifier columns, datetime proxies, and collinear features
    (see _CLUSTERING_EXCLUDE). Keeps all remaining numeric columns,
    including the dynamic pct_<category> and ecommerce_share columns.

    Raises ValueError if any NaN values remain (indicates a pipeline bug
    upstream — should never happen after build_customer_matrix()).

    Returns
    -------
    X            : np.ndarray · shape (n_customers, n_features)
    feature_cols : list[str] · column names in the same order as X
    """
    feature_cols = [
        c for c in customer_matrix.columns
        if c not in _CLUSTERING_EXCLUDE
        and pd.api.types.is_numeric_dtype(customer_matrix[c])
        and not c.startswith("_")
    ]
    feature_cols = sorted(feature_cols)  # deterministic column ordering

    X = customer_matrix[feature_cols].values.astype(np.float64)

    if np.isnan(X).any():
        bad_cols = [
            feature_cols[i]
            for i in np.where(np.isnan(X).any(axis=0))[0]
        ]
        raise ValueError(
            f"NaN detected in clustering features after pipeline — "
            f"check these columns: {bad_cols}"
        )

    return X, feature_cols
