# Log de corridas académicas — Diagnóstico predictivo de diabetes

**Generado:** 2026-05-18 09:32 UTC  
**Dataset:** CDC BRFSS 2015 (diabetes_binary_health_indicators_BRFSS2015.csv)  
**Semilla global:** 42  

---

## Parámetros globales de configuración

| Parámetro | Valor | Motivo |
|---|---|---|
| `SEMILLA_ALEATORIA` | `42` | Reproducibilidad entre corridas |
| `PROPORCION_PRUEBA` | `0.20` | 80/20 estratificado; la estratificación preserva el ratio de clases |
| `use_knn` | `True` | KNNImputer para continuas (BMI, MentHlth, PhysHlth) en lugar de mediana |
| `use_smote` | `True` | SMOTE activo en entrenamiento para corregir desbalance ~14% clase 1 |
| Modelos | `svm, arbol, gbm, mlp` | Catálogo completo del nivel Intermedio |

---

## Arquitectura del pipeline de preprocesamiento

El preprocesador es un `ColumnTransformer` con tres ramas; el pipeline completo es
`ColumnTransformer → SMOTE → Estimador` serializado en un único `.joblib`.

### Rama 1 — Variables continuas (3 columnas: BMI, MentHlth, PhysHlth)

| Paso | Clase | Parámetros clave |
|---|---|---|
| Imputación | `KNNImputer` | `n_neighbors=5` (default sklearn), `weights='uniform'` |
| Escalado | `StandardScaler` | `with_mean=True, with_std=True` (defaults) |

> **Por qué KNN en lugar de mediana:** las tres continuas tienen distribuciones asimétricas y
> valores extremos (BMI puede ser 99). La imputación por vecinos respeta la estructura local;
> la mediana reemplaza con un escalar global que distorsiona casos atípicos.

### Rama 2 — Variables binarias (14 columnas)

| Paso | Clase | Parámetros |
|---|---|---|
| Imputación | `SimpleImputer` | `strategy='most_frequent'` |
| Escalado | `'passthrough'` | Sin transformar — variables 0/1 ya están en escala |

> **Por qué no escalar binarias:** StandardScaler centraría en 0.5 y expandiría a ±0.5,
> perdiendo la interpretabilidad booleana sin ganancia para los modelos de árbol.

### Rama 3 — Variables ordinales (4 columnas: GenHlth, Age, Education, Income)

| Paso | Clase | Parámetros |
|---|---|---|
| Imputación | `SimpleImputer` | `strategy='most_frequent'` |
| Encoding | `OrdinalEncoder` | categorías predefinidas por columna (ver tabla) |

| Variable | Rango | Semántica |
|---|---|---|
| `GenHlth` | 1–5 | 1=Excelente, 5=Mala |
| `Age` | 1–13 | 1=18-24, 13=80+ |
| `Education` | 1–6 | 1=sin estudios, 6=universidad |
| `Income` | 1–8 | 1=<$10k, 8=>$75k |

> **Por qué OrdinalEncoder con categorías explícitas y no OneHotEncoder:** las cuatro
> variables tienen orden clínico real (mayor edad → mayor riesgo). OHE lo destruiría.
> Definir el rango completo evita que valores no vistos en train causen errores en inferencia.

### SMOTE (aplicado post-preprocesador, pre-estimador)

| Parámetro | Valor |
|---|---|
| `k_neighbors` | 5 (default) |
| `random_state` | None (no fijado) — variación aleatoria en los sintéticos |
| Estrategia | `'auto'` → resamplea solo la clase minoritaria hasta igualar clases |

> **Por qué dentro del Pipeline y no antes del split:** para evitar data leakage. Si se
> aplicara SMOTE antes, muestras sintéticas derivadas del test contaminarían el train.

---

## Hiperparámetros por modelo

### SVM — `SVC(kernel='rbf')`

La SVM es el único modelo con búsqueda de hiperparámetros explícita.

**Espacio de búsqueda:**

| Parámetro | Valores explorados | Combinaciones |
|---|---|---|
| `C` | `[0.1, 1.0, 10.0]` | controla margen blando: C alto → menos margen, más sobreajuste |
| `gamma` | `['scale', 'auto']` | `scale` = 1/(n_features·Var(X)); `auto` = 1/n_features |
| **Total** | **6 combinaciones × 5 folds** | **= 30 evaluaciones** |

**Protocolo de búsqueda:** `ParameterGrid` manual sobre `StratifiedKFold(n_splits=5,
shuffle=True, random_state=42)`. Se usa búsqueda manual (no `GridSearchCV`) porque la
calibración interna de probabilidades (`CalibratedClassifierCV`) dentro de cada fold de
GridSearchCV multiplicaría el costo por 3–5×. En cambio, se usa `probability=False`
durante la búsqueda y `probability=True` solo en el refit final.

**Refit final:** `pipeline.fit(X_train, y_train)` con los mejores hiperparámetros sobre
todo el conjunto de entrenamiento.

**Parámetros fijos:** `class_weight='balanced'` (penaliza errores en clase minoritaria
~14× más), `random_state=42`.

---

### Árbol de decisión — `DecisionTreeClassifier`

Sin búsqueda de hiperparámetros; validación cruzada solo para reportar score CV.

| Parámetro | Valor | Motivo |
|---|---|---|
| `max_depth` | `5` | Limita sobreajuste; profundidad suficiente para capturar interacciones clínicas |
| `ccp_alpha` | `0.0` | Sin poda adicional por complejidad |
| `class_weight` | `'balanced'` | Pondera inversamente a la frecuencia de clase |
| `criterion` | `'gini'` (default) | Impureza de Gini para selección de división |
| `random_state` | `42` | Reproducibilidad en desempates |

> **Por qué max_depth=5 y no más profundo:** un árbol sin límite de profundidad en este
> dataset memorizaría el ruido de entrenamiento. Con 5 niveles se pueden representar hasta
> 32 hojas — suficiente para capturar patrones relevantes sin sobreajustar.

---

### Gradient Boosting — `GradientBoostingClassifier`

Sin búsqueda de hiperparámetros; parámetros fijados por diseño.

| Parámetro | Valor | Motivo |
|---|---|---|
| `n_estimators` | `200` | 200 árboles secuenciales de corrección de error |
| `max_depth` | `4` | Árboles base poco profundos para capturar interacciones sin sobreajustar |
| `learning_rate` | `0.05` | Tasa de aprendizaje conservadora — cada árbol contribuye poco; más estable |
| `subsample` | `1.0` (default) | Usa todo el dataset por iteración |
| `loss` | `'log_loss'` (default en clasificación) | Equivalente a regresión logística por iteración |
| `random_state` | `42` | |

> **Por qué learning_rate bajo con muchos estimadores:** el tradeoff clásico boosting.
> lr=0.05 con 200 estimadores supera en generalización a lr=0.2 con 50, especialmente
> en datasets desbalanceados donde el gradient de la pérdida varía mucho entre clases.

---

### Red Neuronal — `MLPClassifier`

Sin búsqueda de hiperparámetros.

| Parámetro | Valor | Motivo |
|---|---|---|
| `hidden_layer_sizes` | `(64, 32)` | 2 capas ocultas: 64 → 32 neuronas con compresión de representación |
| `activation` | `'relu'` | Rectified Linear Unit; evita problema del gradiente que desaparece |
| `solver` | `'adam'` | Optimizador adaptativo; maneja bien datos esparsos/desbalanceados |
| `max_iter` | `500` | Máximo de épocas |
| `early_stopping` | `True` | Detiene si la métrica de validación no mejora en 10 épocas (n_iter_no_change=10) |
| `validation_fraction` | `0.1` | 10% del train como validación interna para early stopping |
| `random_state` | `42` | |

> **Por qué early_stopping=True:** evita que la red memorice el ruido de los datos
> sintéticos generados por SMOTE, que pueden ser más "ruidosos" que los datos reales.

---

## Protocolo de evaluación (todos los modelos)

- **Split:** 80/20 estratificado, `random_state=42`
- **Validación cruzada:** `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`
- **Métrica de selección:** ROC-AUC promedio en los 5 folds (no accuracy — sensible al desbalance)
- **Métrica principal de comparación final:** ROC-AUC en conjunto de test
- **Serialización:** el mejor modelo por ROC-AUC en test se serializa como pipeline completo

---

---

## Resultados por corrida

### Corrida 10k (10,000 muestras)

- **Tiempo total:** 111.3s (1.9 min)
- **Mejor modelo (ROC-AUC):** `svm`
- **Mejor modelo (PR-AUC):** `svm`
- **Prevalencia clase positiva:** 13.6% (ratio 6.4:1)

| Modelo | ROC-AUC | PR-AUC | Sensibilidad | Especificidad | F1 | Brier |
|--------|---------|--------|-------------|--------------|-----|-------|
| `svm` ← **ganador** | 0.8351 | 0.4213 | 0.7721 | 0.7384 | 0.4497 | 0.1672 |
| `gbm` | 0.8236 | 0.3939 | 0.3051 | 0.9450 | 0.3689 | 0.1008 |
| `arbol` | 0.7985 | 0.3304 | 0.4963 | 0.8785 | 0.4376 | 0.1384 |
| `mlp` | 0.7844 | 0.3219 | 0.5551 | 0.8281 | 0.4194 | 0.1561 |

### Corrida 50k (50,000 muestras)

- **Tiempo total:** 2939.1s (49.0 min)
- **Mejor modelo (ROC-AUC):** `gbm`
- **Mejor modelo (PR-AUC):** `gbm`
- **Prevalencia clase positiva:** 13.8% (ratio 6.2:1)

| Modelo | ROC-AUC | PR-AUC | Sensibilidad | Especificidad | F1 | Brier |
|--------|---------|--------|-------------|--------------|-----|-------|
| `gbm` ← **ganador** | 0.8270 | 0.4147 | 0.3787 | 0.9295 | 0.4164 | 0.1033 |
| `svm` | 0.8269 | 0.4143 | 0.7784 | 0.7261 | 0.4463 | 0.1703 |
| `arbol` | 0.7874 | 0.3223 | 0.5366 | 0.8207 | 0.4041 | 0.1541 |
| `mlp` | 0.7776 | 0.3479 | 0.4323 | 0.8873 | 0.4049 | 0.1252 |

---

## Comparativa entre corridas (ganadores por escala)

| n | Modelo ganador | ROC-AUC | PR-AUC | Sensibilidad | Tiempo |
|---|----------------|---------|--------|-------------|--------|
| 10,000 | `svm` | 0.8351 | 0.4213 | 0.7721 | 111s |
| 50,000 | `gbm` | 0.8270 | 0.4147 | 0.3787 | 2939s |

---

## Instrucción para la instancia con dataset completo (253k + SVM)

Esta instrucción permite ejecutar el pipeline en una instancia separada con el
dataset completo (253,680 filas) incluyendo SVM. Los parámetros son idénticos a
las corridas de este log para garantizar comparabilidad directa.

**Requisitos previos:**
```bash
# 1. Python 3.11+ y el repositorio clonado
git clone <repo_url>
cd diasgnostico-pred

# 2. Instalar dependencias
pip install -e .[dev]

# 3. Descargar el dataset (si no está ya en datos/brutos/)
python -c "from entrenamiento.descargador_dataset import descargar_y_persistir; descargar_y_persistir()"
```

**Comando de ejecución:**
```bash
mkdir -p resultados/corrida_253k

python -m entrenamiento.pipeline \
  --modo clasificacion \
  --modelos svm,arbol,gbm,mlp \
  --dataset datos/brutos/diabetes_binary_health_indicators_BRFSS2015.csv \
  --salida-modelo resultados/corrida_253k/modelo_253k.joblib \
  --salida-reporte resultados/corrida_253k/corrida_253k.json \
  --salida-reporte-legible resultados/corrida_253k/corrida_253k.md
```

**Parámetros implícitos (no cambian, vienen de `config.py`):**

| Parámetro | Valor | Archivo |
|---|---|---|
| `SEMILLA_ALEATORIA` | `42` | `config.py` |
| `PROPORCION_PRUEBA` | `0.20` | `config.py` |
| `use_knn` | `True` | `ejecutar_pipeline()` default |
| `use_smote` | `True` | `ejecutar_pipeline()` default |
| SVM grid C | `[0.1, 1.0, 10.0]` | `comparador_modelos.py` |
| SVM grid gamma | `['scale', 'auto']` | `comparador_modelos.py` |
| CV folds | `5 folds StratifiedKFold` | `comparador_modelos.py` |
| GBM n_estimators | `200` | `comparador_modelos.py` |
| GBM learning_rate | `0.05` | `comparador_modelos.py` |
| MLP arquitectura | `(64, 32)` | `comparador_modelos.py` |

**Tiempo estimado:** ~100 min (SVM es el cuello de botella — 6 combinaciones × 5 folds sobre 200k+ filas).

**Artefactos esperados en `resultados/corrida_253k/`:**
```
corrida_253k.json          # métricas brutas de 4 modelos
corrida_253k.md            # reporte Markdown legible
corrida_253k_manifest.json # manifiesto de la corrida
modelo_253k.joblib         # pipeline serializado del ganador
curvas_{ganador}.png       # curvas ROC y PR
calibracion_{ganador}.png  # curva de calibración
dataset_procesado.parquet  # dataset 21 cols CDC sin objetivo
```

**Para copiar las PNGs** (el pipeline las guarda en `reportes/` por defecto):
```bash
# Ejecutar después del pipeline para copiar curvas al directorio de la corrida
cp reportes/curvas_*.png reportes/calibracion_*.png resultados/corrida_253k/
```

**Para comparar con esta corrida:** los JSONs de `resultados/corrida_10k/corrida_10k.json`
y `resultados/corrida_50k/corrida_50k.json` tienen la misma estructura que
`resultados/corrida_253k/corrida_253k.json`. Se puede comparar directamente con:
```bash
python -c "
import json
for tag, f in [('10k','corrida_10k'), ('50k','corrida_50k'), ('253k','corrida_253k')]:
    try:
        d = json.load(open(f'resultados/corrida_{tag}/{f}.json'))
        m = d['modelos']
        mejor = d['mejor_modelo']
        print(f'{tag}: {mejor} ROC-AUC={m[mejor][\"roc_auc\"]:.4f}')
    except FileNotFoundError:
        print(f'{tag}: no disponible')
"
```

---

*Log generado por `scripts/ejecutar_corridas.py`*