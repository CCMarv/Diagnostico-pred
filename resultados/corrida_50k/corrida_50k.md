# Reporte de clasificación — Diagnóstico predictivo de diabetes

**Fecha:** 20260518_093254  
**Parámetros:** n=50000 | KNN=True | SMOTE=True | semilla=42  
**Modelo ganador (ROC-AUC):** `gbm`  
**Mejor por PR-AUC:** `gbm`  
**Origen crudo:** `corrida_50k.json`  

---

## Resumen ejecutivo

- Se compararon **4 modelos** supervisados sobre el mismo conjunto de prueba sin data leakage.
- Mejor ROC-AUC: **0.8270** (`gbm`)
- Mejor PR-AUC: **0.4147** (`gbm`)
- Prevalencia de diabetes en el conjunto: **13.8%** (ratio 6.2:1)

## Tabla comparativa

| nombre_modelo | roc_auc | pr_auc | sensibilidad | especificidad | f1_clase_positiva | brier_score | accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| → **gbm** | **0.8270** | **0.4147** | **0.3787** | **0.9295** | **0.4164** | **0.1033** | **0.8534** |
| svm | 0.8269 | 0.4143 | 0.7784 | 0.7261 | 0.4463 | 0.1703 | 0.7333 |
| arbol | 0.7874 | 0.3223 | 0.5366 | 0.8207 | 0.4041 | 0.1541 | 0.7815 |
| mlp | 0.7776 | 0.3479 | 0.4323 | 0.8873 | 0.4049 | 0.1252 | 0.8245 |

## Interpretación clínica

El modelo **gbm** concentra el mejor balance observado: ROC-AUC 0.8270, PR-AUC 0.4147, sensibilidad 0.3787, especificidad 0.9295 y Brier Score 0.1033. En un contexto de tamizaje clínico, esto sugiere que el modelo ordena correctamente el riesgo y mantiene una calibración razonable para priorización, aunque la sensibilidad debe revisarse antes de un despliegue operativo.

---

*Generado automáticamente por `entrenamiento/pipeline.py`*  
*Para reproducir: `python -m entrenamiento.pipeline --modo clasificacion --modelos svm,arbol,gbm,mlp`*
