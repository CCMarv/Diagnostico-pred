---
Autor: Equipo diasgnostico-pred
Fecha: 2026-05-17
Versión: 0.1.0
ID: DEC-20260517-001
---

# Decisiones de Diseño (resumen ejecutivo)

- **Estructura del proyecto**: capas separadas — `datos`, `entrenamiento`, `inferencia`, `api`. Cada capa tiene responsabilidades claras y límites de contrato.
- **Serialización de modelos**: todos los modelos se guardan como `sklearn.Pipeline` completo (preprocesador + estimador) usando `joblib`. Esto asegura que `PredictorDiabetes` pueda cargar y llamar a `predict_proba` sin cambios.
- **Preprocesamiento**: aplicar `ColumnTransformer` y ajustar SOLO sobre `X_train` para evitar data leakage.
- **Entrenamiento y reproducibilidad**: constantes (rutas, semillas, umbrales) centralizadas en `config.py`.
- **Interfaz de inferencia**: `PredictorDiabetes.predecir()` recibe un `pd.DataFrame` de una fila con las columnas CDC oficiales (`COLUMNAS_CDC`) y devuelve probabilidades; la API realiza el mapeo de nombres de campo.
- **Gestión de datasets**: se provee un script descargador (`entrenamiento/descargador_dataset.py`) que usa `ucimlrepo`. La descarga no ocurre automáticamente por diseño; el usuario puede ejecutarla explícitamente o pasar `--dataset` al pipeline.
- **K-Means (fenotipado)**: declarado como módulo de investigación. No está integrado en el pipeline de clasificación automatizado; su integración está planificada para Sprint 3.
- **Pruebas y calidad**: cada módulo nuevo debe llevar su `pruebas/test_<modulo>.py`. Ejecutar `pytest -q` antes de finalizar PRs.

## Registro de Decisiones

| ID | Fecha | Resumen | Archivos relacionados | Estado |
|---|---:|---|---|---|
| DEC-20260517-001 | 2026-05-17 | Añadida cabecera metadata y registro; confirmó que la descarga del dataset es manual (descargador separado) y que K-Means queda como investigación para Sprint 3. | README.md, entrenamiento/descargador_dataset.py, PROYECTO.md | Adoptada |

## Fuentes y referencias

- Fuente única de constantes y rutas: `config.py`
- Orquestador y contratos: `entrenamiento/pipeline.py`, `entrenamiento/comparador_modelos.py`
- Contrato API / validación: `api/esquemas.py`, `inferencia/predictor.py`

## Alcance excluido

- Esta página no pretende contener código ejecutable ni pruebas automatizadas. Las pruebas y validaciones se mantienen en `pruebas/` y la ejecución por desarrolladores es manual según la checklist de `docs/DOCUMENTATION_GUIDELINES.md`.

Referencias: PROYECTO.md, docs/ROADMAP.md, config.py
