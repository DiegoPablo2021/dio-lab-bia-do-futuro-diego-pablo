from pathlib import Path

from src.services.data_loader import DataLoader
from src.services.finance_analyzer import FinanceAnalyzer


def test_financial_snapshot_matches_mock_data() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    knowledge_base = DataLoader(data_dir).load()
    snapshot = FinanceAnalyzer().build_snapshot(knowledge_base.profile, knowledge_base.transactions)

    assert round(snapshot.total_income, 2) == 5000.00
    assert round(snapshot.total_expenses, 2) == 2488.90
    assert round(snapshot.balance, 2) == 2511.10
    assert snapshot.top_category == "moradia"
    assert round(snapshot.top_category_amount, 2) == 1380.00


def test_seven_day_plan_has_seven_steps() -> None:
    data_dir = Path(__file__).resolve().parent.parent / "data"
    knowledge_base = DataLoader(data_dir).load()
    analyzer = FinanceAnalyzer()
    snapshot = analyzer.build_snapshot(knowledge_base.profile, knowledge_base.transactions)
    plan = analyzer.build_seven_day_plan(knowledge_base.profile, snapshot)

    assert len(plan) == 7
    assert plan[0]["dia"] == "Dia 1"
