from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(slots=True)
class CustomerKnowledgeBase:
    profile: dict
    persona: dict
    transactions: pd.DataFrame
    service_history: pd.DataFrame
    products: list[dict]


class DataLoader:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir

    def load(self) -> CustomerKnowledgeBase:
        profile = self._load_json("perfil_investidor.json")
        return CustomerKnowledgeBase(
            profile=profile,
            persona=self._load_persona(str(profile.get("perfil_investidor", "moderado"))),
            transactions=self._load_csv("transacoes.csv"),
            service_history=self._load_csv("historico_atendimento.csv"),
            products=self._load_json("produtos_financeiros.json"),
        )

    def _load_csv(self, filename: str) -> pd.DataFrame:
        path = self.data_dir / filename
        return pd.read_csv(path)

    def _load_json(self, filename: str) -> dict | list[dict]:
        path = self.data_dir / filename
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _load_persona(self, profile_name: str) -> dict:
        personas = self._load_json("personas_investidor.json")
        if not isinstance(personas, dict):
            return {}
        return dict(personas.get(profile_name, personas.get("moderado", {})))
