---
título: Programa de la materia — Unidad y contenidos
categoría: explicaciones
audiencia: equipo técnico
versión: 1.0.0
última actualización: 2026-05-18
autor: Equipo diasgnostico-pred
estado: archivado
---

UNIDAD 1: El Pipeline de ML y Procesamiento de Datos Avanzado

1.1. Ingeniería del Flujo de Trabajo:  
• El ciclo de vida del ML y el problema de la Fuga de Datos (Data Leakage).  
• Introducción a sklearn.pipeline.Pipeline.

1.2. Transformación Avanzada:  
• Imputación multivariable (KNNImputer).  
• Codificación robusta (TargetEncoder, HashingEncoder).  
• Transformaciones de potencia (Yeo-Johnson) y escalado robusto.

1.3. Gestión del Desbalance:  
• Métricas en desbalance (Precision-Recall vs ROC).  
• Técnicas de remuestreo: SMOTE y NearMiss.  
• Uso de sklearn.compose.ColumnTransformer.

UNIDAD 2: Aprendizaje Supervisado: Modelos No Lineales y Ensambles

2.1. Support Vector Machines (SVM):  
•Intuición geométrica: Maximización del margen.  
•El truco del Kernel (RBF, Polinomial) y la optimización convexa.

2.2. Árboles de Decisión:  
• Algoritmos de división (CART).  
• Métricas de pureza: Entropía de Shannon (conexión V2219) e Índice Gini.

2.3. Métodos de Ensamble (The Wisdom of Crowds):  
• Bagging: Random Forests y la reducción de varianza.  
• Boosting: Gradient Boosting (XGBoost/LightGBM) y su conexión con el Gradiente Descendiente.  
• Análisis de Complejidad Computacional (Big-O) de estos modelos 

UNIDAD 3: Aprendizaje No Supervisado: Clustering y Dimensionalidad

3.1. Agrupamiento (Clustering):  
• K-Means: Algoritmo Expectation-Maximization. Inicialización K-Means++.  
• DBSCAN: Clustering basado en densidad y manejo de ruido.  
• Métricas de validación interna: Método del Codo y Coeficiente de Silueta.

3.2. Reducción de Dimensionalidad:  
• La maldición de la dimensionalidad.  
• PCA (Análisis de Componentes Principales): Fundamento de álgebra lineal (Eigenvectores/Eigenvalores) y maximización de varianza.  
• Visualización de datos de alta dimensión (t-SNE / UMAP).

4.1. Optimización de Hiperparámetros:  
• Búsqueda exhaustiva (GridSearchCV) vs. Aleatoria (RandomizedSearchCV).  
• Validación Cruzada Estratificada (Stratified K-Fold).

4.2. Introducción a Redes Neuronales:  
• El Perceptrón Multicapa (MLP) como generalización de la regresión logística.  
• Funciones de activación (ReLU, Sigmoid, Softmax) y su impacto en el gradiente.  
• Backpropagation: Intuición basada en la Regla de la Cadena y Gradiente Descendiente.  
• Arquitecturas básicas y prevención de overfitting (Dropout).

Evaluación del curso 

| Prácticas | 40% |
| :---- | :---- |
| Proyecto final | 30% |
| Participación | 30% |

... (contenido original)
