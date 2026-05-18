# Reporte de clasificación — Diagnóstico predictivo de diabetes

**Fecha:** 20260518_084354  
**Parámetros:** n=10000 | KNN=True | SMOTE=True | semilla=42  
**Modelo ganador (ROC-AUC):** `svm`  
**Mejor por PR-AUC:** `svm`  
**Origen crudo:** `corrida_10k.json`  

---

## Resumen ejecutivo

- Se compararon **4 modelos** supervisados sobre el mismo conjunto de prueba sin data leakage.
- Mejor ROC-AUC: **0.8351** (`svm`)
- Mejor PR-AUC: **0.4213** (`svm`)
- Prevalencia de diabetes en el conjunto: **13.6%** (ratio 6.4:1)

## Tabla comparativa

| nombre_modelo | roc_auc | pr_auc | sensibilidad | especificidad | f1_clase_positiva | brier_score | accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| → **svm** | **0.8351** | **0.4213** | **0.7721** | **0.7384** | **0.4497** | **0.1672** | **0.7430** |
| gbm | 0.8236 | 0.3939 | 0.3051 | 0.9450 | 0.3689 | 0.1008 | 0.8580 |
| arbol | 0.7985 | 0.3304 | 0.4963 | 0.8785 | 0.4376 | 0.1384 | 0.8265 |
| mlp | 0.7844 | 0.3219 | 0.5551 | 0.8281 | 0.4194 | 0.1561 | 0.7910 |

## Interpretación clínica

El modelo **svm** concentra el mejor balance observado: ROC-AUC 0.8351, PR-AUC 0.4213, sensibilidad 0.7721, especificidad 0.7384 y Brier Score 0.1672. En un contexto de tamizaje clínico, esto sugiere que el modelo ordena correctamente el riesgo y mantiene una calibración razonable para priorización, aunque la sensibilidad debe revisarse antes de un despliegue operativo.

---

*Generado automáticamente por `entrenamiento/pipeline.py`*  
*Para reproducir: `python -m entrenamiento.pipeline --modo clasificacion --modelos svm,arbol,gbm,mlp`*
