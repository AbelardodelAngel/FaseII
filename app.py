from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import lightgbm as lgb
import pickle
import pandas as pd
import numpy as np
import os

app = FastAPI(title="API Control de Incidentes - C5", version="1.0")

model = None
frecuencia_zona = None

# Cambiamos la extensión al formato nativo universal .txt
ruta_modelo = "modelo_lightgbm_tuned.txt"
ruta_densidad = "frecuencia_zona.pkl"

if not os.path.exists(ruta_modelo):
    raise RuntimeError(f"❌ Archivo crítico no encontrado: {ruta_modelo}")
if not os.path.exists(ruta_densidad):
    raise RuntimeError(f"❌ Archivo crítico no encontrado: {ruta_densidad}")

try:
    # Carga nativa ultrarrápida sin problemas de serialización/Pickle
    model = lgb.Booster(model_file=ruta_modelo)
    
    with open(ruta_densidad, "rb") as f:
        frecuencia_zona = pickle.load(f)
        
    print("✅ Todos los artefactos nativos cargados exitosamente de forma global.")
except Exception as e:
    raise RuntimeError(f"❌ Error al cargar los archivos: {str(e)}")


class InferenciaRequest(BaseModel):
    latitud: float
    longitud: float
    hora: int
    dia_semana: int

@app.get("/health")
def health():
    return {
        "status": "healthy" if (model and frecuencia_zona) else "unhealthy",
        "model_loaded": model is not None,
        "density_map_loaded": frecuencia_zona is not None
    }

@app.post("/predict")
def predict(data: InferenciaRequest):
    if model is None or frecuencia_zona is None:
        raise HTTPException(status_code=500, detail="El modelo no se cargó correctamente.")

    if not (0 <= data.hora <= 23):
        raise HTTPException(status_code=400, detail="Hora debe estar entre 0 y 23")
    if not (0 <= data.dia_semana <= 6):
        raise HTTPException(status_code=400, detail="Día de la semana debe estar entre 0 y 6")
        
    lat_round = round(data.latitud, 3)
    lon_round = round(data.longitud, 3)
    densidad = frecuencia_zona.get((lat_round, lon_round), 0)
    
    # Para el booster nativo pasamos los valores en el orden exacto de las columnas de entrenamiento
    input_data = [[data.latitud, data.longitud, data.hora, data.dia_semana, densidad]]
    
    # El método predict del Booster nativo devuelve directamente la probabilidad de la clase positiva [0 a 1]
    probabilidad = float(model.predict(input_data)[0])
    
    UMBRAL = 0.42
    despacho_urgente = probabilidad >= UMBRAL
    
    return {
        "probabilidad_riesgo": round(probabilidad, 4),
        "umbral_operativo": UMBRAL,
        "despacho_urgente": despacho_urgente,
        "densidad_zona": densidad
    }
