from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from basic.config import COLUMNA_OBJETIVO, COLUMNAS_CDC
from basic.entrenamiento.pipeline import ejecutar_pipeline_basico


def _dataset_sintetico(n: int = 120) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    data = {col: rng.integers(0, 2, size=n) for col in COLUMNAS_CDC}
    data["BMI"] = rng.uniform(18, 40, size=n)
    data["MentHlth"] = rng.integers(0, 31, size=n)
    data["PhysHlth"] = rng.integers(0, 31, size=n)
    data["GenHlth"] = rng.integers(1, 6, size=n)
    data["Age"] = rng.integers(1, 14, size=n)
    data["Education"] = rng.integers(1, 7, size=n)
    data["Income"] = rng.integers(1, 9, size=n)
    data[COLUMNA_OBJETIVO] = rng.integers(0, 2, size=n)
    return pd.DataFrame(data)


def test_pipeline_basico_entrena_y_guarda(tmp_path: Path) -> None:
    dataset = _dataset_sintetico()
    ruta_dataset = tmp_path / "dataset.csv"
    dataset.to_csv(ruta_dataset, index=False)

    ruta_modelo = tmp_path / "modelo.joblib"
    ruta_reporte = tmp_path / "metricas.json"
    ruta_comparativa = tmp_path / "comparativa.csv"

    resultado = ejecutar_pipeline_basico(
        ruta_dataset=ruta_dataset,
        ruta_modelo=ruta_modelo,
        ruta_reporte=ruta_reporte,
        ruta_comparativa=ruta_comparativa,
    )

    assert ruta_modelo.exists()
    assert ruta_reporte.exists()
    assert ruta_comparativa.exists()
    assert resultado["mejor_modelo"] in {"logistica", "arbol", "svm"}

    contenido = json.loads(ruta_reporte.read_text(encoding="utf-8"))
    assert set(contenido["modelos"].keys()) == {"logistica", "arbol", "svm"}
