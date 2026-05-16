from __future__ import annotations

from pathlib import Path

import pandas as pd

from basic.config import COLUMNA_OBJETIVO, COLUMNAS_CDC, RUTA_DATASET_PREDETERMINADA


class CargadorDatos:
    """Carga el dataset y valida columnas mínimas para entrenamiento básico."""

    def cargar(self, ruta_dataset: Path | None = None) -> pd.DataFrame:
        ruta = ruta_dataset or RUTA_DATASET_PREDETERMINADA
        if not ruta.exists():
            raise FileNotFoundError(f"No se encontró el dataset en: {ruta}")

        dataframe = pd.read_csv(ruta)
        columnas_requeridas = [*COLUMNAS_CDC, COLUMNA_OBJETIVO]
        faltantes = [col for col in columnas_requeridas if col not in dataframe.columns]
        if faltantes:
            raise ValueError(f"Faltan columnas requeridas en dataset: {faltantes}")

        return dataframe[columnas_requeridas].copy()

    def preparar_xy(self, ruta_dataset: Path | None = None) -> tuple[pd.DataFrame, pd.Series]:
        df = self.cargar(ruta_dataset)
        x = df[list(COLUMNAS_CDC)].apply(pd.to_numeric, errors="coerce")
        y = pd.to_numeric(df[COLUMNA_OBJETIVO], errors="coerce")

        mascara_valida = x.notna().all(axis=1) & y.notna()
        x_limpio = x.loc[mascara_valida].reset_index(drop=True)
        y_limpio = y.loc[mascara_valida].astype(int).reset_index(drop=True)
        return x_limpio, y_limpio
