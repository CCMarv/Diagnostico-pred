from __future__ import annotations

"""Generación de reportes legibles a partir de métricas crudas (ítems S3 y S5)."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from config import REPORTES_DIR


def guardar_json_crudo(datos: dict, ruta_salida: Path) -> Path:
    """Guarda métricas crudas en JSON para su posterior síntesis.

    Args:
        datos: diccionario serializable con la salida bruta del pipeline.
        ruta_salida: ruta donde se guardará el archivo JSON.

    Returns:
        Ruta final del archivo JSON generado.
    """
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_salida.write_text(json.dumps(datos, indent=2, ensure_ascii=False), encoding="utf-8")
    return ruta_salida


def construir_reporte_clasificacion(metricas: dict, tabla: pd.DataFrame, ruta_cruda: Path | None = None) -> str:
    """Convierte las métricas crudas de clasificación en un reporte legible.

    Args:
        metricas: salida cruda serializable generada por el pipeline.
        tabla: tabla comparativa de modelos.
        ruta_cruda: ruta del JSON crudo para documentar el origen.

    Returns:
        Texto Markdown listo para persistirse como reporte humano.
    """
    timestamp = metricas.get("timestamp", datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S"))
    mejor_modelo = metricas.get("mejor_modelo", "desconocido")
    modelos = metricas.get("modelos", {})
    desbalance = metricas.get("desbalance", {})

    mejor = modelos.get(mejor_modelo, {})
    lineas: list[str] = [
        "# Reporte legible de clasificación",
        "",
        f"**Fecha de generación:** {timestamp}",
        f"**Modelo ganador:** {mejor_modelo}",
    ]
    if ruta_cruda is not None:
        lineas.append(f"**Origen crudo:** {ruta_cruda.as_posix()}")
    lineas.extend([
        "",
        "## Resumen ejecutivo",
        f"- Se compararon {len(modelos)} modelos supervisados con el mismo conjunto de prueba.",
        f"- El mejor desempeño global fue de **{mejor.get('roc_auc', 0.0):.4f} ROC-AUC**.",
        f"- La prevalencia de clase positiva observada fue **{desbalance.get('pct_clase_1', 0.0):.4f}**.",
        f"- El desbalance se aproximó a una razón de **{desbalance.get('ratio', 0.0):.2f}:1**.",
        "",
        "## Tabla comparativa",
        _tabla_markdown(tabla),
        "",
        "## Interpretación clínica",
        _interpretar_modelo_ganador(mejor_modelo, mejor),
        "",
        "## Nota operativa",
        "Este reporte se sintetiza a partir de un JSON crudo generado por el pipeline. Los artefactos crudos se mantienen fuera del repositorio para evitar versionar salidas volátiles.",
        "",
    ])
    return "\n".join(lineas)


def tabla_comparativa_desde_metricas(metricas: dict) -> pd.DataFrame:
    """Construye una tabla compacta de métricas a partir del bloque `modelos`.

    Args:
        metricas: diccionario crudo del pipeline con el bloque `modelos`.

    Returns:
        DataFrame con las columnas útiles para lectura humana.
    """
    filas = []
    for nombre, resumen in metricas.get("modelos", {}).items():
        filas.append(
            {
                "nombre_modelo": resumen.get("nombre_modelo", nombre),
                "roc_auc": resumen.get("roc_auc", 0.0),
                "pr_auc": resumen.get("pr_auc", 0.0),
                "sensibilidad": resumen.get("sensibilidad", 0.0),
                "especificidad": resumen.get("especificidad", 0.0),
                "f1_clase_positiva": resumen.get("f1_clase_positiva", 0.0),
                "brier_score": resumen.get("brier_score", 0.0),
                "accuracy": resumen.get("accuracy", 0.0),
            }
        )
    return pd.DataFrame(filas)


def construir_reporte_clustering(metricas: dict, ruta_cruda: Path | None = None) -> str:
    """Convierte las métricas crudas de clustering en un reporte legible.

    Args:
        metricas: salida cruda del modo clustering.
        ruta_cruda: ruta del JSON crudo para documentar el origen.

    Returns:
        Texto Markdown listo para persistirse como reporte humano.
    """
    timestamp = metricas.get("timestamp", datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S"))
    lineas = [
        "# Reporte legible de clustering",
        "",
        f"**Fecha de generación:** {timestamp}",
        f"**Modelo:** {metricas.get('modelo', 'kmeans')}",
    ]
    if ruta_cruda is not None:
        lineas.append(f"**Origen crudo:** {ruta_cruda.as_posix()}")
    lineas.extend([
        "",
        "## Resumen ejecutivo",
        f"- El modelo de clustering obtuvo una inercia de **{metricas.get('puntaje', 0.0):.4f}**.",
        "- Este valor debe interpretarse junto con la coherencia clínica de los fenotipos y no como una métrica supervisada.",
        "",
        "## Nota operativa",
        "El reporte humano se genera a partir del JSON crudo del pipeline y puede reproducirse sin reentrenar el modelo.",
        "",
    ])
    return "\n".join(lineas)


def guardar_reporte_legible(texto: str, ruta_salida: Path) -> Path:
    """Persiste el reporte Markdown legible."""
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    ruta_salida.write_text(texto, encoding="utf-8")
    return ruta_salida


def ruta_legible_desde_crudo(ruta_cruda: Path) -> Path:
    """Deriva una ruta Markdown a partir de una ruta JSON cruda."""
    return ruta_cruda.with_suffix(".md")


def _tabla_markdown(tabla: pd.DataFrame) -> str:
    encabezados = list(tabla.columns)
    lineas = [
        "| " + " | ".join(encabezados) + " |",
        "| " + " | ".join(["---"] * len(encabezados)) + " |",
    ]
    for _, fila in tabla.iterrows():
        valores = []
        for columna in encabezados:
            valor = fila[columna]
            if isinstance(valor, float):
                valores.append(f"{valor:.4f}")
            else:
                valores.append(str(valor))
        lineas.append("| " + " | ".join(valores) + " |")
    return "\n".join(lineas)


def _interpretar_modelo_ganador(nombre_modelo: str, metricas: dict) -> str:
    roc_auc = float(metricas.get("roc_auc", 0.0))
    pr_auc = float(metricas.get("pr_auc", 0.0))
    sensibilidad = float(metricas.get("sensibilidad", 0.0))
    especificidad = float(metricas.get("especificidad", 0.0))
    brier = float(metricas.get("brier_score", 0.0))

    return (
        f"El modelo **{nombre_modelo}** concentra el mejor balance observado: ROC-AUC {roc_auc:.4f}, PR-AUC {pr_auc:.4f}, "
        f"sensibilidad {sensibilidad:.4f}, especificidad {especificidad:.4f} y Brier Score {brier:.4f}. "
        "En un contexto de tamizaje clínico, esto sugiere que el modelo ordena correctamente el riesgo y mantiene una calibración razonable para priorización, aunque la sensibilidad debe revisarse antes de un despliegue operativo."
    )