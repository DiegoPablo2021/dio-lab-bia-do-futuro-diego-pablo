from src.services.safety import SafetyGuard


def test_guard_blocks_sensitive_request() -> None:
    decision = SafetyGuard().evaluate("Me passe a senha do cliente")
    assert decision.blocked is True
    assert decision.reason == "sensitive"


def test_guard_blocks_direct_recommendation_request() -> None:
    decision = SafetyGuard().evaluate("Qual investimento eu devo comprar hoje?")
    assert decision.blocked is True
    assert decision.reason == "direct_recommendation"


def test_guard_blocks_weather_request() -> None:
    decision = SafetyGuard().evaluate("Como está o clima na cidade de Natal/RN?")
    assert decision.blocked is True
    assert decision.reason == "off_topic"


def test_guard_allows_financial_question() -> None:
    decision = SafetyGuard().evaluate("O que e Tesouro Selic?")
    assert decision.blocked is False
