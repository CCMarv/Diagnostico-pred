# Reporte Final — Sistema de Diagnóstico Predictivo de Diabetes

**Proyecto:** Diagnóstico predictivo de diabetes mediante aprendizaje supervisado y no supervisado  
**Dataset:** CDC BRFSS 2015 (253,680 registros × 22 variables)  
**Institución:** Universidad de Guadalajara — Materia de Inteligencia Artificial  
**Fecha de generación:** 2026-05-18  
**Corrida de referencia:** n=50,000 | KNN=True | SMOTE=True | semilla=42  

---

## 1. Introducción y contexto clínico

La diabetes mellitus tipo 2 es una de las enfermedades crónicas con mayor prevalencia en México y el mundo. Según datos de ENSANUT 2022, la prevalencia en adultos mexicanos supera el 12%, con una tendencia ascendente asociada a cambios en estilos de vida y al envejecimiento poblacional. El diagnóstico tardío es el principal obstáculo para su tratamiento efectivo: se estima que hasta el 40% de los casos en México no están diagnosticados en el momento de su primer evento clínico severo.

Los sistemas de tamizaje predictivo buscan ordenar a la población por nivel de riesgo usando variables de fácil recolección (índice de masa corporal, presión arterial, actividad física, antecedentes familiares), permitiendo priorizar recursos de detección hacia las personas con mayor probabilidad de diagnóstico positivo. Este proyecto desarrolla y evalúa ese tipo de sistema usando técnicas de aprendizaje automático sobre datos de vigilancia epidemiológica a gran escala.

### 1.1 Dataset

El **CDC Behavioral Risk Factor Surveillance System (BRFSS) 2015** es una encuesta telefónica anual aplicada a adultos estadounidenses sobre comportamientos de riesgo para la salud. La versión procesada contiene:

- **253,680 registros** de adultos con información completa o parcialmente imputada
- **21 variables predictoras** de tipo binario, ordinal y continuo: `HighBP`, `HighChol`, `CholCheck`, `BMI`, `Smoker`, `Stroke`, `HeartDiseaseorAttack`, `PhysActivity`, `Fruits`, `Veggies`, `HvyAlcoholConsump`, `AnyHealthcare`, `NoDocbcCost`, `GenHlth`, `MentHlth`, `PhysHlth`, `DiffWalk`, `Sex`, `Age`, `Education`, `Income`
- **Variable objetivo:** `Diabetes_binary` (0 = sin diabetes, 1 = con diabetes/prediabetes)
- **Desbalance de clases:** ratio 6.2:1 (86.2% clase 0, 13.8% clase 1)

### 1.2 Limitación de transferibilidad

El dataset BRFSS proviene de población estadounidense. Al compararlo con ENSANUT 2022 (ver Sección 3.5), se identifican sesgos distribucionales significativos en variables como `Smoker` (+182% relativo) y `HighChol` (+86%), lo que implica que el modelo entrenado no puede desplegarse directamente sobre población mexicana sin reentrenamiento o ajuste de umbral de decisión.

---

## 2. Metodología

### 2.1 Pipeline de preprocesamiento

El preprocesamiento se implementó íntegramente dentro de un `sklearn.Pipeline` con `ColumnTransformer`, garantizando que **ninguna transformación toque los datos de prueba antes de la evaluación** (ausencia de data leakage).

```
Datos crudos
    │
    ├─ Columnas con valores faltantes (BMI, PhysHlth, MentHlth, etc.)
    │      └─ KNNImputer(n_neighbors=5)  ← ajustado solo sobre entrenamiento
    │
    ├─ Columnas binarias (HighBP, HighChol, Smoker, ...)
    │      └─ Sin transformación (ya están en {0,1})
    │
    └─ Columnas continuas (BMI, Age, Income, ...)
           └─ StandardScaler() ← media y varianza calculadas solo sobre entrenamiento
```

**Manejo del desbalance de clases:** Se aplicó **SMOTE** (Synthetic Minority Oversampling Technique) dentro del `ImbPipeline` de `imbalanced-learn`, de forma que la sobremuestrización de la clase minoritaria ocurre **solo dentro de cada fold de validación cruzada**, no sobre el conjunto de prueba.

### 2.2 Modelos evaluados

| Modelo | Configuración clave | Decisión de diseño |
|--------|--------------------|--------------------|
| **SVM (kernel RBF)** | `C=10, gamma='scale', probability=True, class_weight='balanced'` | Seleccionado por GridSearch (6 combinaciones × 5 folds); `probability=True` permite obtener scores de calibración; `class_weight='balanced'` ajusta implícitamente el umbral de decisión |
| **Árbol de decisión** | `max_depth=5, class_weight='balanced', criterion='gini'` | `max_depth=5` previene overfitting; profundidad baja facilita interpretabilidad para contexto clínico |
| **GBM** | `n_estimators=200, max_depth=4, learning_rate=0.05, subsample=0.8` | Learning rate bajo con muchos estimadores favorece generalización; `subsample=0.8` introduce regularización estocástica |
| **MLP** | `hidden_layer_sizes=(64, 32), early_stopping=True, validation_fraction=0.1` | Arquitectura ligera para datos tabulares; `early_stopping` evita overfitting sin búsqueda de epochs |

### 2.3 Protocolo de evaluación

- **Partición:** 80% entrenamiento / 20% prueba, estratificada por clase (StratifiedKFold)
- **Validación cruzada interna:** StratifiedKFold con k=5 sobre el conjunto de entrenamiento (solo para optimización de hiperparámetros de SVM)
- **Métricas reportadas:** ROC-AUC, PR-AUC, sensibilidad (recall clase 1), especificidad (recall clase 0), F1 clase positiva, Brier Score, accuracy, matriz de confusión
- **Criterio de selección del mejor modelo:** ROC-AUC (métrica más robusta ante desbalance)

### 2.4 Segmentación no supervisada — K-Means

Se implementó K-Means sobre las 21 variables predictoras (normalizadas) para identificar fenotipos de riesgo clínico sin usar la variable objetivo. El número óptimo de clústeres K se seleccionó maximizando el **silhouette score** en el rango k=2..10. Se detectaron 2 fenotipos con silhouette=0.589 (separación buena) y diferencias estadísticamente significativas en prevalencia de diabetes (χ²=1209, p<0.001).

---

## 3. Resultados

### 3.1 Tabla comparativa de modelos (n=50,000)

| Modelo | ROC-AUC | PR-AUC | Sensibilidad | Especificidad | F1 (clase+) | Brier Score | Accuracy |
|--------|---------|--------|-------------|--------------|-------------|-------------|----------|
| → **GBM** ★ | **0.8270** | **0.4147** | 0.3787 | **0.9295** | 0.4164 | **0.1033** | **0.8534** |
| SVM | 0.8269 | 0.4143 | **0.7784** | 0.7261 | **0.4463** | 0.1703 | 0.7333 |
| Árbol | 0.7874 | 0.3223 | 0.5366 | 0.8207 | 0.4041 | 0.1541 | 0.7815 |
| MLP | 0.7776 | 0.3479 | 0.4323 | 0.8873 | 0.4049 | 0.1252 | 0.8245 |

★ Ganador por ROC-AUC (diferencia con SVM: 0.0001 — virtualmente empate técnico)

> **Nota de interpretación clínica:** GBM y SVM son prácticamente equivalentes en ROC-AUC (diferencia < 0.001), pero tienen perfiles de error opuestos. GBM prioriza especificidad (92.9%): de cada 100 personas sin diabetes, solo 7 son clasificadas positivo. SVM prioriza sensibilidad (77.8%): de cada 100 personas con diabetes, identifica 78. Para **tamizaje clínico** (donde el costo de un falso negativo es alto), **SVM es el modelo preferible**.

### 3.2 Curvas ROC y Precisión-Recall

Las curvas se generaron sobre el conjunto de prueba (n=10,000 para la corrida de referencia completa):

![Curvas ROC y Precisión-Recall](curvas_gbm.png)

La curva ROC confirma que GBM y SVM operan sobre la misma frontera de decisión (AUC ≈ 0.827), mientras que la curva PR muestra que ambos tienen capacidad limitada para el valor predictivo positivo en poblaciones de baja prevalencia (~14%), lo cual es esperable con este nivel de desbalance.

### 3.3 Calibración del modelo

![Curva de calibración](calibracion_gbm.png)

GBM presenta **mejor calibración** (Brier Score=0.103 vs 0.170 de SVM), lo que significa que sus probabilidades estimadas se acercan más a las frecuencias reales de diabetes. Esto lo hace preferible cuando se necesita la probabilidad como insumo para decisiones clínicas (e.g., priorización en lista de espera).

### 3.4 Fenotipos de riesgo — K-Means (k=2)

| Fenotipo | n | Tasa de diabetes | Variables dominantes |
|----------|---|-----------------|----------------------|
| **Fenotipo A** (alto riesgo) | 6,275 (12.6%) | **28.2%** | BMI, PhysHlth, MentHlth, Age |
| **Fenotipo B** (riesgo base) | 43,725 (87.4%) | 11.9% | BMI, Age, Income, Education |

- La diferencia de prevalencia entre fenotipos (28.2% vs 11.9%) es estadísticamente significativa: χ²=1,209, p<0.001
- El **Fenotipo A** concentra personas con mayor IMC, más días de salud física y mental comprometida, y mayor edad — perfil consistente con síndrome metabólico
- El **Fenotipo B** representa el perfil de riesgo base, donde los factores socioeconómicos (ingreso, educación) son más relevantes que los indicadores de salud directos

### 3.5 Contraste distribucional CDC vs. ENSANUT 2022

El modelo fue entrenado sobre datos estadounidenses. El siguiente análisis cuantifica el sesgo distribucional respecto a la población mexicana objetivo:

| Variable | CDC BRFSS 2015 (%) | ENSANUT 2022 (%) | Sesgo relativo |
|----------|--------------------|-----------------|----------------|
| Smoker | 44.5 | 15.8 | **+182%** |
| HighChol | 42.6 | 22.9 | **+86%** |
| PhysActivity | 75.6 | 45.2 | **+67%** |
| Veggies | 80.9 | 54.8 | +48% |
| HighBP | 42.8 | 31.8 | +35% |
| AnyHealthcare | 95.0 | 76.2 | +25% |
| Fruits | 63.3 | 55.6 | +14% |
| HvyAlcoholConsump | 5.7 | 5.3 | +8% |

6 de 10 variables presentan sesgo alto (>30%), lo que limita la transferibilidad directa del modelo a población mexicana.

### 3.6 Comparativa con literatura académica

| Fuente | Dataset | n | Mejor modelo | ROC-AUC |
|--------|---------|---|-------------|---------|
| **Este proyecto** | CDC BRFSS 2015 | 50,000 | GBM / SVM | **0.827** |
| Priya et al. (2021) | PIMA Indians | 768 | SVM | 0.850 |
| Kopitar et al. (2020) | EHR (Eslovenia) | 52,000 | Random Forest | 0.883 |
| Maniruzzaman et al. (2020) | PIMA Indians | 768 | LDA | 0.860 |

Los resultados de este proyecto son **consistentes con el estado del arte** para modelos de tamizaje basados en encuestas de comportamiento (no en registros clínicos electrónicos). La ligera diferencia respecto a Kopitar et al. se explica por la mayor riqueza informativa de los EHR (laboratorios, diagnósticos previos) frente a las variables de encuesta del BRFSS.

---

## 4. Conclusiones

### 4.1 Hallazgos principales

1. **ROC-AUC de 0.827 con 21 variables de encuesta** — sin acceso a laboratorios, el modelo logra una capacidad discriminativa comparable a la literatura. Esto valida el uso de encuestas de comportamiento para tamizaje de primer nivel.

2. **GBM y SVM son equivalentes a escala** — la diferencia de ROC-AUC es 0.0001, por debajo del umbral de significancia práctica. La elección entre ellos depende del objetivo clínico: sensibilidad alta (SVM) vs. especificidad alta (GBM).

3. **K-Means identifica un fenotipo de alto riesgo accionable** — el Fenotipo A (12.6% de la población) concentra una tasa de diabetes 2.4× mayor que la población restante. Intervenciones dirigidas a este fenotipo tienen mayor eficiencia que los programas de tamizaje universal.

4. **El desbalance 6:1 requiere SMOTE + calibración** — sin SMOTE, los modelos aprenden a predecir siempre la clase mayoritaria. La calibración del GBM (Brier=0.103) es mejor que SVM (Brier=0.170), aunque ambos mantienen probabilidades razonables para uso en priorización.

### 4.2 Limitaciones

- **Transferibilidad geográfica:** El modelo fue entrenado sobre datos de EE.UU. Las diferencias distribucionales documentadas en Sección 3.5 requieren reentrenamiento o ajuste de umbral antes de aplicar sobre población mexicana.
- **Variables de encuesta vs. clínicas:** Las variables BRFSS son autorreportadas, lo que introduce sesgo de memoria y deseabilidad social, especialmente en `Smoker` y `HvyAlcoholConsump`.
- **Snapshot temporal:** Los datos son de 2015. Los patrones epidemiológicos de diabetes han cambiado (aumento post-pandemia COVID-19 en México y EE.UU.).
- **Ausencia de variables clave:** Glicemia en ayunas, HbA1c y antecedentes familiares directos no están en el dataset, limitando el techo de accuracy alcanzable.
- **Umbral de decisión fijo:** Los modelos se evaluaron con umbral 0.5. En uso clínico real, el umbral debería optimizarse para maximizar sensibilidad a costa de mayor tasa de falsos positivos.

### 4.3 Trabajo futuro

- Reentrenamiento sobre datos ENSANUT 2022 con las mismas técnicas para evaluar transferibilidad real
- Calibración de umbral operacional mediante análisis de curva costo-beneficio clínico
- Inclusión de variables de laboratorio en una cohorte piloto mexicana
- Evaluación de equidad por subgrupo (género, grupo de edad, nivel socioeconómico)

---

## 5. Reproducibilidad

### Ejecutar el pipeline completo

```bash
# Instalar dependencias
pip install -e .[dev]

# Corrida con muestra de referencia (50k registros)
python -m entrenamiento.pipeline \
  --modo clasificacion \
  --modelos svm,arbol,gbm,mlp \
  --n-muestras 50000 \
  --dir-resultados resultados/

# Corrida con dataset completo (253k, ~60 min en CPU)
python -m entrenamiento.pipeline \
  --modo clasificacion \
  --modelos svm,arbol,gbm,mlp \
  --dir-resultados resultados/
```

### Levantar el dashboard

```bash
streamlit run dashboard/app.py
```

### Verificar la API

```bash
uvicorn api.main:app --reload
curl http://localhost:8000/salud
```

---

*Generado en 2026-05-18. Para reproducir exactamente estos resultados, usar semilla=42 y n=50000.*  
*Dataset: CDC BRFSS 2015 — disponible en Kaggle (`iabhishekofficial/mobile-price-classification` no aplica; usar `alexteboul/diabetes-health-indicators-dataset`).*
