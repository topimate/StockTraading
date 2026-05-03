import json

from agents import (
    industry_expert_agent,
    technical_analyst_agent,
    risk_management_agent,
    supervisor_agent,
)


def build_supervisor_input(
    industry_expert_result: str,
    technical_analyst_result: str,
    risk_management_result: str,
) -> dict:

    return {
        "industry_expert_result": industry_expert_result,
        "technical_analyst_result": technical_analyst_result,
        "risk_management_result": risk_management_result,
    }


def run_stock_analysis(
    industry_input: dict,
    technical_input: dict,
    risk_input: dict,
) -> dict:

    print("Running Industry Expert Agent...")
    industry_expert_result = industry_expert_agent.run(industry_input)

    print("Running Technical Analyst Agent...")
    technical_analyst_result = technical_analyst_agent.run(technical_input)

    print("Running Risk Management Agent...")
    risk_management_result = risk_management_agent.run(risk_input)

    supervisor_input = build_supervisor_input(
        industry_expert_result=industry_expert_result,
        technical_analyst_result=technical_analyst_result,
        risk_management_result=risk_management_result,
    )

    print("Running Supervisor Agent...")
    supervisor_result = supervisor_agent.run(supervisor_input)

    return {
        "agent_inputs": {
            "industry_input": industry_input,
            "technical_input": technical_input,
            "risk_input": risk_input,
            "supervisor_input": supervisor_input,
        },
        "agent_outputs": {
            "industry_expert_result": industry_expert_result,
            "technical_analyst_result": technical_analyst_result,
            "risk_management_result": risk_management_result,
            "supervisor_result": supervisor_result,
        },
    }


if __name__ == "__main__":
    industry_input = {
        "selected_stock": {
            "display_name": "Netflix",
            "ticker": "NFLX",
        },
        "company_info": {
            "company_name": "Netflix, Inc.",
            "sector": "Communication Services",
            "industry": "Entertainment",
            "market_cap_formatted": "Example value",
            "currency": "USD",
        },
        "user_preferences": {
            "risk_profile": "Balanced",
            "investment_horizon": "Medium-term",
            "analysis_depth": "Short",
            "additional_context": "The user wants an educational stock analysis, not personalized investment advice.",
        },
    }

    technical_input = {
        "ticker": "NFLX",
        "period": "6mo",
        "interval": "1d",
        "market_summary": {
            "current_price": 92.06,
            "period_return_percent": -1.66,
            "sma_20": 94.12,
            "sma_50": 97.45,
            "rsi": 48.2,
            "rsi_status": "Neutral",
            "trend": "Bearish",
            "annualized_volatility_percent": 35.4,
            "max_drawdown_percent": -12.8,
        },
        "price_action_summary": {
            "first_close": 93.61,
            "last_close": 92.06,
            "highest_close": 98.20,
            "lowest_close": 89.40,
            "average_close": 93.10,
            "last_5_closes": [91.5, 92.1, 91.8, 92.3, 92.06],
            "average_volume": 12345678,
            "latest_volume": 9876543,
        },
    }

    risk_input = {
        "ticker": "NFLX",
        "user_preferences": {
            "risk_profile": "Balanced",
            "investment_horizon": "Medium-term",
        },
        "market_summary": {
            "period_return_percent": -1.66,
            "annualized_volatility_percent": 35.4,
            "volatility_level": "High",
            "max_drawdown_percent": -12.8,
            "rsi_status": "Neutral",
            "trend": "Bearish",
        },
    }

    result = run_stock_analysis(
        industry_input=industry_input,
        technical_input=technical_input,
        risk_input=risk_input,
    )

    print("\n" + "=" * 80)
    print("INDUSTRY EXPERT RESULT")
    print("=" * 80)
    print(result["agent_outputs"]["industry_expert_result"])

    print("\n" + "=" * 80)
    print("TECHNICAL ANALYST RESULT")
    print("=" * 80)
    print(result["agent_outputs"]["technical_analyst_result"])

    print("\n" + "=" * 80)
    print("RISK MANAGEMENT RESULT")
    print("=" * 80)
    print(result["agent_outputs"]["risk_management_result"])

    print("\n" + "=" * 80)
    print("SUPERVISOR INPUT JSON")
    print("=" * 80)
    print(json.dumps(result["agent_inputs"]["supervisor_input"], indent=2, ensure_ascii=False))

    print("\n" + "=" * 80)
    print("SUPERVISOR RESULT")
    print("=" * 80)
    print(result["agent_outputs"]["supervisor_result"])