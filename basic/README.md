# basic — réplica mínima de diagnóstico de diabetes

## Contexto del proyecto
Esta carpeta contiene una versión académica mínima del proyecto principal. Conserva el objetivo de estimar riesgo de diabetes con el dataset CDC BRFSS 2015, pero con un flujo reducido para facilitar estudio y ejecución.

## Objetivo
Implementar un pipeline simple y reproducible con tres modelos clásicos de machine learning para clasificación binaria de riesgo de diabetes.

## Alcance
- Carga de dataset desde `basic/datos/brutos`.
- Preprocesamiento común (imputación + escalado).
- Entrenamiento y comparación de 3 modelos (`logistica`, `arbol`, `svm`).
- Evaluación con accuracy, precision, recall, F1 y ROC-AUC.
- Guardado de mejor modelo y reportes mínimos.

## Ejecución
```bash
python -m basic.entrenamiento.pipeline \
  --dataset /ruta/a/diabetes_binary_health_indicators_BRFSS2015.csv
```

Salida esperada:
- `basic/modelos/modelo_diabetes_basic.joblib`
- `basic/reportes/metricas_basicas.json`
- `basic/reportes/comparativa_modelos.csv`

## API (opcional)
Si existe un modelo entrenado, se puede levantar una API mínima:

```bash
uvicorn basic.api.main:app --reload
```
