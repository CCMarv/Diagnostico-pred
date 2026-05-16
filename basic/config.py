from __future__ import annotations

from pathlib import Path
from typing import Final

BASE_DIR: Final[Path] = Path(__file__).resolve().parent
DATOS_DIR: Final[Path] = BASE_DIR / "datos"
DATOS_BRUTOS_DIR: Final[Path] = DATOS_DIR / "brutos"
DATOS_PROCESADOS_DIR: Final[Path] = DATOS_DIR / "procesados"
MODELOS_DIR: Final[Path] = BASE_DIR / "modelos"
REPORTES_DIR: Final[Path] = BASE_DIR / "reportes"

NOMBRE_DATASET: Final[str] = "diabetes_binary_health_indicators_BRFSS2015.csv"
RUTA_DATASET_PREDETERMINADA: Final[Path] = DATOS_BRUTOS_DIR / NOMBRE_DATASET
RUTA_DATASET_PROCESADO: Final[Path] = DATOS_PROCESADOS_DIR / "dataset_procesado.parquet"
RUTA_MODELO_FINAL: Final[Path] = MODELOS_DIR / "modelo_diabetes_basic.joblib"
RUTA_REPORTE_METRICAS: Final[Path] = REPORTES_DIR / "metricas_basicas.json"
RUTA_REPORTE_COMPARATIVA: Final[Path] = REPORTES_DIR / "comparativa_modelos.csv"

COLUMNAS_CDC: Final[tuple[str, ...]] = (
    "HighBP",
    "HighChol",
    "CholCheck",
    "BMI",
    "Smoker",
    "Stroke",
    "HeartDiseaseorAttack",
    "PhysActivity",
    "Fruits",
    "Veggies",
    "HvyAlcoholConsump",
    "AnyHealthcare",
    "NoDocbcCost",
    "GenHlth",
    "MentHlth",
    "PhysHlth",
    "DiffWalk",
    "Sex",
    "Age",
    "Education",
    "Income",
)
COLUMNA_OBJETIVO: Final[str] = "Diabetes_binary"

SEMILLA_ALEATORIA: Final[int] = 42
PROPORCION_PRUEBA: Final[float] = 0.2
MODELOS_SUPERVISADOS: Final[tuple[str, ...]] = ("logistica", "arbol", "svm")

TITULO_API: Final[str] = "API básica de diagnóstico de diabetes"
VERSION_SISTEMA: Final[str] = "basic-0.1.0"
UMBRAL_RIESGO_BAJO: Final[float] = 0.33
UMBRAL_RIESGO_ALTO: Final[float] = 0.66
MARGEN_INCERTIDUMBRE: Final[float] = 0.05
