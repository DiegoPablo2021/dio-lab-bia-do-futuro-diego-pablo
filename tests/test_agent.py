from pathlib import Path

from src.services.agent import AuraAgent


def test_build_snapshot_accepts_profile_override() -> None:
    project_root = Path(__file__).resolve().parent.parent
    agent = AuraAgent(project_root)

    knowledge_base, snapshot, _, _ = agent.build_snapshot(
        profile_override={
            "nome": "diego",
            "perfil_investidor": "conservador",
            "objetivo_principal": "Organizar melhor o orçamento",
            "renda_mensal": 7000.0,
            "reserva_emergencia_atual": 3500.0,
        }
    )

    assert knowledge_base.profile["nome"] == "Diego"
    assert knowledge_base.profile["perfil_investidor"] == "conservador"
    assert knowledge_base.profile["objetivo_principal"] == "Organizar melhor o orçamento"
    assert round(snapshot.total_income, 2) == 7000.00
    assert round(snapshot.total_expenses, 2) == 3484.46
    assert round(snapshot.balance, 2) == 3515.54
    assert round(snapshot.top_category_amount, 2) == 1932.00
    assert round(snapshot.reserve_target, 2) == 42000.00
    assert round(snapshot.reserve_current, 2) == 3500.00


def test_answer_personalizes_with_capitalized_name() -> None:
    project_root = Path(__file__).resolve().parent.parent
    agent = AuraAgent(project_root)

    answer = agent.answer(
        "como está minha reserva de emergência?",
        profile_override={
            "nome": "diego",
            "renda_mensal": 6000.0,
            "reserva_emergencia_atual": 2000.0,
        },
    )

    assert answer.text.startswith("Diego,")


def test_fallback_changes_tone_by_persona() -> None:
    project_root = Path(__file__).resolve().parent.parent
    agent = AuraAgent(project_root)

    conservador = agent.answer(
        "o que é selic?",
        profile_override={"nome": "paulo", "perfil_investidor": "conservador"},
    )
    arrojado = agent.answer(
        "o que é selic?",
        profile_override={"nome": "diego", "perfil_investidor": "arrojado"},
    )

    assert "Paulo," in conservador.text
    assert "perfil conservador" in conservador.text.lower()
    assert "Diego," in arrojado.text
    assert "perfil arrojado" in arrojado.text.lower()

def test_follow_up_uses_recent_conversation_focus() -> None:
    project_root = Path(__file__).resolve().parent.parent
    agent = AuraAgent(project_root)

    answer = agent.answer(
        "e no meu caso?",
        conversation_history=[
            {"role": "user", "content": "o que é selic?"},
            {"role": "assistant", "content": "explicação anterior"},
        ],
        profile_override={"nome": "diego", "reserva_emergencia_atual": 2000.0},
    )

    assert "Diego," in answer.text
    assert "Selic" in answer.text or "renda fixa" in answer.text or "reserva" in answer.text


def test_fallback_handles_summary_question_more_naturally() -> None:
    project_root = Path(__file__).resolve().parent.parent
    agent = AuraAgent(project_root)

    answer = agent.answer("Se você tivesse que resumir minha situação em uma frase, qual seria?")

    assert "saldo positivo" in answer.text.lower()
    assert "reserva" in answer.text.lower()


def test_fallback_handles_selic_vs_cdi_as_comparison() -> None:
    project_root = Path(__file__).resolve().parent.parent
    agent = AuraAgent(project_root)

    answer = agent.answer("Qual a diferença entre Selic e CDI?")

    assert "cdi" in answer.text.lower()
    assert "selic" in answer.text.lower()
    assert "não são a mesma coisa" in answer.text.lower()


def test_fallback_explains_selic_as_a_concept_first() -> None:
    project_root = Path(__file__).resolve().parent.parent
    agent = AuraAgent(project_root)

    answer = agent.answer("O que é Selic?")

    assert "taxa básica de juros" in answer.text.lower()
    assert "economia brasileira" in answer.text.lower()


def test_fallback_explains_tesouro_selic_without_falling_into_plain_selic() -> None:
    project_root = Path(__file__).resolve().parent.parent
    agent = AuraAgent(project_root)

    answer = agent.answer("O que é Tesouro Selic?")

    assert "título público" in answer.text.lower()
    assert "rentabilidade acompanha a selic" in answer.text.lower()
