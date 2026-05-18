---
título: Catálogo de modelos — índice
categoría: referencia
audiencia: equipo técnico
versión: 1.0.0
última actualización: 2026-05-18
autor: Equipo diasgnostico-pred
estado: revisado
---

# Catálogo de Modelos: Guía Unificada y Específicas

Esta carpeta contiene la documentación de todos los modelos de predicción de diabetes del proyecto. Está organizada en **dos niveles**:

## Punto de entrada: Flujo común

**[GUIA_UNIFICADA.md](GUIA_UNIFICADA.md)** ← **EMPIEZA AQUÍ**

Esta es la referencia central única. Documenta:
- Cómo todos los modelos siguen los mismos 8 pasos
- Contrato de datos CDC (21 variables)
- Preprocesamiento compartido
- Validación cruzada estratificada
- Entrenamiento productivo
- Carga e inferencia

**Debes leer GUIA_UNIFICADA.md primero para entender la arquitectura completa.**

---

## Guías específicas por modelo

Una vez entiendas el flujo común, consulta la guía específica de cada modelo para parámetros, justificaciones y características únicas:

| Modelo | Tipo | Archivo específico | Caso de uso |
|--------|------|-------|----------|
| **SVM** | Supervisado | [modelos/svm-especifico.md](modelos/svm-especifico.md) | Baseline kernelizado, GridSearchCV |
| **Árbol** | Supervisado | [modelos/arbol-especifico.md](modelos/arbol-especifico.md) | Interpretabilidad máxima |
| **GBM** | Supervisado | [modelos/gbm-especifico.md](modelos/gbm-especifico.md) | Máxima capacidad predictiva |
| **MLP** | Supervisado | [modelos/mlp-especifico.md](modelos/mlp-especifico.md) | No linealidad profunda, redes neuronales |
| **K-Means** | No supervisado | [modelos/kmeans-especifico.md](modelos/kmeans-especifico.md) | Fenotipado, exploración |

---

## Materiales de referencia

Los contenidos teóricos históricos han sido integrados como resúmenes embebidos en **[GUIA_UNIFICADA.md](GUIA_UNIFICADA.md)**. Puedes consultar allí las reglas prácticas sobre escalado, manejo del desbalance e intuiciones de modelos (SVM, redes, etc.).

> Nota: La carpeta de materiales históricos puede eliminarse una vez verificada la migración completa de contenido útil hacia `GUIA_UNIFICADA.md` y los archivos específicos por modelo.

> Estado del repositorio al 2026-05-17: `FenotipadoKMeans` y `OptimizadorHiperparametros` ya existen en `entrenamiento/` y sus pruebas asociadas están en verde, así que la documentación ya puede referenciarlos como implementación real.

> Estado del pipeline al 2026-05-17: los reportes operativos se generan a partir de un JSON crudo y se sintetizan en Markdown legible. No deben editarse manualmente como documentación fuente; si hace falta rehacerlos, se usa el pipeline y el script de síntesis.

---

## Cómo usar esta documentación

### Caso 1: Entender la arquitectura completa
1. Lee [GUIA_UNIFICADA.md](GUIA_UNIFICADA.md) (secciones 1-8)
2. Los materiales históricos se han migrado como resúmenes a `GUIA_UNIFICADA.md`; evita depender de la carpeta de materiales históricos.

### Caso 2: Detalles específicos de un modelo
1. Lee [GUIA_UNIFICADA.md](GUIA_UNIFICADA.md) (especialmente secciones 1-5, 7-8)
2. Ve a [modelos/{nombre}-especifico.md](modelos/)
3. Busca la sección "Parámetros específicos"

### Caso 3: Implementar un nuevo modelo en el catálogo
1. Lee [GUIA_UNIFICADA.md](GUIA_UNIFICADA.md) → "Plantilla reutilizable para futuros modelos"
2. Crea `modelos/{nombre}-especifico.md` siguiendo el patrón
3. Enlaza desde aquí

---

## Flujo de modelos en el proyecto

Independientemente del modelo, todos siguen este flujo:

```
1. Carga de datos (CDC BRFSS 2015, 21 columnas)
   ↓
2. Limpieza y preprocesamiento (imputación, transformación)
   ↓
3. Definición del modelo (parámetros específicos)
   ↓
4. Construcción de Pipeline (preprocesamiento + modelo)
   ↓
5. Entrenamiento (validación cruzada estratificada, ROC-AUC)
   ↓
6. Interpretación/Explicabilidad (según modelo)
   ↓
7. Entrenamiento productivo (train/test split, comparación)
   ↓
8. Carga e inferencia (API)
```

---

## Comparación rápida de modelos

| Característica | SVM | Árbol | GBM | MLP | K-Means |
|---|---|---|---|---|---|
| **Interpretabilidad** | Media | Máxima ✓ | Baja | Baja | Media |
| **Escalado requerido** | Sí ✓ | No | No | Sí ✓ | Sí ✓ |
| **Rendimiento típico** | Alto | Bajo-Medio | Máximo ✓ | Alto | N/A (no supervisa) |
| **Búsqueda hiperparámetros** | Sí (GridSearchCV) | No | No | No | No |
| **Early stopping** | No | No | No | Sí | N/A |
| **Explicabilidad avanzada** | Opcional (SHAP) | Directo | SHAP recomendado | SHAP | Centros + Silhouette |

---

## Referencias del proyecto

Archivos relacionados fuera de esta carpeta:

- [config.py](../../config.py) — Definición del contrato CDC
- [entrenamiento/preprocesador.py](../../entrenamiento/preprocesador.py) — ColumnTransformer compartido
- [entrenamiento/comparador_modelos.py](../../entrenamiento/comparador_modelos.py) — Catálogo de estimadores
- [entrenamiento/pipeline.py](../../entrenamiento/pipeline.py) — Orquestación de entrenamiento
- [inferencia/predictor.py](../../inferencia/predictor.py) — Carga y predicción
- [api/main.py](../../api/main.py) — Exposición HTTP

---

## Estructura de carpetas

```
docs/implementacion_modelos/
├── README.md                    ← Estás aquí (hub de navegación)
├── GUIA_UNIFICADA.md           ← Centro de referencia (flujo común)
├── modelos/
│   ├── svm-especifico.md       ← Detalles de SVM
│   ├── arbol-especifico.md     ← Detalles de Árbol
│   ├── gbm-especifico.md       ← Detalles de GBM
│   ├── mlp-especifico.md       ← Detalles de MLP
│   └── kmeans-especifico.md    ← Detalles de K-Means
└── (material histórico, migrado a GUIA_UNIFICADA.md)
```

---

## Checklist: Onboarding rápido

- [ ] Leo [GUIA_UNIFICADA.md](GUIA_UNIFICADA.md) (5-10 min)
- [ ] Entiendo los 8 pasos comunes
- [ ] Consulto el archivo específico del modelo que me interesa
- [ ] Confirmo que la carpeta de materiales históricos no contiene material crítico que deba preservarse

**¿Listo para implementar?** Ahora sí puedes ir a [entrenamiento/comparador_modelos.py](../../entrenamiento/comparador_modelos.py) con confianza.
