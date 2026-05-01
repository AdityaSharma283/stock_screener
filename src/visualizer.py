import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import os

REPORTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'reports')

def plot_all(screened: pd.DataFrame):
    os.makedirs(REPORTS_DIR, exist_ok=True)

    screened = screened.sort_values("score", ascending=False)
    symbols  = screened["symbol"].tolist()
    colors   = plt.cm.RdYlGn([s / screened["score"].max() for s in screened["score"]])

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("Stock Screener Dashboard", fontsize=18, fontweight="bold", y=1.01)

    # ── 1. Composite Score ──────────────────────────────────────────────
    ax = axes[0, 0]
    bars = ax.barh(symbols[::-1], screened["score"][::-1], color=colors[::-1])
    ax.set_title("Composite Score (higher = better)", fontweight="bold")
    ax.set_xlabel("Score")
    ax.axvline(0.5, color="gray", linestyle="--", linewidth=0.8, label="0.5 threshold")
    for bar, val in zip(bars, screened["score"][::-1]):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                f"{val:.3f}", va="center", fontsize=9)
    ax.legend(fontsize=8)

    # ── 2. P/E Ratio ───────────────────────────────────────────────────
    ax = axes[0, 1]
    bar_colors = ["#e74c3c" if v > 35 else "#2ecc71" for v in screened["pe_ratio"]]
    ax.bar(symbols, screened["pe_ratio"], color=bar_colors)
    ax.set_title("P/E Ratio (lower = cheaper)", fontweight="bold")
    ax.set_ylabel("P/E")
    ax.axhline(35, color="gray", linestyle="--", linewidth=0.8, label="P/E = 35")
    for i, v in enumerate(screened["pe_ratio"]):
        ax.text(i, v + 0.5, f"{v:.1f}", ha="center", fontsize=9)
    red_patch   = mpatches.Patch(color="#e74c3c", label="Expensive (>35)")
    green_patch = mpatches.Patch(color="#2ecc71", label="Reasonable (≤35)")
    ax.legend(handles=[green_patch, red_patch], fontsize=8)

    # ── 3. Debt-to-Equity ──────────────────────────────────────────────
    ax = axes[0, 2]
    bar_colors = ["#e74c3c" if v > 1.0 else "#2ecc71" for v in screened["debt_to_equity"]]
    ax.bar(symbols, screened["debt_to_equity"], color=bar_colors)
    ax.set_title("Debt / Equity (lower = safer)", fontweight="bold")
    ax.set_ylabel("D/E Ratio")
    ax.axhline(1.0, color="gray", linestyle="--", linewidth=0.8, label="D/E = 1.0")
    for i, v in enumerate(screened["debt_to_equity"]):
        ax.text(i, v + 0.01, f"{v:.2f}", ha="center", fontsize=9)
    ax.legend(fontsize=8)

    # ── 4. Profit Margin ───────────────────────────────────────────────
    ax = axes[1, 0]
    bar_colors = ["#2ecc71" if v > 30 else "#f39c12" for v in screened["profit_margin_pct"]]
    ax.bar(symbols, screened["profit_margin_pct"], color=bar_colors)
    ax.set_title("Profit Margin % (higher = better)", fontweight="bold")
    ax.set_ylabel("Margin %")
    ax.axhline(30, color="gray", linestyle="--", linewidth=0.8, label="30% line")
    for i, v in enumerate(screened["profit_margin_pct"]):
        ax.text(i, v + 0.5, f"{v:.1f}%", ha="center", fontsize=9)
    ax.legend(fontsize=8)

    # ── 5. Revenue Growth ──────────────────────────────────────────────
    ax = axes[1, 1]
    bar_colors = ["#2ecc71" if v > 15 else "#f39c12" for v in screened["revenue_growth_pct"]]
    ax.bar(symbols, screened["revenue_growth_pct"], color=bar_colors)
    ax.set_title("Revenue Growth % YoY (higher = better)", fontweight="bold")
    ax.set_ylabel("Growth %")
    ax.axhline(15, color="gray", linestyle="--", linewidth=0.8, label="15% line")
    for i, v in enumerate(screened["revenue_growth_pct"]):
        ax.text(i, v + 0.3, f"{v:.1f}%", ha="center", fontsize=9)
    ax.legend(fontsize=8)

    # ── 6. Bubble chart: Growth vs Margin, sized by score ──────────────
    ax = axes[1, 2]
    sizes = [s * 3000 for s in screened["score"]]
    scatter = ax.scatter(
        screened["revenue_growth_pct"],
        screened["profit_margin_pct"],
        s=sizes,
        c=screened["score"],
        cmap="RdYlGn",
        alpha=0.8,
        edgecolors="black",
        linewidths=0.5
    )
    for _, row in screened.iterrows():
        ax.annotate(row["symbol"],
                    (row["revenue_growth_pct"], row["profit_margin_pct"]),
                    textcoords="offset points", xytext=(6, 4), fontsize=9)
    ax.set_title("Growth vs Margin\n(bubble size = composite score)", fontweight="bold")
    ax.set_xlabel("Revenue Growth %")
    ax.set_ylabel("Profit Margin %")
    ax.axhline(30, color="gray", linestyle="--", linewidth=0.6, alpha=0.5)
    ax.axvline(15, color="gray", linestyle="--", linewidth=0.6, alpha=0.5)
    plt.colorbar(scatter, ax=ax, label="Score")

    plt.tight_layout()
    out_path = os.path.join(REPORTS_DIR, "screener_dashboard.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Chart saved to {out_path}")
    plt.show()