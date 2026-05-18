---
título: Notas sobre cuándo escalar o no escalar
categoría: referencia
audiencia: equipo técnico
versión: 1.0.0
última actualización: 2026-05-18
autor: Equipo diasgnostico-pred
estado: borrador
---

# Escalado: reglas prácticas

Resumen corto de la política de escalado del proyecto:

- **Escalar obligatorio**: SVM, MLP, K-Means (usaron distancias o descenso de gradiente). Use `StandardScaler` ajustado solo en el conjunto de entrenamiento.
- **Escalado opcional**: Árboles y GBM (modelos basados en umbrales). Mantener `Pipeline` compartido para consistencia si se desea.

Referencias: [GUIA_UNIFICADA.md](GUIA_UNIFICADA.md), `entrenamiento/preprocesador.py`.
