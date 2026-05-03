import streamlit as st

from tools.stock_data_tool import get_stock_data, get_company_info
from tools.indicators_tool import (
    calculate_market_summary,
    calculate_price_action_summary,
)
from utils.formatters import build_agent_input, generate_rule_based_summary


STOCK_OPTIONS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Nvidia": "NVDA",
    "Tesla": "TSLA",
    "Amazon": "AMZN",
    "Alphabet / Google": "GOOGL",
    "Meta": "META",
    "Netflix": "NFLX",
    "AMD": "AMD",
    "Coca-Cola": "KO",
}


def render_header():
    st.set_page_config(
        page_title="StockTrading Agent Assistant",
        page_icon="📈",
        layout="wide",
    )

    st.title("📈 StockTrading Agent Assistant")
    st.caption(
        "Educational stock analysis application with an agent-based architecture."
    )

    st.warning(
        "This application is for educational purposes only. "
        "It does not provide financial advice and does not execute trades."
    )


def render_sidebar():
    st.sidebar.header("Analysis Settings")

    selected_company = st.sidebar.selectbox(
        "Select a stock",
        options=list(STOCK_OPTIONS.keys()),
    )

    ticker = STOCK_OPTIONS[selected_company]

    period = st.sidebar.selectbox(
        "Select time period",
        options=["1mo", "3mo", "6mo", "1y", "2y"],
        index=2,
    )

    interval = st.sidebar.selectbox(
        "Select interval",
        options=["1d", "1wk", "1mo"],
        index=0,
    )

    risk_profile = st.sidebar.selectbox(
        "Risk profile",
        options=["Conservative", "Balanced", "Aggressive"],
        index=1,
    )

    investment_horizon = st.sidebar.selectbox(
        "Investment horizon",
        options=["Short-term", "Medium-term", "Long-term"],
        index=1,
    )

    analysis_depth = st.sidebar.selectbox(
        "Analysis depth",
        options=["Short", "Detailed"],
        index=0,
    )

    additional_context = st.sidebar.text_area(
        "Additional context",
        placeholder=(
            "Example: I prefer lower-risk companies, or I am interested in AI-related stocks."
        ),
    )

    run_button = st.sidebar.button("Prepare Analysis", type="primary")

    selected_stock = {
        "name": selected_company,
        "ticker": ticker,
    }

    analysis_settings = {
        "period": period,
        "interval": interval,
    }

    user_preferences = {
        "risk_profile": risk_profile,
        "investment_horizon": investment_horizon,
        "analysis_depth": analysis_depth,
        "additional_context": additional_context,
    }

    return selected_stock, analysis_settings, user_preferences, run_button


def render_selected_setup(
    selected_stock: dict,
    analysis_settings: dict,
    user_preferences: dict,
):
    st.subheader("Selected Analysis Setup")

    st.write(
        f"You selected **{selected_stock['name']} ({selected_stock['ticker']})** "
        f"with a **{analysis_settings['period']}** period and "
        f"**{analysis_settings['interval']}** interval."
    )

    col1, col2, col3 = st.columns(3)

    col1.write("**Risk profile:**")
    col1.write(user_preferences["risk_profile"])

    col2.write("**Investment horizon:**")
    col2.write(user_preferences["investment_horizon"])

    col3.write("**Analysis depth:**")
    col3.write(user_preferences["analysis_depth"])

    if user_preferences["additional_context"]:
        st.write("**Additional context:**")
        st.write(user_preferences["additional_context"])


def render_company_info(company_info: dict):
    st.subheader("Company Information")

    col1, col2, col3, col4 = st.columns(4)

    col1.write("**Company:**")
    col1.write(company_info.get("company_name", "Unknown"))

    col2.write("**Sector:**")
    col2.write(company_info.get("sector", "Unknown"))

    col3.write("**Industry:**")
    col3.write(company_info.get("industry", "Unknown"))

    col4.write("**Currency:**")
    col4.write(company_info.get("currency", "USD"))


def render_data_quality_warning(market_summary: dict):
    data_quality = market_summary.get("data_quality", {})

    if not data_quality.get("has_enough_data", True):
        st.warning(data_quality.get("warning"))

        missing_indicators = data_quality.get("missing_indicators", [])

        if missing_indicators:
            st.write("**Missing indicators:** " + ", ".join(missing_indicators))

        st.caption(
            "The analysis will still be passed to the agents, but the final recommendation should use lower confidence."
        )


def render_market_summary(company_info: dict, market_summary: dict):
    st.subheader("Market Data Summary")

    currency = company_info.get("currency", "USD")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        label="Current Price",
        value=f'{market_summary["current_price"]} {currency}',
    )

    col2.metric(
        label="Period Return",
        value=f'{market_summary["period_return_percent"]}%',
    )

    col3.metric(
        label="RSI",
        value=market_summary["rsi"] if market_summary["rsi"] is not None else "N/A",
    )

    col4.metric(
        label="Trend",
        value=market_summary["trend"],
    )

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        label="SMA20",
        value=market_summary["sma_20"] if market_summary["sma_20"] is not None else "N/A",
    )

    col6.metric(
        label="SMA50",
        value=market_summary["sma_50"] if market_summary["sma_50"] is not None else "N/A",
    )

    col7.metric(
        label="Volatility",
        value=market_summary["volatility_level"],
    )

    col8.metric(
        label="Max Drawdown",
        value=f'{market_summary["max_drawdown_percent"]}%',
    )


def render_price_action_summary(price_action_summary: dict):
    st.subheader("Compact Price Action Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        label="First Close",
        value=price_action_summary.get("first_close", "N/A"),
    )

    col2.metric(
        label="Last Close",
        value=price_action_summary.get("last_close", "N/A"),
    )

    col3.metric(
        label="Highest Close",
        value=price_action_summary.get("highest_close", "N/A"),
    )

    col4.metric(
        label="Lowest Close",
        value=price_action_summary.get("lowest_close", "N/A"),
    )

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        label="Average Close",
        value=price_action_summary.get("average_close", "N/A"),
    )

    col6.metric(
        label="Data Points",
        value=price_action_summary.get("data_points", "N/A"),
    )

    col7.metric(
        label="Latest Volume",
        value=price_action_summary.get("latest_volume", "N/A"),
    )

    col8.metric(
        label="Average Volume",
        value=price_action_summary.get("average_volume", "N/A"),
    )

    with st.expander("Show last 5 closing prices"):
        st.write(price_action_summary.get("last_5_closes", []))


def render_rule_based_summary(market_summary: dict):
    st.subheader("Rule-Based Technical Summary")

    summary_points = generate_rule_based_summary(market_summary)

    for point in summary_points:
        st.write(f"- {point}")


def render_agent_placeholders():
    st.subheader("AI Agent Analysis")

    st.info(
        "The AI agents are not connected yet. "
        "This section is prepared for the next development phase."
    )

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Industry Expert",
            "Technical Analyst",
            "Risk Management",
            "Supervisor",
        ]
    )

    with tab1:
        st.write("**Status:** Waiting for LLM integration.")
        st.write(
            "This agent will analyze the company, sector, industry and general business environment."
        )
        st.write(
            "**Planned input:** selected_stock, company_info, user_preferences."
        )

    with tab2:
        st.write("**Status:** Waiting for LLM integration.")
        st.write(
            "This agent will analyze SMA, RSI, trend, price action and momentum."
        )
        st.write(
            "**Planned input:** market_summary, price_action_summary, data_quality."
        )

    with tab3:
        st.write("**Status:** Waiting for LLM integration.")
        st.write(
            "This agent will evaluate volatility, drawdown, risk profile fit and caution flags."
        )
        st.write(
            "**Planned input:** user_preferences, market_summary, price_action_summary."
        )

    with tab4:
        st.write("**Status:** Waiting for LLM integration.")
        st.write(
            "This agent will combine all agent outputs into one final educational signal."
        )
        st.write(
            "**Planned input:** all agent outputs, market_summary, user_preferences."
        )


def main():
    render_header()

    selected_stock, analysis_settings, user_preferences, run_button = render_sidebar()

    render_selected_setup(
        selected_stock=selected_stock,
        analysis_settings=analysis_settings,
        user_preferences=user_preferences,
    )

    if run_button:
        try:
            with st.spinner("Loading stock data and preparing agent input..."):
                data = get_stock_data(
                    ticker=selected_stock["ticker"],
                    period=analysis_settings["period"],
                    interval=analysis_settings["interval"],
                )

                company_info = get_company_info(selected_stock["ticker"])
                market_summary = calculate_market_summary(data)
                price_action_summary = calculate_price_action_summary(data)

                agent_input = build_agent_input(
                    selected_stock=selected_stock,
                    company_info=company_info,
                    user_preferences=user_preferences,
                    market_summary=market_summary,
                    price_action_summary=price_action_summary,
                    analysis_settings=analysis_settings,
                )

            st.success("Analysis data prepared successfully.")

            render_company_info(company_info)
            render_data_quality_warning(market_summary)
            render_market_summary(company_info, market_summary)
            render_price_action_summary(price_action_summary)
            render_rule_based_summary(market_summary)

            with st.expander("Show raw agent input data"):
                st.json(agent_input)

            render_agent_placeholders()

        except Exception as e:
            st.error("Something went wrong while preparing the analysis.")
            st.exception(e)

    else:
        st.info("Choose your settings in the sidebar and click **Prepare Analysis**.")


if __name__ == "__main__":
    main()