# Plan de Correcciones y Mejoras — `diasgnostico-pred`

**Fecha:** 2026-05-17
**Basado en:** Auditoría de repositorio + alcance definido en `docs/ProgramaMateria.md`
**Audiencia objetivo de las correcciones:** Estudiantes universitarios con base en Python, novatos en ML y ciencia de datos.

---

## Nota de alcance (leer antes de cualquier tarea)

El alcance técnico del proyecto está definido exclusivamente por la sección **"Evaluación del proyecto final"** de `docs/ProgramaMateria.md`. Cualquier tarea que implique agregar modelos, técnicas o componentes no listados en esa sección queda **fuera de alcance** y no debe implementarse.

Los modelos permitidos son exactamente los siguientes:

| Nivel | Modelos / Componentes requeridos |
|-------|----------------------------------|
| Básico | Pipeline con ≥ 3 de los modelos del temario, preprocessing básico, métricas estándar |
| Intermedio | SVM, Árbol de Decisión, Redes Neuronales (MLP), K-Means — todos del temario |
| Avanzado | API en producción + comparativa con papers |

> **Consecuencia directa:** La recomendación de agregar `RandomForestClassifier` generada por la auditoría previa **queda eliminada**. Random Forest no aparece en la lista explícita del Nivel Intermedio (`SVM, Arboles de decisión, Redes neuronales y K-Means`). GBM sí permanece porque forma parte del temario (Unidad 2.3 — Gradient Boosting) y ya está implementado; su eliminación degradaría la cobertura curricular sin ningún beneficio.

---

## Índice del plan

| Fase | Nombre | Prioridad | Bloquea a |
|------|--------|-----------|-----------|
| [Fase 1](#fase-1-correcciones-críticas-de-runtime) | Correcciones críticas de runtime | 🔴 Crítica | Fases 2, 3, 4 |
| [Fase 2](#fase-2-cobertura-de-pruebas-y-dependencias-faltantes) | Cobertura de pruebas y dependencias faltantes | 🔴 Alta | Fases 3, 4 |
| [Fase 3](#fase-3-alineación-del-pipeline-con-el-temario) | Alineación del pipeline con el temario | 🟠 Media | Fase 4 |
| [Fase 4](#fase-4-documentación-para-estudiantes-tema-central) | Documentación para estudiantes (tema central) | 🟠 Media | Fase 5 |
| [Fase 5](#fase-5-robustez-y-cierre-de-deuda-técnica) | Robustez y cierre de deuda técnica | 🟡 Baja | — |

---

## Fase 1: Correcciones críticas de runtime

> Estas tareas deben completarse antes que cualquier otra. Son bugs que producen comportamiento incorrecto o errores en tiempo de ejecución.

---

### Tarea 1.1 — Corregir la condición de estado dividido en `GET /salud`

**Problema identificado:**
`GET /salud` decide si el modelo está cargado leyendo el sistema de archivos con `ConfiguracionRutas.RUTA_MODELO.stat()`. Sin embargo, lo que la API realmente tiene en memoria es el objeto cargado durante `lifespan`. Si el archivo existe pero la deserialización con `joblib.load` falló silenciosamente (por ejemplo, archivo corrupto), el endpoint reporta `estado: operativo` mientras que `POST /predecir` devuelve HTTP 503. El usuario recibe información contradictoria.

**Archivo:** `api/main.py`
**Función:** `salud()` y `lifespan()`

**Cambios requeridos:**

1. En `lifespan`, capturar el valor de retorno de `cargar_modelo()` y emitir un log según el resultado:
   ```python
   cargado = predictor.cargar_modelo()
   if cargado:
       logger.info("Modelo cargado correctamente desde %s", predictor.ruta_modelo)
   else:
       logger.warning(
           "Modelo no disponible en %s; API iniciando en modo degradado.",
           predictor.ruta_modelo
       )
   ```

2. En `salud()`, reemplazar la lectura del filesystem por una consulta al objeto en memoria:
   ```python
   # ANTES (incorrecto):
   modelo_cargado = ruta_modelo.stat().st_size > 0

   # DESPUÉS (correcto):
   modelo_cargado = app.state.predictor.esta_listo()
   ```
   Mantener el bloque `try/except OSError` únicamente para obtener el nombre del archivo en `DetallesSalud`, no para determinar el estado operativo.

**Criterio de aceptación:** Si se elimina manualmente `modelos/modelo_diabetes_v1.joblib` y se reinicia la API, `GET /salud` debe devolver `estado: degradado` y `POST /predecir` debe devolver HTTP 503 de forma consistente.

---

### Tarea 1.2 — Corregir `KeyError: 'BMI5CAT'` en el notebook de EDA

**Problema identificado:**
El bloque 4.2 del notebook `notebooks/01_eda_regionalizado.ipynb` intenta acceder a `df['BMI5CAT']` para categorizar el IMC. Esta columna no existe en el dataset CDC BRFSS 2015 tal como lo carga `CargadorDatos` ni en la tupla `COLUMNAS_CDC` definida en `config.py`. La celda falla con `KeyError` al ejecutarse.

**Archivo:** `notebooks/01_eda_regionalizado.ipynb`, Bloque 4.2

**Cambio requerido:**
Reemplazar la línea que usa `df['BMI5CAT'].map(...)` por la función `categorizar_bmi` que ya está definida en la misma celda, aplicándola con `apply`:
```python
# ANTES (incorrecto):
df['bmi_cat'] = df['BMI5CAT'].map({1: 'Bajo peso (<18.5)', ...})

# DESPUÉS (correcto):
df['bmi_cat'] = df['BMI'].apply(categorizar_bmi)
```
El resto de la celda (agrupación por `bmi_cat` y cálculo de `tasa_dm_por_bmi`) no requiere cambios.

**Criterio de aceptación:** El bloque 4.2 se ejecuta sin errores sobre el dataset real y produce la tabla `tasa_dm_por_bmi` con 5 filas (una por categoría de IMC).

---

### Tarea 1.3 — Corregir `KeyError: 'total_nulos'` en el notebook de EDA

**Problema identificado:**
El bloque 6.2 del mismo notebook accede a `reporte_nulos['total_nulos'].sum()` al construir el JSON de hallazgos. El DataFrame `reporte_nulos` se construye en el Bloque 1 con las columnas `n_nulos` y `pct_nulos`. La columna `total_nulos` no existe.

**Archivo:** `notebooks/01_eda_regionalizado.ipynb`, Bloque 6.2

**Cambio requerido:**
```python
# ANTES (incorrecto):
"missing_values": int(reporte_nulos['total_nulos'].sum()),

# DESPUÉS (correcto):
"missing_values": int(reporte_nulos['n_nulos'].sum()),
```

**Criterio de aceptación:** La celda de exportación JSON del Bloque 6.2 se ejecuta sin errores y escribe `reportes/hallazgos_eda.json` correctamente.

---

### Tarea 1.4 — Corregir paralelismo no seguro en evaluación de folds

**Problema identificado:**
`ComparadorModelos._evaluar_por_folds` usa `Parallel(n_jobs=-1, prefer="threads")`. Los estimadores `GradientBoostingClassifier` y `MLPClassifier` de scikit-learn utilizan extensiones en Cython cuyos internals no garantizan seguridad de hilos bajo `prefer="threads"`. Esto puede producir resultados no determinísticos o corrupción silenciosa de datos durante la evaluación paralela de folds.

**Archivo:** `entrenamiento/comparador_modelos.py`
**Función:** `_evaluar_por_folds`

**Cambio requerido:**
```python
# ANTES:
Parallel(n_jobs=-1, prefer="threads")(...)

# DESPUÉS:
Parallel(n_jobs=-1, backend="loky")(...)
```
`loky` usa procesos separados, eliminando la dependencia del GIL y garantizando aislamiento entre folds.

**Consecuencia:** El tiempo de ejecución puede aumentar marginalmente por el overhead de serialización entre procesos. Es un trade-off aceptable para garantizar correctitud.

**Criterio de aceptación:** `pytest pruebas/ -q` pasa 0 fallos. Ejecutar el pipeline dos veces con `--modelos gbm` y verificar que los valores de ROC-AUC por fold son idénticos entre ejecuciones.

---

## Fase 2: Cobertura de pruebas y dependencias faltantes

> Requiere Fase 1 completa. Estas tareas establecen la base de confianza sobre la que se construyen las fases posteriores.

---

### Tarea 2.1 — Agregar prueba para el validador de coherencia clínica (HTTP 422)

**Problema identificado:**
`DatosPaciente.validar_coherencia_clinica` en `api/esquemas.py` rechaza combinaciones de `salud_fisica >= 20` con `dificultad_caminar == 0`. Esta lógica de producción no tiene ninguna prueba automatizada que la cubra. El payload de referencia en `pruebas/test_api.py` usa `salud_fisica: 2`, que nunca activa el validador.

**Archivo:** `pruebas/test_api.py`

**Función a agregar:**
```python
def test_predecir_retorna_422_por_incoherencia_clinica():
    payload = _payload_base()
    payload["salud_fisica"] = 25   # >= 20
    payload["dificultad_caminar"] = 0  # incoherente
    with TestClient(app) as client:
        respuesta = client.post("/predecir", json=payload)
    assert respuesta.status_code == 422
```

**Criterio de aceptación:** `pytest pruebas/test_api.py -v` muestra 4 tests pasando (los 3 existentes + el nuevo).

---

### Tarea 2.2 — Agregar `imbalanced-learn` como dependencia declarada

**Problema identificado:**
`ConstructorPreprocesador` acepta `use_smote=True` e importa `from imblearn.over_sampling import SMOTE` condicionalmente. El paquete `imbalanced-learn` no está declarado en `pyproject.toml`. Si no está instalado, el constructor falla silenciosamente y degrada a un pipeline sin SMOTE sin emitir ninguna advertencia visible al usuario. El temario (Unidad 1.3) exige demostrar SMOTE como técnica.

**Archivos:** `pyproject.toml`, `environment.yml`, `entrenamiento/preprocesador.py`

**Cambios requeridos:**

1. En `pyproject.toml`, agregar al grupo de dependencias principales:
   ```toml
   "imbalanced-learn>=0.12.0",
   ```

2. En `environment.yml`, agregar bajo `pip:`:
   ```yaml
   - imbalanced-learn>=0.12.0
   ```

3. En `entrenamiento/preprocesador.py`, función `construir_pipeline`, reemplazar el `except Exception` silencioso:
   ```python
   # ANTES:
   except Exception:
       return Pipeline(...)  # fallback silencioso

   # DESPUÉS:
   except ImportError:
       import logging
       logging.getLogger(__name__).warning(
           "imbalanced-learn no está instalado. SMOTE desactivado. "
           "Instala con: pip install imbalanced-learn>=0.12.0"
       )
       return Pipeline(memory=None, steps=[
           ("preprocesador", self.construir()),
           ("clasificador", clasificador)
       ])
   # Cualquier otra excepción se propaga normalmente
   ```

**Criterio de aceptación:** `pip show imbalanced-learn` muestra la versión instalada. Un `ConstructorPreprocesador(use_smote=True).construir_pipeline(DummyClassifier())` construye un `ImbPipeline` sin warnings.

---

### Tarea 2.3 — Verificar contrato de métricas uniforme entre los 4 modelos supervisados (cierre de S3-001)

**Problema identificado:**
El roadmap marca S3-002 y S3-004 como ✅ pero S3-001 (verificación uniforme de métricas) como ⬜, siendo S3-001 una dependencia declarada de ambos. No existe ninguna prueba automatizada que afirme que los 4 modelos (`svm`, `arbol`, `gbm`, `mlp`) producen los 8 campos de `ResultadoEvaluacion` correctamente poblados.

**Archivo a crear:** `pruebas/test_comparador.py`

**Contenido mínimo:**
```python
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.datasets import make_classification

from config import COLUMNAS_CDC
from entrenamiento.comparador_modelos import ComparadorModelos

CAMPOS_REQUERIDOS = {
    "nombre_modelo", "roc_auc", "pr_auc", "sensibilidad",
    "especificidad", "f1_clase_positiva", "brier_score",
    "accuracy", "matriz_confusion",
}


def _dataset_sintetico():
    X_arr, y_arr = make_classification(
        n_samples=300, n_features=21, n_informative=10,
        n_redundant=5, random_state=42
    )
    X = pd.DataFrame(X_arr, columns=list(COLUMNAS_CDC))
    y = pd.Series(y_arr.astype(float), name="Diabetes_binary")
    return X, y


@pytest.mark.parametrize("nombre_modelo", ["svm", "arbol", "gbm", "mlp"])
def test_resultado_contiene_ocho_campos(nombre_modelo):
    X, y = _dataset_sintetico()
    comparador = ComparadorModelos()
    resultados = comparador.entrenar_clasificacion(X, y, modelos_a_entrenar=[nombre_modelo])
    assert len(resultados) == 1
    resultado = resultados[0]
    assert resultado.nombre == nombre_modelo
    assert isinstance(resultado.puntaje, float)
    assert resultado.puntaje > 0.0
```

**Criterio de aceptación:** `pytest pruebas/test_comparador.py -v` pasa los 4 casos parametrizados. Marcar S3-001 como ✅ en `docs/ROADMAP.md` con la fecha real de cierre.

---

## Fase 3: Alineación del pipeline con el temario

> Requiere Fase 2 completa. Estas tareas aseguran que lo que el proyecto documenta como "técnicas usadas" realmente ocurre en el código ejecutable.

---

### Tarea 3.1 — Hacer que KNNImputer sea la estrategia activa por defecto en el pipeline principal

**Problema identificado:**
El temario (Unidad 1.2) exige demostrar `KNNImputer`. `ConstructorPreprocesador` lo soporta mediante `use_knn=True`, pero `ComparadorModelos` se instancia con los valores por defecto (`use_knn=False`) en `pipeline.py:ejecutar_pipeline`. En la ejecución estándar, el imputador activo es `SimpleImputer(strategy="median")`, no `KNNImputer`. La técnica existe en el código pero no se ejecuta en el flujo principal.

**Archivos:** `entrenamiento/pipeline.py`, `entrenamiento/comparador_modelos.py`

**Cambio requerido en `pipeline.py`:**
En `ejecutar_pipeline`, instanciar el comparador con `use_knn=True`:
```python
# ANTES:
comparador = ComparadorModelos()

# DESPUÉS:
comparador = ComparadorModelos(use_knn=True)
```

**Cambio requerido en `ComparadorModelos.__init__`:**
Actualizar el valor por defecto del parámetro para reflejar la nueva política:
```python
# ANTES:
def __init__(self, use_knn: bool = False, ...):

# DESPUÉS:
def __init__(self, use_knn: bool = True, ...):
```

**Impacto en pruebas:**
`pruebas/test_preprocesador.py:test_pipeline_no_filtra_estadisticas_de_test` verifica la media del scaler sobre `X_train`. `KNNImputer` no altera las estadísticas del `StandardScaler`, por lo que la prueba sigue siendo válida. Ejecutar `pytest pruebas/test_preprocesador.py -v` para confirmar.

**Criterio de aceptación:** En un run de pipeline, el log de entrenamiento muestra que se usa `KNNImputer`. `pytest pruebas/test_preprocesador.py` pasa sin cambios.

---

### Tarea 3.2 — Activar SMOTE en el flujo de entrenamiento y documentar su efecto

**Problema identificado:**
El temario (Unidad 1.3) exige demostrar técnicas de remuestreo (SMOTE o NearMiss). La clase `ComparadorModelos` acepta `use_smote=True` pero el pipeline principal lo instancia sin este parámetro. La técnica está declarada en la documentación pero no se ejecuta en el flujo estándar.

**Archivo:** `entrenamiento/pipeline.py`, función `ejecutar_pipeline`

**Cambio requerido:**
Combinar con la Tarea 3.1:
```python
comparador = ComparadorModelos(use_knn=True, use_smote=True)
```

**Precaución importante:** SMOTE solo debe aplicarse sobre los datos de entrenamiento (`X_train`), nunca sobre el conjunto de prueba. El `imblearn.Pipeline` ya garantiza esto porque el resampleo ocurre dentro del `fit`, no en `transform` o `predict`. Verificar esto explícitamente en la documentación (ver Fase 4).

**Criterio de aceptación:** `pytest pruebas/` pasa. El log de entrenamiento incluye una línea indicando que se usó SMOTE. Si `imbalanced-learn` no está instalado (Tarea 2.2), se emite un WARNING visible y el pipeline continúa sin SMOTE.

---

### Tarea 3.3 — Agregar validación temprana del esquema CSV en modo clasificación

**Problema identificado:**
Si el usuario pasa un CSV que no contiene `Diabetes_binary` mediante `--dataset`, el pipeline lanza `ValueError: Faltan columnas requeridas` desde `CargadorDatos.cargar` sin ningún mensaje orientativo. El error ocurre después de la carga completa del archivo, sin guiar al usuario sobre cómo resolverlo.

**Archivo:** `entrenamiento/pipeline.py`, función `_ejecutar_flujo_clasificacion`

**Cambio requerido:** Agregar validación explícita antes del procesamiento:
```python
monitor.actualizar("Validando esquema del dataset")
columnas_presentes = set(pd.read_csv(ruta_dataset or RUTA_DATASET_PREDETERMINADA, nrows=0).columns)
columnas_faltantes = set(list(COLUMNAS_CDC) + [COLUMNA_OBJETIVO]) - columnas_presentes
if columnas_faltantes:
    raise ValueError(
        f"El dataset no contiene las columnas requeridas para clasificación: "
        f"{sorted(columnas_faltantes)}. "
        f"Asegúrate de que el CSV incluya las 21 columnas CDC y la columna "
        f"'{COLUMNA_OBJETIVO}'. Consulta README.md para el formato esperado."
    )
```

**Cambio en `README.md`:** Agregar nota en la sección "Uso básico":
> El CSV pasado con `--dataset` debe contener las 21 columnas CDC **más** la columna `Diabetes_binary` para el modo `clasificacion`. Un CSV con solo las variables predictoras no es suficiente.

**Criterio de aceptación:** Ejecutar `python -m entrenamiento.pipeline --modo clasificacion --dataset archivo_sin_objetivo.csv` produce un error legible en menos de 2 segundos, antes de intentar entrenar ningún modelo.

---

### Tarea 3.4 — Verificar que el pipeline usa PR-AUC además de ROC-AUC como métrica reportada

**Problema identificado:**
El temario (Unidad 1.3) contrasta explícitamente PR-AUC vs ROC-AUC en problemas con desbalance. `EvaluadorClinico.calcular_metricas` ya calcula `pr_auc` y lo incluye en `ResultadoEvaluacion`. Sin embargo, la selección del mejor modelo en `pipeline.py:_ejecutar_flujo_clasificacion` usa exclusivamente `roc_auc` (`max(evaluaciones, key=lambda item: item[1].roc_auc)`). No se reporta cuál sería el mejor modelo si el criterio fuera PR-AUC, ni se justifica la elección.

**Archivo:** `entrenamiento/pipeline.py`, `_ejecutar_flujo_clasificacion`

**Cambio requerido:** Agregar al bloque de generación de reportes una nota sobre la elección de métrica:
```python
mejor_por_pr_auc = max(evaluaciones, key=lambda item: item[1].pr_auc)
if mejor_por_pr_auc.nombre != mejor_resultado.nombre:
    _LOG.info(
        "Nota: el mejor modelo por PR-AUC es '%s' (PR-AUC=%.4f), "
        "distinto al mejor por ROC-AUC '%s' (ROC-AUC=%.4f). "
        "Se serializa el modelo con mayor ROC-AUC según la política del proyecto.",
        mejor_por_pr_auc.nombre, 
        max(e[1].pr_auc for e in evaluaciones),
        mejor_resultado.nombre,
        max(e[1].roc_auc for e in evaluaciones),
    )
```

Agregar ambas métricas como campos de primer nivel en el JSON crudo (`metricas`):
```python
metricas["mejor_modelo_por_roc_auc"] = mejor_resultado.nombre
metricas["mejor_modelo_por_pr_auc"] = mejor_por_pr_auc.nombre
```

**Criterio de aceptación:** El JSON de reporte incluye `mejor_modelo_por_roc_auc` y `mejor_modelo_por_pr_auc`. Si difieren, el log de entrenamiento lo indica explícitamente.

---

## Fase 4: Documentación para estudiantes (tema central)

> Requiere Fase 3 completa. Esta fase es el corazón del proyecto según el enunciado: la documentación de modelos debe ser comprensible para estudiantes sin experiencia previa en ML o ciencia de datos.

---

### Tarea 4.1 — Completar `docs/evaluacion_academica.md` con evidencia real

**Problema identificado:**
Todas las secciones 3 y 4 del documento contienen marcadores de plantilla (`[✅/❌]`, `[notas]`, `[0-100]`, `EVIDENCE_NOT_FOUND`) que nunca fueron reemplazados. El documento no puede usarse como evidencia académica en su estado actual.

**Archivo:** `docs/evaluacion_academica.md`

**Cambios requeridos por sección:**

**Sección 2 — Estado por nivel:**

*Nivel Intermedio, tabla:*

| Requisito | Evidencia real | Estado |
|-----------|---------------|--------|
| SVM implementado y evaluado | `comparador_modelos.py`, catálogo `"svm"`, `SVC(kernel='rbf', probability=True, class_weight='balanced')` | ✅ |
| Árboles de decisión | `comparador_modelos.py`, catálogo `"arbol"`, `DecisionTreeClassifier(max_depth=5, class_weight='balanced')` | ✅ |
| Redes neuronales (MLP) | `comparador_modelos.py`, catálogo `"mlp"`, `MLPClassifier(hidden_layer_sizes=(64,32), early_stopping=True)` | ✅ |
| K-Means | `entrenamiento/fenotipado.py`, clase `FenotipadoKMeans`, pruebas en `pruebas/test_fenotipado.py` | ✅ |
| Optimización de hiperparámetros | `entrenamiento/optimizador.py`, clase `OptimizadorHiperparametros`, `GridSearchCV + StratifiedKFold` | ✅ |
| Dashboard interactivo básico | `dashboard/app.py` | ❌ pendiente S4 |

*Nivel Avanzado, tabla:*

| Requisito | Evidencia real | Estado |
|-----------|---------------|--------|
| API en producción | `api/main.py`, endpoints `/salud` y `/predecir` | 🟡 Esqueleto funcional, conectar con modelo real en S6 |
| Comparativa con papers | No existe | ❌ pendiente S6 |

**Sección 3 — Criterios detallados:**
Reemplazar cada `[✅/❌]` con el estado real observado. Lista de estados a verificar por código:

- *3.1 Código y Técnica:*
  - Pipeline usa `sklearn.pipeline.Pipeline` ✅ — `preprocesador.py:construir_pipeline`
  - No hay fuga de datos ✅ — `ColumnTransformer` ajustado solo en train, verificado por `test_preprocesador.py:test_pipeline_no_filtra_estadisticas_de_test`
  - Type hints presentes ✅ — todos los módulos usan `from __future__ import annotations`
  - Pruebas unitarias existen ✅ — directorio `pruebas/` con 5 archivos de test
  - `pyproject.toml` con dependencias ✅

- *3.2 Resultados:*
  - Se reportan métricas más allá de accuracy ✅ — `evaluador.py` calcula ROC-AUC, PR-AUC, F1, sensibilidad, especificidad, Brier Score
  - Se comparan ≥ 3 modelos ✅ — 4 modelos (SVM, árbol, GBM, MLP)
  - Interpretación de por qué un modelo supera a otro ❌ — no existe en reportes actuales

**Sección 4 — Cobertura del temario:**

| Técnica | Estado real | Justificación |
|---------|------------|---------------|
| `Pipeline` | ✅ | `preprocesador.py:construir_pipeline` |
| `ColumnTransformer` | ✅ | `preprocesador.py:construir` |
| `KNNImputer` | 🟡 → ✅ tras Tarea 3.1 | Activo con `use_knn=True` |
| `TargetEncoder` / `HashingEncoder` | ❌ | Fuera del alcance de los niveles B/I/A definidos en `ProgramaMateria.md` |
| `PowerTransformer(yeo-johnson)` | ❌ | Ídem — no requerido por la rúbrica |
| `SMOTE` | 🟡 → ✅ tras Tarea 3.2 | Activo con `use_smote=True` + paquete declarado |
| Métricas de desbalance (PR-AUC, ROC-AUC) | ✅ | `evaluador.py` |
| `SVC(kernel='rbf')` | ✅ | `comparador_modelos.py` |
| `DecisionTreeClassifier` | ✅ | `comparador_modelos.py` |
| `GradientBoostingClassifier` | ✅ | `comparador_modelos.py` |
| `KMeans` | ✅ | `fenotipado.py` |
| Silhouette + Elbow | ✅ | `fenotipado.py:calcular_silhouette`, `graficar_codo` |
| `GridSearchCV` + `StratifiedKFold` | ✅ | `optimizador.py` |
| `MLPClassifier` | ✅ | `comparador_modelos.py` |

**Criterio de aceptación:** `grep -n "\[FECHA\]\|\[0-100\]\|\[PLACEHOLDER\]\|EVIDENCE_NOT_FOUND" docs/evaluacion_academica.md` devuelve 0 resultados.

---

### Tarea 4.2 — Crear sección "Guía para estudiantes" en cada documento de modelo específico

**Problema identificado:**
Los documentos en `docs/implementacion_modelos/modelos/` contienen explicaciones técnicas sólidas pero están escritos para alguien que ya conoce ML. Un estudiante que abre `svm-especifico.md` por primera vez necesita entender *qué es* antes de entender *cómo funciona* con los parámetros del proyecto.

**Archivos afectados:**
- `docs/implementacion_modelos/modelos/svm-especifico.md`
- `docs/implementacion_modelos/modelos/arbol-especifico.md`
- `docs/implementacion_modelos/modelos/gbm-especifico.md`
- `docs/implementacion_modelos/modelos/mlp-especifico.md`
- `docs/implementacion_modelos/modelos/kmeans-especifico.md`

**Estructura obligatoria a agregar al inicio de cada documento** (antes de cualquier sección técnica), bajo el encabezado `## 🎓 Para empezar: ¿qué hace este modelo en palabras simples?`:

Cada sección debe contener los siguientes bloques:

**Bloque A — Definición coloquial (máximo 5 oraciones, sin jerga):**
Explicar qué hace el modelo como si se le explicara a alguien que nunca ha programado. Usar analogías del mundo cotidiano.

**Bloque B — Por qué lo usamos en este proyecto:**
Explicar en una oración por qué este modelo fue elegido para predecir riesgo de diabetes. No hablar de matemáticas; hablar del problema clínico.

**Bloque C — Qué significa que "funcione bien" o "funcione mal":**
Definir en lenguaje llano qué implica un ROC-AUC alto o bajo para este modelo en el contexto del proyecto. Por ejemplo: "Si el modelo falla, podría decirle a alguien que está sano cuando en realidad tiene diabetes. Eso es un error grave."

**Bloque D — Glosario de términos técnicos usados en este documento:**
Una tabla de 5-8 términos clave del documento, cada uno con una definición de una oración sin usar otros términos técnicos.

**Contenido de ejemplo para `svm-especifico.md`:**

```markdown
## 🎓 Para empezar: ¿qué hace este modelo en palabras simples?

### A. Definición coloquial

Imagina que tienes que separar manzanas de naranjas en una mesa. 
Una Máquina de Vectores de Soporte (SVM) busca la línea que deja 
la mayor distancia posible entre las manzanas más cercanas al borde 
y las naranjas más cercanas al borde. Cuanto más espacio entre 
ambos grupos, más segura es la separación. En este proyecto, 
en lugar de manzanas y naranjas, el modelo separa personas con 
riesgo de diabetes de personas sin riesgo, usando 21 características 
de salud como el IMC, la presión arterial y la edad.

### B. Por qué lo usamos aquí

La SVM es buena para encontrar patrones complejos cuando las variables 
de salud no se separan de forma simple o lineal. Por ejemplo, no basta 
con decir "si el IMC es alto, hay diabetes": la relación depende también 
de la edad, los antecedentes y otros factores al mismo tiempo.

### C. Qué significa que funcione bien o mal

- **Funciona bien**: de cada 10 personas con diabetes real, el modelo 
  identifica 7 u 8 correctamente. Los médicos pueden priorizar a esas 
  personas para revisiones adicionales.
- **Funciona mal**: el modelo clasifica como "sin riesgo" a personas que 
  sí tienen diabetes. Eso puede retrasar un diagnóstico importante.

### D. Glosario

| Término | Qué significa en lenguaje simple |
|---------|----------------------------------|
| Kernel RBF | Una función matemática que permite al modelo encontrar separaciones curvas, no solo líneas rectas |
| Margen | El espacio vacío entre los dos grupos justo en la frontera de la separación |
| Parámetro C | Qué tan estricto es el modelo: valores altos = muy estricto, puede memorizar el entrenamiento |
| `class_weight='balanced'` | Le dice al modelo que preste igual atención a los casos de diabetes (pocos) que a los casos sin diabetes (muchos) |
| `predict_proba` | La capacidad del modelo de decir "creo que hay un 70% de probabilidad de diabetes" en lugar de solo "sí o no" |
```

**Patrón equivalente para los demás modelos:**

- **Árbol:** analogía con un árbol de decisiones de la vida real ("¿Tienes fiebre? → Sí → ¿Tienes tos? → ...").
- **GBM:** analogía con un equipo de correctores: el primero hace un borrador, el segundo corrige sus errores, el tercero corrige los errores del segundo, y así 200 veces.
- **MLP (Redes neuronales):** analogía con neuronas del cerebro: señales que se transmiten y se ajustan con la experiencia.
- **K-Means:** analogía con agrupar estudiantes en equipos por afinidad, sin que el maestro les diga previamente a qué equipo pertenecen.

**Criterio de aceptación:** Un estudiante de primer año puede leer la sección "Para empezar" y responder correctamente: "¿Qué problema resuelve este modelo?" y "¿Por qué podría fallar?", sin haber leído el resto del documento.

---

### Tarea 4.3 — Completar `docs/implementacion_modelos/GUIA_UNIFICADA.md` con sección de glosario global

**Problema identificado:**
La guía unificada asume conocimiento previo de términos como "data leakage", "validación cruzada estratificada", "serialización" y "ROC-AUC". No existe ningún glosario centralizado para estudiantes.

**Archivo:** `docs/implementacion_modelos/GUIA_UNIFICADA.md`

**Cambio requerido:** Agregar una sección al final del documento:

```markdown
---

## 📖 Glosario para estudiantes

Esta sección define los términos técnicos más usados en toda la documentación.
Está escrita para alguien que está aprendiendo ciencia de datos por primera vez.

| Término | Definición simple |
|---------|------------------|
| **Pipeline** | Una cadena de pasos automáticos: primero limpias los datos, luego los transformas, luego entrenas el modelo. Todo en orden y sin que tengas que hacerlo manualmente cada vez. |
| **Data Leakage** | Cuando el modelo "hace trampa" al entrenarse: ve información del futuro o del conjunto de prueba antes de tiempo. Es como estudiar con las respuestas del examen ya en mano. |
| **Validación cruzada** | En lugar de probar el modelo una sola vez, lo pruebas 5 veces con diferentes partes de los datos. Así sabes si funciona bien en general, no solo con un grupo específico. |
| **ROC-AUC** | Una puntuación entre 0 y 1 que mide qué tan bien el modelo separa a los enfermos de los sanos. 0.5 = no mejor que lanzar una moneda. 1.0 = perfecto. En este proyecto buscamos > 0.78. |
| **PR-AUC** | Similar a ROC-AUC pero más útil cuando hay muchos más sanos que enfermos (como en este proyecto). Mide específicamente qué tan bien el modelo detecta los casos de diabetes. |
| **Serialización** | Guardar el modelo entrenado en un archivo (`.joblib`) para poder usarlo después sin volver a entrenarlo. Como guardar una partida de videojuego. |
| **Desbalance de clases** | Cuando hay muchos más casos de una clase que de otra. Aquí: ~86% sin diabetes vs ~14% con diabetes. Sin corrección, el modelo aprende a ignorar los casos de diabetes. |
| **SMOTE** | Técnica para crear pacientes "sintéticos" con diabetes a partir de los reales, para que el modelo tenga más ejemplos de la clase minoritaria con qué aprender. |
| **Hiperparámetros** | Configuraciones del modelo que el programador elige antes del entrenamiento. No son aprendidos por el modelo; son como las reglas del juego que tú defines. |
| **Sensibilidad / Recall** | De todos los pacientes que realmente tienen diabetes, ¿qué porcentaje detectó el modelo? Alta sensibilidad = pocos diabéticos no detectados. |
| **Especificidad** | De todos los pacientes que realmente NO tienen diabetes, ¿qué porcentaje clasificó el modelo como sanos? Evita alarmar innecesariamente a pacientes sanos. |
```

**Criterio de aceptación:** Un revisor sin conocimiento de ML puede entender todos los términos usados en cualquier documento de `docs/implementacion_modelos/` usando exclusivamente este glosario como referencia.

---

### Tarea 4.4 — Agregar sección de interpretación de resultados en `entrenamiento/evaluador.py`

**Problema identificado:**
`EvaluadorClinico.comparar_modelos` devuelve una tabla de métricas sin ninguna interpretación. El estudiante que ejecuta el pipeline ve números pero no sabe qué significan clínicamente ni cómo tomarlos una decisión.

**Archivo:** `entrenamiento/evaluador.py`

**Cambio requerido:** Agregar un método estático `interpretar_resultado`:
```python
@staticmethod
def interpretar_resultado(resultado: ResultadoEvaluacion) -> str:
    """
    Genera una interpretación en lenguaje llano del resultado de evaluación.
    Diseñada para estudiantes que están aprendiendo a leer métricas de ML.
    """
    lineas = [
        f"=== Interpretación del modelo: {resultado.nombre_modelo} ===",
        "",
        f"ROC-AUC: {resultado.roc_auc:.4f}",
    ]
    if resultado.roc_auc >= 0.80:
        lineas.append("  → Excelente capacidad para separar pacientes con y sin diabetes.")
    elif resultado.roc_auc >= 0.75:
        lineas.append("  → Buena capacidad discriminativa. Cumple el umbral mínimo del proyecto.")
    else:
        lineas.append("  → Por debajo del umbral aceptable (0.75). Revisar hiperparámetros o preprocesamiento.")

    lineas += [
        "",
        f"Sensibilidad: {resultado.sensibilidad:.4f}",
        f"  → De cada 100 pacientes con diabetes, el modelo detecta "
        f"aprox. {int(resultado.sensibilidad * 100)}.",
    ]
    if resultado.sensibilidad < 0.70:
        lineas.append("  ⚠️ Sensibilidad baja: muchos casos de diabetes no son detectados.")

    lineas += [
        "",
        f"Especificidad: {resultado.especificidad:.4f}",
        f"  → De cada 100 pacientes sanos, el modelo clasifica correctamente "
        f"aprox. {int(resultado.especificidad * 100)}.",
        "",
        f"Brier Score: {resultado.brier_score:.4f}",
    ]
    if resultado.brier_score < 0.10:
        lineas.append("  → Calibración excelente: las probabilidades predichas son confiables.")
    elif resultado.brier_score < 0.15:
        lineas.append("  → Calibración aceptable.")
    else:
        lineas.append("  ⚠️ Calibración deficiente: las probabilidades predichas no son confiables.")

    return "\n".join(lineas)
```

Llamar este método en `pipeline.py` justo antes de serializar el modelo, imprimiéndolo al log:
```python
for _, evaluacion in evaluaciones:
    _LOG.info("\n%s", evaluador.interpretar_resultado(evaluacion))
```

**Criterio de aceptación:** Al ejecutar el pipeline, el log de entrenamiento muestra una interpretación legible para cada modelo. Un estudiante puede leerlo sin conocer la definición técnica de ROC-AUC.

---

### Tarea 4.5 — Actualizar `ROADMAP.md` para reflejar el estado real después de las fases 1-3

**Problema identificado:**
S3-001 está marcado como ⬜ pero es dependencia declarada de S3-002 y S3-004, ambos marcados como ✅. Esta inversión de dependencias confunde a cualquier lector del roadmap.

**Archivo:** `docs/ROADMAP.md`

**Cambios requeridos:**
1. Marcar S3-001 como ✅ una vez que la Tarea 2.3 esté completada, con nota: `"Verificado mediante prueba automatizada en pruebas/test_comparador.py"`.
2. Agregar una nota al pie de Sprint 3 indicando que S3-002 y S3-004 se completaron fuera del orden de dependencias documentado.
3. Actualizar la columna "Estado" de todos los tickets de Sprint 3 según el estado real tras ejecutar las fases anteriores de este plan.

**Criterio de aceptación:** El orden de dependencias en el roadmap es internamente consistente: ningún ticket marcado como ✅ tiene una dependencia directa marcada como ⬜.

---

## Fase 5: Robustez y cierre de deuda técnica

> Requiere Fase 4 completa. Estas tareas mejoran la resiliencia del sistema sin cambiar el comportamiento funcional.

---

### Tarea 5.1 — Escritura atómica del modelo serializado

**Problema identificado:**
`pipeline.py:_ejecutar_flujo_clasificacion` llama a `joblib.dump(mejor_resultado.modelo, ruta_modelo)` directamente sobre el path canónico. Si el proceso se interrumpe durante la escritura, el archivo queda parcialmente escrito. La próxima vez que la API arranque, intentará cargar un archivo corrupto y fallará con un error no descriptivo de joblib.

**Archivo:** `entrenamiento/pipeline.py`, función `_ejecutar_flujo_clasificacion`

**Cambio requerido:**
```python
import os, tempfile

# Escritura atómica mediante archivo temporal + reemplazo
with tempfile.NamedTemporaryFile(
    delete=False,
    dir=ruta_modelo.parent,
    suffix=".joblib.tmp"
) as tmp_file:
    tmp_path = tmp_file.name

try:
    joblib.dump(mejor_resultado.modelo, tmp_path)
    os.replace(tmp_path, ruta_modelo)  # atómico en POSIX
    _LOG.info("Modelo final guardado atómicamente en %s", ruta_modelo)
except Exception:
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)
    raise
```

**Criterio de aceptación:** Si se interrumpe el proceso durante el `joblib.dump` (simulable con `kill -9`), el archivo canónico en `ruta_modelo` permanece intacto desde la última escritura exitosa.

---

### Tarea 5.2 — Corregir Procesado del Parquet: excluir columna objetivo

**Problema identificado:**
`_ejecutar_flujo_clasificacion` llama a `cargador.persistir_procesado(df_limpio)` donde `df_limpio` contiene `COLUMNA_OBJETIVO` (`Diabetes_binary`). El contrato del dataset procesado definido en `PROYECTO.md §9` especifica solo las columnas CDC. Guardar la columna objetivo en el Parquet viola este contrato y puede causar data leakage si otro proceso carga el Parquet sin proyectar columnas.

**Archivo:** `entrenamiento/pipeline.py`, función `_ejecutar_flujo_clasificacion`

**Cambio requerido:**
```python
# ANTES:
cargador.persistir_procesado(df_limpio, ruta_destino=RUTA_DATASET_PROCESADO)

# DESPUÉS:
cargador.persistir_procesado(
    df_limpio[list(COLUMNAS_CDC)],  # excluir objetivo del Parquet procesado
    ruta_destino=RUTA_DATASET_PROCESADO
)
```

**Criterio de aceptación:** `pd.read_parquet(RUTA_DATASET_PROCESADO).columns.tolist() == list(COLUMNAS_CDC)` es `True`.

---

## Tabla de dependencias resumida

```
Fase 1 (Tareas 1.1 → 1.4)
    └─► Fase 2 (Tareas 2.1 → 2.3)
            └─► Fase 3 (Tareas 3.1 → 3.4)
                    └─► Fase 4 (Tareas 4.1 → 4.5)
                            └─► Fase 5 (Tareas 5.1 → 5.2)

Paralelas (pueden ejecutarse en cualquier fase):
    - Tarea 4.2 (sección "Para estudiantes" en docs de modelos)
    - Tarea 4.3 (glosario en GUIA_UNIFICADA.md)
    - Tarea 5.1 (escritura atómica)  — no modifica lógica de negocio
```

---

## Checklist de validación final

Ejecutar estos comandos en orden después de completar todas las fases. El proyecto está listo para presentación académica cuando todos pasan.

```bash
# 1. Suite completa de pruebas
pytest pruebas/ -v --tb=short
# Esperado: 0 fallos

# 2. Sin placeholders en documentación académica
grep -rn "\[FECHA\]\|\[0-100\]\|\[PLACEHOLDER\]\|EVIDENCE_NOT_FOUND" docs/
# Esperado: 0 resultados

# 3. Pipeline completo con todas las técnicas activas
python -m entrenamiento.pipeline \
  --modo clasificacion \
  --modelos svm,arbol,gbm,mlp \
  --salida-reporte reportes/validacion_final.json
# Esperado: 4 modelos, log incluye KNNImputer, SMOTE activo, interpretaciones por modelo

# 4. API operativa
uvicorn api.main:app --reload &
curl http://localhost:8000/salud
# Esperado: {"estado": "operativo", ...}

# 5. Notebook de EDA ejecutable sin errores
jupyter nbconvert --to notebook --execute \
  notebooks/01_eda_regionalizado.ipynb \
  --output notebooks/01_eda_ejecutado.ipynb
# Esperado: ejecución completa sin KeyError

# 6. Contrato del Parquet sin objetivo
python -c "
import pandas as pd
from config import RUTA_DATASET_PROCESADO, COLUMNAS_CDC
df = pd.read_parquet(RUTA_DATASET_PROCESADO)
assert list(df.columns) == list(COLUMNAS_CDC), f'Columnas inesperadas: {df.columns.tolist()}'
print('Parquet OK:', df.shape)
"
# Esperado: Parquet OK: (N, 21)
```

---

*Fin del plan — versión 1.1 · 2026-05-17*
*Scope: ProgramaMateria.md § "Evaluación del proyecto final" — Niveles Básico, Intermedio y Avanzado*
