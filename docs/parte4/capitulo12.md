# Capítulo 12. MQTT y comunicaciones IoT

## Objetivos del capítulo

En este capítulo utilizaremos **Arduino UNO Q como plataforma de comunicaciones IoT** desde su sistema Linux. Instalaremos un broker MQTT, intercambiaremos mensajes desde la terminal y crearemos clientes Python para publicar telemetría y recibir órdenes. Finalmente, habilitaremos conexiones autenticadas desde otros equipos de una red de laboratorio.

Al finalizar seremos capaces de:

- Explicar la arquitectura de publicación y suscripción de MQTT.
- Identificar broker, cliente, *topic*, QoS y mensaje retenido.
- Instalar y comprobar Eclipse Mosquitto en Arduino UNO Q.
- Publicar y recibir mensajes con `mosquitto_pub` y `mosquitto_sub`.
- Programar publicadores y suscriptores con `paho-mqtt` 2.x.
- Enviar telemetría en formato JSON y procesar órdenes MQTT.
- Configurar un usuario y conectar clientes desde otro ordenador.
- Aplicar medidas básicas de seguridad y diagnóstico.

!!! note "Requisitos previos"
    Partimos del Arduino UNO Q con Linux operativo, conexión de red, acceso SSH y Python 3. El capítulo 11 ya está instalado y comprobado. Los ejemplos Python se ejecutan en Linux y **no accionan directamente los pines del microcontrolador**. Todos los comentarios y cadenas de texto de los programas Python utilizan caracteres ASCII, sin acentos ni eñes.

## 12.1. ¿Qué es MQTT?

**MQTT** (*Message Queuing Telemetry Transport*) es un protocolo ligero de mensajería especialmente útil para dispositivos conectados, sensores y sistemas de automatización. A diferencia del modelo petición-respuesta habitual de HTTP, MQTT utiliza **publicación/suscripción**: los clientes envían mensajes a un servidor intermediario y otros clientes reciben los mensajes de los temas a los que están suscritos.

```text
 Arduino UNO Q                    Broker MQTT                 Ordenador
 (publicador)                     Mosquitto                  (suscriptor)
      |                               |                           |
      | PUBLISH monlau/aula1/temp     |                           |
      |------------------------------>|                           |
      |                               | Mensaje: 24.5             |
      |                               |-------------------------->|
      |                               |                           |
```

El **broker** recibe y distribuye mensajes. El **publicador** envía información a un tema o *topic*. El **suscriptor** solicita recibir mensajes de uno o varios temas. Un mismo cliente puede publicar y suscribirse simultáneamente.

### Organización de los topics

Usaremos nombres jerárquicos separados por barras:

```text
monlau/aula1/temperatura
monlau/aula1/humedad
monlau/aula1/telemetria
monlau/aula1/led/comando
monlau/aula1/led/estado
```

En las suscripciones, `+` sustituye **un nivel** y `#` sustituye **cero o más niveles**, siempre al final. Por ejemplo, `monlau/+/temperatura` recibe temperaturas de cualquier aula y `monlau/#` recibe todos los mensajes de ese prefijo.

### Puertos y calidad de servicio

| Elemento | Significado |
|---|---|
| TCP 1883 | MQTT sin cifrado TLS. |
| TCP 8883 | MQTT con TLS, si el broker está configurado para ello. |
| QoS 0 | Entrega como máximo una vez. |
| QoS 1 | Entrega al menos una vez; puede haber duplicados. |
| QoS 2 | Entrega exactamente una vez en el intercambio MQTT. |
| `retain` | Conserva el último mensaje retenido de un topic para futuros suscriptores. |
| LWT | Mensaje de última voluntad que el broker puede publicar si un cliente se desconecta inesperadamente. |

!!! tip "MQTT no es una base de datos"
    MQTT transporta mensajes. Para conservar históricos y representar gráficas será necesario integrar posteriormente otros servicios, como Node-RED, InfluxDB o Grafana.

## 12.2. Instalar el broker Mosquitto

Conectamos por SSH al Arduino UNO Q y actualizamos el índice de paquetes:

```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients -y
```

Activamos el servicio y comprobamos su estado:

```bash
sudo systemctl enable --now mosquitto
sudo systemctl status mosquitto
```

La salida debe contener `Active: active (running)`. Pulsamos `Q` para salir del visor. Comprobamos el puerto:

```bash
sudo ss -lntp | grep 1883
```

En una instalación inicial de Mosquitto 2.x es normal que solo escuche en `127.0.0.1` y/o `::1`. Por ahora es suficiente: las primeras pruebas se harán dentro del Arduino UNO Q.

!!! warning "No abrir todavía el puerto a Internet"
    No redirijas el puerto 1883 desde el router. Primero probaremos la comunicación local y después habilitaremos el acceso desde la red de laboratorio con autenticación.

## 12.3. Primera comunicación desde la terminal

Abrimos **dos sesiones SSH** hacia Arduino UNO Q.

En la **terminal A**, iniciamos un suscriptor:

```bash
mosquitto_sub -h localhost -t 'monlau/aula1/temperatura' -v
```

En la **terminal B**, publicamos un mensaje:

```bash
mosquitto_pub -h localhost -t 'monlau/aula1/temperatura' -m '24.5'
```

La terminal A debe mostrar:

```text
monlau/aula1/temperatura 24.5
```

Publicamos nuevos valores:

```bash
mosquitto_pub -h localhost -t 'monlau/aula1/temperatura' -m '25.1'
mosquitto_pub -h localhost -t 'monlau/aula1/temperatura' -m '25.7'
```

Detenemos el suscriptor con `Ctrl+C` y nos suscribimos a todos los temas del aula:

```bash
mosquitto_sub -h localhost -t 'monlau/aula1/#' -v
```

Desde la terminal B publicamos:

```bash
mosquitto_pub -h localhost -t 'monlau/aula1/humedad' -m '58'
mosquitto_pub -h localhost -t 'monlau/aula1/led/estado' -m 'OFF'
```

El suscriptor recibe ambos mensajes porque el comodín `#` incluye todos los subtemas.

### Comprobar los mensajes retenidos

Publicamos un estado retenido:

```bash
mosquitto_pub -h localhost -t 'monlau/aula1/led/estado' -m 'OFF' -r
```

Abrimos un nuevo suscriptor:

```bash
mosquitto_sub -h localhost -t 'monlau/aula1/led/estado' -v -C 1
```

El mensaje aparece inmediatamente aunque se haya publicado antes de iniciar la suscripción. Para eliminar el mensaje retenido, enviamos una carga vacía con `-r`:

```bash
mosquitto_pub -h localhost -t 'monlau/aula1/led/estado' -n -r
```

!!! example "Práctica 12.1. Comunicación desde dos terminales"
    1. Comprueba que Mosquitto está activo.
    2. Publica tres temperaturas y dos valores de humedad.
    3. Utiliza el comodín `#` para recibir todos los mensajes del aula.
    4. Publica y comprueba un mensaje retenido.
    5. Guarda capturas de las dos terminales y explica qué hace cada comando.

## 12.4. Preparar el entorno Python

Crearemos una carpeta de trabajo y un entorno virtual independiente:

```bash
mkdir -p ~/capitulo12_mqtt
cd ~/capitulo12_mqtt
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install 'paho-mqtt>=2,<3'
python -m pip show paho-mqtt
```

Si falta el módulo `venv`, instalamos `python3-venv` con `sudo apt install python3-venv -y` y repetimos la creación del entorno. Cuando volvamos a abrir una sesión SSH, activaremos el entorno con `source ~/capitulo12_mqtt/.venv/bin/activate`.

Los ejemplos utilizan la **API de callbacks versión 2** de `paho-mqtt`.

## 12.5. Programa 1: publicador de temperatura

Creamos el archivo `01_publicador.py`:

```python
import random
import time
import paho.mqtt.client as mqtt

BROKER = "localhost"
PUERTO = 1883
TOPIC = "monlau/aula1/temperatura"

cliente = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

cliente.connect(BROKER, PUERTO, 60)
cliente.loop_start()

try:
    while True:
        temperatura = round(random.uniform(20, 30), 2)
        mensaje = str(temperatura)

        resultado = cliente.publish(TOPIC, mensaje, qos=1)
        resultado.wait_for_publish()
        print("Temperatura enviada:", mensaje)

        time.sleep(5)
except KeyboardInterrupt:
    print("Programa detenido")
finally:
    cliente.disconnect()
    cliente.loop_stop()
```

El programa genera un valor simulado entre 20 y 30 grados y lo publica cada cinco segundos. `loop_start()` atiende el tráfico MQTT en segundo plano; `wait_for_publish()` espera a que finalice el envío conforme al nivel de servicio solicitado.

En una terminal ejecutamos:

```bash
mosquitto_sub -h localhost -t 'monlau/aula1/temperatura' -v
```

En otra, con el entorno virtual activo:

```bash
cd ~/capitulo12_mqtt
python 01_publicador.py
```

**Resultado esperado:** aparece una nueva temperatura aproximadamente cada cinco segundos. Finalizamos con `Ctrl+C`.

## 12.6. Programa 2: suscriptor Python

Creamos `02_suscriptor.py`:

```python
import paho.mqtt.client as mqtt

BROKER = "localhost"
PUERTO = 1883
TOPIC = "monlau/aula1/temperatura"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Conectado al broker MQTT")
        client.subscribe(TOPIC, qos=1)
    else:
        print("Error de conexion:", reason_code)


def on_message(client, userdata, msg):
    mensaje = msg.payload.decode("utf-8")
    print("Topic:", msg.topic)
    print("Temperatura:", mensaje)
    print("------------------------")


cliente = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)
cliente.on_connect = on_connect
cliente.on_message = on_message
cliente.connect(BROKER, PUERTO, 60)

print("Esperando mensajes MQTT...")
try:
    cliente.loop_forever()
except KeyboardInterrupt:
    print("Programa detenido")
finally:
    cliente.disconnect()
```

La función `on_connect()` se ejecuta al conectar y registra la suscripción. La función `on_message()` recibe cada mensaje, decodifica su contenido y lo muestra. Suscribirse dentro de `on_connect()` permite recuperar la suscripción si el cliente vuelve a conectarse.

Ejecutamos `python 02_suscriptor.py` en una terminal y `python 01_publicador.py` en otra. Deben aparecer los valores publicados en tiempo real.

!!! example "Práctica 12.2. Dos programas Python"
    Ejecuta el publicador y el suscriptor simultáneamente. Cambia el intervalo de publicación de cinco a dos segundos y comprueba que los mensajes llegan con la nueva frecuencia. Explica qué ocurriría si el suscriptor estuviera desconectado y no existiera una sesión persistente ni mensajes retenidos.

## 12.7. Programa 3: telemetría con JSON

Un único mensaje puede contener varias mediciones. Crearemos `03_publicador_json.py`:

```python
import json
import random
import time
import paho.mqtt.client as mqtt

BROKER = "localhost"
PUERTO = 1883
TOPIC = "monlau/aula1/telemetria"

cliente = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)
cliente.connect(BROKER, PUERTO, 60)
cliente.loop_start()

try:
    while True:
        datos = {
            "dispositivo": "arduino_uno_q",
            "temperatura": round(random.uniform(20, 30), 2),
            "humedad": round(random.uniform(40, 70), 2),
            "estado": "activo"
        }

        mensaje = json.dumps(datos)
        resultado = cliente.publish(TOPIC, mensaje, qos=1)
        resultado.wait_for_publish()
        print("Datos enviados:", mensaje)

        time.sleep(5)
except KeyboardInterrupt:
    print("Programa detenido")
finally:
    cliente.disconnect()
    cliente.loop_stop()
```

Ejemplo de mensaje:

```json
{
  "dispositivo": "arduino_uno_q",
  "temperatura": 24.5,
  "humedad": 58.2,
  "estado": "activo"
}
```

Para comprobarlo, abrimos:

```bash
mosquitto_sub -h localhost -t 'monlau/aula1/telemetria' -v
```

Y ejecutamos:

```bash
python 03_publicador_json.py
```

!!! tip "Ventaja de JSON"
    JSON facilita que otros servicios interpreten los campos de cada mensaje. Por ejemplo, Node-RED puede extraer la temperatura y enviarla a una base de datos de series temporales.

## 12.8. Programa 4: recepción de órdenes MQTT

Simularemos un LED que puede estar encendido o apagado. **Esta práctica modifica una variable Python; todavía no controla un LED físico.** Creamos `04_control_mqtt.py`:

```python
import paho.mqtt.client as mqtt

BROKER = "localhost"
PUERTO = 1883
TOPIC = "monlau/aula1/led/comando"

estado_led = False


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Conectado al broker MQTT")
        client.subscribe(TOPIC, qos=1)
    else:
        print("Error de conexion:", reason_code)


def on_message(client, userdata, msg):
    global estado_led

    comando = msg.payload.decode("utf-8").strip().upper()

    if comando == "ON":
        estado_led = True
        print("LED encendido")
    elif comando == "OFF":
        estado_led = False
        print("LED apagado")
    else:
        print("Comando no reconocido:", comando)


cliente = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)
cliente.on_connect = on_connect
cliente.on_message = on_message
cliente.connect(BROKER, PUERTO, 60)

print("Esperando comandos MQTT...")
try:
    cliente.loop_forever()
except KeyboardInterrupt:
    print("Programa detenido")
finally:
    cliente.disconnect()
```

Con el receptor ejecutándose, enviamos órdenes desde otra terminal:

```bash
mosquitto_pub -h localhost -t 'monlau/aula1/led/comando' -m 'ON'
mosquitto_pub -h localhost -t 'monlau/aula1/led/comando' -m 'OFF'
```

El receptor mostrará `LED encendido` y `LED apagado`. Una ampliación futura será integrar esta lógica con el microcontrolador mediante los mecanismos compatibles con Arduino App Lab.

## 12.9. Acceso desde otro ordenador de la red

Hasta ahora los clientes se conectan a `localhost`. Para permitir el acceso desde otro ordenador debemos configurar un listener de red y exigir autenticación.

### Paso 1. Crear el usuario MQTT

En Arduino UNO Q ejecutamos:

```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd alumno
```

El comando solicita una contraseña. **No la incluyas en capturas ni en archivos que vayas a compartir.** La opción `-c` crea el archivo; no la utilices al añadir usuarios posteriores, porque sobrescribiría los anteriores.

### Paso 2. Configurar el listener

Abrimos:

```bash
sudo nano /etc/mosquitto/conf.d/arduino.conf
```

Añadimos:

```ini
listener 1883 0.0.0.0
allow_anonymous false
password_file /etc/mosquitto/passwd
```

Guardamos con `Ctrl+O`, `Enter` y salimos con `Ctrl+X`. Reiniciamos y verificamos:

```bash
sudo systemctl restart mosquitto
sudo systemctl status mosquitto
sudo ss -lntp | grep 1883
```

!!! warning "Cambio importante"
    Desde este momento el listener exige usuario y contraseña, **incluso para los clientes que se conectan desde el propio Arduino UNO Q**. Por tanto, los comandos y programas de los apartados anteriores necesitan credenciales si se vuelven a ejecutar.

### Paso 3. Probar la autenticación

En una terminal:

```bash
mosquitto_sub -h localhost -u alumno -P - -t 'monlau/#' -v
```

En otra:

```bash
mosquitto_pub -h localhost -u alumno -P - -t 'monlau/aula1/prueba' -m 'Conexion correcta'
```

La opción `-P -` permite introducir la contraseña sin escribirla directamente en la línea de comandos. Si la versión instalada de los clientes no admite este uso, consulta `mosquitto_sub --help` y utiliza un archivo de configuración de cliente protegido en lugar de exponer la contraseña en el historial.

### Paso 4. Adaptar los programas Python

En los cuatro programas, añadimos **antes de `cliente.connect(...)`**:

```python
import getpass

usuario = "alumno"
clave = getpass.getpass("Clave MQTT: ")
cliente.username_pw_set(usuario, clave)
```

`getpass` solicita la contraseña sin mostrarla en pantalla. En las prácticas de aula, cada programa puede solicitarla al arrancar. En servicios automáticos se utilizará un mecanismo de gestión de secretos adecuado.

### Paso 5. Conectar desde otro ordenador

Consultamos la IP del Arduino UNO Q:

```bash
hostname -I
```

En un segundo ordenador Linux con `mosquitto-clients` instalado, sustituimos `IP_ARDUINO` por la dirección real:

```bash
mosquitto_sub -h IP_ARDUINO -p 1883 -u alumno -P - -t 'monlau/#' -v
```

Si no conecta, comprobamos que ambos dispositivos están en la misma red o que existe conectividad entre ellos, que el servicio escucha en el puerto 1883 y que no hay reglas de firewall que lo bloqueen.

!!! warning "Seguridad de la red"
    Usuario y contraseña **no cifran** el tráfico MQTT. El puerto 1883 solo debe usarse en una red de laboratorio aislada y confiable. Para producción, configura TLS (habitualmente puerto 8883), certificados y permisos por topic. No expongas el broker directamente a Internet.

## 12.10. Diagnóstico y resolución de problemas

| Síntoma | Causa probable | Comprobación o solución |
|---|---|---|
| `Connection refused` | Broker detenido o puerto incorrecto. | `systemctl status mosquitto` y `ss -lntp`. |
| `Not authorized` | Faltan credenciales o son incorrectas. | Revisar usuario y contraseña. |
| No aparecen mensajes | Topic distinto o suscriptor no conectado. | Suscribirse temporalmente a `monlau/#`. |
| Python no encuentra `paho` | Entorno virtual inactivo. | Activar `.venv` y comprobar `pip show`. |
| El ordenador remoto no conecta | Listener local, firewall o red. | Revisar IP, puerto 1883 y conectividad. |
| El servicio no arranca tras configurar | Error de configuración o listener duplicado. | Consultar el registro de Mosquitto. |

Comandos útiles:

```bash
systemctl is-active mosquitto
sudo journalctl -u mosquitto -n 50 --no-pager
sudo ss -lntp | grep 1883
```

!!! note "Consejo de diagnóstico"
    Antes de modificar un programa Python, comprueba la comunicación con `mosquitto_pub` y `mosquitto_sub`. Así podrás distinguir los errores de configuración del broker de los errores del programa.

## 12.11. Práctica integradora: estación IoT simulada

**Objetivo:** desarrollar un pequeño sistema de monitorización ambiental con un publicador y un suscriptor MQTT en Arduino UNO Q, y comprobar el acceso desde otro equipo.

**Requisitos:**

1. Instalar y verificar Mosquitto.
2. Publicar temperaturas simuladas cada cinco segundos.
3. Crear un suscriptor Python que muestre los mensajes.
4. Publicar temperatura y humedad conjuntamente en JSON.
5. Recibir las órdenes `ON` y `OFF` mediante un topic independiente.
6. Configurar un usuario MQTT y comprobar el acceso desde otro ordenador de laboratorio.
7. Documentar las pruebas y los problemas encontrados.

**Estructura de entrega:**

```text
capitulo12_mqtt/
|-- 01_publicador.py
|-- 02_suscriptor.py
|-- 03_publicador_json.py
|-- 04_control_mqtt.py
|-- capturas/
|   |-- servicio.png
|   |-- publicacion.png
|   |-- suscripcion.png
|   `-- conexion_remota.png
`-- memoria.pdf
```

### Rúbrica de evaluación

| Criterio | Puntuación |
|---|---:|
| Instalación y verificación del broker | 2 puntos |
| Publicación periódica desde Python | 2 puntos |
| Suscripción y recepción desde Python | 2 puntos |
| Telemetría estructurada con JSON | 2 puntos |
| Acceso autenticado desde otro equipo | 1 punto |
| Memoria, capturas y claridad técnica | 1 punto |
| **Total** | **10 puntos** |

!!! example "Ampliación voluntaria"
    Añade un topic `monlau/aula1/alerta` y publica un mensaje cuando la temperatura simulada supere los 28 grados. Comprueba la alerta con un suscriptor independiente.

## 12.12. Conclusiones

En este capítulo hemos aprendido a comunicar dispositivos y programas mediante MQTT. Hemos instalado Mosquitto en el Arduino UNO Q, comprobado el intercambio de mensajes desde la terminal, creado publicadores y suscriptores Python, enviado datos JSON y simulado el control remoto de un LED. También hemos habilitado conexiones autenticadas desde la red local y revisado las principales medidas de seguridad.

Estos conocimientos servirán de base para conectar sensores y actuadores reales y, posteriormente, integrar la telemetría con herramientas de automatización y monitorización.

### Referencias de consulta

- [MQTT.org — Información sobre el protocolo](https://mqtt.org/)
- [Eclipse Mosquitto — Documentación](https://mosquitto.org/documentation/)
- [Eclipse Paho MQTT Python — Documentación](https://eclipse.dev/paho/files/paho.mqtt.python/html/)
- [Python — Módulo `json`](https://docs.python.org/3/library/json.html)
