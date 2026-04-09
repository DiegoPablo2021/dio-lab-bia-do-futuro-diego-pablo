from __future__ import annotations

from dataclasses import dataclass

from src.services.data_loader import CustomerKnowledgeBase
from src.services.external_sources import OfficialMarketData, SourceReference
from src.services.finance_analyzer import FinancialSnapshot, format_brl


@dataclass(slots=True)
class AuraContext:
    prompt_context: str
    references: list[SourceReference]


class ContextBuilder:
    def build(
        self,
        knowledge_base: CustomerKnowledgeBase,
        snapshot: FinancialSnapshot,
        market_data: OfficialMarketData,
    ) -> AuraContext:
        profile = knowledge_base.profile
        persona = knowledge_base.persona
        products = "\n".join(
            [
                (
                    f"- {item['nome']}: risco {item['risco']}, aporte mínimo {format_brl(float(item['aporte_minimo']))}, "
                    f"indicado para {item['indicado_para']}."
                )
                for item in knowledge_base.products
            ]
        )
        history = "\n".join(
            [
                f"- {row.data}: canal={row.canal}, tema={row.tema}, resumo={row.resumo}, resolvido={row.resolvido}"
                for row in knowledge_base.service_history.itertuples(index=False)
            ]
        )
        spending = "\n".join(
            [
                f"- {category}: {format_brl(value)}"
                for category, value in snapshot.expense_by_category.items()
            ]
        )
        market_lines = []
        if market_data.selic_rate and market_data.selic_date:
            market_lines.append(
                f"- Selic oficial mais recente disponível: {market_data.selic_rate} em {market_data.selic_date}."
            )
        if market_data.tesouro_titles:
            market_lines.append(f"- Títulos encontrados no Tesouro Direto: {', '.join(market_data.tesouro_titles)}.")
        if not market_lines:
            market_lines.append("- Fontes oficiais indisponíveis no momento; use apenas os dados locais e assuma limitação.")

        prompt_context = f"""
CLIENTE:
- Nome: {profile['nome']}
- Idade: {profile['idade']}
- Profissão: {profile['profissao']}
- Renda mensal: {format_brl(float(profile['renda_mensal']))}
- Perfil investidor: {profile['perfil_investidor']}
- Objetivo principal: {profile['objetivo_principal']}
- Reserva atual: {format_brl(float(profile['reserva_emergencia_atual']))}

RESUMO FINANCEIRO:
- Entradas: {format_brl(snapshot.total_income)}
- Saídas: {format_brl(snapshot.total_expenses)}
- Saldo do período: {format_brl(snapshot.balance)}
- Maior categoria de gasto: {snapshot.top_category} ({format_brl(snapshot.top_category_amount)})
- Meta de reserva estimada: {format_brl(snapshot.reserve_target)}
- Gap de reserva: {format_brl(snapshot.reserve_gap)}

GASTOS POR CATEGORIA:
{spending}

HISTÓRICO DE ATENDIMENTO:
{history}

PRODUTOS DISPONÍVEIS PARA EDUCAÇÃO:
{products}

FONTES OFICIAIS:
{chr(10).join(market_lines)}

PERSONA DE COMUNICAÇÃO:
- Nome da persona: {persona.get('nome', 'Persona Moderada')}
- Descrição: {persona.get('descricao', 'Perfil equilibrado entre clareza e profundidade.')}
- Tom desejado: {persona.get('tom', 'consultivo e acolhedor')}
- Estilo de resposta: {persona.get('estilo_resposta', 'explique com clareza e responsabilidade')}
- Prioridades: {", ".join(persona.get('prioridades', []))}
- Termos preferidos: {", ".join(persona.get('termos_preferidos', []))}
- Termos a evitar: {", ".join(persona.get('termos_evitar', []))}
""".strip()

        return AuraContext(prompt_context=prompt_context, references=market_data.references)
