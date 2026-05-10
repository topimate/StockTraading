import yfinance as yf
import pandas as pd


def get_stock_data(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)

    if data.empty:
        raise ValueError(f"No data found for ticker: {ticker}")

    data = data.reset_index()
    return data


def get_company_info(ticker: str) -> dict:

    stock = yf.Ticker(ticker)

    try:
        info = stock.info
    except Exception:
        info = {}

    return {
        "ticker": ticker,
        "company_name": info.get("longName", ticker),
        "sector": info.get("sector", "Unknown"),
        "industry": info.get("industry", "Unknown"),
        "market_cap": info.get("marketCap", None),
        "currency": info.get("currency", "USD"),
    }