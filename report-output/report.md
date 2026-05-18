# Portada

**Reporte técnico-académico del proyecto:** `CCMarv/Diasgnostico-pred`  
**Asignatura:** Procesamiento de Datos / Inteligencia Artificial  
**Fecha de elaboración:** 2026-05-18  
**Repositorio analizado:** `../` (raíz del proyecto local)

---

## Resumen ejecutivo

Se verificó evidencia del pipeline de datos y modelado del proyecto con enfoque en trazabilidad y reproducibilidad. El sistema implementa un flujo completo de clasificación supervisada con 4 modelos (SVM, Árbol, GBM, MLP), módulo de fenotipado con K-Means, optimización de hiperparámetros para SVM, evaluación con métricas estándar (ROC-AUC, PR-AUC, sensibilidad, especificidad, F1, Brier, accuracy), dashboard interactivo en Streamlit y despliegue vía API FastAPI.

Resultados principales verificados desde artefactos versionados:
- Corrida 10k: mejor modelo por ROC-AUC = **SVM (0.8351)** (`../resultados/corrida_10k/corrida_10k.json`).
- Corrida 50k: mejor modelo por ROC-AUC = **GBM (0.8270)** (`../resultados/corrida_50k/corrida_50k.json`).
- Fenotipado K-Means (notebook ejecutado): **k óptimo=2**, silhouette **0.585**, diferencia de prevalencia entre fenotipos **15.1 pp** (`notebooks_processed/02_fenotipado_kmeans_extract.md`).

---

## Introducción

El proyecto desarrolla un sistema de estimación de riesgo de diabetes tipo 2 usando el dataset CDC BRFSS 2015 y lo estructura en capas: entrenamiento, inferencia y servicio (API/dashboard). El tema central de la materia (procesamiento de datos) está explícito en la cadena: carga/limpieza → preprocesamiento reproducible → entrenamiento comparativo → evaluación clínica → serialización → consumo en producción.

Fuentes base:
- `../README.md`
- `../PROYECTO.md`
- `../config.py`

---

## Datos y contexto

- Dataset objetivo del proyecto: `diabetes_binary_health_indicators_BRFSS2015.csv` (CDC BRFSS 2015) (`../config.py`, `../resultados/LOG_CORRIDAS.md`).
- Variables: 21 columnas CDC (`COLUMNAS_CDC`) + objetivo `Diabetes_binary` (`../config.py`).
- Contexto epidemiológico y transferencia CDC↔México documentado en:
  - Notebook EDA (`../notebooks/01_eda_regionalizado.ipynb`)
  - Extracto procesado (`notebooks_processed/01_eda_regionalizado_extract.md`)
  - Documento de diseño (`../PROYECTO.md`)

---

## Preprocesamiento

Implementación verificada en `../entrenamiento/preprocesador.py`:

1. **Continuas** (`BMI`, `MentHlth`, `PhysHlth`): imputación (`KNNImputer` o mediana) + `StandardScaler`.
2. **Binarias** (14 variables): `SimpleImputer(strategy='most_frequent')` + passthrough (sin escalado).
3. **Ordinales** (`GenHlth`, `Age`, `Education`, `Income`): imputación + `OrdinalEncoder` con orden explícito.
4. **Control de desbalance**: SMOTE dentro de `ImbPipeline` cuando está activo.

Conexión con procesamiento de datos: el preprocesamiento está encapsulado en pipeline serializable para evitar leakage y mantener simetría entrenamiento/inferencia.

---

## Pipeline y modelos

Flujo principal verificado en `../entrenamiento/pipeline.py` y `../entrenamiento/comparador_modelos.py`:

- Split estratificado train/test (`PROPORCION_PRUEBA=0.2`, semilla 42).
- Entrenamiento comparativo de modelos supervisados:
  - `svm`
  - `arbol`
  - `gbm`
  - `mlp`
- Modo clustering con `KMeans` (`--modo clustering`).
- Persistencia de:
  - JSON crudo de métricas
  - reporte legible markdown
  - modelo `.joblib`
  - curvas ROC/PR y calibración

### Verificación del requisito “al menos 3 modelos”
Cumplido: hay 4 modelos supervisados en producción experimental (`../config.py`, `../entrenamiento/comparador_modelos.py`).

### Verificación del requisito de modelos del temario
- **SVM:** implementado y optimizado (`../entrenamiento/comparador_modelos.py`).
- **Árbol de decisión:** implementado (`../entrenamiento/comparador_modelos.py`).
- **Red neuronal (MLP):** implementada (`../entrenamiento/comparador_modelos.py`).
- **K-Means:** implementado en módulo y notebook (`../entrenamiento/fenotipado.py`, `../notebooks/02_fenotipado_kmeans.ipynb`).

---

## Optimización de hiperparámetros

Evidencia:
- Búsqueda manual para SVM con `ParameterGrid` y validación cruzada estratificada 5-fold (`../entrenamiento/comparador_modelos.py`).
- Módulo dedicado `OptimizadorHiperparametros` con `GridSearchCV` (`../entrenamiento/optimizador.py`).

Grilla SVM verificada:
- `C`: [0.1, 1, 10]
- `gamma`: ["scale", "auto"]

---

## Evaluación

Métricas estándar verificadas en artefactos JSON y reportes (`../resultados/corrida_10k/corrida_10k.json`, `../resultados/corrida_50k/corrida_50k.json`):
- ROC-AUC
- PR-AUC
- Sensibilidad
- Especificidad
- F1 clase positiva
- Brier Score
- Accuracy
- Matriz de confusión

### Resumen de desempeño (extraído a `metrics.csv`)

| Corrida | Mejor modelo | ROC-AUC mejor | PR-AUC mejor |
|---|---:|---:|---:|
| 10k | SVM | 0.8351 | 0.4213 |
| 50k | GBM | 0.8270 | 0.4147 |

Fuente tabular completa: `metrics.csv`.

### Figuras verificadas
- `figures/curvas_svm_10k.png`
- `figures/calibracion_svm_10k.png`
- `figures/curvas_gbm_50k.png`
- `figures/calibracion_gbm_50k.png`

---

## Dashboard interactivo

Implementación verificada en `../dashboard/app.py`.

Vistas implementadas:
1. Comparativa de modelos.
2. Predicción individual.
3. Fenotipos K-Means.
4. Calibración/explicabilidad.

Comando de ejecución documentado en repo:
- `streamlit run dashboard/app.py` (`../README.md`, `../README_demo.md`).

Nota de evidencia: el dashboard espera archivos `reportes/benchmark_*.json` y `reportes/hallazgos_fenotipado.json`; en este snapshot no se encontraron (ver sección final).

---

## API / sistema en producción

Implementación verificada:
- Servicio: `../api/main.py`
- Contrato de entrada/salida: `../api/esquemas.py`
- Inferencia: `../inferencia/predictor.py`

Características verificadas:
- Endpoints: `/salud`, `/predecir`.
- Modo degradado cuando falta modelo serializado.
- Validación clínica de entrada con Pydantic.
- Categorización de riesgo con umbrales (`0.33`, `0.66`) y margen de incertidumbre (`±0.05`).

Comando de ejecución:
- `uvicorn api.main:app --reload` (`../README.md`, `../README_demo.md`).

---

## Comparativa con papers académicos

Se encontró comparativa académica en documentación interna del proyecto (no en archivos bibliográficos formales):
- `../reportes/reporte_final.md` (tabla comparativa con Priya et al., Kopitar et al., Maniruzzaman et al.).
- `../PROYECTO.md` (tabla de benchmarks con Tigga & Garg, Zou et al., Huang et al., Sisodia & Sisodia).

Interpretación técnica: el proyecto se posiciona en rango competitivo para datos tabulares de tamizaje (AUC alrededor de 0.80–0.83), con limitación explícita de transferibilidad geográfica.

---

## Discusión

1. **Fortaleza de procesamiento de datos:** la separación de tipos de variables y el pipeline serializado favorecen reproducibilidad y control de leakage.
2. **Trade-off clínico entre modelos:** en 50k, SVM prioriza sensibilidad y GBM especificidad/calibración; esto impacta estrategia de tamizaje.
3. **K-Means aporta segmentación poblacional:** el fenotipado muestra diferencia significativa entre grupos y puede enriquecer etapas de análisis/intervención.
4. **Brecha de integración operativa:** algunos artefactos que el dashboard espera no están presentes en el árbol actual.

---

## Conclusiones y recomendaciones

### Conclusiones
- El repositorio cumple de forma verificable con un flujo de procesamiento de datos de extremo a extremo.
- Se cubren los modelos del temario requeridos (SVM, Árbol, MLP, K-Means).
- Existen artefactos reproducibles y evidencia cuantitativa de dos corridas académicas.
- API y dashboard están implementados como componentes de despliegue.

### Recomendaciones
1. Estandarizar generación y versionado de `reportes/benchmark_*.json` y `reportes/hallazgos_fenotipado.json` para evitar desalineación con el dashboard.
2. Consolidar referencias académicas en un artefacto bibliográfico trazable (por ejemplo, tabla con DOI/URL validada).
3. Añadir corrida de dataset completo 253k con mismos metadatos para cerrar comparación de escalabilidad.
4. Mantener `metrics.csv` como resumen compacto para discusión académica y presentación.

---

## Anexos

### Anexo A. Artefactos generados en esta entrega
- `report-output/metrics.csv`
- `report-output/figures/*`
- `report-output/notebooks_processed/*`
- `report-output/deploy/links.md`
- `report-output/evidence.log`
- `report-output/README.md`

### Anexo B. Rutas de artefactos base del proyecto
- `../resultados/corrida_10k/corrida_10k.json`
- `../resultados/corrida_50k/corrida_50k.json`
- `../resultados/LOG_CORRIDAS.md`
- `../reportes/reporte_final.md`

---

## Elementos no encontrados

1. `../reportes/benchmark_*.json` (el dashboard los referencia para la vista comparativa).
2. `../reportes/hallazgos_fenotipado.json` (el dashboard lo referencia para la vista de fenotipos; el notebook indica exportación, pero el archivo no está en el árbol actual).
3. Evidencia de API desplegada en entorno remoto (solo se verificó implementación local y comandos de ejecución).
4. Repositorio bibliográfico formal de papers (p. ej., `.bib` o lista con DOI/URL canónica); hay tablas comparativas internas, pero sin fuente formal consolidada.
