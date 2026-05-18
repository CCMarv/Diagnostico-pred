---
título: Preguntas de defensa y respuestas
categoría: explicaciones
audiencia: evaluadores académicos
versión: 1.0.0
última actualización: 2026-05-18
autor: Equipo diasgnostico-pred
estado: revisado
---

# Preguntas frecuentes de defensa

Documento de preparación para la defensa oral del proyecto. 33 preguntas cubren los 11 temas técnicos de la rúbrica, 3 por tema. Para cada pregunta se proporciona la respuesta esperada en el contexto específico de este proyecto.

---

## 1. Pipeline y preprocesamiento

**P1. ¿Por qué usar Pipeline en lugar de transformar el dataset directamente antes de entrenar?**

El Pipeline de sklearn aplica cada transformación solo sobre los datos que el estimador "ha visto". Si transformáramos el dataset completo antes de dividir, el imputador y el escalador aprenderían estadísticas (media, vecinos más cercanos) sobre los datos de prueba, filtrando información del futuro al modelo — esto se llama **data leakage** y produce estimaciones de desempeño artificialmente optimistas. El Pipeline garantiza que `fit()` solo toque datos de entrenamiento y `transform()` aplique esas mismas estadísticas al conjunto de prueba.

... (contenido original completado en el archivo fuente)
