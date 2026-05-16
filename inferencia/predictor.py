from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from config import COLUMNAS_CDC, RUTA_MODELO_FINAL, VERSION_SISTEMA


class PredictorDiabetes:
    """
    Encapsula la carga del modelo y la predicción de riesgo de diabetes.

    Notas para colaboradores:
    - Esta clase solo se encarga de inferencia.
    - No entrena modelos ni modifica artefactos de entrenamiento.
    """

    def __init__(self, ruta_modelo: Path | None = None, version: str = VERSION_SISTEMA) -> None:
        """Inicializa ruta del modelo, versión y estado interno."""
        self.ruta_modelo = ruta_modelo or RUTA_MODELO_FINAL
        self.version = version
        self._modelo: Any | None = None

    def cargar_modelo(self) -> bool:
        """Carga el artefacto `.joblib` si existe y devuelve si quedó disponible."""
        if not self.ruta_modelo.exists():
            self._modelo = None
            return False
        self._modelo = joblib.load(self.ruta_modelo)
        return True

    def esta_listo(self) -> bool:
        """Indica si hay un modelo cargado y listo para predecir."""
        return self._modelo is not None

    def predecir(self, entrada: pd.DataFrame) -> dict[str, float | int | str]:
        """
        Ejecuta una predicción para una sola fila de entrada.

        Requisitos:
        - `entrada` debe tener exactamente una fila.
        - Debe contener todas las columnas CDC en el orden esperado.
        """
        if self._modelo is None:
            raise FileNotFoundError("Modelo no cargado. Ejecuta cargar_modelo() primero.")
        if entrada.empty or len(entrada) != 1:
            raise ValueError("La entrada debe contener exactamente una fila.")

        faltantes = [col for col in COLUMNAS_CDC if col not in entrada.columns]
        if faltantes:
            raise ValueError(f"Faltan columnas CDC en la entrada: {faltantes}")

        entrada_ordenada = entrada[list(COLUMNAS_CDC)]
        inicio = time.perf_counter()

        if hasattr(self._modelo, "predict_proba"):
            proba_raw = self._modelo.predict_proba(entrada_ordenada)
            probabilidad = float(proba_raw[0][-1])
            clase = int(probabilidad >= 0.5)
        else:
            clase = int(self._modelo.predict(entrada_ordenada)[0])
            probabilidad = float(clase)

        tiempo_ms = int((time.perf_counter() - inicio) * 1000)
        return {
            "probabilidad": probabilidad,
            "clase": clase,
            "version": self.version,
            "tiempo_ms": tiempo_ms,
        }
