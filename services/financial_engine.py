from schemas.financial import FinancialInput, FinancialMetrics


def compute_metrics(data: FinancialInput) -> FinancialMetrics:
    gross_margin = data.gross_profit / data.revenue
    net_margin = data.net_income / data.revenue
    free_cash_flow = data.operating_cash_flow - data.capital_expenditure

    debt_to_equity = (
        data.total_debt / data.total_equity
        if data.total_equity != 0
        else None
    )

    current_ratio = (
        data.current_assets / data.current_liabilities
        if data.current_liabilities != 0
        else None
    )

    return FinancialMetrics(
        gross_margin=gross_margin,
        net_margin=net_margin,
        free_cash_flow=free_cash_flow,
        debt_to_equity=debt_to_equity,
        current_ratio=current_ratio
    )


def detect_mechanical_flags(metrics: FinancialMetrics) -> list[str]:
    flags = []

    if metrics.gross_margin < 0.2:
        flags.append("Low gross margin")

    if metrics.net_margin < 0.05:
        flags.append("Low net profit margin")

    if metrics.debt_to_equity is not None and metrics.debt_to_equity > 2:
        flags.append("High debt-to-equity ratio")

    if metrics.current_ratio is not None and metrics.current_ratio < 1:
        flags.append("Liquidity risk (current ratio < 1)")

    if metrics.free_cash_flow < 0:
        flags.append("Negative free cash flow")

    return flags
