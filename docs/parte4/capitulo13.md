# Capítulo 13. InfluxDB y Grafana

## 13.1. Introducción

En el capítulo 12 hemos instalado y comprobado Mosquitto y hemos intercambiado mensajes MQTT desde Arduino UNO Q. Ahora construiremos una plataforma de **almacenamiento y visualización de datos IoT** con dos herramientas complementarias:

- **InfluxDB 2.x**: base de datos de series temporales, adecuada para almacenar mediciones con fecha y hora.
- **Grafana**: plataforma de visualización que consulta los datos y los presenta mediante gráficos y paneles.

La arquitectura que construiremos será:

```text
Arduino UNO Q / simulador Python
           |
           | MQTT: monlau/aula1/telemetria
           v
      Mosquitto :1883
           |
           | Suscriptor Python
           v
      InfluxDB 2.x :8086
           |
           | Consulta Flux
           v
        Grafana :3000
           |
           v
     Navegador del PC
```

!!! note "Continuidad con el capítulo 12"
    Aprovecharemos el broker Mosquitto ya instalado y los mensajes JSON del capítulo anterior. No es necesario reinstalar MQTT.

### Objetivos

Al finalizar el capítulo serás capaz de:

1. Explicar qué es una base de datos de series temporales.
2. Instalar y comprobar InfluxDB 2.x en un contenedor Docker.
3. Crear una organización, un bucket y un token de acceso.
4. Escribir y consultar mediciones mediante Python.
5. Integrar un suscriptor MQTT con InfluxDB.
6. Instalar Grafana, configurar su origen de datos y construir un dashboard.
7. Verificar la persistencia de los datos y diagnosticar incidencias.

### Requisitos previos

- Arduino UNO Q con Linux, conexión a Internet y acceso SSH.
- Docker operativo y espacio libre suficiente para imágenes y datos.
- Mosquitto funcionando según el capítulo 12.
- Python 3 y un entorno virtual.
- Un ordenador en la misma red para acceder a las interfaces web.

!!! warning "Recursos de Arduino UNO Q"
    InfluxDB y Grafana consumen memoria y almacenamiento. Antes de instalarlos, comprueba la capacidad disponible. Si el rendimiento de la placa es insuficiente, puedes ejecutar los contenedores en otro ordenador Linux de la red y mantener Arduino UNO Q como cliente MQTT. No elimines contenedores ni volúmenes de otros capítulos.

## 13.2. Conceptos fundamentales de InfluxDB

Una **serie temporal** es una sucesión de mediciones asociadas a instantes de tiempo. En InfluxDB 2.x se utilizan estos conceptos:

| Concepto | Función | Ejemplo |
|---|---|---|
| Organización | Agrupa usuarios y recursos | `monlau` |
| Bucket | Almacena las mediciones | `iot` |
| Measurement | Tipo de medición | `ambiente` |
| Tag | Etiqueta indexada para filtrar | `dispositivo=arduino_uno_q` |
| Field | Valor medido | `temperatura=24.5` |
| Timestamp | Instante de la medición | Fecha y hora de escritura |

Un registro en **line protocol** podría ser:

```text
ambiente,dispositivo=arduino_uno_q temperatura=24.5,humedad=58.2
```

El timestamp puede omitirse: en ese caso, InfluxDB asigna el instante de recepción. Para los ejemplos de este capítulo utilizaremos InfluxDB **2.x**, no InfluxDB 3, porque sus interfaces y mecanismos de consulta son distintos.

## 13.3. Comprobaciones iniciales de Docker

Accede mediante SSH a Arduino UNO Q y ejecuta:

```bash
docker --version
docker info
free -h
df -h
docker ps -a
```

Si `docker info` devuelve un error de permisos, comprueba que el servicio Docker esté activo y utiliza `sudo docker` si tu configuración lo requiere. No cambies permisos sin necesidad.

Comprueba que los puertos de InfluxDB y Grafana estén libres:

```bash
sudo ss -lntp | grep -E ':8086|:3000' || true
```

Si ya existe un contenedor InfluxDB o Grafana, **no crees otro sin comprobar su configuración**. En ese caso, reutiliza el servicio existente y adapta los pasos siguientes.

## 13.4. Preparar el directorio de trabajo

Crearemos una carpeta independiente para los archivos de este capítulo:

```bash
mkdir -p ~/capitulo13_iot
cd ~/capitulo13_iot
```

Crearemos una red Docker para que Grafana pueda comunicarse con InfluxDB mediante el nombre del contenedor:

```bash
docker network inspect iot-net >/dev/null 2>&1 || docker network create iot-net
```

## 13.5. Instalar InfluxDB 2.x con Docker

Para evitar cambios inesperados entre versiones, utilizaremos una etiqueta de la rama 2.7:

```bash
docker pull influxdb:2.7-alpine
```

Crearemos dos volúmenes para conservar los datos y la configuración:

```bash
docker volume create influxdb2-data
docker volume create influxdb2-config
```

### Primera puesta en marcha

En un laboratorio aislado, iniciaremos el contenedor con acceso al puerto 8086:

```bash
docker run -d \
  --name influxdb2 \
  --restart unless-stopped \
  --network iot-net \
  -p 8086:8086 \
  -v influxdb2-data:/var/lib/influxdb2 \
  -v influxdb2-config:/etc/influxdb2 \
  influxdb:2.7-alpine
```

!!! warning "Contenedor existente"
    Si Docker responde que el nombre `influxdb2` ya está en uso, inspecciona el contenedor con `docker ps -a` y `docker inspect influxdb2`. No lo borres: podría contener datos de otras prácticas.

Comprueba el arranque:

```bash
docker ps
docker logs --tail 40 influxdb2
curl -i http://localhost:8086/health
```

La respuesta del endpoint `/health` debe indicar que el servicio está disponible. El código HTTP y el contenido pueden variar según el estado de inicialización.

## 13.6. Configuración inicial de InfluxDB

Desde el navegador de un ordenador de la misma red, accede a:

```text
http://IP_ARDUINO:8086
```

Sustituye `IP_ARDUINO` por la dirección obtenida con:

```bash
hostname -I
```

Si es la primera vez que abres la aplicación, selecciona el proceso de configuración inicial y utiliza estos valores de ejemplo:

| Campo | Valor recomendado |
|---|---|
| Usuario | `admin_iot` |
| Contraseña | Una contraseña robusta y privada |
| Organización | `monlau` |
| Bucket inicial | `iot` |

Guarda el **token de API** en un lugar seguro: lo necesitaremos para escribir y consultar datos. No lo incluyas en GitHub ni en las capturas de pantalla.

!!! tip "Si InfluxDB ya estaba configurado"
    Si aparece la pantalla de inicio de sesión, accede con las credenciales existentes. Comprueba en la interfaz que dispones de la organización `monlau`, del bucket `iot` y de un token con permisos de lectura y escritura sobre ese bucket. No repitas el asistente inicial ni borres datos.

## 13.7. Instalar y comprobar Grafana

Descarga la imagen de Grafana:

```bash
docker pull grafana/grafana:latest
```

Crea un volumen persistente:

```bash
docker volume create grafana-data
```

Inicia el contenedor:

```bash
docker run -d \
  --name grafana-iot \
  --restart unless-stopped \
  --network iot-net \
  -p 3000:3000 \
  -v grafana-data:/var/lib/grafana \
  grafana/grafana:latest
```

Comprueba el estado:

```bash
docker ps
docker logs --tail 40 grafana-iot
curl -I http://localhost:3000/login
```

Desde el navegador abre:

```text
http://IP_ARDUINO:3000
```

En una instalación nueva, Grafana suele solicitar las credenciales iniciales `admin` / `admin` y obliga a cambiar la contraseña. Si ya estaba configurado, utiliza las credenciales existentes.

!!! warning "Seguridad"
    Los puertos 8086 y 3000 se publican en la red del laboratorio. No expongas estos servicios directamente a Internet. Configura contraseñas robustas y utiliza HTTPS o un proxy seguro si se despliegan fuera de un entorno aislado.

## 13.8. Preparar Python para enviar mediciones

En la terminal de Arduino UNO Q:

```bash
cd ~/capitulo13_iot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install 'influxdb-client>=1,<2' 'paho-mqtt>=2,<3'
```

Si no está disponible el módulo `venv`, instala `python3-venv` y repite la creación del entorno.

Para no introducir el token directamente en el código, define las variables de entorno **en la terminal desde la que ejecutarás los programas**:

```bash
export INFLUX_URL='http://localhost:8086'
export INFLUX_ORG='monlau'
export INFLUX_BUCKET='iot'
read -rsp 'Token InfluxDB: ' INFLUX_TOKEN; echo
export INFLUX_TOKEN
```

El comando `read -s` permite introducir el token sin mostrarlo en pantalla. Estas variables solo estarán disponibles en esa sesión de terminal.

## 13.9. Programa 1. Escribir datos en InfluxDB

Crea el archivo `01_escribir_influx.py`:

```python
import os
import random
import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

URL = os.environ["INFLUX_URL"]
TOKEN = os.environ["INFLUX_TOKEN"]
ORG = os.environ["INFLUX_ORG"]
BUCKET = os.environ["INFLUX_BUCKET"]

with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)

    for numero in range(10):
        temperatura = round(random.uniform(20, 30), 2)
        humedad = round(random.uniform(40, 70), 2)

        punto = (
            Point("ambiente")
            .tag("dispositivo", "arduino_uno_q")
            .field("temperatura", temperatura)
            .field("humedad", humedad)
            .time(time.time_ns(), WritePrecision.NS)
        )

        write_api.write(bucket=BUCKET, org=ORG, record=punto)
        print("Medicion enviada:", numero + 1, temperatura, humedad)
        time.sleep(5)
```

Ejecútalo:

```bash
python 01_escribir_influx.py
```

El programa escribe diez mediciones, separadas cinco segundos. Cada punto contiene dos campos numéricos y una etiqueta que identifica el dispositivo.

### Comprobación en la interfaz

En InfluxDB, abre **Data Explorer**, selecciona el bucket `iot`, la medición `ambiente` y los campos `temperatura` y `humedad`. Ajusta el intervalo temporal para incluir los últimos minutos.

!!! example "Actividad 13.1"
    Ejecuta el programa y verifica que aparecen diez mediciones. Realiza una captura del resultado en la terminal y otra de la consulta en InfluxDB, sin mostrar el token.

## 13.10. Programa 2. Consultar datos desde Python

Crea `02_consultar_influx.py`:

```python
import os
from influxdb_client import InfluxDBClient

URL = os.environ["INFLUX_URL"]
TOKEN = os.environ["INFLUX_TOKEN"]
ORG = os.environ["INFLUX_ORG"]
BUCKET = os.environ["INFLUX_BUCKET"]

consulta = f'''
from(bucket: "{BUCKET}")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "ambiente")
  |> filter(fn: (r) => r._field == "temperatura")
  |> last()
'''

with InfluxDBClient(url=URL, token=TOKEN, org=ORG) as client:
    tablas = client.query_api().query(consulta, org=ORG)

    for tabla in tablas:
        for registro in tabla.records:
            print("Fecha:", registro.get_time())
            print("Temperatura:", registro.get_value())
```

Ejecuta:

```bash
python 02_consultar_influx.py
```

La consulta está escrita en **Flux**, lenguaje utilizado por InfluxDB 2.x para filtrar y transformar datos. Si no aparece ningún registro, revisa que el bucket contenga mediciones dentro de la última hora.

## 13.11. Integración MQTT → InfluxDB

Ahora conectaremos los dos capítulos. El programa del capítulo 12 publicará mensajes JSON en el topic `monlau/aula1/telemetria`, y un nuevo suscriptor almacenará los datos en InfluxDB.

### Configuración de MQTT

Si en el capítulo 12 activaste la autenticación, introduce también las credenciales MQTT en esta sesión:

```bash
export MQTT_HOST='localhost'
export MQTT_PORT='1883'
export MQTT_USER='alumno'
read -rsp 'Clave MQTT: ' MQTT_PASSWORD; echo
export MQTT_PASSWORD
```

Si el broker funciona sin autenticación, puedes dejar `MQTT_USER` y `MQTT_PASSWORD` sin definir.

### Programa 3. Puente MQTT a InfluxDB

Crea `03_mqtt_a_influx.py`:

```python
import json
import os
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

TOPIC = "monlau/aula1/telemetria"

influx = InfluxDBClient(
    url=os.environ["INFLUX_URL"],
    token=os.environ["INFLUX_TOKEN"],
    org=os.environ["INFLUX_ORG"]
)
write_api = influx.write_api(write_options=SYNCHRONOUS)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("MQTT conectado")
        client.subscribe(TOPIC, qos=1)
    else:
        print("Error MQTT:", reason_code)


def on_message(client, userdata, msg):
    try:
        datos = json.loads(msg.payload.decode("utf-8"))
        dispositivo = str(datos.get("dispositivo", "desconocido"))
        temperatura = float(datos["temperatura"])
        humedad = float(datos["humedad"])

        punto = (
            Point("ambiente")
            .tag("dispositivo", dispositivo)
            .field("temperatura", temperatura)
            .field("humedad", humedad)
        )

        write_api.write(
            bucket=os.environ["INFLUX_BUCKET"],
            org=os.environ["INFLUX_ORG"],
            record=punto
        )
        print("Datos guardados:", dispositivo, temperatura, humedad)

    except (ValueError, KeyError, TypeError, UnicodeDecodeError) as error:
        print("Mensaje incorrecto:", error)
    except Exception as error:
        print("Error al guardar datos:", error)


cliente = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

usuario = os.getenv("MQTT_USER")
clave = os.getenv("MQTT_PASSWORD")
if usuario:
    cliente.username_pw_set(usuario, clave)

cliente.on_connect = on_connect
cliente.on_message = on_message

try:
    cliente.connect(
        os.getenv("MQTT_HOST", "localhost"),
        int(os.getenv("MQTT_PORT", "1883")),
        60
    )
    print("Esperando telemetria MQTT...")
    cliente.loop_forever()
except KeyboardInterrupt:
    print("Programa detenido")
finally:
    cliente.disconnect()
    influx.close()
```

### Prueba paso a paso

1. En una terminal, activa el entorno virtual y define las variables de InfluxDB y MQTT.
2. Ejecuta el suscriptor:

```bash
python 03_mqtt_a_influx.py
```

3. En otra terminal, publica un mensaje de prueba. Si tu broker requiere usuario y contraseña, añade `-u alumno -P` y escribe la contraseña cuando se solicite:

```bash
mosquitto_pub -h localhost -t 'monlau/aula1/telemetria' -m '{"dispositivo":"arduino_uno_q","temperatura":25.4,"humedad":57.2}'
```

4. Comprueba que el programa muestra `Datos guardados`.
5. Abre Data Explorer y verifica que aparece la nueva medición.

!!! note "Mensajes reales o simulados"
    Para generar un flujo continuo puedes ejecutar `03_publicador_json.py` del capítulo 12. Los datos serán simulados hasta que conectemos sensores reales. No confundas una simulación con una medida física.

## 13.12. Configurar InfluxDB como origen de datos en Grafana

Abre Grafana en `http://IP_ARDUINO:3000` e inicia sesión.

1. En el menú de conexiones, selecciona **Data sources** y añade **InfluxDB**.
2. Selecciona **Flux** como lenguaje de consulta.
3. En el campo URL introduce **`http://influxdb2:8086`**.
4. En Organization introduce `monlau`.
5. En Token pega un token de InfluxDB con permisos de lectura sobre `iot`.
6. En Default Bucket introduce `iot`.
7. Guarda y pulsa **Save & test**.

!!! tip "¿Por qué no utilizamos localhost en Grafana?"
    Grafana e InfluxDB se ejecutan en contenedores diferentes. Dentro del contenedor Grafana, `localhost` apunta al propio Grafana, no a InfluxDB. Ambos contenedores están en la red `iot-net`, por lo que Grafana puede resolver el nombre `influxdb2`.

Si la conexión falla, comprueba que ambos contenedores aparecen en la misma red:

```bash
docker network inspect iot-net
```

## 13.13. Crear el primer dashboard

En Grafana, selecciona **Dashboards → New → New dashboard** y añade una visualización.

Selecciona el origen de datos InfluxDB y utiliza esta consulta Flux para representar la temperatura:

```flux
from(bucket: "iot")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "ambiente")
  |> filter(fn: (r) => r._field == "temperatura")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "temperatura")
```

Configura la visualización como **Time series**, con el título **Temperatura aula 1** y la unidad **Celsius (°C)**.

Crea un segundo panel para la humedad, sustituyendo el filtro por:

```flux
|> filter(fn: (r) => r._field == "humedad")
```

El segundo panel debe mostrar la unidad **Porcentaje (0-100)**.

Guarda el dashboard con el nombre **Monitorización IoT Arduino UNO Q**.

### Actualización automática

Selecciona un rango temporal adecuado, por ejemplo los últimos 15 minutos, y activa un intervalo de refresco disponible en tu instalación de Grafana, como 10 segundos. Si no hay datos, comprueba primero que el publicador y el puente MQTT están funcionando.

!!! example "Actividad 13.2"
    Construye un dashboard con dos paneles: temperatura y humedad. Verifica que ambos se actualizan mientras el publicador MQTT está enviando mensajes.

## 13.14. Persistencia y reinicio de servicios

Los volúmenes Docker permiten conservar los datos aunque se detenga el contenedor. Comprueba los volúmenes:

```bash
docker volume ls
```

Reinicia únicamente los contenedores creados en este capítulo:

```bash
docker restart influxdb2 grafana-iot
```

Después, vuelve a abrir InfluxDB y Grafana y comprueba que siguen existiendo el bucket, las mediciones y el dashboard.

!!! warning "No borrar volúmenes"
    `docker rm` elimina contenedores, y `docker volume rm` puede eliminar permanentemente los datos asociados. No utilices comandos de limpieza masiva como `docker system prune --volumes` en la placa del laboratorio.

## 13.15. Resolución de problemas

| Problema | Causa probable | Comprobación o solución |
|---|---|---|
| No abre InfluxDB | Contenedor detenido o puerto ocupado | `docker ps -a` y `docker logs influxdb2` |
| No abre Grafana | Contenedor detenido | `docker logs grafana-iot` |
| Grafana no conecta con InfluxDB | URL o red Docker incorrectas | Usar `http://influxdb2:8086` y revisar `iot-net` |
| `401 Unauthorized` | Token incorrecto o sin permisos | Revisar token y permisos del bucket |
| No aparecen datos | Bucket, rango temporal o campos incorrectos | Revisar Data Explorer y consulta Flux |
| MQTT no recibe mensajes | Broker, credenciales o topic incorrectos | Probar `mosquitto_sub` con las mismas credenciales |
| Python no encuentra una biblioteca | Entorno virtual inactivo | Activar `.venv` y revisar `pip show` |
| Datos desaparecen tras reiniciar | Volúmenes no configurados | Revisar montajes con `docker inspect` |
| Error de conexión desde otro PC | IP, firewall o puertos | Comprobar `hostname -I` y `ss -lntp` |

Comandos útiles:

```bash
docker ps -a
docker logs --tail 50 influxdb2
docker logs --tail 50 grafana-iot
curl -i http://localhost:8086/health
sudo ss -lntp | grep -E ':1883|:8086|:3000'
```

## 13.16. Práctica integradora: estación IoT monitorizada

**Enunciado:** desarrolla una estación de monitorización ambiental simulada que publique temperatura y humedad mediante MQTT, almacene las mediciones en InfluxDB y las visualice en Grafana.

### Tareas

1. Comprueba que Mosquitto funciona correctamente.
2. Instala o reutiliza InfluxDB 2.x y Grafana.
3. Configura la organización `monlau` y el bucket `iot`.
4. Ejecuta un publicador MQTT de telemetría JSON.
5. Programa un suscriptor Python que almacene las mediciones en InfluxDB.
6. Diseña un dashboard con gráficos de temperatura y humedad.
7. Activa la actualización automática del dashboard.
8. Reinicia los contenedores y verifica que se conservan los datos.
9. Documenta el procedimiento y las incidencias encontradas.

### Entrega

```text
capitulo13_iot/
|-- 01_escribir_influx.py
|-- 02_consultar_influx.py
|-- 03_mqtt_a_influx.py
|-- capturas/
|   |-- influxdb.png
|   |-- mqtt.png
|   |-- grafana.png
|   |-- persistencia.png
|-- memoria.pdf
```

No incluyas tokens, contraseñas ni archivos con credenciales en la entrega o en GitHub.

### Rúbrica de evaluación

| Criterio | Puntos |
|---|---:|
| Instalación y comprobación de InfluxDB | 2 |
| Instalación y configuración de Grafana | 1,5 |
| Escritura y consulta de datos con Python | 2 |
| Integración MQTT con InfluxDB | 2 |
| Dashboard con dos gráficos funcionales | 1,5 |
| Documentación y pruebas de persistencia | 1 |
| **Total** | **10** |

## 13.17. Conclusiones

En este capítulo hemos conectado tres tecnologías fundamentales para el Internet de las Cosas: **MQTT** para transportar los mensajes, **InfluxDB** para conservar mediciones con marcas temporales y **Grafana** para visualizar su evolución. La combinación permite construir un sistema de monitorización reproducible y ampliable.

En próximos capítulos podremos incorporar sensores reales, alarmas, automatización de respuestas y servicios adicionales.

!!! note "Comprobación antes de publicar"
    Verifica los comandos y programas en tu Arduino UNO Q antes de dar el capítulo por cerrado. Una vez comprobado, integra `capitulo13.md` en la navegación de `mkdocs.yml`, ejecuta `mkdocs build` y publica con `mkdocs gh-deploy` siguiendo el procedimiento habitual del libro.
