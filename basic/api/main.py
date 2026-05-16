from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from basic.api.config import (
    MARGEN_INCERTIDUMBRE,
    TITULO_API,
    UMBRAL_RIESGO_ALTO,
    UMBRAL_RIESGO_BAJO,
    VERSION_SISTEMA,
)
from basic.api.esquemas import DatosPaciente, DetallesSalud, RespuestaPrediccion, RespuestaSalud
from basic.config import RUTA_MODELO_FINAL
from basic.inferencia.predictor import PredictorDiabetes


@asynccontextmanager
async def lifespan(app: FastAPI):
    predictor = PredictorDiabetes()
    predictor.cargar_modelo()
    app.state.predictor = predictor
    yield


app = FastAPI(title=TITULO_API, version=VERSION_SISTEMA, lifespan=lifespan)


@app.get("/salud", response_model=RespuestaSalud)
def salud() -> RespuestaSalud:
    modelo_cargado = RUTA_MODELO_FINAL.exists() and RUTA_MODELO_FINAL.stat().st_size > 0
    return RespuestaSalud(
        estado="operativo" if modelo_cargado else "degradado",
        version=VERSION_SISTEMA,
        detalles=DetallesSalud(
            modelo_cargado=modelo_cargado,
            ruta_modelo=RUTA_MODELO_FINAL.name,
            timestamp_servidor=datetime.now(tz=timezone.utc).isoformat(),
        ),
    )


@app.post("/predecir", response_model=RespuestaPrediccion)
def predecir(payload: DatosPaciente) -> RespuestaPrediccion:
    predictor: PredictorDiabetes = app.state.predictor
    if not predictor.esta_listo():
        raise HTTPException(status_code=503, detail="El modelo aún no está disponible.")

    try:
        resultado = predictor.predecir(payload.a_dataframe())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail="El modelo aún no está disponible.") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Error interno al ejecutar predicción.") from exc

    probabilidad = float(resultado["probabilidad"])
    if probabilidad < UMBRAL_RIESGO_BAJO:
        categoria = "bajo"
    elif probabilidad < UMBRAL_RIESGO_ALTO:
        categoria = "medio"
    else:
        categoria = "alto"

    advertencia = None
    cerca_bajo = abs(probabilidad - UMBRAL_RIESGO_BAJO) <= MARGEN_INCERTIDUMBRE
    cerca_alto = abs(probabilidad - UMBRAL_RIESGO_ALTO) <= MARGEN_INCERTIDUMBRE
    if cerca_bajo or cerca_alto:
        advertencia = "Resultado en zona de incertidumbre; requiere evaluación clínica."

    return RespuestaPrediccion(
        categoria_riesgo=categoria,
        confianza=probabilidad,
        version=str(resultado["version"]),
        tiempo_ms=int(resultado["tiempo_ms"]),
        advertencia=advertencia,
    )
