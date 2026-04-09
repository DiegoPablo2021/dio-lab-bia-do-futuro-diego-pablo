from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import json
from pathlib import Path

import pandas as pd
import requests


BACEN_DATASET_URL = "https://dadosabertos.bcb.gov.br/dataset/11-taxa-de-juros---selic"
BACEN_API_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados"
TESOURO_URL = "https://www.tesourodireto.com.br/titulos/tipos-de-tesouro.htm"
TESOURO_TITLES = [
    "Tesouro Selic",
    "Tesouro IPCA+",
    "Renda+",
    "Tesouro Prefixado",
    "Tesouro Educa+",
]


@dataclass(slots=True)
class SourceReference:
    label: str
    url: str
    detail: str


@dataclass(slots=True)
class OfficialMarketData:
    selic_rate: str | None
    selic_date: str | None
    tesouro_titles: list[str]
    references: list[SourceReference]


class OfficialSourcesClient:
    def __init__(self, timeout: int = 10, data_dir: Path | None = None) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.data_dir = data_dir

    def collect(self) -> OfficialMarketData:
        selic_rate, selic_date = self._fetch_selic()
        tesouro_titles = self._fetch_tesouro_titles()
        return OfficialMarketData(
            selic_rate=selic_rate,
            selic_date=selic_date,
            tesouro_titles=tesouro_titles,
            references=[
                SourceReference(
                    label="Selic aberta do Banco Central",
                    url=BACEN_DATASET_URL,
                    detail="Serie 11 da Selic consultada via endpoint oficial do Banco Central.",
                ),
                SourceReference(
                    label="Produtos do Tesouro Direto",
                    url=TESOURO_URL,
                    detail="Pagina oficial dos titulos usada para enriquecer a explicacao dos produtos publicos.",
                ),
            ],
        )

    def _fetch_selic(self) -> tuple[str | None, str | None]:
        local = self._read_local_selic()
        if local is not None:
            return local

        today = date.today()
        start = today - timedelta(days=45)
        params = {
            "formato": "json",
            "dataInicial": start.strftime("%d/%m/%Y"),
            "dataFinal": today.strftime("%d/%m/%Y"),
        }
        try:
            response = self.session.get(BACEN_API_URL, params=params, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError):
            return None, None

        if not payload:
            return None, None

        latest = payload[-1]
        return f"{latest['valor']}% a.a.", latest["data"]

    def _fetch_tesouro_titles(self) -> list[str]:
        local_titles = self._read_local_tesouro_titles()
        if local_titles:
            return local_titles

        try:
            response = self.session.get(TESOURO_URL, timeout=self.timeout)
            response.raise_for_status()
            content = response.text
        except requests.RequestException:
            return TESOURO_TITLES

        available_titles = [title for title in TESOURO_TITLES if title in content]
        return available_titles or TESOURO_TITLES

    def _read_local_selic(self) -> tuple[str | None, str | None] | None:
        if self.data_dir is None:
            return None
        csv_path = self.data_dir / "bcdata.sgs.11.csv"
        if csv_path.exists():
            try:
                frame = pd.read_csv(csv_path, sep=";", decimal=",")
                latest = frame.iloc[-1]
                return f"{latest['valor']}% a.a.", str(latest["data"])
            except (KeyError, IndexError, ValueError, TypeError):
                pass

        path = self.data_dir / "selic_bacen.json"
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            latest = payload["data"][-1]
            return f"{latest['valor']}% a.a.", latest["data"]
        except (KeyError, IndexError, ValueError, TypeError):
            return None

    def _read_local_tesouro_titles(self) -> list[str]:
        if self.data_dir is None:
            return []
        path = self.data_dir / "tesouro_direto_produtos.json"
        if not path.exists():
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return [item["nome"] for item in payload["titles"]]
        except (KeyError, ValueError, TypeError):
            return []
