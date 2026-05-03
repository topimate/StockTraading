import pandas as pd
import numpy as np


def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculates the RSI indicator based on the Close price.
    """
    delta = data["Close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def classify_volatility(volatility: float) -> str:
    """
    Classifies annualized volatility.
    """
    if volatility < 0.20:
        return "Low"
    elif volatility < 0.40:
        return "Medium"
    else:
        return "High"


def classify_trend(sma_20: float, sma_50: float) -> str:
    """
    Simple trend classification based on SMA20 and SMA50.
    """
    if sma_20 > sma_50:
        return "Bullish"
    elif sma_20 < sma_50:
        return "Bearish"
    return "Neutral"


def classify_rsi(rsi: float) -> str:
    """
    Classifies RSI status.
    """
    if rsi >= 70:
        return "Overbought"
    elif rsi <= 30:
        return "Oversold"
    return "Neutral"


def calculate_max_drawdown(data: pd.DataFrame) -> float:
    """
    Calculates max drawdown percentage.
    """
    cumulative_max = data["Close"].cummax()
    drawdown = (data["Close"] - cumulative_max) / cumulative_max
    max_drawdown = drawdown.min()

    return float(max_drawdown * 100)


def calculate_price_action_summary(data: pd.DataFrame) -> dict:
    """
    Creates a compact price action summary for the LLM agents.
    This is better than sending the full Yahoo Finance dataset to the agents.
    """
    df = data.copy()

    closes = df["Close"].dropna()
    volumes = df["Volume"].dropna() if "Volume" in df.columns else pd.Series(dtype=float)

    last_5_closes = closes.tail(5).round(2).tolist()

    latest_volume = None
    average_volume = None

    if not volumes.empty:
        latest_volume = int(volumes.iloc[-1])
        average_volume = int(volumes.mean())

    return {
        "first_close": round(float(closes.iloc[0]), 2) if not closes.empty else None,
        "last_close": round(float(closes.iloc[-1]), 2) if not closes.empty else None,
        "highest_close": round(float(closes.max()), 2) if not closes.empty else None,
        "lowest_close": round(float(closes.min()), 2) if not closes.empty else None,
        "average_close": round(float(closes.mean()), 2) if not closes.empty else None,
        "last_5_closes": last_5_closes,
        "latest_volume": latest_volume,
        "average_volume": average_volume,
        "data_points": len(df),
    }


def calculate_market_summary(data: pd.DataFrame) -> dict:
    """
    Calculates the main stock indicators needed by the agents.

    Important:
    If there is not enough historical data, some indicators will be None.
    In that case, a data_quality warning is added instead of stopping the analysis.
    """
    df = data.copy()

    df["SMA20"] = df["Close"].rolling(window=20).mean()
    df["SMA50"] = df["Close"].rolling(window=50).mean()
    df["RSI"] = calculate_rsi(df)

    latest = df.iloc[-1]
    first = df.iloc[0]

    current_price = float(latest["Close"])
    start_price = float(first["Close"])

    period_return = ((current_price - start_price) / start_price) * 100

    daily_returns = df["Close"].pct_change().dropna()

    if daily_returns.empty:
        annualized_volatility = 0.0
    else:
        annualized_volatility = float(daily_returns.std() * np.sqrt(252))

    sma_20 = latest["SMA20"]
    sma_50 = latest["SMA50"]
    rsi = latest["RSI"]

    if pd.isna(sma_20):
        sma_20 = None
    else:
        sma_20 = float(sma_20)

    if pd.isna(sma_50):
        sma_50 = None
    else:
        sma_50 = float(sma_50)

    if pd.isna(rsi):
        rsi = None
    else:
        rsi = float(rsi)

    if sma_20 is not None and sma_50 is not None:
        trend = classify_trend(sma_20, sma_50)
    else:
        trend = "Not enough data"

    if rsi is not None:
        rsi_status = classify_rsi(rsi)
    else:
        rsi_status = "Not enough data"

    volatility_level = classify_volatility(annualized_volatility)
    max_drawdown = calculate_max_drawdown(df)

    missing_indicators = []

    if sma_20 is None:
        missing_indicators.append("SMA20")

    if sma_50 is None:
        missing_indicators.append("SMA50")

    if rsi is None:
        missing_indicators.append("RSI")

    has_enough_data = len(missing_indicators) == 0

    if has_enough_data:
        data_quality_warning = None
    else:
        data_quality_warning = (
            "There is not enough historical price data to calculate all technical indicators. "
            "The agent analysis may be less accurate and should be interpreted with caution."
        )

    return {
        "current_price": round(current_price, 2),
        "period_return_percent": round(period_return, 2),
        "sma_20": round(sma_20, 2) if sma_20 is not None else None,
        "sma_50": round(sma_50, 2) if sma_50 is not None else None,
        "rsi": round(rsi, 2) if rsi is not None else None,
        "rsi_status": rsi_status,
        "annualized_volatility_percent": round(annualized_volatility * 100, 2),
        "volatility_level": volatility_level,
        "max_drawdown_percent": round(max_drawdown, 2),
        "trend": trend,
        "data_quality": {
            "has_enough_data": has_enough_data,
            "missing_indicators": missing_indicators,
            "warning": data_quality_warning,
        },
    }