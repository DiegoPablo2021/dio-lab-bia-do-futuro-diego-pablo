from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias, cast

import pandas as pd

JsonObject: TypeAlias = dict[str, Any]
JsonList: TypeAlias = list[JsonObject]


@dataclass(slots=True)
class CustomerKnowledgeBase:
    profile: JsonObject
    persona: JsonObject
    transactions: pd.DataFrame
    service_history: pd.DataFrame
    products: JsonList


class DataLoader:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir

    def load(self) -> CustomerKnowledgeBase:
        profile = self._load_json_object("perfil_investidor.json")
        return CustomerKnowledgeBase(
            profile=profile,
            persona=self._load_persona(str(profile.get("perfil_investidor", "moderado"))),
            transactions=self._load_csv("transacoes.csv"),
            service_history=self._load_csv("historico_atendimento.csv"),
            products=self._load_json_list("produtos_financeiros.json"),
        )

    def _load_csv(self, filename: str) -> pd.DataFrame:
        path = self.data_dir / filename
        return pd.read_csv(path)

    def _load_json(self, filename: str) -> JsonObject | JsonList:
        path = self.data_dir / filename
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _load_json_object(self, filename: str) -> JsonObject:
        payload = self._load_json(filename)
        if isinstance(payload, dict):
            return cast(JsonObject, payload)
        return {}

    def _load_json_list(self, filename: str) -> JsonList:
        payload = self._load_json(filename)
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        return []

    def _load_persona(self, profile_name: str) -> JsonObject:
        personas = self._load_json_object("personas_investidor.json")
        selected = personas.get(profile_name, personas.get("moderado", {}))
        return dict(selected) if isinstance(selected, dict) else {}
