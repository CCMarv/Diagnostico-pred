# Documentación básica

## Contexto
Esta documentación resume la versión mínima del proyecto para uso académico.

## Objetivo
Explicar de forma breve por qué se usa un pipeline simple con tres modelos clásicos y métricas estándar.

## Alcance
- Dataset CDC BRFSS 2015 como fuente.
- Flujo lineal: carga -> limpieza -> entrenamiento -> evaluación -> guardado.
- Sin optimización avanzada ni infraestructura adicional.

## Decisiones principales
- Se prioriza claridad sobre sofisticación.
- Se usan técnicas estándar de `pandas` y `scikit-learn`.
- Se conserva una API mínima solo como capa opcional.

## Limitaciones
- El desempeño depende de la calidad del dataset local.
- No incluye búsqueda de hiperparámetros avanzada.
- No incluye análisis comparativo con literatura en esta versión.
