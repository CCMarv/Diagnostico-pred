from __future__ import annotations

from dataclasses import fields

import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import make_classification

from config import COLUMNAS_CDC
from entrenamiento.comparador_modelos import ComparadorModelos
from entrenamiento.evaluador import EvaluadorClinico, ResultadoEvaluacion

CAMPOS_CONTRATO = {
    "nombre_modelo",
    "roc_auc",
    "pr_auc",
    "sensibilidad",
    "especificidad",
    "f1_clase_positiva",
    "brier_score",
    "accuracy",
}


def _dataset_sintetico() -> tuple[pd.DataFrame, pd.Series]:
    x_array, y_array = make_classification(
        n_samples=180,
        n_features=len(COLUMNAS_CDC),
        n_informative=10,
        n_redundant=5,
        random_state=42,
    )
    x = pd.DataFrame(x_array, columns=list(COLUMNAS_CDC))
    y = pd.Series(y_array.astype(int), name="Diabetes_binary")
    return x, y


@pytest.mark.parametrize("nombre_modelo", ["svm", "arbol", "gbm", "mlp"])
def test_contrato_uniforme_de_ocho_metricas(nombre_modelo: str) -> None:
    x, y = _dataset_sintetico()
    comparador = ComparadorModelos()
    evaluador = EvaluadorClinico()

    resultados = comparador.entrenar_clasificacion(x, y, modelos_a_entrenar=[nombre_modelo])

    assert len(resultados) == 1
    assert resultados[0].nombre == nombre_modelo

    probabilidades = np.asarray(resultados[0].modelo.predict_proba(x), dtype=float)[:, -1]
    evaluacion = evaluador.calcular_metricas(y.to_numpy(), probabilidades, nombre_modelo=nombre_modelo)

    campos_resultado = {campo.name for campo in fields(ResultadoEvaluacion)}
    assert CAMPOS_CONTRATO.issubset(campos_resultado)
    assert evaluacion.nombre_modelo == nombre_modelo

    for campo in CAMPOS_CONTRATO - {"nombre_modelo"}:
        valor = getattr(evaluacion, campo)
        assert isinstance(valor, float)
        assert np.isfinite(valor)

