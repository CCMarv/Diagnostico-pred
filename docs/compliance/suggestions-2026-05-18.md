---
título: Propuestas de split/merge/redo por archivo
autor: Equipo diasgnostico-pred (automatizado)
fecha: 2026-05-18
estado: provisional
---

# Resumen

Este documento lista recomendaciones de estructura y contenido para cada archivo bajo `docs/` con el objetivo de alinear toda la documentación al `docs/referencia/estandar-de-documentacion.md` (Diátaxis). Las propuestas son sugerencias; ejecutar cambios por defecto requiere aprobación.

# Recomendaciones por archivo

- `docs/README.md` — Mantener como hub. No requiere split. Asegurarse de que el índice refleje la estructura final y que los enlaces a `referencia/estandar-de-documentacion.md` sean prominentes.

- `docs/referencia/estandar-de-documentacion.md` — Fuente de la verdad. NO tocar salvo para versiones mayores; añadir sección de mapeo entre categorías y carpetas si no existe.

- `docs/guias/guia-documentacion.md` — Mantener como guía operativa. No dividir. Añadir una subsección breve con ejemplos concretos de `SST` (ej.: cómo enlazar a `config.py`).

- `docs/explicaciones/decisiones-diseno.md` — Mantener como ADR-lite y registro. Propuesta: extraer la tabla de registro (ID/Fecha/Resumen) a `docs/adr/` si se espera crecimiento; si son pocas decisiones, mantener integrado.

- `docs/explicaciones/programa-materia.md` — Documento largo de enseñanza. Propuesta: si se va a usar como material de curso, mover a `docs/tutoriales/` o crear una versión resumida en `docs/explicaciones/` y mantener el detalle en `notebooks/` o `docs/material_curso/`.

- `docs/explicaciones/preguntas-defensa.md` — Mantener como checklist para evaluadores; no dividir. Añadir metadatos de audiencia (ya presente).

- `docs/reporte/evaluacion-academica.md` — Mantener en `reporte`. Verificar que los datos numéricos no estén duplicados en `reportes/` producidos por pipeline; si existen, dejar aquí solo el comentario interpretativo y enlazar al artefacto generado.

- `docs/implementacion_modelos/GUIA_UNIFICADA.md` — Centro de la sección de modelos; NO dividir. Es la SST para flujo de modelos.

- `docs/implementacion_modelos/modelos/*-especifico.md` — Cada archivo combina: (a) resumen para no-programadores, (b) parámetros técnicos, (c) snippets de código. Esto encaja bien con Diátaxis (explicaciones + referencia). Recomendación: mantener tal cual; si un archivo crece > 3k palabras, dividir en `...-tutorial.md` y `...-referencia.md`.

- `docs/compliance/audit-2026-05-18.md` y `docs/compliance/suggestions-2026-05-18.md` — Mantener en carpeta `docs/compliance/` y agregar a `.gitignore` si no deben publicarse.

# Acciones recomendadas (prioridad)

1. Aprobar y aplicar la eliminación de emojis (ya ejecutada). Verificar visualmente los archivos clave.  (Hecho)
2. Decidir sobre `programa-materia.md`: ¿material de curso público en docs o en `notebooks/`? Si se mantiene en docs, añadir índice y dividir por unidades (split opcional).
3. Si se espera más ADRs, mover registro a `docs/adr/` y dejar `decisiones-diseno.md` como narrativa de alto nivel.
4. Ejecutar link-checker automático y documentar hallazgos en `docs/compliance/links-2026-05-18.md`.

---
