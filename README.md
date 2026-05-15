# Diasgnostico-pred

Proyecto de diagnóstico predictivo de diabetes con arquitectura modular en español. El objetivo es cumplir la rúbrica académica por niveles y dejar claro qué parte del proyecto hace cada cosa, dónde se implementan los modelos, cómo se ajustan sus hiperparámetros y dónde se guardan los resultados.

## Objetivo por nivel

### Nivel Básico  
Requisito mínimo del proyecto.

- Pipeline completo con 3 modelos supervisados.
- Preprocessing básico y reproducible.
- Métricas de evaluación estándar.

### Nivel Intermedio

- Todos los modelos del temario: SVM, árboles de decisión, redes neuronales y K-Means.
- Dashboard interactivo básico.

### Nivel Avanzado

- Sistema en producción mediante API.
- Comparativa con papers académicos.

## Dónde vive cada parte

| Componente | Qué resuelve | Archivo principal | Resultado esperado |
|---|---|---|---|
| Carga y validación de datos | Leer el dataset CDC y verificar columnas y desbalance | [entrenamiento/cargador_datos.py](entrenamiento/cargador_datos.py) | DataFrame limpio y separación `X/y` |
| Preprocesamiento | Imputación, escalado y codificación por tipo de variable | [entrenamiento/preprocesador.py](entrenamiento/preprocesador.py) | `ColumnTransformer` y `Pipeline` listos para entrenamiento |
| Modelado supervisado | Entrenar y comparar SVM, árbol, GBM y MLP | [entrenamiento/comparador_modelos.py](entrenamiento/comparador_modelos.py) | Lista de modelos comparados con ROC-AUC |
| Evaluación clínica | Calcular ROC-AUC, PR-AUC, sensibilidad, especificidad, F1 y Brier | [entrenamiento/evaluador.py](entrenamiento/evaluador.py) | Tabla comparativa y gráficas de desempeño |
| Orquestación del entrenamiento | Ejecutar split, entrenamiento, evaluación y guardado | [entrenamiento/pipeline.py](entrenamiento/pipeline.py) | Modelo final `.joblib` y reporte de métricas |
| Inferencia | Cargar el modelo serializado y predecir | [inferencia/predictor.py](inferencia/predictor.py) | Predicción clínica con probabilidad y clase |
| API productiva | Exponer `/salud` y `/predecir` | [api/main.py](api/main.py) | Servicio FastAPI ejecutable |
| Notebook EDA | Exploración regionalizada CDC vs. ENSANUT | [notebooks/01_eda_regionalizado.ipynb](notebooks/01_eda_regionalizado.ipynb) | Gráficas, contrastes y conclusiones del EDA |

## Modelos, hiperparámetros y dónde se ajustan

La implementación de modelos está centralizada en [entrenamiento/comparador_modelos.py](entrenamiento/comparador_modelos.py). Cada modelo se entrena dentro de un `Pipeline` que ya incluye el preprocesamiento, para evitar data leakage.

| Modelo | Qué aporta | Hiperparámetros clave | Resultado que produce |
|---|---|---|---|
| SVM | Buen separador en espacios con variables mixtas | `kernel='rbf'`, `C`, `gamma`, `class_weight='balanced'`, `probability=True` | Predicción con probabilidad y ROC-AUC comparativa |
| Árbol de decisión | Interpretabilidad y reglas clínicas | `max_depth=5`, `ccp_alpha=0.0`, `class_weight='balanced'` | Reglas simples y comparables contra otros modelos |
| Gradient Boosting | Mejor rendimiento con ensamble de árboles | `n_estimators=200`, `max_depth=4`, `learning_rate=0.05` | Modelo fuerte para comparar contra literatura |
| MLP | Captura relaciones no lineales más complejas | `hidden_layer_sizes=(64, 32)`, `max_iter=500`, `early_stopping=True` | Red neuronal base dentro del mismo Pipeline |
| K-Means | Agrupación no supervisada para fenotipado | `n_clusters=3`, `random_state=42` | Inercia y agrupaciones clínicas exploratorias |

Los ajustes del catálogo de modelos están en [entrenamiento/comparador_modelos.py](entrenamiento/comparador_modelos.py). El preprocesamiento que alimenta esos modelos está en [entrenamiento/preprocesador.py](entrenamiento/preprocesador.py).

## Qué entrega cada módulo

### `entrenamiento/preprocesador.py`

Define el `ColumnTransformer` que separa variables en:

- Continuas: `BMI`, `MentHlth`, `PhysHlth`.
- Binarias: `HighBP`, `HighChol`, `CholCheck`, `Smoker`, `Stroke`, `HeartDiseaseorAttack`, `PhysActivity`, `Fruits`, `Veggies`, `HvyAlcoholConsump`, `AnyHealthcare`, `NoDocbcCost`, `DiffWalk`, `Sex`.
- Ordinales: `GenHlth`, `Age`, `Education`, `Income`.

Su función es dejar los datos listos para entrenar sin mezclar tipos de variables ni filtrar información del conjunto de prueba.

### `entrenamiento/comparador_modelos.py`

Contiene el catálogo de modelos y sus parámetros. Aquí se decide:

- qué modelos se entrenan,
- cómo se comparan,
- con qué validación cruzada,
- y cuál es el mejor según ROC-AUC.

### `entrenamiento/evaluador.py`

Calcula las métricas clínicas y genera los artefactos de análisis:

- ROC-AUC,
- PR-AUC,
- sensibilidad,
- especificidad,
- F1,
- Brier score,
- matriz de confusión,
- curva ROC,
- curva Precision-Recall,
- curva de calibración.

### `entrenamiento/pipeline.py`

Es el orquestador. Ejecuta el flujo completo:

1. carga datos,
2. hace split entrenamiento/prueba,
3. entrena modelos,
4. evalúa resultados,
5. guarda el mejor `.joblib`,
6. escribe un reporte JSON con métricas.

### `api/main.py`

Expone el modelo entrenado en producción.

- `GET /salud`: verifica si el modelo está disponible.
- `POST /predecir`: recibe un paciente y devuelve clase de riesgo y probabilidad.

## Dónde quedan los resultados

Los artefactos importantes del entrenamiento quedan en estas rutas:

- Modelo final: `modelos/modelo_diabetes_v1.joblib`.
- Modelo versionado por corrida: `modelos/modelo_diabetes_vYYYYMMDD_HHMMSS.joblib`.
- Reporte principal de métricas: `reportes/metricas_sprint1.json`.
- Comparativa de modelos: `reportes/comparativa_modelos.md`.
- Curvas ROC y Precision-Recall: `reportes/curvas_<modelo>.png`.
- Curvas de calibración: `reportes/calibracion_<modelo>.png`.
- Dataset procesado: `datos/procesados/dataset_procesado.parquet`.

## Qué debe hacer cada nivel de la rúbrica

### Para cumplir el nivel básico

Hay que cerrar el flujo mínimo de entrenamiento en [entrenamiento/pipeline.py](entrenamiento/pipeline.py): preprocesamiento, 3 modelos, comparación y métricas estándar. El modelo final debe quedar serializado y ser compatible con [inferencia/predictor.py](inferencia/predictor.py).

### Para cumplir el nivel intermedio

Además del flujo básico, deben estar presentes todos los modelos del temario. En este repositorio eso se traduce en el catálogo de [entrenamiento/comparador_modelos.py](entrenamiento/comparador_modelos.py), donde ya están SVM, árbol de decisión, GBM, MLP y K-Means.

### Para cumplir el nivel avanzado

La API ya cubre la parte de producción en [api/main.py](api/main.py). Lo que queda es mantener coherencia entre el modelo entrenado, el reporte de métricas y la comparación con literatura académica y contexto regional.

## Ejecución local

```bash
python -m pip install -e .[dev]
pytest
uvicorn api.main:app --reload
```

