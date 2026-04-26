#!/usr/bin/env python3
"""
generate_report.py
──────────────────
Generates docs/academic_report.pdf — the formal academic project report for the
Jakala × LUISS Customer Segmentation project.

Requirements:
    pip install reportlab

Run:
    python generate_report.py

Output:
    docs/academic_report.pdf
"""

from pathlib import Path
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT

# ── Constants ─────────────────────────────────────────────────────────────────

PAGE_W, PAGE_H = A4
MARGIN_LR = 2.5 * cm
MARGIN_TOP = 2.5 * cm
MARGIN_BOT = 2.2 * cm

NAVY    = colors.HexColor("#1a1a2e")
BLUE    = colors.HexColor("#16213e")
ACCENT  = colors.HexColor("#4361ee")
GREY    = colors.HexColor("#555555")
LGREY   = colors.HexColor("#cccccc")
BGLIGHT = colors.HexColor("#f8f9ff")
BGBOX   = colors.HexColor("#eef2ff")

OUTPUT = Path("docs/academic_report.pdf")


# ── Page decorators ───────────────────────────────────────────────────────────

def _header_footer(canvas, doc):
    canvas.saveState()
    page = canvas.getPageNumber()
    if page > 1:
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(GREY)
        # footer left
        canvas.drawString(MARGIN_LR, 1.4 * cm,
                          "LUISS Guido Carli × Jakala  ·  Data Science in Action  ·  2026")
        # footer right
        canvas.drawRightString(PAGE_W - MARGIN_LR, 1.4 * cm,
                               f"Customer Segmentation Report  ·  p. {page}")
        # footer rule
        canvas.setStrokeColor(LGREY)
        canvas.setLineWidth(0.4)
        canvas.line(MARGIN_LR, 1.85 * cm, PAGE_W - MARGIN_LR, 1.85 * cm)
        # header rule
        canvas.line(MARGIN_LR, PAGE_H - MARGIN_TOP + 0.4 * cm,
                    PAGE_W - MARGIN_LR, PAGE_H - MARGIN_TOP + 0.4 * cm)
    canvas.restoreState()


# ── Style factory ─────────────────────────────────────────────────────────────

def _styles():
    S = {}

    def add(name, **kw):
        S[name] = ParagraphStyle(name, **kw)

    # ---- title page
    add("doc_title",  fontName="Helvetica-Bold",   fontSize=20, leading=26,
        spaceAfter=10, textColor=NAVY, alignment=TA_LEFT)
    add("doc_sub",    fontName="Helvetica",         fontSize=13, leading=18,
        spaceAfter=6,  textColor=BLUE, alignment=TA_LEFT)
    add("doc_meta",   fontName="Helvetica",         fontSize=9.5, leading=14,
        spaceAfter=5,  textColor=GREY, alignment=TA_LEFT)

    # ---- headings
    add("h1", fontName="Helvetica-Bold",  fontSize=13, leading=17,
        spaceBefore=18, spaceAfter=5, textColor=NAVY)
    add("h2", fontName="Helvetica-Bold",  fontSize=11, leading=15,
        spaceBefore=12, spaceAfter=4, textColor=BLUE)
    add("h3", fontName="Helvetica-BoldOblique", fontSize=10, leading=14,
        spaceBefore=8,  spaceAfter=3, textColor=colors.HexColor("#333333"))

    # ---- body
    add("body", fontName="Helvetica", fontSize=10, leading=15,
        spaceBefore=3, spaceAfter=6,
        alignment=TA_JUSTIFY, textColor=colors.HexColor("#222222"))
    add("body_tight", fontName="Helvetica", fontSize=10, leading=14,
        spaceBefore=2, spaceAfter=3,
        alignment=TA_JUSTIFY, textColor=colors.HexColor("#222222"))

    # ---- abstract / callout
    add("abstract", fontName="Helvetica-Oblique", fontSize=10, leading=15,
        spaceBefore=4, spaceAfter=6, alignment=TA_JUSTIFY,
        leftIndent=1*cm, rightIndent=1*cm, textColor=colors.HexColor("#333333"))
    add("callout", fontName="Helvetica", fontSize=9.5, leading=14,
        spaceBefore=4, spaceAfter=4, alignment=TA_JUSTIFY,
        leftIndent=0.6*cm, rightIndent=0.6*cm,
        backColor=BGBOX, borderColor=ACCENT, borderWidth=0.8,
        borderPadding=8, textColor=NAVY)

    # ---- bullet
    add("bullet", fontName="Helvetica", fontSize=10, leading=14,
        spaceBefore=2, spaceAfter=3, alignment=TA_JUSTIFY,
        leftIndent=0.8*cm, firstLineIndent=-0.45*cm,
        textColor=colors.HexColor("#222222"))

    # ---- monospace / formula
    add("mono", fontName="Courier", fontSize=9, leading=13,
        spaceBefore=4, spaceAfter=4, leftIndent=1.2*cm,
        backColor=colors.HexColor("#f4f4f4"))

    # ---- caption
    add("caption", fontName="Helvetica-Oblique", fontSize=8.5, leading=12,
        spaceBefore=2, spaceAfter=10, alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"))

    # ---- keywords
    add("kw", fontName="Helvetica", fontSize=9, leading=13,
        spaceAfter=6, textColor=GREY)

    return S


# ── Shorthand helpers ─────────────────────────────────────────────────────────

def P(text, s, key="body"):   return Paragraph(text, s[key])
def H1(text, s):              return Paragraph(text, s["h1"])
def H2(text, s):              return Paragraph(text, s["h2"])
def H3(text, s):              return Paragraph(text, s["h3"])
def B(text, s):               return Paragraph(f"•  {text}", s["bullet"])
def SP(n=6):                  return Spacer(1, n)
def HR():
    return HRFlowable(width="100%", thickness=0.4,
                      color=LGREY, spaceAfter=6, spaceBefore=4)


def tbl(data, col_w, header_color=NAVY):
    t = Table(data, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1,  0), header_color),
        ("TEXTCOLOR",     (0, 0), (-1,  0), colors.white),
        ("FONTNAME",      (0, 0), (-1,  0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1,  0), 8.5),
        ("BOTTOMPADDING", (0, 0), (-1,  0), 7),
        ("TOPPADDING",    (0, 0), (-1,  0), 7),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8.5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("TOPPADDING",    (0, 1), (-1, -1), 5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, BGLIGHT]),
        ("GRID",          (0, 0), (-1, -1), 0.25, LGREY),
        ("LINEBELOW",     (0, 0), (-1,  0), 1.2, header_color),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    return t


# ── Story ─────────────────────────────────────────────────────────────────────

def build_story(s):
    S = []

    # ════════════════════════════════════════════════════════════════════════════
    # TITLE PAGE
    # ════════════════════════════════════════════════════════════════════════════
    S += [
        SP(3 * cm),
        P("Customer Segmentation for an Italian Fashion Retailer", s, "doc_title"),
        P("A Data-Driven Approach Using UMAP and Gaussian Mixture Models", s, "doc_sub"),
        HRFlowable(width="100%", thickness=2, color=NAVY,
                   spaceAfter=14, spaceBefore=10),
        SP(0.4*cm),
        P("Group Project Report", s, "doc_meta"),
        P("Data Science in Action — LUISS Guido Carli", s, "doc_meta"),
        P("In partnership with Jakala S.p.A. — JScience Advanced Analytics", s, "doc_meta"),
        SP(0.35*cm),
        P("Academic Year 2025–2026  ·  April 2026", s, "doc_meta"),
        SP(2.5*cm),
        P("<b>Business Case:</b> Customer Segmentation  ·  Fashion Retailer Company", s, "doc_meta"),
        P("<b>Dataset:</b> 21,477 customers  ·  March 2023 – February 2025", s, "doc_meta"),
        P("<b>Revenue (observed):</b> €11.96M  ·  <b>CLV (projected):</b> €15.3M", s, "doc_meta"),
        P("<b>Methodology:</b> RobustScaler → UMAP (3D) → GMM (K=6)", s, "doc_meta"),
        SP(0.8*cm),
        HR(),
        P(
            "This report presents the complete methodology, technical decisions, statistical "
            "evaluation, and business implications of a customer segmentation project developed "
            "for a large Italian fashion retailer. It is submitted as the final group assessment "
            "deliverable for the Data Science in Action module at LUISS Guido Carli, in the "
            "context of the Jakala business case challenge. Every analytical and methodological "
            "decision documented herein is justified with reference to both technical criteria "
            "and business requirements.",
            s, "abstract"
        ),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════════════════════
    # ABSTRACT
    # ════════════════════════════════════════════════════════════════════════════
    S += [
        H1("Abstract", s), HR(),
        P(
            "This report documents a complete customer segmentation project conducted on the "
            "transactional database of an anonymised Italian fashion retailer. The dataset "
            "encompasses 21,477 registered customers, approximately 24 months of transactional "
            "history (March 2023 – February 2025), and four source tables: customer anagraphics, "
            "line-level transactions (including returns), product catalogue, and email marketing "
            "interactions. Following the CRISP-DM framework, we engineered 32 behavioural "
            "features across six dimensions — Recency/Frequency/Monetary (RFM), discount "
            "propensity, email engagement, return behaviour, category affinity, and channel mix "
            "— before applying RobustScaler normalisation and UMAP dimensionality reduction to "
            "three components. A Gaussian Mixture Model with K=6 components, selected via "
            "Bayesian Information Criterion (BIC) optimisation and validated against operational "
            "constraints, identified six behaviourally distinct customer segments. Statistical "
            "evaluation using Silhouette Score, Davies-Bouldin Index, and Calinski-Harabasz Score "
            "confirms cluster validity. The six segments — The Inner Circle, Rising Stars, Style "
            "Explorers, Deal Chasers, Dormant Potential, and Quality Seekers — exhibit "
            "substantially different behavioural profiles that prescribe distinct marketing "
            "levers, enabling the transition from mass marketing to targeted, data-driven "
            "customer engagement. A financial modelling framework projects €15.3M in discounted "
            "Customer Lifetime Value, with a proposed €140K/year strategic investment expected "
            "to yield +€718K/year in incremental revenue, corresponding to a 5.1× gross return multiple.",
            s, "abstract"
        ),
        SP(8),
        P(
            "<b>Keywords:</b> customer segmentation, unsupervised learning, Gaussian Mixture "
            "Model, UMAP, RFM, Customer Lifetime Value, fashion retail, CRISP-DM, BIC",
            s, "kw"
        ),
        SP(8),
    ]

    # ════════════════════════════════════════════════════════════════════════════
    # 1. INTRODUCTION
    # ════════════════════════════════════════════════════════════════════════════
    S += [
        H1("1.  Introduction", s), HR(),
        H2("1.1  Digitalisation and the Strategic Value of Customer Data", s),
        P(
            "The digitalisation of the retail sector has fundamentally altered the relationship "
            "between firms and their customers. Physical point-of-sale interactions, once the "
            "primary source of purchase data, have been supplemented — and in many cases "
            "supplanted — by digital touchpoints that generate high-frequency, granular "
            "behavioural signals: transaction timestamps, product-level purchase records, "
            "promotional exposure and response, returns, and email marketing interactions. "
            "The aggregate of these signals constitutes a strategic intangible asset whose "
            "value lies not in its raw form, but in the firm's capacity to extract actionable "
            "intelligence from it.", s
        ),
        P(
            "Customer segmentation — the partitioning of a heterogeneous customer base into "
            "homogeneous groups sharing similar behavioural profiles — represents one of the "
            "most direct mechanisms by which firms convert data assets into competitive "
            "advantage. Modern machine learning approaches allow for the discovery of naturally "
            "occurring clusters in high-dimensional behavioural spaces without imposing "
            "pre-defined thresholds, a shift from rule-based to data-driven segmentation that "
            "exemplifies the broader productivity gain associated with AI adoption in marketing "
            "operations. Crucially, this productivity gain is not simply about generating "
            "insights faster — it is about <b>allocative efficiency</b>: redirecting budget "
            "from undifferentiated mass campaigns toward interventions calibrated to each "
            "segment's specific behavioural profile and economic potential. A uniform marketing "
            "strategy applied to a structurally heterogeneous customer base is, by definition, "
            "an allocatively inefficient use of resources — it simultaneously over-serves low-"
            "value segments and under-invests in the highest-value cohorts.", s
        ),
        H2("1.2  Business Problem", s),
        P(
            "The client is a large Italian fashion retailer selling clothing and accessories. "
            "Despite operating a CRM programme that has generated 24 months of transactional "
            "data covering 21,477 customers and €11.96M in observed revenue, the retailer has "
            "historically employed a uniform, one-size-fits-all marketing approach. This "
            "ignores the structural heterogeneity of the customer base: high-value customers, "
            "discount-dependent buyers, occasional purchasers, and dormant accounts receive "
            "identical communications and promotional treatment, leading to suboptimal retention, "
            "margin erosion, and misallocation of marketing resources.", s
        ),
        H2("1.3  Research Objectives", s),
        B("<b>RQ1:</b> Can unsupervised machine learning identify behaviourally distinct, "
          "interpretable, and actionable customer segments from the available transactional data?", s),
        B("<b>RQ2:</b> What are the key behavioural characteristics that differentiate each "
          "segment, and what marketing strategies do they prescribe?", s),
        B("<b>RQ3:</b> What is the estimated financial impact of deploying segment-specific "
          "strategies relative to the current undifferentiated approach?", s),
        SP(4),
        H2("1.4  Report Structure", s),
        P(
            "The report follows the CRISP-DM framework: Section 2 (Theoretical Background), "
            "Section 3 (Data Understanding), Section 4 (Data Preparation and Feature "
            "Engineering), Section 5 (Dimensionality Reduction), Section 6 (Clustering "
            "Methodology), Section 7 (Model Evaluation), Section 8 (Segment Profiles), "
            "Section 9 (Business Implications), Section 10 (Deployment), Section 11 "
            "(Limitations), Section 12 (Conclusions).", s
        ),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════════════════════
    # 2. THEORETICAL BACKGROUND
    # ════════════════════════════════════════════════════════════════════════════
    S += [
        H1("2.  Theoretical Background", s), HR(),
        H2("2.1  Customer Segmentation", s),
        P(
            "Customer segmentation is a foundational concept in marketing science, rooted in "
            "the recognition that a firm's customer base is intrinsically heterogeneous. The "
            "objective is to partition customers into mutually exclusive groups that are "
            "internally homogeneous — sharing similar needs, behaviours, or value profiles — "
            "while being maximally distinct from one another. The managerial rationale is that "
            "distinct segments respond differently to marketing stimuli, and tailoring "
            "communication, pricing, and product recommendations to each segment yields "
            "superior outcomes relative to undifferentiated mass marketing.", s
        ),
        H2("2.2  The RFM Framework", s),
        P(
            "Recency, Frequency, and Monetary (RFM) analysis, formalised by Bult and Wansbeek "
            "(1995) and widely operationalised in CRM practice, provides a compact behavioural "
            "summary of customer purchase patterns. <b>Recency</b> (days since last purchase) "
            "captures engagement currency and churn risk. <b>Frequency</b> (number of distinct "
            "purchase occasions) reflects loyalty and habit formation. <b>Monetary</b> value "
            "(total spend or average order value) quantifies direct economic contribution. "
            "Together, these three dimensions account for a large proportion of variance in "
            "customer value and form the core of the feature matrix in this project, "
            "supplemented by five additional behavioural dimensions.", s
        ),
        H2("2.3  Customer Lifetime Value", s),
        P(
            "Customer Lifetime Value (CLV) projects the expected discounted future revenue a "
            "customer will generate over their relationship with the firm. The discounted CLV "
            "formula employed in this project is:", s
        ),
        P("dCLV = AOV × freq_annual × (retention_rate / (1 + r − retention_rate))", s, "mono"),
        P(
            "where r = 10% serves as a WACC (Weighted Average Cost of Capital) proxy. This "
            "formulation is consistent with the Pareto/NBD and BG/NBD literature (Fader et "
            "al., 2005) in treating CLV as a function of frequency, monetary value, and "
            "retention probability, while remaining computationally tractable at scale. The "
            "WACC proxy of 10% reflects a conservative discount rate appropriate for a "
            "medium-sized Italian retailer operating in the current macroeconomic environment.", s
        ),
        H2("2.4  Unsupervised Learning for Customer Analytics", s),
        P(
            "Unsupervised learning methods discover latent structure in feature space without "
            "labelled training data. In the customer analytics context, they are preferred over "
            "supervised classification because (i) ground-truth segment labels do not exist a "
            "priori, and (ii) the objective is discovery rather than prediction. The choice "
            "among algorithms involves trade-offs between computational efficiency, cluster "
            "shape assumptions, robustness to outliers, and interpretability — all of which "
            "are examined in Section 6.", s
        ),
        H2("2.5  CRISP-DM Framework", s),
        P(
            "The Cross-Industry Standard Process for Data Mining (CRISP-DM) provides a "
            "structured, iterative framework for data science projects, comprising six phases: "
            "Business Understanding, Data Understanding, Data Preparation, Modelling, "
            "Evaluation, and Deployment. This report follows the CRISP-DM structure both as "
            "an organisational device and as a quality standard: each phase is explicitly "
            "documented, decisions are justified with reference to both technical criteria and "
            "business requirements, and the Deployment phase is addressed in Section 10.", s
        ),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════════════════════
    # 3. DATA UNDERSTANDING
    # ════════════════════════════════════════════════════════════════════════════
    S += [
        H1("3.  Data Understanding", s), HR(),
        P(
            "The retailer provided four pipe-separated text files covering the period "
            "March 2023 to February 2025. All four sources share a common customer "
            "identifier (CRM ID), enabling unambiguous record linkage across tables.", s
        ),
        H2("3.1  Source Tables", s),
        SP(4),
        tbl(
            [
                ["Source", "Granularity", "Key Fields", "Role in Project"],
                ["Anagraphics",
                 "1 row / customer",
                 "gender, date_of_birth,\nprovince, subscription_date",
                 "Demographic descriptors:\nage, geographic index,\ncustomer tenure"],
                ["Transactions",
                 "N rows / customer\n(includes returns)",
                 "date, store_id, product_id,\nquantity, list_price,\ndiscount_pct, amount_spent",
                 "Core behavioural features:\nRFM, discount propensity,\nreturn behaviour, channel"],
                ["Products",
                 "1 row / product",
                 "product_id, category,\nsubcategory, gender",
                 "Category affinity features:\nn_categories_explored,\ntop_category_share"],
                ["Marketing\nCampaigns",
                 "N rows / customer",
                 "date, email_id,\nopened (Y/N), clicked (Y/N)",
                 "Email engagement features:\nopen_rate, click_rate,\nengagement_score"],
            ],
            [3.0*cm, 2.8*cm, 4.0*cm, 4.8*cm]
        ),
        SP(4),
        P("Table 1: Summary of the four source datasets provided by the client.", s, "caption"),
        H2("3.2  Scope and Coverage", s),
        P(
            "The merged dataset covers <b>21,477 unique customers</b> with at least one "
            "recorded purchase within the observation window. The transaction log explicitly "
            "encodes returns as negative-quantity line items, providing behavioural data on "
            "reverse logistics. Email campaign data covers only newsletter subscribers; "
            "non-subscribers are treated as zero-engagement rather than missing.", s
        ),
        H2("3.3  Data Quality Assessment", s),
        P(
            "A systematic audit was performed prior to feature engineering. Four material "
            "data quality issues were identified:", s
        ),
        B("<b>Negative net spend:</b> A subset of customers had return_value > gross_spend, "
          "yielding economically impossible negative net monetary values. These customers "
          "were flagged for removal (resolution in §4.1).", s),
        B("<b>Missing recency:</b> Customers with no recorded transactions in the window "
          "were assigned recency_days equal to the dataset maximum, representing maximum "
          "dormancy rather than absence.", s),
        B("<b>Newsletter non-subscribers:</b> All email engagement features assigned 0, "
          "consistent with treating non-subscription as zero digital engagement rather than "
          "as missing data.", s),
        B("<b>Extreme outliers:</b> A small number of customers with anomalously high "
          "monetary values (likely corporate accounts or data entry errors) required "
          "winsorization prior to scaling (§4.5).", s),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════════════════════
    # 4. DATA PREPARATION & FEATURE ENGINEERING
    # ════════════════════════════════════════════════════════════════════════════
    S += [
        H1("4.  Data Preparation and Feature Engineering", s), HR(),
        P(
            "Feature engineering is the most consequential step in this project. The "
            "choice of input features determines which dimensions of customer behaviour "
            "the model can distinguish. The guiding principle was that features should "
            "capture independent dimensions of behavioural variation — not correlated "
            "proxies of the same construct — and each feature must be interpretable "
            "in a business context.", s
        ),
        H2("4.1  Removal of Negative Spend Anomalies", s),
        P(
            "Customers whose total return_value exceeds gross_spend exhibit a negative "
            "net_spend. This is economically impossible under standard retail operations "
            "and signals either data entry errors or returns processed against purchases "
            "outside the 24-month observation window.", s
        ),
        P(
            "<b>Decision:</b> These customers were removed from the feature matrix. "
            "<b>Justification:</b> Retaining them would introduce a spurious 'negative "
            "monetary' cluster that reflects data inconsistency, not genuine customer "
            "behaviour. A clustering model trained on corrupted records would produce "
            "unreliable segment assignments for all customers, not just the anomalous ones, "
            "because the contaminated records shift the position of cluster centroids in "
            "feature space. The correct resolution is removal at the data preparation "
            "stage, with a recommendation to the client to investigate the root cause "
            "in the source transaction system.", s
        ),
        H2("4.2  One-Timer Treatment", s),
        P(
            "One-timers are customers with exactly one purchase occasion in the 24-month "
            "window. They represent a legitimate behavioural segment: they have demonstrated "
            "purchase intent but have not developed repeat purchase behaviour.", s
        ),
        P(
            "<b>Decision:</b> One-timers were <b>retained</b> and flagged with "
            "is_one_timer = True. <b>Justification:</b> Removing them would bias the "
            "clustering toward active customers and systematically prevent the identification "
            "of the Dormant Potential segment — a commercially important group for "
            "low-cost reactivation campaigns. The is_one_timer flag is classified as a "
            "post-hoc descriptive feature (used to characterise clusters after formation) "
            "rather than a clustering input, avoiding the distortion that a binary flag "
            "would introduce into the continuous behavioural feature space.", s
        ),
        H2("4.3  The Clustering-vs-Description Distinction", s),
        P(
            "A critical architectural decision in the feature engineering pipeline is the "
            "separation of features into two categories: (i) <b>clustering features</b> — "
            "continuous behavioural metrics used as direct inputs to the scaling and "
            "dimensionality reduction pipeline — and (ii) <b>descriptive features</b> — "
            "variables used to characterise and interpret clusters post-hoc but excluded "
            "from the clustering input. Binary flags (is_one_timer, has_newsletter), "
            "raw counts (nl_count, n_items_bought), and financial aggregates already "
            "captured by derived features (gross_spend, net_spend) fall into the descriptive "
            "category. Mixing binary and continuous features in a Euclidean distance metric "
            "creates dimensional dominance: a binary flag whose variance is bounded by 0.25 "
            "will be overwhelmed by continuous features with standard deviations of several "
            "hundred euros, even after scaling. The _CLUSTERING_EXCLUDE list in "
            "data_processing.py enforces this separation systematically.", s
        ),
        H2("4.4  The 32-Feature Matrix: Six Behavioural Dimensions", s),
        SP(4),
        tbl(
            [
                ["Dimension", "Key Features", "Business Rationale"],
                ["RFM",
                 "recency_days, frequency,\nmonetary, aov, freq_annual",
                 "Core purchase intensity and value. Recency captures engagement currency "
                 "and churn risk. Frequency reflects habit formation. Monetary quantifies "
                 "direct revenue contribution. Together they define the customer's 'weight' "
                 "in the revenue model."],
                ["Discount\nPropensity",
                 "avg_discount_pct,\npct_items_discounted,\ndiscount_weighted_spend",
                 "Measures price sensitivity and promotional dependency. High values identify "
                 "customers whose purchasing behaviour is conditioned on discounts — a "
                 "margin risk that cannot be detected from gross revenue alone."],
                ["Email\nEngagement",
                 "open_rate, click_rate,\nengagement_score",
                 "Captures responsiveness to digital CRM communication. Distinguishes "
                 "actively engaged customers (reachable via email) from passive or "
                 "uncontactable ones, which directly affects campaign channel selection."],
                ["Return\nBehaviour",
                 "return_rate,\nreturn_value_ratio,\nhas_returns",
                 "High return rates signal information asymmetry (fit/quality uncertainty) "
                 "or opportunistic buying behaviour. Critical for identifying segments where "
                 "operational reverse logistics costs are disproportionate to revenue."],
                ["Category\nAffinity",
                 "n_categories_explored,\ntop_category_share,\ncross_category_ratio",
                 "Measures breadth of product interest. High breadth signals cross-category "
                 "affinity and openness to bundle recommendations. Low breadth indicates "
                 "single-category loyalty requiring different retention mechanics."],
                ["Channel Mix",
                 "n_stores_visited,\necommerce_share",
                 "Captures omnichannel engagement. Distinguishes digitally native customers "
                 "from in-store-only shoppers, enabling channel-appropriate communication "
                 "and fulfilment strategy."],
            ],
            [2.8*cm, 3.8*cm, 8.0*cm]
        ),
        SP(4),
        P("Table 2: Feature engineering — six behavioural dimensions and business rationale.", s, "caption"),
        H2("4.5  Outlier Handling: Winsorization at the 99th Percentile", s),
        P(
            "Winsorization caps values above a specified quantile at that quantile's value, "
            "preserving all records while reducing the disproportionate influence of extremes. "
            "It is preferred over trimming (which removes records) because every customer "
            "in the database represents a real individual whose segment assignment matters "
            "for campaign targeting.", s
        ),
        P(
            "<b>Why the 99th percentile specifically:</b> The 95th percentile would "
            "aggressively cap the top 5% of customers, including the genuine high-value "
            "core of The Inner Circle segment — the very group whose distinct profile "
            "we need to preserve. The 100th percentile offers no protection against data "
            "errors. The 99th percentile surgically removes genuine anomalies (corporate "
            "accounts, data entry errors above realistic purchase thresholds) while "
            "preserving the full behavioural range of the top 1% of legitimate high-value "
            "customers. Applied to: monetary, average order value, and return_value.", s
        ),
        H2("4.6  Feature Scaling: RobustScaler", s),
        P(
            "Clustering algorithms operating on Euclidean distances — including UMAP's "
            "graph construction and GMM's covariance estimation — are sensitive to the "
            "relative scale of input features. Without scaling, features measured in euros "
            "(monetary, ranging from tens to thousands) would dominate over normalised "
            "ratios (return_rate, ranging from 0 to 1).", s
        ),
        P(
            "<b>Why RobustScaler over alternatives:</b> StandardScaler (mean ± standard "
            "deviation) is sensitive to residual outliers that survive winsorization, "
            "because extreme values in the tail inflate the standard deviation used for "
            "normalisation. MinMaxScaler maps features to [0, 1] but is equally sensitive "
            "to any surviving extremes. RobustScaler uses the median and interquartile "
            "range (IQR) for centring and scaling, making it inherently robust to "
            "non-Gaussian, right-skewed distributions of the kind characteristic of "
            "customer spend data. The theoretical justification is that for heavy-tailed "
            "distributions, the median is a more robust location estimator than the mean, "
            "and the IQR is a more robust scale estimator than the standard deviation.", s
        ),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════════════════════
    # 5. DIMENSIONALITY REDUCTION
    # ════════════════════════════════════════════════════════════════════════════
    S += [
        H1("5.  Dimensionality Reduction: UMAP", s), HR(),
        H2("5.1  Motivation", s),
        P(
            "With 32 input features after engineering, the feature matrix occupies a "
            "high-dimensional space in which Euclidean distances lose discriminative power "
            "— the curse of dimensionality (Bellman, 1961). As dimensionality increases, "
            "the ratio of maximum to minimum pairwise distance approaches 1, making it "
            "progressively difficult for distance-based algorithms to identify meaningful "
            "cluster structure. Additionally, several of the 32 features exhibit linear or "
            "non-linear correlations: frequency and monetary value are positively correlated "
            "for high-value customers; avg_discount_pct and pct_items_discounted measure "
            "overlapping constructs. Dimensionality reduction compresses this redundancy "
            "while preserving the independent variance that drives segment separation.", s
        ),
        H2("5.2  Algorithm Comparison", s),
        SP(4),
        tbl(
            [
                ["Algorithm", "Mechanism", "Limitation", "Verdict"],
                ["PCA", "Linear projection maximising\nvariance along orthogonal axes",
                 "Cannot capture non-linear behavioural\nmanifolds. Testing confirmed >32% of\nvariance in first 2 components but no\nmeaningful cluster separation in the\nresulting 2D space.", "Rejected"],
                ["t-SNE", "Non-linear; optimises local\nneighbourhood preservation in 2D",
                 "No transform() method — cannot score\nnew customers without rerunning the\nfull algorithm. Does not preserve global\nstructure. Sensitive to perplexity\nhyperparameter.", "Rejected\n(visualisation only)"],
                ["UMAP", "Non-linear; Riemannian geometry\nand algebraic topology; preserves\nboth local and global structure",
                 "Minor stochastic variation across\nhardware environments even with\nfixed random_state (addressed via\nseed and documentation).", "Selected"],
            ],
            [2.5*cm, 4.2*cm, 5.5*cm, 2.4*cm]
        ),
        SP(4),
        P("Table 3: Dimensionality reduction algorithm comparison.", s, "caption"),
        H2("5.3  UMAP Configuration and Rationale", s),
        SP(4),
        tbl(
            [
                ["Parameter", "Value", "Justification"],
                ["n_components", "3 (clustering)\n2 (visualisation)",
                 "Three components retain substantially more of the original manifold structure "
                 "than two, improving cluster separation in the subsequent GMM fitting step. "
                 "The additional component captures behavioural variance — particularly along "
                 "the discount/return dimensions — that is compressed into noise at n=2. "
                 "A separate 2D embedding is computed exclusively for visual diagnostics and "
                 "is not used as clustering input."],
                ["n_neighbors", "30",
                 "Controls the trade-off between local and global structure preservation. "
                 "Low values (5–15) over-fragment the embedding, creating spurious micro-clusters "
                 "that do not correspond to actionable behavioural groups. High values (>50) "
                 "over-smooth the embedding, merging genuinely distinct segments. n_neighbors=30 "
                 "was selected after visual inspection of the 3D embedding at n=15, 20, 30, 40, "
                 "balancing local resolution with global coherence for a 21,477-customer dataset."],
                ["min_dist", "0.1",
                 "Minimum distance between points in the embedded space. The standard recommended "
                 "value for clustering applications (vs. 0.5–1.0 for visualisation). Lower "
                 "values pack clusters more tightly, which benefits GMM fitting by creating "
                 "cleaner density peaks for each Gaussian component."],
                ["metric", "euclidean",
                 "Standard metric for scaled continuous features. Manhattan and cosine metrics "
                 "were tested and showed no improvement in downstream Silhouette Score."],
                ["random_state", "42",
                 "Ensures reproducibility of the spectral initialisation. Without a fixed seed, "
                 "different runs may produce topologically equivalent but geometrically different "
                 "embeddings, causing instability in downstream GMM fits."],
            ],
            [2.4*cm, 2.6*cm, 9.6*cm]
        ),
        SP(4),
        P("Table 4: UMAP hyperparameter configuration and justification.", s, "caption"),
        H2("5.4  The Hairball Problem — Why Density-Based Methods Failed", s),
        P(
            "Prior to selecting UMAP as the dimensionality reduction framework, DBSCAN "
            "and OPTICS were evaluated directly on the scaled 32-feature matrix. Both "
            "algorithms require that clusters be separable by regions of low point density "
            "— density gaps. Customer behavioural data, however, exhibits near-uniform "
            "density in feature space: there are no sharp boundaries between customer "
            "types, only gradual transitions along continuous behavioural dimensions. "
            "A customer on the boundary between The Inner Circle and Rising Stars is "
            "genuinely an intermediate case, not an outlier to be classified as noise.", s
        ),
        P(
            "In practice, for every epsilon value tested with DBSCAN across three orders "
            "of magnitude, over 99.7% of customers collapsed into a single mega-cluster, "
            "with only a handful of extreme outliers assigned to separate components. This "
            "empirical result — informally termed the 'hairball problem' in reference to "
            "the undifferentiated mass of points it produces in visualisation — is not a "
            "failure of DBSCAN per se, but rather a reflection of the data's intrinsic "
            "topological structure. It directly motivated the selection of GMM, a "
            "probabilistic model that does not require density gaps and instead fits "
            "overlapping Gaussian distributions to a continuous data manifold.", s
        ),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════════════════════
    # 6. CLUSTERING METHODOLOGY
    # ════════════════════════════════════════════════════════════════════════════
    S += [
        H1("6.  Clustering Methodology", s), HR(),
        H2("6.1  Algorithm Selection", s),
        SP(4),
        tbl(
            [
                ["Algorithm", "Core Assumption", "Why Rejected / Selected"],
                ["K-Means",
                 "Spherical clusters of equal\nvariance; hard assignment",
                 "Customer segments are not spherical. A high-spending, high-frequency customer "
                 "may be geometrically closer to a moderate customer on all 32 dimensions than "
                 "to another VIP with a different product affinity profile. Hard assignment "
                 "forces an arbitrary boundary on what is a continuous behavioural spectrum. "
                 "Rejected."],
                ["Hierarchical\nClustering",
                 "Hierarchical tree structure;\nagglomerative bottom-up",
                 "O(n² log n) time complexity is computationally prohibitive at 21,477 records. "
                 "The dendrogram at this scale becomes uninterpretable. Critically, HC provides "
                 "no transform() method, making it impossible to score new customers without "
                 "re-running the full algorithm. Rejected."],
                ["DBSCAN",
                 "Density-connected clusters\nseparated by low-density regions",
                 "Hairball problem (§5.4): customer behavioural data has no density gaps. "
                 "All epsilon values tested collapsed 99.7%+ of customers into one component. "
                 "Rejected."],
                ["OPTICS",
                 "Variable-density extension\nof DBSCAN",
                 "Same fundamental density-gap requirement as DBSCAN. Same failure mode in "
                 "the absence of natural density boundaries. Rejected."],
                ["GMM",
                 "Data drawn from a mixture of K\nmultivariate Gaussian distributions;\nsoft assignment",
                 "Flexible covariance structure allows ellipsoidal, overlapping cluster "
                 "geometries. Soft assignment (probability per cluster) correctly represents "
                 "boundary uncertainty. EM algorithm is well-studied and computationally "
                 "efficient. transform() / predict() available for new data. Selected."],
            ],
            [2.5*cm, 3.2*cm, 8.9*cm]
        ),
        SP(4),
        P("Table 5: Clustering algorithm comparison and selection rationale.", s, "caption"),
        H2("6.2  GMM Configuration", s),
        P(
            "A Gaussian Mixture Model treats the data as a superposition of K multivariate "
            "Gaussian distributions, each characterised by a mean vector, covariance matrix, "
            "and mixing weight. The Expectation-Maximisation (EM) algorithm iteratively "
            "computes soft responsibilities (probabilities of cluster membership) and "
            "updates component parameters until convergence.", s
        ),
        SP(4),
        tbl(
            [
                ["Parameter", "Value", "Justification"],
                ["covariance_type", "'full'",
                 "Each GMM component has its own unconstrained covariance matrix, allowing "
                 "clusters to have different shapes, sizes, and orientations in the UMAP space. "
                 "'tied' (shared covariance) would force all clusters to have the same shape — "
                 "inappropriate when The Inner Circle (compact, high-value) and Dormant Potential "
                 "(diffuse, low-engagement) have fundamentally different geometric profiles. "
                 "'diag' and 'spherical' impose further constraints that reduce flexibility "
                 "without any business justification."],
                ["n_init", "10",
                 "The EM algorithm is susceptible to convergence at local optima depending on "
                 "random parameter initialisation. Running 10 independent initialisations and "
                 "retaining the best by log-likelihood substantially reduces this risk. At "
                 "21,477 records, 10 initialisations adds acceptable computational overhead "
                 "(roughly 10× the single-run time) in exchange for a materially more stable "
                 "and reproducible final model."],
                ["random_state", "42", "Fixed seed for reproducibility across environments."],
                ["n_components", "6", "Determined by BIC optimisation and business validation (§6.3)."],
            ],
            [3.0*cm, 2.2*cm, 9.4*cm]
        ),
        SP(4),
        P("Table 6: GMM configuration and justification.", s, "caption"),
        H2("6.3  K Selection via BIC Optimisation", s),
        P(
            "The number of GMM components K is the primary hyperparameter requiring "
            "external specification. Two complementary criteria were used:", s
        ),
        B(
            "<b>Statistical criterion — Bayesian Information Criterion (BIC):</b> "
            "BIC = k·ln(n) − 2·ln(L̂), where k is the number of free parameters "
            "(proportional to K²×d for covariance_type='full') and L̂ is the maximised "
            "likelihood. BIC penalises model complexity more strongly than AIC, making "
            "it the preferred criterion when parsimony and interpretability are priorities. "
            "The BIC curve was computed for K = 3 to K = 10. The elbow — the point "
            "beyond which additional components yield diminishing BIC improvements — "
            "was identified at K = 6. The AIC curve confirmed a consistent pattern, "
            "providing convergent statistical evidence.", s
        ),
        B(
            "<b>Operational constraint:</b> The marketing team can realistically develop, "
            "execute, and monitor at most 6 simultaneous segment-specific campaigns within "
            "a given budget cycle. K > 6 produces segments that are statistically "
            "distinguishable but not operationally distinct — the incremental difference "
            "between K=7 and K=6 segments does not translate into a materially different "
            "marketing lever, budget allocation, or campaign brief.", s
        ),
        B(
            "<b>Interpretability validation:</b> At K=6, all six segments exhibit clearly "
            "differentiated radar chart profiles, and no two segments share an identical "
            "optimal marketing strategy. Testing K=4 confirmed the loss of the Inner "
            "Circle / Rising Stars distinction: these two segments merged into a generic "
            "'active customers' group, eliminating the most commercially critical "
            "differentiator (VIP retention vs. upgrade path activation).", s
        ),
        H2("6.4  Cluster Consolidation: 10 Components → 6 Segments", s),
        P(
            "An exploratory GMM with 10 components was run to examine raw cluster structure "
            "before applying the K=6 constraint. Four components (2, 3, 6, 8) exhibited "
            "near-identical behavioural profiles: low purchase frequency, high recency "
            "(extended inactivity), and low average order value. Pairwise Euclidean "
            "distances in UMAP coordinates confirmed their proximity. These four were "
            "consolidated into the single <i>Dormant Potential</i> segment. Two mid-tier "
            "components (0 and 9) showed near-identical KPIs across all six behavioural "
            "dimensions and were merged into <i>Rising Stars</i>. The K=6 final model "
            "directly encodes this consolidated structure, with BIC confirming that the "
            "merged model is statistically preferable to the 10-component version.", s
        ),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════════════════════
    # 7. MODEL EVALUATION
    # ════════════════════════════════════════════════════════════════════════════
    S += [
        H1("7.  Model Evaluation", s), HR(),
        P(
            "The K=6 GMM was evaluated using three standard internal clustering validation "
            "metrics. Internal metrics assess cluster quality using only the data, without "
            "external labels, making them appropriate for unsupervised segmentation.", s
        ),
        SP(4),
        tbl(
            [
                ["Metric", "Formula / Principle", "Interpretation"],
                ["Silhouette Score",
                 "s(i) = (b(i) − a(i)) / max(a(i), b(i))\na(i) = mean intra-cluster distance\nb(i) = mean nearest-cluster distance",
                 "Range [−1, 1]. Higher = better separation and cohesion. "
                 "Values > 0.5 indicate strong structure. For continuous behavioural "
                 "data without sharp density boundaries, values in [0.2, 0.5] are "
                 "characteristic of well-formed, actionable segments."],
                ["Davies-Bouldin\nIndex (DBI)",
                 "Average ratio of intra-cluster scatter\nto inter-cluster separation\nfor each cluster pair",
                 "Lower = better. DBI = 0 indicates perfect separation. "
                 "Values < 1.0 indicate good cluster quality. "
                 "Customer behavioural data typically yields DBI in [0.8, 1.5]; "
                 "values in this range do not preclude business utility."],
                ["Calinski-Harabasz\nScore (CHI)",
                 "Ratio of between-cluster variance to\nwithin-cluster variance, weighted\nby cluster sizes",
                 "Higher = better; no upper bound. A higher CHI indicates "
                 "compact clusters (low intra-cluster variance) that are "
                 "well-separated (high inter-cluster variance). "
                 "Computed on the UMAP 3D embedding."],
            ],
            [3.0*cm, 4.5*cm, 7.1*cm]
        ),
        SP(4),
        P("Table 7: Clustering evaluation metrics. Values computed in final_segmentation.ipynb.", s, "caption"),
        P(
            "<b>Important interpretive note:</b> Silhouette scores above 0.5 are typically "
            "achievable only when cluster boundaries are sharp and well-defined. Customer "
            "behavioural data is characterised by gradual, continuous transitions: a customer "
            "on the boundary between The Inner Circle and Rising Stars genuinely shares "
            "characteristics of both segments. This structural continuity means that metric "
            "scores moderate by standard benchmarks can still correspond to highly actionable, "
            "business-valid segments. The primary validation criterion is not metric optimality "
            "in isolation, but the combination of metric acceptability and demonstrably "
            "different optimal marketing strategies for each segment — a standard that the "
            "K=6 solution satisfies.", s
        ),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════════════════════
    # 8. SEGMENT PROFILES
    # ════════════════════════════════════════════════════════════════════════════
    S += [
        H1("8.  Results: The Six Customer Segments", s), HR(),
        P(
            "The K=6 GMM identifies six behaviourally distinct customer archetypes. "
            "Each segment is profiled below with its quantitative characteristics, "
            "naming rationale, and the behavioural logic that underpins the assigned "
            "persona. All percentage figures are validated against the client's "
            "presentation materials.", s
        ),
        H2("8.1  Revenue and Size Overview", s),
        SP(4),
        tbl(
            [
                ["Segment", "% Customers", "~N", "% Revenue", "Est. Revenue", "Defining KPI"],
                ["💎 The Inner Circle", "25.6%", "5,498", "42.8%", "~€5.12M",
                 "Highest monetary + frequency;\nlowest avg_discount_pct"],
                ["🌱 Rising Stars",      "28.3%", "6,078", "20.2%", "~€2.41M",
                 "Stable mid-tier behaviour;\nhigh CLV upgrade potential"],
                ["🛍️ Style Explorers",  "15.6%", "3,350", "13.7%", "~€1.64M",
                 "High n_categories_explored;\ncross-category breadth"],
                ["🏷️ Deal Chasers",     "14.2%", "3,050", "11.9%", "~€1.42M",
                 "74.6% promotional\ntransaction rate"],
                ["👋 Dormant Potential","11.1%", "2,385", " 3.8%", "~€0.45M",
                 "Highest recency_days;\nlowest engagement"],
                ["🔄 Quality Seekers",  " 5.2%", "1,113", " 7.6%", "~€0.91M",
                 "33% return rate;\nabove-avg basket value"],
                ["TOTAL",               "100%",  "21,477","100%",  "€11.96M", ""],
            ],
            [3.8*cm, 2.0*cm, 1.5*cm, 2.0*cm, 2.3*cm, 3.0*cm]
        ),
        SP(4),
        P("Table 8: Segment size, revenue contribution, and primary behavioural differentiator.", s, "caption"),
    ]

    # segment detail blocks
    segs = [
        ("8.2  💎 The Inner Circle  —  25.6% of Customers, 42.8% of Revenue",
         "The Inner Circle is the retailer's highest-value customer cohort: approximately "
         "5,498 individuals who collectively generate 42.8% of observed revenue (~€5.12M). "
         "Their defining profile combines high purchase frequency, high average order value, "
         "minimal recency (they purchased recently), and critically, the lowest avg_discount_pct "
         "of any segment — indicating a willingness to pay full price that materially exceeds "
         "the retailer's average. This full-price purchasing behaviour is the single most "
         "commercially significant characteristic: revenue from this segment carries the highest "
         "net margin per euro generated, entirely unlike Deal Chasers whose nominally similar "
         "basket values are heavily discounted.",
         "The name 'Inner Circle' reflects the exclusive status of this group and the retailer's "
         "existential financial dependency on it. The extreme revenue concentration — 25.6% of "
         "customers generating 42.8% of revenue, more concentrated than the standard Pareto "
         "80/20 rule — means that a 5 percentage-point churn increase in this segment alone "
         "would eliminate approximately €256K in annual revenue, exceeding the entire proposed "
         "strategic investment of €140K/year. This concentration risk transforms what would "
         "ordinarily be a retention strategy into a financial risk management imperative."),

        ("8.3  🌱 Rising Stars  —  28.3% of Customers, 20.2% of Revenue",
         "Rising Stars is simultaneously the largest segment by customer count (~6,078) and "
         "the second largest by revenue (~€2.41M). Their behavioural profile is characterised "
         "by stable, moderate-frequency purchasing at moderate average order values, without "
         "strong promotional dependency. This combination — regular purchasing, modest basket, "
         "low discount dependency — is the hallmark of a customer whose relationship with the "
         "brand is developing but not yet at VIP maturity.",
         "The strategic significance of Rising Stars lies in their position as the natural "
         "feeder pool for The Inner Circle. The CLV model estimates that a Rising Stars "
         "customer successfully upgraded to Inner Circle behaviour generates approximately "
         "€534 in incremental CLV. Given the segment's size (~6,078 customers), even a 5% "
         "conversion rate represents 304 customers × €534 = ~€162K in CLV uplift, at an "
         "estimated campaign cost of €18K/year. 'Rising Stars' was chosen over alternative "
         "names (e.g., 'Regular Buyers') precisely because it encodes the upgrade trajectory "
         "as the primary strategic lens for this group."),

        ("8.4  🛍️ Style Explorers  —  15.6% of Customers, 13.7% of Revenue",
         "Style Explorers are defined by high category breadth — they purchase across multiple "
         "product categories — and exhibit cross-category exploration behaviour. Their monetary "
         "value is moderate, but their category affinity profile reveals a qualitatively "
         "different kind of brand engagement: they are not anchored to a single product type "
         "but are actively exploring the brand's product range. A customer already purchasing "
         "across Tops, Bottoms, and Accessories has implicitly signalled affinity with the "
         "brand's overall aesthetic, not merely a single product's utility.",
         "The name reflects their defining behaviour pattern. The strategic implication is "
         "that this segment is the most receptive to editorial marketing content (lookbook "
         "campaigns, outfit-completion recommendations, seasonal style guides) that would "
         "be ineffective on, for example, Dormant Potential customers who have not yet "
         "established multi-category purchase behaviour."),

        ("8.5  🏷️ Deal Chasers  —  14.2% of Customers, 11.9% of Revenue",
         "Deal Chasers present the most structurally complex challenge in the segmentation. "
         "They purchase at high average basket values (€249 per transaction) but 74.6% of "
         "their transactions involve a promotional discount. The paradox is that they appear "
         "commercially valuable by gross revenue but their net margin contribution is "
         "substantially lower than the headline figures imply. More critically, systematic "
         "discounting to this segment creates promotional conditioning: customers learn "
         "through repeated experience to defer purchasing until a discount is available, "
         "progressively increasing the minimum discount threshold required to trigger a "
         "purchase. Left unaddressed, this dynamic erodes margin on the retailer's "
         "highest-ticket items indefinitely.",
         "'Deal Chasers' is deliberately neutral rather than pejorative. These customers "
         "are not intrinsically low-value — their average basket of €249 is above the "
         "dataset average, and they spend significantly when promotions are available. "
         "The challenge is re-conditioning their purchasing behaviour toward full-price "
         "engagement through loyalty incentives, exclusivity framing, and a gradual "
         "promotional step-down strategy. The name signals the diagnosis (discount "
         "dependency) without presupposing the customer's intention."),

        ("8.6  👋 Dormant Potential  —  11.1% of Customers, 3.8% of Revenue",
         "Dormant Potential customers exhibit the highest recency_days of any segment "
         "(they have not purchased recently), the lowest purchase frequency, and minimal "
         "monetary contribution. This segment is the consolidated result of four GMM "
         "components that shared identical low-engagement profiles — high inactivity, low "
         "frequency, low spend. Despite their low revenue contribution (3.8%), their "
         "presence in the CRM database confirms a historical purchase relationship with "
         "the brand, which has three important implications: (i) they are known to the "
         "retailer's systems; (ii) reactivation cost is lower than cold acquisition; "
         "(iii) their prior purchase history provides a preference signal for "
         "targeted reactivation messaging.",
         "The compound name encodes both the diagnostic reality ('Dormant') and the "
         "commercial opportunity ('Potential'). This framing is intentional: it prevents "
         "the segment from being dismissed as a lost cause while accurately representing "
         "the reactivation challenge. A 15% reactivation rate on 2,385 customers at "
         "€189 average first-purchase spend generates approximately €68K in incremental "
         "revenue from a win-back campaign costing ~€10K/year — a 6.8× gross return "
         "multiple and the single highest ROI initiative in the portfolio."),

        ("8.7  🔄 Quality Seekers  —  5.2% of Customers, 7.6% of Revenue",
         "Quality Seekers are the smallest segment by customer count (5.2%, ~1,113 "
         "customers) but their revenue contribution per customer is disproportionately "
         "high: 7.6% of revenue from 5.2% of customers implies an above-average spend "
         "rate. Their defining characteristic is a 33% return rate — equivalent to 1 in 3 "
         "items returned, the highest of any segment — combined with above-average basket "
         "values on non-returned items. This behavioural pattern reflects a well-documented "
         "phenomenon in fashion retail: customers with high quality standards and specific "
         "fit requirements who engage in a trial-and-selection purchasing process, ordering "
         "multiple sizes or styles to identify the optimal item.",
         "The name 'Quality Seekers' encodes the hypothesis that their return behaviour "
         "is driven by high standards and genuine fit uncertainty rather than "
         "opportunistic purchasing with intent to return. This hypothesis is supported "
         "by their above-average spend on retained items: a customer returning 33% "
         "of purchases by volume but generating above-average revenue from the 67% "
         "retained is a genuinely engaged buyer, not a serial returner. The correct "
         "intervention is therefore informational — specifically a data-driven Size Advisor "
         "Engine that leverages this customer's own purchase-and-return history to surface "
         "personalised size recommendations — rather than punitive (return fees or "
         "restrictions), which would risk alienating a high-revenue cohort."),
    ]

    for name, desc, naming in segs:
        S += [
            KeepTogether([
                H2(name, s),
                P(desc, s),
                P(f"<b>Naming rationale:</b> {naming}", s, "body_tight"),
                SP(6),
            ])
        ]

    S += [PageBreak()]

    # ════════════════════════════════════════════════════════════════════════════
    # 9. BUSINESS IMPLICATIONS
    # ════════════════════════════════════════════════════════════════════════════
    S += [
        H1("9.  Business Implications and Strategic Recommendations", s), HR(),
        H2("9.1  Revenue Concentration Risk", s),
        P(
            "The most structurally significant finding of the segmentation is the extreme "
            "revenue concentration in The Inner Circle: 25.6% of customers generate 42.8% "
            "of total revenue. This concentration is materially more severe than the "
            "canonical Pareto 80/20 rule and has direct implications for how the retailer "
            "should prioritise its marketing investment. A 5 percentage-point increase in "
            "Inner Circle churn rate would reduce annual revenue by approximately €256K. "
            "This single figure — €256K in potential loss from a single 5pp churn shock "
            "to 25.6% of the customer base — motivates treating Inner Circle retention "
            "not as a marketing option but as a financial risk management priority, "
            "warranting the highest per-customer investment of any segment.", s
        ),
        H2("9.2  Per-Segment Strategy Matrix", s),
        SP(4),
        tbl(
            [
                ["Segment", "Primary Strategy", "Key Initiative", "Budget (est.)"],
                ["💎 The Inner Circle", "Retention + Exclusivity",
                 "VIP loyalty programme with exclusive access tiers, "
                 "dedicated client advisor, early product launches. "
                 "Goal: reduce churn by 5pp.", "€45K/yr"],
                ["🌱 Rising Stars", "Upgrade Path Activation",
                 "Gamified loyalty programme: personalised 'You are €X from Silver "
                 "tier' milestone emails triggered at 70% of threshold spend. "
                 "Editorial newsletter (non-promotional) to increase brand affinity. "
                 "Local event invitations (pop-up previews). "
                 "Goal: 5% conversion to Inner Circle (304 customers × €534 CLV uplift = €162K).", "€30K/yr"],
                ["🛍️ Style Explorers", "Cross-Sell & Bundle",
                 "'Complete the Look' recommendation engine in post-purchase email "
                 "and checkout overlay, personalised by the category just purchased. "
                 "Bundle pricing: 10% incentive on second category added to basket. "
                 "Goal: raise avg. categories/order from 2.1 to 2.6 "
                 "(670 customers × €109 incremental basket = €73K).", "€20K/yr"],
                ["🏷️ Deal Chasers", "Margin Protection",
                 "A/B test on two equal sub-groups: Control (standard 20% discount "
                 "email); Treatment (editorial new-collection content + loyalty points "
                 "equivalent in value). Flash sales on unexplored full-price categories "
                 "to trigger first full-price purchase in a new area. "
                 "Goal: shift 20% of segment to at least one full-price purchase "
                 "(609 customers × €249 basket × 15% margin recovery = €23K gross margin).", "€20K/yr"],
                ["👋 Dormant Potential", "Reactivation",
                 "Three-touch win-back sequence: Day 30 — 'How is your [purchased "
                 "category]?' + complementary product suggestion. Day 60 — 10% voucher "
                 "expiring in 15 days. Day 90 — last-chance flash offer. "
                 "Email-engaged sub-group (high historical open rate): editorial "
                 "content only — no discount, as they read but do not convert on price. "
                 "Goal: 15% reactivation on 2,385 customers × €189 avg. spend = €68K.", "€10K/yr"],
                ["🔄 Quality Seekers", "Fit & Information Tools",
                 "ML-powered Size Advisor Engine on Product Detail Pages: "
                 "personalised size recommendations derived from the customer's own "
                 "purchase-and-return history (data already present in CRM). "
                 "Detailed fit guides by sub-category (outerwear and suits: "
                 "highest-return sub-categories identified in EDA). "
                 "E-commerce virtual try-on pilot. Return-cost transparency at checkout. "
                 "Goal: reduce return rate from 33% to below 20%, recovering "
                 "~€13K/yr in logistics cost (1,113 customers × 4.3× annual freq. "
                 "× 13pp improvement × €18/return — IT fashion benchmark).", "€15K/yr"],
                ["TOTAL", "", "", "€140K/yr"],
            ],
            [3.5*cm, 2.8*cm, 6.0*cm, 2.3*cm]
        ),
        SP(4),
        P("Table 9: Per-segment strategy matrix with directional initiative cost estimates.", s, "caption"),
        H2("9.3  Customer Lifetime Value Projection", s),
        P(
            "Discounted CLV was computed per customer using the formula in §2.3. Segment-level "
            "CLV aggregates to a total projected portfolio value of <b>€15.3M</b>, representing "
            "a 27.9% premium over the €11.96M observed revenue — reflecting the forward-looking "
            "value of successfully retaining and upgrading the customer base. The Inner Circle "
            "accounts for the largest share of projected CLV, further confirming the "
            "disproportionate return on investment from retention initiatives targeting that "
            "segment. CLV projections by segment are visualised in assets/clv_analysis.png.", s
        ),
        H2("9.4  Revenue at Risk: Scenario Analysis", s),
        P(
            "A symmetric ±20% perturbation of churn rates was applied to each segment to "
            "stress-test the revenue model under adverse and favourable conditions. The ±20% "
            "boundary represents a reasonable upper bound for marketing-driven churn variation "
            "within a 12-month horizon. Key findings: (i) The Inner Circle dominates the "
            "downside risk profile — a 20% churn rate increase generates the largest "
            "absolute revenue reduction of any segment. (ii) Rising Stars presents the "
            "largest combined risk-and-opportunity profile given its size. (iii) For "
            "Dormant Potential, the churn perturbation framework is less meaningful; the "
            "relevant metric is reactivation rate, modelled separately.", s
        ),
        H2("9.5  ROI Framework: €140K → +€718K → 5.1×", s),
        P(
            "The aggregate €140K/year strategic investment across all six initiatives was "
            "validated against projected incremental revenue uplift. Uplift estimates are "
            "derived from segment-specific conversion and retention improvement assumptions "
            "applied to the addressable customer population in each segment. The resulting "
            "projected uplift of <b>+€718K/year</b> implies a <b>5.1× gross return multiple</b>. This figure "
            "should be interpreted as a directional decision-support estimate, not an audited "
            "financial forecast. It is presented to demonstrate that the proposed reallocation "
            "of marketing spend from undifferentiated mass campaigns toward segment-specific "
            "initiatives is economically justified under conservative assumptions about "
            "campaign execution quality and customer response rates. Full ROI breakdown "
            "is visualised in assets/roi_framework.png.", s
        ),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════════════════════
    # 10. DEPLOYMENT
    # ════════════════════════════════════════════════════════════════════════════
    S += [
        H1("10.  Deployment Considerations", s), HR(),
        P(
            "The CRISP-DM framework's sixth phase addresses the transition from a validated "
            "analytical model to a production system generating business value on an ongoing "
            "basis. While a full cloud deployment is beyond the scope of this academic "
            "project, the architectural recommendations below reflect sound MLOps practice "
            "for a CRM integration context.", s
        ),
        H2("10.1  Scoring New Customers", s),
        P(
            "The segmentation pipeline comprises three serialised objects: the RobustScaler, "
            "the UMAP reducer, and the GMM classifier, each persisted as a pickle file in "
            "the models/ directory. To assign a new customer to a segment, the inference "
            "sequence is:", s
        ),
        P("new_features → scaler.transform() → reducer.transform() → gmm.predict()",
          s, "mono"),
        P(
            "This pipeline can be exposed as a microservice REST API that receives a "
            "customer feature vector (computed from transactional data upstream) and "
            "returns a segment assignment and a probability vector across all six "
            "components. The probabilistic output is a key advantage of GMM over hard "
            "assignment methods: customers with low maximum probability score are "
            "genuine behavioural boundary cases, and may warrant deferred classification "
            "or a blended treatment strategy until their behavioural profile stabilises.", s
        ),
        H2("10.2  Re-Training Cadence", s),
        P("The model should be re-trained when any of the following conditions are met:", s),
        B("Cluster size distribution drifts by more than 10% from the baseline over a "
          "rolling 90-day window (e.g., The Inner Circle declining from 25.6% to below 23%).", s),
        B("A scheduled quarterly re-training cycle is completed, incorporating the most "
          "recent 24-month rolling data window to reflect evolved purchasing patterns.", s),
        B("The Silhouette Score on the current production dataset falls below 80% of the "
          "training-time score, indicating that the UMAP embedding no longer accurately "
          "represents the current behavioural manifold.", s),
        H2("10.3  CRM Integration", s),
        P(
            "The model output — customer_segmentation_results.csv with fields cluster_gmm, "
            "cluster_name, cluster_confidence, and all 32 behavioural KPIs — is designed "
            "for direct ingestion into a CRM platform (e.g., Salesforce, Adobe Campaign, "
            "or Jakala's proprietary Loyalty/Activation stack). The cluster_name field maps "
            "directly to campaign audience definitions. The cluster_confidence field enables "
            "high-certainty-first campaign rollout: targeting the top 50% of each segment "
            "by confidence in a pilot phase before scaling to the full segment reduces "
            "the risk of early-stage campaign errors affecting borderline customers.", s
        ),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════════════════════
    # 11. LIMITATIONS
    # ════════════════════════════════════════════════════════════════════════════
    S += [
        H1("11.  Limitations", s), HR(),
        B("<b>Single-retailer scope:</b> The segmentation was developed and validated on "
          "data from a single Italian fashion retailer. The specific segment profiles, KPI "
          "thresholds, and persona characteristics reflect this retailer's particular "
          "customer base and product mix. The methodology is transferable; the segment "
          "definitions are not, and should not be applied directly to other retailers "
          "without re-training.", s),
        B("<b>24-month observation window:</b> Customers active before March 2023 but "
          "dormant within the window may be misclassified as Dormant Potential when they "
          "may be seasonal buyers with multi-year cycles. A longer observation window would "
          "improve the recency signal for such customers.", s),
        B("<b>Demographic features excluded from clustering:</b> Age, gender, and geography "
          "were excluded from the clustering input to ensure that segments are driven by "
          "behavioural patterns, not demographics. While this is the methodologically "
          "defensible choice for a behavioural segmentation, it means the model does not "
          "capture demographic heterogeneity within segments — an important caveat for "
          "campaigns where channel selection depends on age or geography.", s),
        B("<b>UMAP non-determinism:</b> Despite fixing random_state=42, UMAP's spectral "
          "initialisation introduces minor numerical non-determinism across different "
          "hardware environments and operating system versions. Results may differ "
          "marginally when the pipeline is re-run on different machines.", s),
        B("<b>Production deployment not implemented:</b> The deployment section describes "
          "an architectural approach rather than a working production system. Full "
          "deployment requires cloud infrastructure, API development, CRM integration, "
          "data governance workflows, and GDPR-compliant data handling procedures "
          "beyond the scope of this academic project.", s),
        B("<b>Financial projections are directional:</b> CLV, Revenue at Risk, and ROI "
          "estimates are based on segment-level assumptions that have not been validated "
          "against historical campaign lift data. They are presented as structured "
          "decision-support tools, not audited financial forecasts.", s),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════════════════════
    # 12. CONCLUSIONS
    # ════════════════════════════════════════════════════════════════════════════
    S += [
        H1("12.  Conclusions", s), HR(),
        P(
            "This project demonstrates that unsupervised machine learning — specifically a "
            "pipeline of RobustScaler normalisation, UMAP dimensionality reduction, and "
            "Gaussian Mixture Model clustering — can transform a heterogeneous transactional "
            "database into a structured, actionable segmentation framework for a fashion "
            "retailer. The three central conclusions are as follows.", s
        ),
        B("<b>The customer base is structurally concentrated.</b> 25.6% of customers "
          "generate 42.8% of revenue — a concentration more severe than the standard "
          "Pareto rule. This makes Inner Circle retention a financial risk management "
          "priority rather than merely a marketing objective. Any undifferentiated "
          "approach that fails to distinguish and protect this cohort creates "
          "disproportionate revenue exposure.", s),
        B("<b>Behavioural segments require qualitatively different marketing levers.</b> "
          "The six segments are not simply high/medium/low value tiers. Deal Chasers and "
          "Quality Seekers both generate above-average transaction values but require "
          "diametrically opposite interventions: margin protection vs. informational "
          "fit tools. A coarser segmentation that collapses these into a single category "
          "would prescribe contradictory strategies, rendering the segmentation "
          "operationally useless.", s),
        B("<b>Data-driven segmentation is financially justified.</b> The proposed "
          "€140K/year investment in segment-specific initiatives is projected to generate "
          "+€718K/year in incremental revenue, a 5.1× gross return multiple. Even under conservative "
          "assumptions, the directional argument for moving from mass marketing to "
          "targeted, data-driven engagement is robust.", s),
        SP(8),
        P(
            "From a broader perspective, this project illustrates the value creation "
            "mechanism of data as a strategic intangible asset in the digital economy "
            "(Corrado et al., 2009; Haskel and Westlake, 2018). The same 24 months of "
            "transactional records that existed in the retailer's CRM database without "
            "analytical structure can, through the application of AI-driven segmentation "
            "methods, yield a concrete and measurable marketing capability. The data itself "
            "has not changed; its <b>economic value has been unlocked through analytical "
            "investment</b> — a direct illustration of how digitalisation converts raw "
            "information into a productive intangible asset on the firm's balance sheet. "
            "The resulting capability — a segmented, CLV-weighted customer map with "
            "segment-specific intervention playbooks — constitutes proprietary intelligence "
            "that competitors without equivalent analytical infrastructure cannot replicate. "
            "This is the core economic logic of AI adoption in digital commerce: "
            "it raises <b>marketing productivity</b> (more revenue per euro of marketing "
            "spend) and improves <b>allocative efficiency</b> (budget directed to where "
            "the marginal return is highest, not distributed uniformly). The €140K/year "
            "investment generating a 5.1× gross return multiple is the quantified "
            "expression of that productivity gain.", s
        ),
        PageBreak(),
    ]

    # ════════════════════════════════════════════════════════════════════════════
    # REFERENCES
    # ════════════════════════════════════════════════════════════════════════════
    S += [
        H1("References", s), HR(),
        P("Bellman, R.E. (1961). <i>Adaptive Control Processes: A Guided Tour.</i> Princeton University Press.", s, "body_tight"),
        SP(4),
        P("Bult, J.R., &amp; Wansbeek, T. (1995). Optimal selection for direct mail. <i>Marketing Science</i>, 14(4), 378–394.", s, "body_tight"),
        SP(4),
        P("Dempster, A.P., Laird, N.M., &amp; Rubin, D.B. (1977). Maximum likelihood from incomplete data via the EM algorithm. <i>Journal of the Royal Statistical Society: Series B</i>, 39(1), 1–22.", s, "body_tight"),
        SP(4),
        P("Fader, P.S., Hardie, B.G.S., &amp; Lee, K.L. (2005). 'Counting your customers' the easy way: An alternative to the Pareto/NBD model. <i>Marketing Science</i>, 24(2), 275–284.", s, "body_tight"),
        SP(4),
        P("Jakala S.p.A. (2026). <i>Customer Segmentation — Business Case Brief.</i> JAKALA × LUISS Academic Partnership Presentation, February 2026.", s, "body_tight"),
        SP(4),
        P("McInnes, L., Healy, J., &amp; Melville, J. (2018). UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction. <i>arXiv preprint arXiv:1802.03426.</i>", s, "body_tight"),
        SP(4),
        P("Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. <i>Journal of Machine Learning Research</i>, 12, 2825–2830.", s, "body_tight"),
        SP(4),
        P("Schwarz, G. (1978). Estimating the dimension of a model. <i>The Annals of Statistics</i>, 6(2), 461–464.", s, "body_tight"),
        SP(30),
    ]

    return S


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    s = _styles()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=MARGIN_LR,
        leftMargin=MARGIN_LR,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOT,
        title="Customer Segmentation for an Italian Fashion Retailer",
        author="LUISS Data Science in Action — Group Project × Jakala",
    )
    doc.build(
        build_story(s),
        onFirstPage=_header_footer,
        onLaterPages=_header_footer,
    )
    print(f"✓  Report generated: {OUTPUT.resolve()}")


if __name__ == "__main__":
    main()
