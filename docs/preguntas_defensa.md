# Preguntas frecuentes de defensa

Documento de preparación para la defensa oral del proyecto. 33 preguntas cubren los 11 temas técnicos de la rúbrica, 3 por tema. Para cada pregunta se proporciona la respuesta esperada en el contexto específico de este proyecto.

---

## 1. Pipeline y preprocesamiento

**P1. ¿Por qué usar Pipeline en lugar de transformar el dataset directamente antes de entrenar?**

El Pipeline de sklearn aplica cada transformación solo sobre los datos que el estimador "ha visto". Si transformáramos el dataset completo antes de dividir, el imputador y el escalador aprenderían estadísticas (media, vecinos más cercanos) sobre los datos de prueba, filtrando información del futuro al modelo — esto se llama **data leakage** y produce estimaciones de desempeño artificialmente optimistas. El Pipeline garantiza que `fit()` solo toque datos de entrenamiento y `transform()` aplique esas mismas estadísticas al conjunto de prueba.

**P2. ¿Cómo garantizan que no hay data leakage?**

Por tres mecanismos: (1) el `Pipeline` de sklearn impide que transformaciones se ajusten sobre datos de prueba; (2) SMOTE está dentro del `ImbPipeline` de imbalanced-learn, que aplica la sobremuestrización solo dentro de cada fold de validación cruzada, nunca sobre el conjunto de prueba final; (3) la validación cruzada anidada en `OptimizadorHiperparametros` usa conjuntos separados para la búsqueda de hiperparámetros y para la estimación de desempeño. Los 27 tests de integración verifican que la partición entrenamiento/prueba se mantiene en todos los flujos.

**P3. ¿Qué ventaja tiene ColumnTransformer sobre transformar columna por columna?**

`ColumnTransformer` aplica transformaciones distintas a distintos subconjuntos de columnas en un solo paso, lo que permite serializar todo el preprocesamiento como un único objeto junto con el modelo. Si transformáramos columna por columna en código imperativo, tendríamos que guardar y restaurar cada transformador por separado, lo que hace el despliegue frágil. Adicionalmente, `ColumnTransformer` garantiza el orden de las columnas de salida, lo que es crítico para la API que recibe JSON y necesita reconstruir el vector de características.

---

## 2. Imputación con KNNImputer

**P4. ¿Por qué KNNImputer en lugar de SimpleImputer con la media?**

La imputación con la media asume que los valores faltantes son independientes del resto de variables (MCAR — Missing Completely At Random). En este dataset, variables como `BMI` y `PhysHlth` tienen faltantes que tienden a correlacionar: personas con peor salud reportan más frecuentemente valores faltantes en varios indicadores. KNNImputer usa los k=5 vecinos más cercanos (en el espacio de las variables observadas) para estimar el valor faltante, preservando la estructura de correlación del dataset. Esto reduce el sesgo de imputación en escenarios MAR (Missing At Random).

**P5. ¿Cuántos vecinos usa y cómo se eligió ese valor?**

Se usan k=5 vecinos. Este valor es el default de sklearn y un punto de partida estándar en la literatura para datasets tabulares de tamaño mediano. Con k=5 hay suficientes vecinos para suavizar outliers sin diluir la señal local. En datasets muy grandes (>100k filas) se suele reducir a k=3 por costo computacional. En este proyecto, el KNNImputer se ajusta sobre el 80% de entrenamiento (~200k filas), lo que hace que k=5 sea computacionalmente viable y estadísticamente robusto.

**P6. ¿El KNNImputer se ajusta también sobre los datos de prueba? ¿Por qué no?**

No. El KNNImputer está dentro del Pipeline como paso anterior al clasificador. Cuando se llama a `pipeline.fit(X_train, y_train)`, el imputador aprende los k vecinos candidatos usando solo `X_train`. Cuando se llama a `pipeline.predict(X_test)`, el imputador usa esos mismos vecinos aprendidos para imputar los faltantes de `X_test`. El conjunto de prueba no participa en el `fit()` bajo ninguna circunstancia. Ajustar el imputador sobre datos de prueba introduciría data leakage, ya que el imputador "vería" patrones de datos que el modelo no debería conocer durante el entrenamiento.

---

## 3. Desbalance de clases y SMOTE

**P7. ¿Qué problema causa el desbalance si no se corrige?**

Con un ratio 6:1 (86.2% clase 0, 13.8% clase 1), un clasificador puede lograr 86.2% de accuracy prediciendo siempre "sin diabetes". Los modelos aprenden a minimizar la función de pérdida sobre la clase mayoritaria, resultando en sensibilidad cercana a cero (no detecta los diabéticos). En tamizaje clínico esto es inaceptable: el objetivo es detectar casos positivos, no simplemente acertar en la mayoría. Por eso usamos métricas como PR-AUC y sensibilidad, que son sensibles al desempeño sobre la clase minoritaria.

**P8. ¿SMOTE genera datos reales o sintéticos? ¿Es válido usarlos?**

SMOTE genera datos **sintéticos**: para cada ejemplo de la clase minoritaria, selecciona aleatoriamente uno de sus k vecinos más cercanos (en el espacio de características) y crea un nuevo punto interpolando linealmente entre ellos. No replica ejemplos existentes. Es válido porque: (1) los puntos generados están dentro de la distribución real de la clase minoritaria; (2) SMOTE se aplica solo dentro de cada fold de entrenamiento, nunca en el conjunto de prueba, por lo que las métricas se calculan sobre datos reales. La limitación conocida es que SMOTE puede generar ejemplos en regiones de frontera con alta densidad de clase 0, lo que puede reducir especificidad — efecto visible en SVM (especificidad 72.6%) vs. GBM que usa `class_weight` internamente (especificidad 92.9%).

**P9. ¿Por qué PR-AUC es más informativo que ROC-AUC en este dataset?**

ROC-AUC mide la capacidad de discriminación integrando TPR vs. FPR. Con desbalance fuerte, el FPR puede mantenerse bajo incluso con muchos falsos positivos, porque el denominador (TN+FP) es grande. PR-AUC usa Precisión (TP/(TP+FP)) vs. Recall (TPR) — ambas métricas se calculan sobre la clase positiva únicamente, sin involucrar los negativos verdaderos. Esto hace que PR-AUC sea más sensible al desempeño real sobre la clase minoritaria. En este proyecto, con prevalencia 13.8%, una PR-AUC de 0.41 ya implica un valor predictivo positivo usable en la práctica clínica.

---

## 4. SVM (Support Vector Machine)

**P10. ¿Qué significa el parámetro C y qué pasa si es muy alto o muy bajo?**

C es el parámetro de regularización inversa: controla el trade-off entre maximizar el margen de separación y minimizar el error de clasificación en entrenamiento. C alto → pocos errores en entrenamiento pero margen pequeño → riesgo de overfitting; C bajo → se toleran más errores pero el margen es mayor → mejor generalización. En este proyecto, el GridSearch exploró C ∈ {1, 10} sobre 5 folds y seleccionó C=10, lo que sugiere que el dataset es suficientemente grande y ruidoso como para que un margen blando reducido sea beneficioso.

**P11. ¿Por qué kernel RBF y no lineal?**

El kernel RBF (Radial Basis Function) proyecta implícitamente los datos a un espacio de alta dimensión donde las clases son linealmente separables, sin necesidad de definir explícitamente ese espacio. Para diabetes, la relación entre variables como BMI, edad y presión arterial con el diagnóstico es no lineal (interacciones multiplicativas, umbrales, etc.). Un kernel lineal requeriría que los factores de riesgo tuvieran efecto aditivo independiente, lo que no es consistente con la epidemiología de la enfermedad. RBF captura estas no linealidades con solo dos hiperparámetros (C y gamma).

**P12. ¿Por qué class_weight='balanced'?**

`class_weight='balanced'` hace que sklearn asigne pesos inversamente proporcionales a la frecuencia de cada clase: la clase 1 (diabéticos, 13.8%) recibe un peso ~6.2× mayor que la clase 0. Esto penaliza más los errores en la clase minoritaria durante el entrenamiento de la función de pérdida, produciendo fronteras de decisión que no favorecen sistemáticamente a la clase mayoritaria. Es una alternativa complementaria a SMOTE: ambas técnicas atacan el desbalance pero a niveles distintos (SMOTE a nivel de datos, `class_weight` a nivel de función de pérdida).

---

## 5. Árbol de Decisión

**P13. ¿Por qué limitar max_depth=5?**

Sin limitación, el árbol puede crecer hasta memorizar el conjunto de entrenamiento (sobreajuste), creando ramas que capturan ruido en lugar de señal. Con max_depth=5 el árbol tiene como máximo 32 hojas, lo que obliga a que cada hoja capture un patrón frecuente y generalizable. Empíricamente, árboles de profundidad 3-6 son los más usados en clasificación clínica porque también son interpretables: un médico puede seguir el árbol a mano para entender la lógica de la predicción.

**P14. ¿Cómo interpreta un árbol de decisión un clínico no técnico?**

El árbol se lee como una serie de preguntas binarias: "¿El IMC del paciente es mayor a 30? → si sí: ¿Tiene presión arterial alta? → si sí: riesgo alto". Cada nodo interior es una pregunta sobre una variable, cada rama es una respuesta (sí/no), y cada hoja es la clase predicha con la distribución de clases en ese subconjunto. A diferencia de SVM o GBM, el árbol produce reglas explícitas que pueden ser auditadas, cuestionadas y eventualmente validadas por expertos clínicos. Esta interpretabilidad es crítica en contextos médicos donde la "caja negra" no es aceptable.

**P15. ¿Qué es el Gini impurity y cómo guía las divisiones?**

Gini impurity mide la probabilidad de clasificar incorrectamente un elemento elegido aleatoriamente si se etiquetara según la distribución de clases del nodo: Gini = 1 − Σ(pᵢ²). Gini=0 significa nodo puro (una sola clase), Gini=0.5 máxima impureza (clases equiprobables). En cada nodo, el árbol busca el umbral de la variable que produce la mayor reducción de Gini ponderada entre los dos nodos hijos. Esto es equivalente a buscar la partición más "limpia" de los datos en ese punto del árbol.

---

## 6. Gradient Boosting (GBM)

**P16. ¿Qué significa que el GBM "corrija errores del modelo anterior"?**

GBM construye el modelo de forma iterativa: el primer árbol intenta predecir la variable objetivo. El segundo árbol no intenta predecir la variable objetivo directamente, sino el **residuo** (error) del primero. El tercer árbol intenta predecir el residuo del modelo formado por los dos árboles anteriores, y así sucesivamente. Cada árbol nuevo corrige lo que el ensemble anterior no pudo capturar. En la práctica esto se implementa como descenso de gradiente sobre la función de pérdida en el espacio funcional, donde el "gradiente" es el residuo de la iteración anterior.

**P17. ¿Por qué GBM obtiene mayor ROC-AUC que SVM en este caso a escala 50k?**

La diferencia es de 0.0001 (GBM=0.8270, SVM=0.8269), que está dentro del margen de variabilidad estadística y no es significativa. La ligera ventaja de GBM puede atribuirse a: (1) GBM modela interacciones entre variables de forma implícita mediante árboles, mientras que SVM depende del kernel para capturarlas; (2) con n=50k, GBM tiene suficientes datos para construir 200 árboles robustos; (3) el parámetro `subsample=0.8` introduce regularización estocástica que previene overfitting en datasets grandes. A n=10k, SVM fue el ganador (0.8351 vs 0.8236), lo que sugiere que GBM necesita más datos para materializarse su ventaja.

**P18. ¿Cuál es el riesgo de usar demasiados estimadores (n_estimators alto)?**

Con muchos estimadores, GBM puede sobreajustar: los árboles finales capturan ruido estadístico en lugar de patrones generalizables. Además, el costo computacional de predicción crece linealmente con n_estimators (cada predicción requiere evaluar todos los árboles). En este proyecto se usaron n_estimators=200 con learning_rate=0.05, un balance estándar en la literatura. Para mitigar overfitting adicional se usa `subsample=0.8` (cada árbol ve solo el 80% de los datos) y `max_depth=4` (árboles poco profundos). El early stopping (disponible en sklearn 1.1+) es una alternativa que detiene el entrenamiento automáticamente cuando la métrica de validación deja de mejorar.

---

## 7. Redes Neuronales (MLPClassifier)

**P19. ¿Qué significa la arquitectura (64, 32)?**

La red tiene dos capas ocultas: la primera con 64 neuronas y la segunda con 32. La capa de entrada tiene tantas neuronas como variables predictoras (21 en este caso), y la capa de salida tiene 2 neuronas (una por clase). El flujo de activación es: input (21) → hidden1 (64, ReLU) → hidden2 (32, ReLU) → output (2, softmax). Esta arquitectura embudo (64→32) reduce la dimensionalidad progresivamente, forzando a la red a extraer representaciones cada vez más abstractas. Para datos tabulares con 21 features, esta arquitectura es suficientemente expresiva sin ser computacionalmente costosa.

**P20. ¿Para qué sirve early_stopping=True?**

`early_stopping=True` reserva un 10% del conjunto de entrenamiento como validación interna y detiene el entrenamiento si la pérdida en ese subconjunto no mejora durante `n_iter_no_change=10` épocas consecutivas. Esto evita que la red memorice el conjunto de entrenamiento sin necesidad de definir explícitamente el número de épocas. Sin early stopping, habría que hacer un grid search sobre `max_iter` para encontrar el punto óptimo de parada, lo que multiplicaría el costo computacional. En la práctica, con early stopping el MLP converge en 50-200 épocas dependiendo del dataset.

**P21. ¿Por qué MLP puede tener menor ROC-AUC que GBM con muchos más parámetros?**

Los datos tabulares estructurados con variables heterogéneas (binarias, ordinales, continuas) tienden a favorecen a los métodos basados en árboles. Las redes neuronales están optimizadas para datos con estructura espacial o secuencial (imágenes, texto) donde cada neurona puede especializarse en un patrón local. En datos tabulares, GBM puede explotar directamente los umbrales naturales de las variables (e.g., BMI>30) que los árboles capturan exactamente, mientras que el MLP aproxima esos umbrales con funciones de activación suaves. Adicionalmente, el MLP de sklearn no tiene regularización L2 por defecto en esta configuración, lo que puede causar más varianza en datasets de tamaño moderado.

---

## 8. K-Means y fenotipos

**P22. ¿Por qué K-Means y no un modelo supervisado para segmentar pacientes?**

La segmentación con K-Means es **no supervisada**: no usa la etiqueta de diabetes para definir los grupos. Esto permite identificar fenotipos de riesgo que emergen de los patrones naturales del dataset, independientemente del diagnóstico. Un modelo supervisado definiría grupos según la predicción de diabetes, pero eso crea una circularidad (el fenotipo sería trivialmente "diabético" vs. "no diabético"). El valor de K-Means es que puede revelar subgrupos con perfiles distintos dentro de los no diabéticos, o identificar grupos de alto riesgo antes de que el diagnóstico ocurra. En este proyecto, el Fenotipo A tiene 28.2% de prevalencia de diabetes a pesar de ser definido por variables no clínicas.

**P23. ¿Cómo se eligió el número de clústeres K?**

Se evaluaron valores de k entre 2 y 10, ajustando K-Means para cada k y calculando el **silhouette score** promedio. El silhouette score mide la cohesión interna de cada clúster (qué tan cerca están los puntos de su centroide) y la separación entre clústeres (qué tan lejos están de los centroides vecinos): valores cercanos a 1 indican clústeres bien definidos, cercanos a -1 indican asignación incorrecta. Se seleccionó k=2 porque maximizó el silhouette score (0.589), que indica separación buena según los umbrales de Kaufman & Rousseeuw (>0.5 = structure is reasonable). El método del codo confirmó k=2 como punto de inflexión en la curva de inercia.

**P24. ¿Qué significa que un fenotipo tenga silhouette bajo?**

Un silhouette score bajo (cercano a 0) indica que los puntos de ese clúster están cerca del límite con otro clúster — el clúster no está bien separado. Silhouette negativo indica que un punto estaría mejor asignado al clúster vecino. En la práctica clínica, un fenotipo con silhouette bajo representa un grupo con fronteras difusas: sus miembros comparten algunas características pero no forman un grupo claramente diferenciable. Esto implica que la intervención dirigida a ese fenotipo podría tener menor precisión, ya que el grupo incluye perfiles heterogéneos. En este proyecto el silhouette global de 0.589 indica separación razonable entre los dos fenotipos.

---

## 9. Optimización de hiperparámetros

**P25. ¿Qué es GridSearchCV y por qué es costoso computacionalmente?**

GridSearchCV evalúa exhaustivamente todas las combinaciones posibles de los hiperparámetros especificados usando validación cruzada. Si se exploran 2 valores de C y 3 valores de gamma con k=5 folds, se entrenan 2×3×5=30 modelos. Para SVM con n=50k, cada entrenamiento toma ~10 minutos, por lo que el GridSearch completo tomaría ~5 horas solo para SVM. En este proyecto se restringió el grid a 6 combinaciones (C∈{1,10}, gamma∈{'scale','0.1','1.0'} reducido) para hacerlo viable académicamente. En producción, RandomizedSearchCV o optimización bayesiana (Optuna, Hyperopt) son alternativas más eficientes.

**P26. ¿Por qué usar StratifiedKFold en lugar de KFold simple?**

Con desbalance 6:1, si la partición en folds es aleatoria sin estratificación, algunos folds pueden terminar con muy pocos ejemplos de la clase minoritaria (o ninguno). Esto produce estimaciones de desempeño con alta varianza y sesgadas, porque el fold de validación no representa la distribución real del dataset. StratifiedKFold garantiza que cada fold tiene la misma proporción de clases que el dataset completo (≈13.8% clase 1), produciendo estimaciones más estables y representativas del desempeño real.

**P27. ¿Qué riesgo existe al optimizar sobre el conjunto de validación y no uno de prueba independiente?**

Si se usa el conjunto de prueba para seleccionar hiperparámetros, el modelo ha sido indirectamente "entrenado" sobre él: las métricas reportadas sobre el conjunto de prueba ya no son una estimación honesta del desempeño en datos nuevos. Esto se llama **optimismo del evaluador**. En este proyecto se usa una metodología de tres particiones: (1) entrenamiento para ajustar el modelo, (2) validación (dentro del GridSearchCV, vía KFold) para seleccionar hiperparámetros, y (3) prueba para reportar métricas finales — el conjunto de prueba no se toca hasta el final. Los 5 folds del GridSearch solo operan sobre el 80% de entrenamiento.

---

## 10. API en producción

**P28. ¿Cómo la API maneja el caso de que el modelo no esté cargado?**

La API tiene un modo de operación **degradado**: si `modelos/modelo_diabetes_v1.joblib` no existe al iniciar el servidor, el endpoint `/salud` responde con `{"estado": "degradado", "modelo": null}` en lugar de fallar con error 500. El endpoint `/predecir` responde con HTTP 503 (Service Unavailable) y un mensaje descriptivo. Esto permite desplegar la API antes de que el modelo esté disponible, facilita el monitoreo (el healthcheck sabe que el servicio existe pero no tiene modelo), y evita que una falta del modelo haga caer el servidor completo.

**P29. ¿Qué es el endpoint /salud y para qué sirve en un sistema real?**

`/salud` es un healthcheck endpoint. En sistemas reales, los orquestadores de contenedores (Kubernetes, Docker Swarm) o los load balancers verifican periódicamente este endpoint para determinar si la instancia está disponible para recibir tráfico. Si `/salud` retorna error o tarda más de un timeout configurable, la instancia se marca como no saludable y el tráfico se redirige a otras instancias. En este proyecto también reporta qué modelo está cargado, lo que facilita verificar que un despliegue nuevo cargó la versión correcta del modelo.

**P30. ¿Por qué serializar el Pipeline completo y no solo el clasificador?**

Si solo se serializa el clasificador, al momento de inferencia tendríamos que reproducir exactamente el mismo preprocesamiento (KNNImputer, StandardScaler, ColumnTransformer) en el código de la API, con el riesgo de inconsistencias sutiles (e.g., distintos valores de media calculados, distinto orden de columnas). Al serializar el Pipeline completo con joblib, la API solo necesita llamar a `pipeline.predict(datos_crudos)` — el Pipeline aplica automáticamente todas las transformaciones con los parámetros exactos aprendidos durante el entrenamiento. Esto garantiza que la API en producción hace exactamente lo mismo que el código de evaluación.

---

## 11. Métricas de evaluación

**P31. ¿Qué significa un ROC-AUC de 0.827 en términos clínicos?**

ROC-AUC de 0.827 significa que si tomamos aleatoriamente una persona con diabetes y una sin diabetes, el modelo asignará mayor probabilidad de riesgo a la persona con diabetes en el 82.7% de los casos. En contexto clínico, un ROC-AUC entre 0.80 y 0.90 se considera "bueno" y sugiere que el modelo tiene capacidad discriminativa útil para tamizaje, aunque no suficiente para diagnóstico definitivo (eso requiere laboratorio). Comparativamente, el azar puro daría 0.5 y un clasificador perfecto daría 1.0. Para tamizaje de primer nivel con solo 21 variables de encuesta, 0.827 es un resultado sólido consistente con la literatura.

**P32. ¿Cuándo es más importante la sensibilidad que la especificidad?**

En tamizaje clínico de enfermedades tratables, el costo de un **falso negativo** (decirle a un diabético que está sano) suele ser mayor que el costo de un **falso positivo** (enviar a un análisis adicional a alguien sano). Un falso negativo implica que la persona no recibe tratamiento y puede desarrollar complicaciones graves (retinopatía, nefropatía, pie diabético). Un falso positivo implica realizar un análisis de glucosa adicional, que es barato. Por eso para tamizaje se prioriza sensibilidad alta (mínimo 75-80% en guías clínicas), aceptando menor especificidad. En este contexto SVM (sensibilidad=0.778) es preferible a GBM (sensibilidad=0.379) aunque GBM tenga mayor especificidad.

**P33. ¿Qué es el Brier Score y qué mide que ROC-AUC no mide?**

El Brier Score es el error cuadrático medio entre la probabilidad predicha por el modelo y el resultado real (0 o 1): BS = (1/n) Σ(pᵢ − yᵢ)². Valores cercanos a 0 indican buena calibración; valor máximo es 1.0. ROC-AUC mide solo **discriminación**: si el modelo ordena correctamente los pacientes por riesgo relativo. Brier Score mide **calibración**: si las probabilidades absolutas son correctas. Un modelo puede tener ROC-AUC=0.85 pero Brier Score alto si predice 0.9 de probabilidad para todos los positivos cuando la prevalencia real es 14% — discrimina bien pero las probabilidades son incorrectas. En este proyecto, GBM tiene mejor calibración (BS=0.103) que SVM (BS=0.170), lo que importa cuando la probabilidad se usa directamente para priorizar pacientes (e.g., lista de espera para análisis de laboratorio).
