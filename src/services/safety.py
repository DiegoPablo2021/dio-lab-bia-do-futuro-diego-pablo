from __future__ import annotations

import unicodedata
from dataclasses import dataclass


@dataclass(slots=True)
class GuardrailDecision:
    blocked: bool
    message: str | None = None
    reason: str | None = None


class SafetyGuard:
    SENSITIVE_KEYWORDS = ("senha", "token", "cvv", "codigo de seguranca", "cpf de outro", "cartao de outro")
    OFF_TOPIC_KEYWORDS = (
        "clima",
        "previsao do tempo",
        "resultado do jogo",
        "jogo do flamengo",
        "placar",
        "horoscopo",
        "receita de bolo",
    )
    DIRECT_RECOMMENDATION_KEYWORDS = (
        "qual acao comprar",
        "onde investir",
        "qual investimento eu devo comprar",
        "o que devo comprar",
        "qual e o melhor investimento",
    )

    def evaluate(self, message: str) -> GuardrailDecision:
        normalized = self._normalize_text(message).strip()

        if not normalized:
            return GuardrailDecision(
                blocked=True,
                message="Escreva sua dúvida financeira em uma frase para eu conseguir te ajudar.",
                reason="empty",
            )

        if any(keyword in normalized for keyword in self.SENSITIVE_KEYWORDS):
            return GuardrailDecision(
                blocked=True,
                message=(
                    "Não posso acessar nem compartilhar dados sensíveis. Posso ajudar explicando boas práticas "
                    "de segurança financeira."
                ),
                reason="sensitive",
            )

        if any(keyword in normalized for keyword in self.OFF_TOPIC_KEYWORDS):
            return GuardrailDecision(
                blocked=True,
                message=(
                    "Não consigo te responder isso com segurança dentro da proposta da Aura. "
                    "Se você quiser, eu posso te ajudar com orçamento, gastos, reserva, dívidas ou produtos financeiros."
                ),
                reason="off_topic",
            )

        if any(keyword in normalized for keyword in self.DIRECT_RECOMMENDATION_KEYWORDS):
            return GuardrailDecision(
                blocked=True,
                message=(
                    "Não faço recomendação de investimento. Posso comparar como cada produto funciona "
                    "e te ajudar a entender riscos, liquidez e objetivos."
                ),
                reason="direct_recommendation",
            )

        return GuardrailDecision(blocked=False)

    def _normalize_text(self, text: str) -> str:
        normalized = unicodedata.normalize("NFKD", text)
        return "".join(char for char in normalized if not unicodedata.combining(char)).lower()
