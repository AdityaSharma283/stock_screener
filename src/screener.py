import pandas as pd

def screen_stocks(metrics: pd.DataFrame) -> pd.DataFrame:
    print("Applying screening filters...")

    # ── Filters (tweak these numbers to change your screen) ────────────
    MAX_PE            = 50     # not wildly overpriced
    MAX_DEBT_EQUITY   = 1.5    # not too leveraged
    MIN_CURRENT_RATIO = 1.0    # can pay short-term bills
    MIN_PROFIT_MARGIN = 10.0   # actually profitable
    MIN_REV_GROWTH    = 0.0    # revenue not shrinking

    df = metrics.copy()

    filters = {
        "P/E below 50"          : df["pe_ratio"]           < MAX_PE,
        "Debt/Equity below 1.5" : df["debt_to_equity"]     < MAX_DEBT_EQUITY,
        "Current ratio above 1" : df["current_ratio"]      >= MIN_CURRENT_RATIO,
        "Profit margin above 10%": df["profit_margin_pct"] >= MIN_PROFIT_MARGIN,
        "Revenue growing"       : df["revenue_growth_pct"] >= MIN_REV_GROWTH,
    }

    # Show which stocks pass/fail each filter
    print("\n--- Filter breakdown ---")
    for label, mask in filters.items():
        passing = df[mask]["symbol"].tolist()
        print(f"  {label}: {passing}")

    # Apply all filters combined
    combined = pd.Series([True] * len(df), index=df.index)
    for mask in filters.values():
        combined = combined & mask.fillna(False)

    passed = df[combined].copy()

    # ── Rank by a composite score ───────────────────────────────────────
    # Normalize each metric to 0-1 scale, then combine into one score
    # Lower P/E = better, Lower D/E = better, Higher of rest = better

    def normalize(series, higher_is_better=True):
        mn, mx = series.min(), series.max()
        if mx == mn:
            return pd.Series([0.5] * len(series), index=series.index)
        normed = (series - mn) / (mx - mn)
        return normed if higher_is_better else 1 - normed

    if len(passed) > 1:
        passed["score"] = (
            normalize(passed["pe_ratio"],           higher_is_better=False) * 0.20 +
            normalize(passed["debt_to_equity"],     higher_is_better=False) * 0.20 +
            normalize(passed["current_ratio"],      higher_is_better=True)  * 0.15 +
            normalize(passed["profit_margin_pct"],  higher_is_better=True)  * 0.25 +
            normalize(passed["revenue_growth_pct"], higher_is_better=True)  * 0.20
        ).round(4)
        passed = passed.sort_values("score", ascending=False)
    else:
        passed["score"] = 1.0

    print(f"\n{len(passed)} stock(s) passed all filters.\n")
    return passed


def print_report(screened: pd.DataFrame):
    cols = ["symbol", "latest_price", "pe_ratio", "debt_to_equity",
            "current_ratio", "profit_margin_pct", "revenue_growth_pct", "score"]

    print("=" * 70)
    print("         STOCK SCREENER RESULTS — RANKED BY COMPOSITE SCORE")
    print("=" * 70)

    if screened.empty:
        print("No stocks passed all filters. Try relaxing your criteria.")
        return

    print(screened[cols].to_string(index=False))
    print("=" * 70)
    print("\nScore explanation: 0 = worst, 1 = best across filtered stocks")
    print("Weights: Profit margin 25% | P/E 20% | D/E 20% | Rev growth 20% | Current ratio 15%")