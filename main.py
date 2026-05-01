from src.data_loader import load_data
from src.metrics import compute_metrics
from src.screener import screen_stocks, print_report
from src.visualizer import plot_all

if __name__ == "__main__":
    prices, statement, profile = load_data()
    metrics  = compute_metrics(prices, statement)
    screened = screen_stocks(metrics)
    print_report(screened)
    plot_all(screened)