---
título: Guía de documentación y checklist para PRs
categoría: guias
audiencia: equipo técnico
versión: 0.1.0
última actualización: 2026-05-17
autor: Equipo diasgnostico-pred
estado: revisado
---

# Guía de documentación y checklist para PRs

Objetivo: mantener documentación sincronizada con el código y accesible para lectores técnicos y no técnicos.

- **Quién edita qué**: cambios de diseño → `docs/explicaciones/decisiones-diseno.md` y `PROYECTO.md`. Instrucciones de uso → `README.md`.
- **Marcar artefactos generados**: todos los archivos en `reportes/` deben incluir una cabecera indicando que son generados por el pipeline y no deben editarse manualmente.

## Single Source of Truth (SST)

Las siguientes ubicaciones son las fuentes canónicas para cada tipo de información. Actualizar la documentación solo después de cambiar el SST correspondiente.

- Constantes, rutas y umbrales: `config.py`
- Catálogo de modelos y parámetros por defecto: `entrenamiento/comparador_modelos.py`
- Orquestación del pipeline y argumentos CLI: `entrenamiento/pipeline.py`
- Contrato público de la API y validación: `api/esquemas.py` y `inferencia/predictor.py`

## Estructura de los documentos de modelo

- Resumen ejecutivo (1-2 párrafos) para no-programadores.
- Parámetros clave (tabla): nombre, valor en código, explicación en lenguaje llano.
- Procedimiento de entrenamiento (comando exacto).
- Artefactos producidos (rutas).

## Estilo

- Escribir en español.
- Usar nombres técnicos como `COLUMNAS_CDC` en código (monoespaciado) cuando se refieran a símbolos del proyecto.
- Evitar contradicciones: si un comportamiento es automático en código, documentarlo como tal; si requiere acción del usuario, indicar comandos exactos.

## Checklist para PR de documentación (manual)

Antes de marcar la PR lista para merge, completar esta verificación manual:

- [ ] `README.md` y `PROYECTO.md` describen correctamente los comandos y el flujo.
- [ ] `docs/explicaciones/decisiones-diseno.md` refleja cualquier cambio de diseño o decisión arquitectónica.
- [ ] Se añadieron notas de compatibilidad (Python/paquetes) cuando aplica.
- [ ] Archivos generados en `reportes/` contienen cabecera `ARTEFACTO GENERADO`.
- [ ] Documentos de modelo incluyen la sección para no-programadores.
- [ ] Se verificaron enlaces y referencias a `config.py`, `entrenamiento/comparador_modelos.py`, `entrenamiento/pipeline.py` y `api/esquemas.py`.
- [ ] Las instrucciones de entrenamiento incluyen el comando exacto y ejemplo de `--dataset` cuando aplica.
- [ ] Se corrieron localmente las pruebas relevantes: `pytest -q pruebas/test_cargador.py pruebas/test_predictor.py pruebas/test_preprocesador.py` (si no pasan, documentar fallo en la PR).

... (contenido original resumido)
