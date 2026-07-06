# 🚀 API de Control de Incidentes y Priorización - C5

Este repositorio contiene la arquitectura de empaquetado, el código del microservicio y los artefactos de Machine Learning optimizados para predecir el riesgo de incidentes urbanos y automatizar el despacho de unidades de emergencia en tiempo real. 

El proyecto fue migrado desde una fase de experimentación en **Google Colab (MLflow)** hacia un contenedor independiente, portátil y altamente concurrente mediante **FastAPI** y **Docker**.

---

## 📅 Bitácora de Desarrollo: Solución de Errores en Producción

Durante el despliegue del día de hoy, se resolvieron de forma iterativa múltiples cuellos de botella críticos de MLOps:

1. **Error de Mapeo Interno (`Could not import module "app"`):** Los archivos internos se reorganizaron en un espacio aislado (`workspace`) para que el servidor Uvicorn localizara de forma exacta el punto de entrada de la API REST.
2. **Falla de Contexto Global (`NameError: frecuencia_zona`):** Se blindó la inicialización del script mediante una validación asertiva de existencia de archivos en el disco duro del contenedor.
3. **Incompatibilidad de Serialización (`UnpicklingError` / Metadatos de MLflow):** Al intentar cargar los archivos `.pkl` exportados por MLflow, el deserializador de Python falló debido a instrucciones de persistencia exclusivas del framework de tracking.
4. **Solución Definitiva:** Se migró el pipeline para extraer el modelo de la memoria RAM y guardarlo en el **formato nativo universal de texto plano (`.txt`)** de LightGBM, eliminando dependencias de terceros y asegurando un arranque del contenedor en milisegundos.

---

## 🏗️ Arquitectura del Proyecto (`Build Context`)

Para compilar la imagen de Docker, el espacio aislado de desarrollo debe contener exactamente la siguiente estructura de archivos raíz:

```text
workspace/
├── app.py                       # Código de la API REST asíncrona (FastAPI)
├── Dockerfile                   # Configuración e Infraestructura como Código
├── requirements.txt             # Manifiesto de dependencias optimizado
├── modelo_lightgbm_tuned.txt    # Pesos del modelo en formato nativo de LightGBM
└── frecuencia_zona.pkl          # Diccionario estructurado de densidad urbana (Feature Engineering)
🛠️ Configuración de los Componentes Core
```
---

## 📑 Evidencia de Despliegue: Contenedorización de la API de Incidentes

A continuación, se presentan los entregables técnicos que demuestran la correcta construcción, aislamiento y ejecución del microservicio predictivo utilizando Docker.

---

### 1. Imagen Construida Correctamente
Se ejecutó de manera exitosa el proceso de compilación de la infraestructura como código definida en el `Dockerfile`. La imagen base ligera de Python se configuró instalando las dependencias nativas de C++ (como `libgomp1` para OpenMP) y las librerías del entorno de ejecución de Python.

* **Comando utilizado para la compilación:**
  ```powershell
  docker build -t api-seguridad:tuned-independiente .

2. Contenedor Docker Funcional
El ciclo de vida del contenedor se encuentra activo en estado estable (Up). Las variables de entorno de optimización (PYTHONUNBUFFERED=1) permiten que el servidor web asíncrono Uvicorn se mantenga escuchando peticiones concurrentes a través de los 4 hilos (workers) configurados en el puerto 8000.

* **Comando utilizado para la compilación:**
  ```powershell
   docker run -d -p 8000:8000 --name api-prioridades api-seguridad:tuned-independiente
```
#

### 1. Imagen Construida Correctamente
Se ejecutó de manera exitosa el proceso de compilación de la infraestructura como código definida en el `Dockerfile`. La imagen base ligera de Python se configuró instalando las dependencias nativas de C++ (como `libgomp1` para OpenMP) y las librerías del entorno de ejecución de Python.


<img width="1266" height="715" alt="image" src="https://github.com/user-attachments/assets/7d61423d-bea1-43f8-9b98-e00ef05affb8" />
