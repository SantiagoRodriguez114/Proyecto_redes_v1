# red-sensores

Proyecto Dockerizado que integra un broker MQTT (Mosquitto), un backend + frontend en Flask y un simulador de nodos sensores. Con un único comando puedes levantar un entorno IoT completo para pruebas, desarrollo y demostraciones sin hardware físico.

- Estado: listo para ejecutar con Docker Compose
- Servicios principales: Mosquitto (MQTT), Web (Flask + dashboard), Simulator (publicador de datos)


---

Propósito general
Proyecto Dockerizado completo que integra backend, frontend, broker MQTT y simulador de nodos. Al ejecutar:

```bash
docker compose up --build
```

se levantan tres servicios principales:
-  Mosquitto → broker MQTT (puerto 1883).
-  Web (Flask) → servidor backend + frontend (API + dashboard) en el puerto 5000.
-  Simulator → genera datos falsos de sensores para pruebas.

Los contenedores se comunican entre sí mediante una red interna de Docker.

---

Estructura del proyecto (árbol y descripción)

red-sensores/
- docker-compose.yml
  - Orquesta los servicios: define build/context, redes, volúmenes y mapeos de puertos.
  - Contiene los servicios `mosquitto`, `web`, `simulator` y volúmenes para persistencia.
- README.md
  - Este archivo con instrucciones y descripción del proyecto.

mosquitto/
- config/
  - mosquitto.conf
    - Archivo de configuración del broker MQTT:
      - Puerto por defecto: 1883
      - allow_anonymous true/false según configuración
      - Rutas de logs y persistencia
      - Opciones para habilitar usuarios/TLS si se desea
- data/
  - Carpeta montada como volumen donde Mosquitto guarda logs, mensajes persistentes y sesiones (permite persistencia entre reinicios).

web/
- Dockerfile
  - Instrucciones para construir la imagen del servidor Flask (base Python 3.11, instalación de dependencias y comando para arrancar Gunicorn).
- requirements.txt
  - Lista de dependencias Python necesarias (ej.: Flask, paho-mqtt, flask-cors, gevent, gunicorn).
- app.py
  - Código del backend Flask. Funcionalidades principales:
    - Cliente MQTT (paho-mqtt) que se conecta a Mosquitto y se suscribe a topics.
    - Parseo de mensajes JSON recibidos de los sensores.
    - Inserción de lecturas en SQLite (ubicada en `./data_web/measurements.db`).
    - Endpoints:
      - GET / → sirve `index.html` (dashboard).
      - GET /stream → Server-Sent Events (SSE) para lecturas en tiempo real.
      - GET /api/latest → devuelve las últimas lecturas.
      - GET /api/history → devuelve historial (posible filtrado por nodo/fechas).
- templates/
  - index.html
    - Frontend que muestra el dashboard:
      - Usa Bootstrap para el layout.
      - Chart.js para gráficas.
      - Se suscribe a `/stream` para recibir datos en tiempo real.
- static/ (opcional)
  - Archivos estáticos: CSS, JS, imágenes (puede no existir si todo está inline en `index.html`).

simulator/
- Dockerfile
  - Imagen ligera de Python que instala dependencias mínimas y ejecuta el script de simulación.
- sim.py
  - Script que simula N nodos (por defecto 4) con coordenadas distintas.
  - Publica periódicamente mensajes JSON al broker MQTT con campos:
    - node_id, timestamp, soil_moisture, temperature, solar_radiation, ph, lat, lon
  - Topic de ejemplo
    - `sensors/<node_id>/measurements`

data_web/
- measurements.db (creada en ejecución)
  - Base de datos SQLite donde `web/app.py` almacena las lecturas de sensores.
  - Montada como volumen para persistencia en el host.

Volúmenes / redes / puertos (definidos en docker-compose.yml)
- Red interna de Docker para comunicación entre contenedores.
- Puertos:
  - MQTT: 1883 (Mosquitto)
  - Web (Flask/Gunicorn): 5000 (host)
- Volúmenes:
  - `mosquitto/data` → persistencia del broker.
  - `data_web` → persistencia de la DB SQLite.

---

Flujo de funcionamiento completo
1. `simulator/sim.py` publica lecturas MQTT en JSON al topic configurado.
2. `mosquitto` (broker) recibe los mensajes.
3. `web/app.py` (Flask) está suscrito a los topics, parsea y guarda en SQLite.
4. `web/templates/index.html` se conecta a `/stream` (SSE) y actualiza UI con gráficos y mapa.

Visual:

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/1f22b451-f77c-46fc-98bd-c12adc70e8dc" />

---

Cómo ejecutar

Requisitos:
- Docker y Docker Compose instalados.

1. Clonar el repositorio:
```bash
git clone https://github.com/SantiagoRodriguez114/Proyecto_redes_v1.git
cd Proyecto_redes_v1/red-sensores
```

2. Levantar con Docker Compose:
```bash
docker compose up --build
```
- Esto construye imágenes y levanta 3 contenedores (`mosquitto`, `web`, `simulator`).
- Accede al dashboard en: http://localhost:5000

3. Parar y limpiar:
```bash
docker compose down
```
- Para eliminar volúmenes persistentes:
```bash
docker compose down -v
```

Ejecución individual (sin Docker):
- Necesitas un broker MQTT accesible (ej. Mosquitto local) y ajustar las variables de conexión en `web/app.py` y `simulator/sim.py`.
- Instalar dependencias y ejecutar:
```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
pip install -r web/requirements.txt
python web/app.py
# En otra terminal:
python simulator/sim.py
```


---

API, topics y payload de ejemplo

Ejemplo de topic:
- `sensors/node-01/measurements`

Ejemplo de payload JSON:
```json
{
  "node_id": "node-01",
  "timestamp": "2025-10-28T12:34:56Z",
  "soil_moisture": 23.5,
  "temperature": 27.1,
  "solar_radiation": 654,
  "ph": 6.8,
  "lat": -33.45,
  "lon": -70.66
}
```

Endpoints principales expuestos por el backend:
- GET / → Dashboard (index.html)
- GET /stream → SSE (datos en tiempo real)
- GET /api/latest → últimas lecturas
- GET /api/history → historial de lecturas (posible filtrado por nodo/fecha)

---

Persistencia
- SQLite en `./data_web/measurements.db` (montado como volumen para persistencia).
- Mosquitto persiste datos en `mosquitto/data/` según `mosquitto.conf`.

---


