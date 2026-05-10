def format_market_cap(value):
    if value is None:
        return "Unknown"

    if value >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:.2f}T"
    elif value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    return str(value)


def build_agent_input(
    selected_stock: dict,
    company_info: dict,
    user_preferences: dict,
    market_summary: dict,
    price_action_summary: dict,
    analysis_settings: dict,
) -> dict:

    return {
        "selected_stock": {
            "display_name": selected_stock["name"],
            "ticker": selected_stock["ticker"],
        },
        "analysis_settings": analysis_settings,
        "company_info": {
            "company_name": company_info.get("company_name"),
            "sector": company_info.get("sector"),
            "industry": company_info.get("industry"),
            "market_cap": company_info.get("market_cap"),
            "market_cap_formatted": format_market_cap(company_info.get("market_cap")),
            "currency": company_info.get("currency"),
        },
        "user_preferences": user_preferences,
        "market_summary": market_summary,
        "price_action_summary": price_action_summary,
        "important_note": (
            "This analysis is for educational purposes only. "
            "It is not financial advice and should not be used as the only basis for investment decisions."
        ),
    }


def generate_rule_based_summary(market_summary: dict) -> list[str]:

    summary = []

    trend = market_summary.get("trend")
    rsi = market_summary.get("rsi")
    rsi_status = market_summary.get("rsi_status")
    volatility = market_summary.get("volatility_level")
    period_return = market_summary.get("period_return_percent")
    max_drawdown = market_summary.get("max_drawdown_percent")

    summary.append(f"The current trend is classified as: {trend}.")
    summary.append(f"The RSI is {rsi}, which is classified as: {rsi_status}.")
    summary.append(f"The volatility level is: {volatility}.")
    summary.append(f"The selected period return is: {period_return}%.")
    summary.append(f"The maximum drawdown during the selected period is: {max_drawdown}%.")

    data_quality = market_summary.get("data_quality", {})

    if not data_quality.get("has_enough_data", True):
        summary.append(
            "Data quality warning: Some technical indicators could not be calculated because there was not enough historical data."
        )

    return summary