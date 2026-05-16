from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score


@dataclass(slots=True)
class ResultadoEvaluacion:
    nombre_modelo: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    matriz_confusion: list[list[int]]


def evaluar_modelo(nombre: str, modelo, x_pru: pd.DataFrame, y_pru: pd.Series) -> ResultadoEvaluacion:
    y_pred = modelo.predict(x_pru)

    if hasattr(modelo, "predict_proba"):
        y_prob = modelo.predict_proba(x_pru)[:, 1]
    else:
        y_prob = y_pred.astype(float)

    matriz = confusion_matrix(y_pru, y_pred, labels=[0, 1]).astype(int).tolist()
    return ResultadoEvaluacion(
        nombre_modelo=nombre,
        accuracy=float(accuracy_score(y_pru, y_pred)),
        precision=float(precision_score(y_pru, y_pred, zero_division=0)),
        recall=float(recall_score(y_pru, y_pred, zero_division=0)),
        f1=float(f1_score(y_pru, y_pred, zero_division=0)),
        roc_auc=float(roc_auc_score(y_pru, y_prob)),
        matriz_confusion=matriz,
    )


def a_dataframe(resultados: list[ResultadoEvaluacion]) -> pd.DataFrame:
    return pd.DataFrame([asdict(r) for r in resultados]).sort_values("roc_auc", ascending=False).reset_index(drop=True)


def guardar_comparativa_csv(tabla: pd.DataFrame, ruta: Path) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(ruta, index=False)
