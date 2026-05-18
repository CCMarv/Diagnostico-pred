---
título: Estándar de Documentación para Proyectos Académicos de IA y Ciencia de Datos
versión: 1.0.0
estado: estándar de referencia
ámbito: proyecto-agnóstico
idioma: español
audiencia: equipos académicos de ciencia de datos, machine learning e inteligencia artificial
---

# Estándar de Documentación para Proyectos Académicos de IA y Ciencia de Datos

> **Propósito de este documento.** Definir un conjunto de prácticas concretas y verificables para crear, organizar y mantener la documentación de un proyecto académico de ciencia de datos o inteligencia artificial. El documento es agnóstico al proyecto: no asume un dominio, lenguaje o framework específico, y está pensado para servir como referencia que se carga al inicio de un proyecto y se consulta a lo largo de su ciclo de vida.

> **Cómo usar este estándar.** Cada sección es autocontenida y puede leerse de forma independiente. Las secciones 1–4 establecen principios y arquitectura general; las 5–6 ofrecen plantillas copiables; las 7–9 cierran con mantenimiento, antipatrones y checklist. Las plantillas pueden adaptarse, pero la jerarquía de secciones y los campos de metadatos deben preservarse para asegurar consistencia entre documentos.

---

## Tabla de contenidos

1. Principios rectores
2. Las cuatro categorías de documentación (marco Diátaxis)
3. Arquitectura de documentación del repositorio
4. Estilo y convenciones de escritura
5. Plantillas de documentos
6. Reproducibilidad, artefactos generados y trazabilidad
7. Mantenimiento y ciclo de vida de la documentación
8. Antipatrones frecuentes
9. Checklist de calidad antes de fusionar cambios
10. Apéndice A — Glosario
11. Apéndice B — Referencias y lecturas recomendadas

---

## 1. Principios rectores

Estos principios son los criterios contra los cuales se evalúa cualquier documento del proyecto. Cuando exista tensión entre prácticas concretas, se resuelve apelando a estos principios.

### 1.1. Audiencia primero

Antes de escribir, identificar al lector objetivo y qué necesita lograr. En proyectos académicos de IA y ciencia de datos coexisten al menos cuatro audiencias:

- **Equipo técnico actual** (quien implementa y prueba el código hoy).
- **Equipo técnico futuro** (quien recibe el proyecto en otro semestre, o el propio autor seis meses después).
- **Evaluadores académicos** (profesores, sinodales, revisores de papers) que evalúan rigor, claridad y reproducibilidad.
- **Lectores no programadores** (asesores de dominio, médicos, biólogos, economistas, etc.) que necesitan entender qué hace el sistema sin leer código.

Cada documento debe declarar explícitamente su audiencia primaria en el frontmatter o en la primera línea. Mezclar audiencias en un mismo documento es la causa más común de documentación que confunde a todos y no satisface a nadie.

### 1.2. Single Source of Truth (SST)

Para cada hecho del proyecto (una constante, una ruta, un parámetro por defecto, el contrato de una API, el catálogo de modelos), existe **un único lugar canónico** donde reside ese hecho. La documentación referencia ese lugar; no lo duplica.

Reglas operativas:

- Si una constante está definida en código, el documento la cita por nombre (en monoespaciado) y enlaza al archivo. No reescribe su valor.
- Si el valor cambia, se cambia en el SST y la documentación que lo referencia se valida automáticamente o por checklist.
- Los duplicados detectados se eliminan en favor del SST. Un documento puede explicar el porqué de un valor, pero el valor mismo vive en el código o en un archivo de configuración versionado.

... (contenido original continuado)
