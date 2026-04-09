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
    assert "segurança e liquidez" in conservador.text
    assert "Diego," in arrojado.text
    assert "volatilidade e horizonte de longo prazo" in arrojado.text
