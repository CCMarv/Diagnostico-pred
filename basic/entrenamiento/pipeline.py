from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
from sklearn.model_selection import train_test_split

from basic.config import PROPORCION_PRUEBA, RUTA_MODELO_FINAL, RUTA_REPORTE_COMPARATIVA, RUTA_REPORTE_METRICAS, SEMILLA_ALEATORIA
from basic.entrenamiento.cargador_datos import CargadorDatos
from basic.entrenamiento.comparador_modelos import ComparadorModelos
from basic.entrenamiento.evaluador import a_dataframe, evaluar_modelo, guardar_comparativa_csv


def ejecutar_pipeline_basico(
    ruta_dataset: Path | None = None,
    ruta_modelo: Path = RUTA_MODELO_FINAL,
    ruta_reporte: Path = RUTA_REPORTE_METRICAS,
    ruta_comparativa: Path = RUTA_REPORTE_COMPARATIVA,
) -> dict[str, object]:
    """Ejecuta flujo básico: carga -> split -> 3 modelos -> evaluación -> guardado."""
    cargador = CargadorDatos()
    comparador = ComparadorModelos()

    x, y = cargador.preparar_xy(ruta_dataset=ruta_dataset)
    x_ent, x_pru, y_ent, y_pru = train_test_split(
        x,
        y,
        test_size=PROPORCION_PRUEBA,
        random_state=SEMILLA_ALEATORIA,
        stratify=y,
    )

    resultados_entrenamiento = comparador.entrenar_y_comparar(x_ent, y_ent)

    evaluaciones = [
        evaluar_modelo(resultado.nombre, resultado.modelo, x_pru, y_pru)
        for resultado in resultados_entrenamiento
    ]
    tabla = a_dataframe(evaluaciones)

    mejor = max(evaluaciones, key=lambda r: r.roc_auc)
    mejor_modelo = next(r.modelo for r in resultados_entrenamiento if r.nombre == mejor.nombre_modelo)

    ruta_modelo.parent.mkdir(parents=True, exist_ok=True)
    ruta_reporte.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(mejor_modelo, ruta_modelo)
    guardar_comparativa_csv(tabla, ruta_comparativa)

    metricas = {
        "mejor_modelo": mejor.nombre_modelo,
        "modelos": {fila["nombre_modelo"]: fila for fila in tabla.to_dict(orient="records")},
        "ruta_modelo": str(ruta_modelo),
        "ruta_comparativa": str(ruta_comparativa),
    }
    ruta_reporte.write_text(json.dumps(metricas, indent=2), encoding="utf-8")
    return metricas


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pipeline básico de diagnóstico de diabetes")
    parser.add_argument("--dataset", type=Path, default=None)
    parser.add_argument("--salida-modelo", type=Path, default=RUTA_MODELO_FINAL)
    parser.add_argument("--salida-reporte", type=Path, default=RUTA_REPORTE_METRICAS)
    parser.add_argument("--salida-comparativa", type=Path, default=RUTA_REPORTE_COMPARATIVA)
    return parser


def main() -> None:
    args = construir_parser().parse_args()
    ejecutar_pipeline_basico(
        ruta_dataset=args.dataset,
        ruta_modelo=args.salida_modelo,
        ruta_reporte=args.salida_reporte,
        ruta_comparativa=args.salida_comparativa,
    )


if __name__ == "__main__":
    main()
