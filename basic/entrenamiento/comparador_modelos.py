from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from basic.config import SEMILLA_ALEATORIA
from basic.entrenamiento.preprocesador import construir_preprocesador


@dataclass(slots=True)
class ResultadoModelo:
    nombre: str
    roc_auc_cv: float
    modelo: Pipeline


class ComparadorModelos:
    """Entrena y compara 3 modelos clásicos para clasificación binaria."""

    def __init__(self) -> None:
        self._catalogo = {
            "logistica": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=SEMILLA_ALEATORIA),
            "arbol": DecisionTreeClassifier(max_depth=6, class_weight="balanced", random_state=SEMILLA_ALEATORIA),
            "svm": SVC(kernel="rbf", C=1.0, gamma="scale", probability=True, class_weight="balanced", random_state=SEMILLA_ALEATORIA),
        }

    def entrenar_y_comparar(self, x_ent: pd.DataFrame, y_ent: pd.Series) -> list[ResultadoModelo]:
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMILLA_ALEATORIA)
        resultados: list[ResultadoModelo] = []

        for nombre, estimador in self._catalogo.items():
            pipeline = Pipeline(
                steps=[
                    ("preprocesador", construir_preprocesador()),
                    ("clasificador", clone(estimador)),
                ]
            )
            puntajes = cross_val_score(pipeline, x_ent, y_ent, cv=cv, scoring="roc_auc", n_jobs=-1)
            pipeline.fit(x_ent, y_ent)
            resultados.append(ResultadoModelo(nombre=nombre, roc_auc_cv=float(np.mean(puntajes)), modelo=pipeline))

        return resultados
