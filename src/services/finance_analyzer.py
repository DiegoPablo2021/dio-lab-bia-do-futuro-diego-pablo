from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeAlias

import pandas as pd

ProfileData: TypeAlias = dict[str, Any]


def format_brl(value: float) -> str:
    formatted = f"{value:,.2f}"
    return f"R$ {formatted}".replace(",", "X").replace(".", ",").replace("X", ".")


@dataclass(slots=True)
class FinancialSnapshot:
    total_income: float
    total_expenses: float
    balance: float
    top_category: str
    top_category_amount: float
    expense_by_category: dict[str, float]
    reserve_target: float
    reserve_current: float
    reserve_gap: float
    reserve_progress: float


class FinanceAnalyzer:
    def build_snapshot(self, profile: ProfileData, transactions: pd.DataFrame) -> FinancialSnapshot:
        income = transactions.loc[transactions["tipo"] == "entrada", "valor"].sum()
        expenses = transactions.loc[transactions["tipo"] == "saida", "valor"].sum()

        expense_by_category = (
            transactions.loc[transactions["tipo"] == "saida"]
            .groupby("categoria")["valor"]
            .sum()
            .sort_values(ascending=False)
            .to_dict()
        )

        if expense_by_category:
            top_category, top_category_amount = next(iter(expense_by_category.items()))
        else:
            top_category, top_category_amount = "Sem categoria", 0.0
        reserve_target = self._reserve_target(profile)
        reserve_current = float(profile.get("reserva_emergencia_atual", 0.0))
        reserve_gap = max(reserve_target - reserve_current, 0.0)
        reserve_progress = min((reserve_current / reserve_target) * 100, 100.0) if reserve_target else 0.0
        normalized_expense_by_category = {
            key: float(value) for key, value in expense_by_category.items()
        }

        return FinancialSnapshot(
            total_income=float(income),
            total_expenses=float(expenses),
            balance=float(income - expenses),
            top_category=top_category,
            top_category_amount=float(top_category_amount),
            expense_by_category=normalized_expense_by_category,
            reserve_target=reserve_target,
            reserve_current=reserve_current,
            reserve_gap=reserve_gap,
            reserve_progress=reserve_progress,
        )

    def build_diagnostic_insights(self, profile: ProfileData, snapshot: FinancialSnapshot) -> list[str]:
        insights = [
            (
                f"A maior concentração de gastos está em {snapshot.top_category}, "
                f"com {format_brl(snapshot.top_category_amount)} no período analisado."
            ),
            (
                f"O saldo do período ficou em {format_brl(snapshot.balance)}, considerando "
                f"entradas de {format_brl(snapshot.total_income)} e saídas de {format_brl(snapshot.total_expenses)}."
            ),
            (
                f"A reserva de emergência atual cobre {snapshot.reserve_progress:.1f}% da meta estimada, "
                f"com gap de {format_brl(snapshot.reserve_gap)}."
            ),
        ]

        if profile.get("perfil_investidor") == "moderado":
            insights.append(
                "O perfil moderado combina com explicações equilibradas: segurança primeiro, depois diversificação."
            )
        return insights

    def build_seven_day_plan(self, profile: ProfileData, snapshot: FinancialSnapshot) -> list[dict[str, str]]:
        objective = profile.get("objetivo_principal", "fortalecer a saúde financeira")
        return [
            {
                "dia": "Dia 1",
                "titulo": "Mapa rápido da vida financeira",
                "acao": (
                    f"Revise entradas, saídas e saldo. Hoje o saldo observado está em {format_brl(snapshot.balance)}."
                ),
            },
            {
                "dia": "Dia 2",
                "titulo": "Entender para onde o dinheiro vai",
                "acao": (
                    f"Olhe com carinho para {snapshot.top_category}, sua principal categoria de gasto no período."
                ),
            },
            {
                "dia": "Dia 3",
                "titulo": "Reserva de emergência sem mistério",
                "acao": (
                    f"Compare sua reserva atual ({format_brl(snapshot.reserve_current)}) com a meta "
                    f"estimada ({format_brl(snapshot.reserve_target)})."
                ),
            },
            {
                "dia": "Dia 4",
                "titulo": "CDI, Selic e renda fixa",
                "acao": "Estude os conceitos básicos que sustentam produtos conservadores e liquidez diária.",
            },
            {
                "dia": "Dia 5",
                "titulo": "Produtos antes de decisões",
                "acao": "Compare Tesouro Selic, CDB com liquidez diária e LCI/LCA pelo objetivo e risco.",
            },
            {
                "dia": "Dia 6",
                "titulo": "Meta principal em foco",
                "acao": f"Reveja o objetivo '{objective}' e defina um próximo passo concreto para ele.",
            },
            {
                "dia": "Dia 7",
                "titulo": "Rotina de manutenção",
                "acao": "Agende uma revisão semanal de gastos, reserva e aprendizados para manter consistência.",
            },
        ]

    def _reserve_target(self, profile: ProfileData) -> float:
        income = float(profile.get("renda_mensal", 0.0))
        goal_target = 0.0
        metas = profile.get("metas", [])
        if not isinstance(metas, list):
            metas = []
        for item in metas:
            if not isinstance(item, dict):
                continue
            if "reserva" in str(item.get("meta", "")).lower():
                goal_target = max(goal_target, float(item.get("valor_necessario", 0.0)))
        return max(income * 6, goal_target)
