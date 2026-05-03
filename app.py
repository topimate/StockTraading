import json
import streamlit as st

from tools.stock_data_tool import get_stock_data, get_company_info
from tools.indicators_tool import (
    calculate_market_summary,
    calculate_price_action_summary,
)
from utils.formatters import build_agent_input, generate_rule_based_summary

from flow import run_stock_analysis


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
    st.caption("Created by **Szénás Anna & Topolyai Máté**")

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

    prepare_button = st.sidebar.button("Prepare Analysis", type="primary")

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

    return selected_stock, analysis_settings, user_preferences, prepare_button


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


def build_agent_specific_inputs(agent_input: dict) -> tuple[dict, dict, dict]:
    """
    Converts the general Streamlit agent_input into the exact input objects
    expected by the 3 specialist agents.

    The supervisor input is NOT built here because flow.py builds it
    from the outputs of the 3 specialist agents.
    """

    selected_stock = agent_input["selected_stock"]
    company_info = agent_input["company_info"]
    user_preferences = agent_input["user_preferences"]
    market_summary = agent_input["market_summary"]
    price_action_summary = agent_input["price_action_summary"]
    analysis_settings = agent_input["analysis_settings"]

    industry_input = {
        "selected_stock": selected_stock,
        "company_info": company_info,
        "user_preferences": user_preferences,
    }

    technical_input = {
        "ticker": selected_stock["ticker"],
        "period": analysis_settings["period"],
        "interval": analysis_settings["interval"],
        "market_summary": market_summary,
        "price_action_summary": price_action_summary,
    }

    risk_input = {
        "ticker": selected_stock["ticker"],
        "user_preferences": {
            "risk_profile": user_preferences["risk_profile"],
            "investment_horizon": user_preferences["investment_horizon"],
            "analysis_depth": user_preferences["analysis_depth"],
            "additional_context": user_preferences["additional_context"],
        },
        "market_summary": {
            "period_return_percent": market_summary.get("period_return_percent"),
            "annualized_volatility_percent": market_summary.get("annualized_volatility_percent"),
            "volatility_level": market_summary.get("volatility_level"),
            "max_drawdown_percent": market_summary.get("max_drawdown_percent"),
            "rsi_status": market_summary.get("rsi_status"),
            "trend": market_summary.get("trend"),
            "data_quality": market_summary.get("data_quality"),
        },
        "price_action_summary": price_action_summary,
    }

    return industry_input, technical_input, risk_input

def detect_agent_api_errors(agent_result: dict) -> list[str]:
    """
    Detects API/rate-limit/token/quota related errors from agent outputs.

    The agents.py file returns errors as text, so we inspect the returned strings.
    """
    outputs = agent_result.get("agent_outputs", {})

    error_keywords = [
        "rate limit",
        "ratelimit",
        "rate_limit",
        "429",
        "quota",
        "token limit",
        "tokens per minute",
        "tokens per day",
        "maximum tokens",
        "max tokens",
        "max_completion_tokens",
        "too many requests",
        "insufficient_quota",
        "An error occurred while running the agent",
    ]

    detected_errors = []

    for agent_key, output in outputs.items():
        if not isinstance(output, str):
            continue

        output_lower = output.lower()

        if any(keyword.lower() in output_lower for keyword in error_keywords):
            detected_errors.append(
                f"{agent_key}: The API may have reached a rate limit, token limit, quota limit, or another provider-side restriction."
            )

    return detected_errors


def render_agent_api_warning(agent_result: dict):
    """
    Shows a user-friendly warning if the AI provider/API failed.
    """
    detected_errors = detect_agent_api_errors(agent_result)

    if not detected_errors:
        return

    st.error(
        "The AI agent analysis could not be completed reliably because the API provider may have reached a rate limit, token limit, or temporary usage quota."
    )

    st.warning(
        "Please try again later. If the issue continues, contact the project creators: "
        "Szénás Anna & Topolyai Máté."
    )

    with st.expander("Technical details"):
        for error in detected_errors:
            st.write(f"- {error}")

def render_agent_results(agent_result: dict):
    """
    Displays the full agent analysis result returned by flow.py.
    """

    st.subheader("AI Agent Analysis Results")

    outputs = agent_result.get("agent_outputs", {})
    inputs = agent_result.get("agent_inputs", {})

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Industry Expert",
            "Technical Analyst",
            "Risk Management",
            "Supervisor",
        ]
    )

    with tab1:
        st.markdown("### Industry Expert Agent")
        st.write(outputs.get("industry_expert_result", "No output available."))

    with tab2:
        st.markdown("### Technical Analyst Agent")
        st.write(outputs.get("technical_analyst_result", "No output available."))

    with tab3:
        st.markdown("### Risk Management Agent")
        st.write(outputs.get("risk_management_result", "No output available."))

    with tab4:
        st.markdown("### Supervisor Agent")
        st.write(outputs.get("supervisor_result", "No output available."))



def prepare_analysis_data(
    selected_stock: dict,
    analysis_settings: dict,
    user_preferences: dict,
) -> dict:
    """
    Loads stock data, calculates metrics and builds the general agent input.
    """

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

    return {
        "company_info": company_info,
        "market_summary": market_summary,
        "price_action_summary": price_action_summary,
        "agent_input": agent_input,
    }


def main():
    render_header()

    selected_stock, analysis_settings, user_preferences, prepare_button = render_sidebar()

    render_selected_setup(
        selected_stock=selected_stock,
        analysis_settings=analysis_settings,
        user_preferences=user_preferences,
    )

    if "prepared_analysis" not in st.session_state:
        st.session_state["prepared_analysis"] = None

    if "agent_result" not in st.session_state:
        st.session_state["agent_result"] = None

    if prepare_button:
        try:
            with st.spinner("Loading stock data and preparing agent input..."):
                prepared_analysis = prepare_analysis_data(
                    selected_stock=selected_stock,
                    analysis_settings=analysis_settings,
                    user_preferences=user_preferences,
                )

            st.session_state["prepared_analysis"] = prepared_analysis
            st.session_state["agent_result"] = None

            st.success("Analysis data prepared successfully.")

        except Exception as e:
            st.error("Something went wrong while preparing the analysis.")
            st.exception(e)

    prepared_analysis = st.session_state.get("prepared_analysis")

    if prepared_analysis is None:
        st.info("Choose your settings in the sidebar and click **Prepare Analysis**.")
        return

    company_info = prepared_analysis["company_info"]
    market_summary = prepared_analysis["market_summary"]
    price_action_summary = prepared_analysis["price_action_summary"]
    agent_input = prepared_analysis["agent_input"]

    render_company_info(company_info)
    render_data_quality_warning(market_summary)
    render_market_summary(company_info, market_summary)
    render_price_action_summary(price_action_summary)
    render_rule_based_summary(market_summary)

    with st.expander("Show raw general agent input data"):
        st.json(agent_input)

    st.download_button(
        label="Download general agent input as JSON",
        data=json.dumps(agent_input, indent=2, ensure_ascii=False),
        file_name=f"{agent_input['selected_stock']['ticker']}_agent_input.json",
        mime="application/json",
    )

    st.divider()

    st.subheader("Run AI Agents")

    st.write(
        "Click the button below to run the Industry Expert, Technical Analyst, "
        "Risk Management and Supervisor agents using the prepared input data."
    )

    st.caption(
        "The Supervisor Agent receives only the outputs of the three specialist agents, "
        "because this logic is defined in flow.py."
    )

    run_agents_button = st.button(
        "Run AI Agent Analysis",
        type="primary",
        help=(
            "Runs the LLM-based agents through a free/limited API provider. "
            "The request may fail if the provider rate limit or token limit is reached."
        ),
    )

    if run_agents_button:
        try:
            with st.spinner("Running AI agents through Groq API... This may take a moment."):
                industry_input, technical_input, risk_input = build_agent_specific_inputs(
                    agent_input
                )

                agent_result = run_stock_analysis(
                    industry_input=industry_input,
                    technical_input=technical_input,
                    risk_input=risk_input,
                )

            st.session_state["agent_result"] = agent_result
            detected_errors = detect_agent_api_errors(agent_result)

            if detected_errors:
                st.warning(
                    "The agent flow finished, but one or more agents reported an API-related issue."
                )
            else:
                st.success("AI agent analysis completed successfully.")

        except Exception as e:
            st.error(
                "The AI agent analysis could not be completed. "
                "The API may have reached a rate limit, token limit, or temporary provider restriction."
            )
            st.warning(
                "Please try again later. If the issue continues, contact the project creators: "
                "Szénás Anna & Topolyai Máté."
            )

            with st.expander("Technical error details"):
                st.exception(e)

    agent_result = st.session_state.get("agent_result")

    if agent_result is not None:
        render_agent_results(agent_result)
    else:
        st.info("AI agents have not been run yet.")


if __name__ == "__main__":
    main()