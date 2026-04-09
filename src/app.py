from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.services.agent import AuraAgent, DEFAULT_GEMINI_MODEL, DEFAULT_OPENAI_MODEL  # noqa: E402
from src.services.finance_analyzer import format_brl  # noqa: E402


load_dotenv(PROJECT_ROOT / ".env")


@st.cache_resource
def get_agent() -> AuraAgent:
    return AuraAgent(PROJECT_ROOT)


def main() -> None:
    st.set_page_config(
        page_title="Aura | Mentora de Saúde Financeira",
        page_icon=":material/auto_awesome:",
        layout="wide",
    )
    _apply_pending_reset()
    _apply_theme()

    agent = get_agent()
    profile_override = _sidebar_profile_override(agent)
    knowledge_base, snapshot, market_data, _ = agent.build_snapshot(profile_override=profile_override)

    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">Diagnóstico financeiro com IA, dados e guardrails</div>
            <h1>Aura, Mentora de Saúde Financeira</h1>
            <p>
                Uma mentora digital que explica, organiza e contextualiza. Sem promessas vazias,
                sem recomendação direta de investimento e com foco em clareza para iniciantes.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### Configuração de IA")
        provider = st.selectbox(
            "Provedor de IA",
            options=["gemini", "openai", "fallback-local"],
            index=0,
            help="Gemini é a opção gratuita recomendada para este projeto. OpenAI fica como alternativa opcional.",
        )
        env_gemini_key = os.getenv("GEMINI_API_KEY", "")
        env_openai_key = os.getenv("OPENAI_API_KEY", "")
        gemini_api_key = ""
        openai_api_key = ""

        if provider == "gemini":
            if env_gemini_key:
                st.success("Chave do Gemini carregada com segurança a partir do arquivo `.env`.")
                with st.expander("Usar outra chave temporariamente", expanded=False):
                    gemini_api_key = st.text_input(
                        "Gemini API Key temporária",
                        value="",
                        type="password",
                        help="Use apenas se quiser testar outra chave nesta sessão. O campo não é preenchido automaticamente.",
                    )
            else:
                gemini_api_key = st.text_input(
                    "Gemini API Key",
                    value="",
                    type="password",
                    help="Crie sua chave no Google AI Studio para usar a faixa gratuita da Gemini API.",
                )
        elif provider == "openai":
            if env_openai_key:
                st.success("Chave da OpenAI carregada com segurança a partir do arquivo .env.")
                with st.expander("Usar outra chave temporariamente", expanded=False):
                    openai_api_key = st.text_input(
                        "OpenAI API Key temporária",
                        value="",
                        type="password",
                        help="Use apenas se quiser testar outra chave nesta sessão. O campo não é preenchido automaticamente.",
                    )
            else:
                openai_api_key = st.text_input(
                    "OpenAI API Key",
                    value="",
                    type="password",
                    help="Opcional. A API da OpenAI geralmente exige faturamento, então não é a melhor escolha se o foco for gratuito.",
                )

        default_model = (
            DEFAULT_GEMINI_MODEL
            if provider == "gemini"
            else DEFAULT_OPENAI_MODEL if provider == "openai" else "fallback-local"
        )
        model = st.text_input("Modelo", value=os.getenv("AURA_MODEL", default_model))
        mode_label = provider
        st.caption(f"Modo atual: {mode_label}")

        st.markdown("### Fontes oficiais")
        if market_data.selic_rate and market_data.selic_date:
            st.success(f"Selic oficial: {market_data.selic_rate} em {market_data.selic_date}")
        else:
            st.warning("Selic oficial indisponível no momento da consulta.")
        st.write("Tesouro Direto:")
        for title in market_data.tesouro_titles:
            st.write(f"- {title}")

    metrics = st.columns(4)
    metrics[0].metric("Entradas", format_brl(snapshot.total_income))
    metrics[1].metric("Saídas", format_brl(snapshot.total_expenses))
    metrics[2].metric("Saldo do período", format_brl(snapshot.balance))
    metrics[3].metric("Reserva concluída", f"{snapshot.reserve_progress:.1f}%")
    if st.session_state.get("aura_experience_mode") == "agente_livre":
        st.caption(
            "Os indicadores financeiros agora simulam o contexto informado ao lado, preservando a estrutura da base demonstrativa da DIO."
        )

    tab_chat, tab_diag, tab_plan, tab_eval = st.tabs(
        ["Chat educativo", "Diagnóstico", "Plano de 7 dias", "Avaliação"]
    )

    with tab_chat:
        st.markdown("#### Converse com a Aura")
        st.caption("Perguntas sugeridas: Onde estou gastando mais? | O que é Selic? | Me explique Tesouro Selic.")
        if st.button("Nova conversa", type="secondary", use_container_width=False):
            st.session_state["aura_pending_reset"] = True
            st.rerun()

        if "aura_messages" not in st.session_state:
            st.session_state.aura_messages = _initial_messages()

        for message in st.session_state.aura_messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    _render_assistant_content(message["content"])
                else:
                    st.markdown(message["content"])
                if message.get("references"):
                    with st.expander("Fontes usadas"):
                        for reference in message["references"]:
                            st.markdown(f"- **{reference.label}**: {reference.detail}  \n  {reference.url}")
                if message.get("mode"):
                    st.caption(f"Modo: {message['mode']}")

        prompt = st.chat_input("Digite sua dúvida sobre saúde financeira")
        if prompt:
            st.session_state.aura_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            history = [
                {"role": item["role"], "content": item["content"]}
                for item in st.session_state.aura_messages
                if item["role"] in {"user", "assistant"}
            ]
            if provider == "gemini":
                if gemini_api_key:
                    os.environ["GEMINI_API_KEY"] = gemini_api_key
                os.environ["AURA_PROVIDER"] = "gemini"
            elif provider == "openai":
                if openai_api_key:
                    os.environ["OPENAI_API_KEY"] = openai_api_key
                os.environ["AURA_PROVIDER"] = "openai"
            else:
                os.environ["AURA_PROVIDER"] = "fallback-local"
                os.environ.pop("GEMINI_API_KEY", None)
                os.environ.pop("OPENAI_API_KEY", None)

            os.environ["AURA_MODEL"] = model
            answer = agent.answer(
                prompt,
                conversation_history=history[:-1],
                api_key=openai_api_key,
                model=model,
                profile_override=profile_override,
            )
            st.session_state.aura_messages.append(
                {
                    "role": "assistant",
                    "content": answer.text,
                    "mode": answer.mode,
                    "references": answer.references,
                }
            )
            st.rerun()

    with tab_diag:
        st.markdown("#### Diagnóstico financeiro explicável")
        for insight in agent.diagnostic_insights(profile_override=profile_override):
            _render_diagnostic_bullet(insight)

        st.markdown("#### Gastos por categoria")
        diagnostic_columns = st.columns(len(snapshot.expense_by_category))
        for index, (category, value) in enumerate(snapshot.expense_by_category.items()):
            diagnostic_columns[index].metric(category.title(), format_brl(value))

    with tab_plan:
        st.markdown("#### Plano educativo de 7 dias")
        for item in agent.seven_day_plan(profile_override=profile_override):
            st.markdown(
                f"""
                <div class="plan-card">
                    <div class="plan-day">{item['dia']}</div>
                    <div class="plan-title">{item['titulo']}</div>
                    <div class="plan-action">{item['acao']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab_eval:
        st.markdown("#### Mapa de avaliação")
        st.caption("Use estes cenários para validar assertividade, segurança, coerência e clareza.")
        st.dataframe(agent.evaluation_cases(), use_container_width=True)


def _apply_theme() -> None:
    st.markdown(
        """
        <style>
            header[data-testid="stHeader"] {
                background: transparent;
            }
            .stAppHeader {
                background: transparent;
            }
            div[data-testid="stToolbar"] {
                background: transparent;
            }
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(255, 199, 123, 0.18), transparent 28%),
                    radial-gradient(circle at top right, rgba(94, 122, 255, 0.16), transparent 24%),
                    linear-gradient(180deg, #07111f 0%, #0a1628 100%);
            }
            .hero {
                padding: 1.5rem 1.5rem 1.2rem 1.5rem;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 24px;
                background: linear-gradient(135deg, rgba(15, 29, 51, 0.92), rgba(9, 17, 31, 0.92));
                margin-bottom: 1.25rem;
            }
            .hero-kicker {
                font-size: 0.82rem;
                text-transform: uppercase;
                letter-spacing: 0.16em;
                color: #f3b562;
                margin-bottom: 0.4rem;
            }
            .hero h1 {
                margin: 0;
                color: #f8fbff;
                font-size: 2.6rem;
            }
            .hero p {
                margin-top: 0.8rem;
                color: #d8e2f0;
                max-width: 840px;
                line-height: 1.6;
            }
            .plan-card {
                border: 1px solid rgba(255,255,255,0.08);
                background: rgba(11, 22, 38, 0.92);
                border-radius: 18px;
                padding: 1rem 1.1rem;
                margin-bottom: 0.8rem;
            }
            .plan-day {
                font-size: 0.8rem;
                color: #f3b562;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                margin-bottom: 0.3rem;
            }
            .plan-title {
                font-size: 1.05rem;
                font-weight: 700;
                color: #f8fbff;
                margin-bottom: 0.35rem;
            }
            .plan-action {
                color: #d8e2f0;
                line-height: 1.55;
            }
            .assistant-text {
                color: #f8fbff;
                line-height: 1.75;
                white-space: normal;
                word-break: break-word;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _sanitize_assistant_content(content: str) -> str:
    cleaned = re.sub(r"`([^`]*)`", r"\1", content)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"R\$\s+", "R$ ", cleaned)
    return cleaned.strip()


def _render_assistant_content(content: str) -> None:
    sanitized = _sanitize_assistant_content(content)
    escaped = html.escape(sanitized).replace("\n", "<br>")
    st.markdown(
        f'<div class="assistant-text">{escaped}</div>',
        unsafe_allow_html=True,
    )


def _render_diagnostic_bullet(content: str) -> None:
    sanitized = _sanitize_assistant_content(content)
    escaped = html.escape(sanitized)
    st.markdown(
        f'<div class="assistant-text" style="margin-bottom:0.8rem;">&bull; {escaped}</div>',
        unsafe_allow_html=True,
    )


def _sidebar_profile_override(agent: AuraAgent) -> dict | None:
    sample_profile = agent.load_knowledge_base().profile
    with st.sidebar:
        st.markdown("### Contexto da conversa")
        previous_mode = st.session_state.get("aura_experience_mode", "demo")
        experience_mode = st.radio(
            "Modo de experiência",
            options=["Demonstração guiada", "Agente livre"],
            index=0,
            key="aura_experience_mode_radio",
            help="Use a demonstração guiada para apresentar o cenário do desafio. Use agente livre para personalizar o contexto e conversar de forma mais aberta.",
        )
        current_mode = "demo" if experience_mode == "Demonstração guiada" else "agente_livre"
        if previous_mode != current_mode:
            st.session_state.aura_messages = _initial_messages()
        st.session_state.aura_experience_mode = current_mode

        if experience_mode == "Demonstração guiada":
            st.info("Cenário pronto para demo com dados da DIO e contexto financeiro consistente.")
            st.write(f"**Nome:** {sample_profile['nome']}")
            st.write(f"**Perfil:** {sample_profile['perfil_investidor'].title()}")
            st.write(f"**Objetivo:** {sample_profile['objetivo_principal']}")
            st.write(f"**Reserva atual:** {format_brl(float(sample_profile['reserva_emergencia_atual']))}")
            return None

        st.caption("Personalize o perfil para usar a Aura como agente educacional em um atendimento mais livre.")
        custom_name = st.text_input("Nome da pessoa", value="", key="aura_custom_name")
        custom_age = st.number_input(
            "Idade",
            min_value=18,
            max_value=100,
            value=int(sample_profile["idade"]),
            key="aura_custom_age",
        )
        custom_job = st.text_input("Profissão", value="", key="aura_custom_job")
        custom_income = st.number_input(
            "Renda mensal",
            min_value=0.0,
            value=float(sample_profile["renda_mensal"]),
            step=500.0,
            key="aura_custom_income",
        )
        custom_profile = st.selectbox(
            "Perfil investidor",
            options=["conservador", "moderado", "arrojado"],
            index=["conservador", "moderado", "arrojado"].index(sample_profile["perfil_investidor"]),
            key="aura_custom_profile",
        )
        persona_copy = {
            "conservador": "Respostas mais didáticas, prudentes e focadas em segurança.",
            "moderado": "Respostas equilibradas, com comparação entre segurança e diversificação.",
            "arrojado": "Respostas mais analíticas, com maior profundidade sobre risco e horizonte.",
        }
        st.caption(persona_copy[custom_profile])
        custom_goal = st.text_input("Objetivo principal", value="", key="aura_custom_goal")
        custom_reserve = st.number_input(
            "Reserva atual",
            min_value=0.0,
            value=float(sample_profile["reserva_emergencia_atual"]),
            step=500.0,
            key="aura_custom_reserve",
        )

        return {
            "nome": _normalize_person_name(custom_name) or "Pessoa em atendimento",
            "idade": int(custom_age),
            "profissao": custom_job.strip() or "Profissão não informada",
            "renda_mensal": float(custom_income),
            "perfil_investidor": custom_profile,
            "objetivo_principal": custom_goal.strip() or "Fortalecer a saúde financeira",
            "reserva_emergencia_atual": float(custom_reserve),
            "metas": sample_profile.get("metas", []),
        }


def _initial_messages() -> list[dict]:
    return [
        {
            "role": "assistant",
            "content": (
                "Sou a Aura. Posso analisar seus gastos, explicar conceitos financeiros e montar um plano "
                "educativo com base no seu contexto."
            ),
            "mode": "intro",
            "references": [],
        }
    ]


def _normalize_person_name(name: str) -> str:
    normalized = " ".join(name.split()).strip()
    return normalized.title() if normalized else ""


def _reset_sidebar_context() -> None:
    st.session_state["aura_custom_name"] = ""
    st.session_state["aura_custom_age"] = 32
    st.session_state["aura_custom_job"] = ""
    st.session_state["aura_custom_income"] = 5000.0
    st.session_state["aura_custom_profile"] = "moderado"
    st.session_state["aura_custom_goal"] = ""
    st.session_state["aura_custom_reserve"] = 10000.0


def _apply_pending_reset() -> None:
    if not st.session_state.pop("aura_pending_reset", False):
        return
    st.session_state["aura_messages"] = _initial_messages()
    _reset_sidebar_context()


if __name__ == "__main__":
    main()
