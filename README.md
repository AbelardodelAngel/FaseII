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
##

### 2. Imagen del modelo desplegado localmente
Se instaló el modelo usando Docker Desktop

<img width="1266" height="715" alt="image" src="https://github.com/user-attachments/assets/7d61423d-bea1-43f8-9b98-e00ef05affb8" />

### 3. Ejecución Local Comprobable (Inferencia)
Para comprobar que el pipeline de Machine Learning (el mapa de densidad .pkl y el modelo nativo .txt) se cargó correctamente en la memoria RAM del contenedor, se realizó una petición HTTP de prueba al endpoint de producción.

Ruta de Consulta: POST http://localhost:8000/predict
Cuerpo de la Petición (Payload de Prueba):
  ```powershell
   {
  "latitud": 19.4326,
  "longitud": -99.1332,
  "hora": 22,
  "dia_semana": 5
  }  
  ```
##### Nota: Las coordenadas deben corresponde a la Ciudad de México el modelo fue alimentado con incidentes de esta ciudad.

Respuesta Exitosa del Servidor (Output Verificable): El servicio web responde en milisegundos calculando la probabilidad de riesgo, aplicando el umbral operativo optimizado de 0.42 y retornando de manera correcta la bandera booleana despacho_urgente.
  ```powershell
{
    "probabilidad_riesgo": 0.6185,
    "umbral_operativo": 0.42,
    "despacho_urgente": true,
    "densidad_zona": 139
}
  ```
📸 Evidencia Gráfica de la Inferencia:
<img width="1490" height="613" alt="image" src="https://github.com/user-attachments/assets/92424482-5256-42c5-8932-4cd7501c5814" />

# 📘 Manual de Despliegue en la Nube: API de Control de Incidentes

Este documento constituye el manual técnico estandarizado para la migración, aprovisionamiento y puesta en producción del microservicio de priorización de incidentes desde un entorno de desarrollo efímero hacia una infraestructura en la nube de nivel empresarial.

---

## 🛠️ 1. Requerimientos Técnicos

Para garantizar el correcto funcionamiento, reproducibilidad y escalabilidad del sistema en la nube, el entorno debe cumplir con los siguientes prerrequisitos:

### Componentes de Software y Artefactos
* **Código Fuente (`app.py`):** Servidor asíncrono desarrollado en FastAPI.
* **Estrategia de Contenedores (`Dockerfile`):** Archivo de configuración basado en `python:3.11-slim` optimizado con hilos de ejecución paralelos (*4 workers*).
* **Manifiesto de Dependencias (`requirements.txt`):** Declaración estricta de librerías, incluyendo `lightgbm>=4.0.0` y `fastapi>=0.100.0`.
* **Artefactos del Modelo en RAM:**
    * `modelo_lightgbm_tuned.txt` (Pesos matemáticos en formato nativo serializado).
    * `frecuencia_zona.pkl` (Diccionario de ingeniería de variables indexado).

### Infraestructura Mínima Recomendada (Nube)
* **Cómputo:** 1 vCPU (Arquitectura x86_64 o ARM64).
* **Memoria RAM:** 1 GB a 2 GB mínimo (Suficiente para instanciar en memoria los diccionarios geográficos).
* **Red:** Puerto `8000` expuesto internamente, mapeado a los puertos estándar `80` (HTTP) o `443` (HTTPS) mediante un balanceador de carga o proxy inverso nativo.

---

## 🏗️ 2. Estrategia de Despliegue

La arquitectura de este microservicio se rige bajo una estrategia híbrida basada en **Contenedores (Containerization)** y **Plataformas como Servicio (PaaS / Serverless)**.

### Justificación de la Estrategia:
1.  **Portabilidad Absoluta (Docker):** Al empaquetar la lógica y las dependencias compiladas de C++ (como `libgomp1` para OpenMP) dentro de una imagen Docker, eliminamos el riesgo del clásico *"en mi máquina sí funcionaba"*. El contenedor correrá exactamente igual en local que en cualquier nube.
2.  **Arquitectura Serverless (PaaS):** Se selecciona el despliegue administrado (ej. *Google Cloud Run*, *AWS App Runner* o *Render*) sobre Servidores Virtuales tradicionales (VPS) debido a los siguientes beneficios operativos:
    * **Escalabilidad Automática:** La plataforma incrementa los contenedores si el tráfico de incidentes sube de golpe, y los reduce a cero en horas de baja demanda para minimizar costos.
    * **Abstracción de Infraestructura:** El equipo de desarrollo se enfoca en el código; la nube se encarga de los parches de seguridad del sistema operativo, el aprovisionamiento de certificados SSL (`https://`) y el balanceo de carga.

---

## 🚀 3. Descripción del Proceso Paso a Paso (Pipeline MLOps)

El flujo de despliegue continuo se compone de cuatro fases secuenciales:

```text
[Código en Colab] ──► [Repositorio GitHub] ──► [Compilación en la Nube] ──► [API Pública HTTPS]
```

## 🚀 4. Guía Rápida para Publicar en Render
Dado que ya se subio el repositorio a GitHub (AbelardodelAngel/FaseII), Render compilará tu Dockerfile de forma automática.
* Se debe entrar a render.com y créar una cuenta iniciando sesión directamente con tu cuenta de GitHub.
* En el panel principal, se da clic en el botón New + y se selecciona Web Service.
* Aparecerá una lista con tus repositorios de GitHub. Busca tu repositorio FaseII y dale clic en Connect.
* Se configura los siguientes campos en el formulario:
  - Name: api-prioridades-c5 (o el nombre que gustes para tu URL).
  - Region: Selecciona la más cercana (ej. Ohio o Oregon).
  - Branch: main
  - Runtime: Selecciona estrictamente Docker (Render leerá tu Dockerfile automáticamente).
* Se debe bajar hasta la sección de precios y asegúrarse de seleccionar la opción Free ($0/month).
* Se da clic al botón inferior Advanced e inyecta una variable de entorno obligatoria para que FastAPI sepa en qué puerto operar:
  - Key: PORT
  - Value: 8000
* Se debe dar clic en Create Web Service.
