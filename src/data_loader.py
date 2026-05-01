import duckdb
import pandas as pd

BASE_URL = "https://huggingface.co/datasets/defeatbeta/yahoo-finance-data/resolve/main/data"

# These are the stocks we will screen — feel free to change these
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'JNJ', 'V']

def load_data():
    print("Loading data from HuggingFace...")
    con = duckdb.connect()

    symbols_str = ", ".join([f"'{s}'" for s in SYMBOLS])

    prices = con.execute(f"""
        SELECT * FROM '{BASE_URL}/stock_prices.parquet'
        WHERE symbol IN ({symbols_str})
    """).df()
    print(f"  Prices loaded: {len(prices)} rows")

    statement = con.execute(f"""
        SELECT * FROM '{BASE_URL}/stock_statement.parquet'
        WHERE symbol IN ({symbols_str})
    """).df()
    print(f"  Statements loaded: {len(statement)} rows")

    profile = con.execute(f"""
        SELECT * FROM '{BASE_URL}/stock_profile.parquet'
        WHERE symbol IN ({symbols_str})
    """).df()
    print(f"  Profiles loaded: {len(profile)} rows")

    con.close()
    print("Done.\n")
    return prices, statement, profile


def preview_data():
    prices, statement, profile = load_data()

    print("=== STOCK PRICES ===")
    print(prices.head(3))
    print("Columns:", list(prices.columns), "\n")

    print("=== STOCK STATEMENT ===")
    print(statement.head(3))
    print("Columns:", list(statement.columns), "\n")

    print("=== STOCK PROFILE ===")
    print(profile.head(3))
    print("Columns:", list(profile.columns), "\n")