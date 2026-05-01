import pandas as pd

def compute_metrics(prices: pd.DataFrame, statement: pd.DataFrame) -> pd.DataFrame:
    print("Computing financial metrics...")

    # ── 1. Latest closing price per stock ──────────────────────────────
    latest_price = (
        prices.sort_values("report_date")
              .groupby("symbol")["close"]
              .last()
              .reset_index()
              .rename(columns={"close": "latest_price"})
    )

    # ── 2. Separate income statement and balance sheet (annual only) ────
    income = statement[
        (statement["finance_type"] == "income_statement") &
        (statement["period_type"] == "annual")
    ]

    balance = statement[
        (statement["finance_type"] == "balance_sheet") &
        (statement["period_type"] == "annual")
    ]

    # ── 3. Helper: extract one item for each stock's latest annual row ──
    def get_latest(df, item_name, col_alias):
        filtered = df[df["item_name"] == item_name].copy()
        latest = (
            filtered.sort_values("report_date")
                    .groupby("symbol")
                    .last()
                    .reset_index()[["symbol", "report_date", "item_value"]]
                    .rename(columns={"item_value": col_alias})
        )
        return latest[["symbol", col_alias]]

    # ── 4. Pull the items we need ───────────────────────────────────────
    net_income     = get_latest(income,  "net_income",         "net_income")
    total_revenue  = get_latest(income,  "total_revenue",      "total_revenue")
    diluted_eps    = get_latest(income,  "diluted_eps",        "diluted_eps")
    total_debt     = get_latest(balance, "total_debt",         "total_debt")
    equity         = get_latest(balance, "stockholders_equity","total_equity")
    current_assets = get_latest(balance, "current_assets",     "current_assets")
    current_liab   = get_latest(balance, "current_liabilities","current_liabilities")

    # ── 5. Revenue growth (compare last 2 annual rows) ─────────────────
    rev_rows = (
        statement[
            (statement["item_name"] == "total_revenue") &
            (statement["period_type"] == "annual")
        ]
        .sort_values("report_date")
        .copy()
    )

    def calc_growth(g):
        g = g.sort_values("report_date")
        if len(g) < 2:
            return None
        prev, curr = g["item_value"].iloc[-2], g["item_value"].iloc[-1]
        if prev and prev != 0:
            return round((curr - prev) / abs(prev) * 100, 2)
        return None

    rev_growth = (
        rev_rows.groupby("symbol")
                .apply(calc_growth)
                .reset_index()
                .rename(columns={0: "revenue_growth_pct"})
    )

    # ── 6. Merge everything ─────────────────────────────────────────────
    metrics = latest_price.copy()
    for df in [net_income, total_revenue, diluted_eps,
               total_debt, equity, current_assets, current_liab, rev_growth]:
        metrics = metrics.merge(df, on="symbol", how="left")

    # ── 7. Compute ratios ───────────────────────────────────────────────

    # P/E = latest price / diluted EPS
    metrics["pe_ratio"] = (
        metrics["latest_price"] / metrics["diluted_eps"]
    ).round(2)

    # Debt-to-Equity
    metrics["debt_to_equity"] = (
        metrics["total_debt"] / metrics["total_equity"]
    ).round(2)

    # Current Ratio (liquidity — higher = safer)
    metrics["current_ratio"] = (
        metrics["current_assets"] / metrics["current_liabilities"]
    ).round(2)

    # Net Profit Margin
    metrics["profit_margin_pct"] = (
        metrics["net_income"] / metrics["total_revenue"] * 100
    ).round(2)

    print(f"  Metrics computed for {len(metrics)} stocks.\n")
    return metrics