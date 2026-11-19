# Capitulo 11. Servidores web y API REST

!!! info "Parte IV - Conectividad y servicios IoT"
    En este capitulo utilizaremos el entorno Linux del Arduino UNO Q para publicar un servicio HTTP accesible desde otros equipos de la red local. Partimos de los conocimientos de redes del capitulo 10 y de automatizacion con `systemd` del capitulo 9.

## 11.1. Objetivos y resultados de aprendizaje

Al finalizar el capitulo, el alumnado sera capaz de:

- Explicar el modelo cliente-servidor y distinguir HTTP de HTTPS.
- Identificar una direccion IP, un puerto TCP y una URL.
- Interpretar los metodos HTTP `GET` y `POST` y los codigos de estado habituales.
- Crear un servidor web basico con Python 3 y su biblioteca estandar.
- Implementar una API REST sencilla que intercambie informacion JSON.
- Comprobar un servicio desde Linux, Windows y un navegador.
- Registrar peticiones, tratar errores y aplicar medidas basicas de seguridad.
- Ejecutar un servicio HTTP mediante `systemd` de usuario.

**Relacion curricular orientativa:** instalacion y configuracion de software, diagnostico de servicios y redes, y monitorizacion de un equipo Linux. La correspondencia exacta con los criterios de evaluacion del modulo 0371 debe concretarse en la programacion del centro.

**Duracion orientativa:** 4-6 horas, adaptable a la programacion docente.

**Requisitos previos:** capitulos 7-10 completados; Arduino UNO Q conectado a la misma red que el ordenador de pruebas; acceso SSH y Python 3 operativo.

## 11.2. Fundamentos: cliente, servidor y HTTP

En una comunicacion web, el **cliente** inicia una peticion y el **servidor** responde. En nuestras practicas, el navegador del ordenador sera el cliente y el Arduino UNO Q sera el servidor.

Una URL de ejemplo es:

```text
http://192.168.1.49:8080/
```

- `http`: protocolo de aplicacion.
- `192.168.1.49`: direccion IPv4 del servidor (solo es un ejemplo).
- `8080`: puerto TCP de escucha.
- `/`: ruta solicitada.

El puerto `8080` es una eleccion didactica para evitar ejecutar el servidor con privilegios de administrador. No hay que confundir el puerto HTTP con el puerto SSH (habitualmente 22).

| Metodo | Finalidad habitual | Ejemplo |
|---|---|---|
| `GET` | Consultar un recurso | `GET /api/estado` |
| `POST` | Enviar datos o crear un registro | `POST /api/lecturas` |

| Codigo | Significado |
|---|---|
| `200` | Peticion correcta |
| `201` | Recurso creado |
| `400` | Peticion incorrecta |
| `404` | Recurso inexistente |
| `405` | Metodo no permitido |
| `413` | Cuerpo de peticion demasiado grande |
| `500` | Error interno del servidor |

!!! note "HTTP y HTTPS"
    HTTP transmite los datos sin cifrado. En este capitulo utilizaremos HTTP **solo en una red local de laboratorio de confianza**. No se debe publicar este servidor directamente en Internet ni enviar contrasenas o datos sensibles. HTTPS requiere una configuracion adicional de TLS o un proxy inverso.

## 11.3. Preparacion del entorno

En el Arduino UNO Q, conectado por SSH:

```bash
mkdir -p ~/practicas/capitulo11/datos
cd ~/practicas/capitulo11
python3 --version
ip -brief address
ip route
```

Anota la direccion IPv4 de la interfaz conectada a tu red. En las instrucciones siguientes se utiliza `IP_DEL_ARDUINO` como marcador: **sustituyelo por la IP real**, sin escribir literalmente ese texto.

Comprueba que el puerto elegido no esta ocupado:

```bash
ss -ltn | grep ':8080 ' || echo 'Puerto 8080 libre'
```

Si aparece una aplicacion escuchando en el puerto 8080, detente y averigua cual es antes de continuar. Puedes elegir otro puerto libre, modificandolo en todos los ejemplos.

!!! warning "Codificacion de los programas"
    Todos los programas Python de este capitulo estan escritos con **caracteres ASCII**, sin acentos, eñes, simbolos de grado ni caracteres especiales. Los archivos JSON se generan explicitamente en UTF-8. Esta precaucion evita los problemas de codificacion observados en el capitulo 8.

## 11.4. Programa 1: servidor web minimo

Crea el archivo:

```bash
nano ~/practicas/capitulo11/01_servidor_web.py
```

Introduce el codigo completo:

```python
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "0.0.0.0"
PORT = 8080


class ServidorWeb(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404, "Ruta no encontrada")
            return

        contenido = (
            "<!doctype html><html lang='es'><head>"
            "<meta charset='utf-8'><title>Arduino UNO Q</title>"
            "</head><body><h1>Servidor Arduino UNO Q</h1>"
            "<p>Servidor HTTP funcionando.</p></body></html>"
        ).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(contenido)))
        self.end_headers()
        self.wfile.write(contenido)


def main():
    servidor = ThreadingHTTPServer((HOST, PORT), ServidorWeb)
    print(f"Servidor disponible en el puerto {PORT}", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("Servidor detenido")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
```

Verifica la sintaxis y ejecuta:

```bash
python3 -m py_compile 01_servidor_web.py
python3 -u 01_servidor_web.py
```

Desde **otra terminal SSH**, comprueba el servicio:

```bash
curl -i http://127.0.0.1:8080/
curl -i http://127.0.0.1:8080/no-existe
```

El primer comando debe devolver `HTTP/1.0 200 OK` y una pagina HTML. El segundo debe devolver `404`.

Desde Chrome en Windows, abre:

```text
http://IP_DEL_ARDUINO:8080/
```

!!! tip "Por que se utiliza 0.0.0.0"
    `0.0.0.0` permite escuchar en todas las interfaces IPv4 del dispositivo. Si se utilizara `127.0.0.1`, solo se podria acceder desde el propio Arduino. Esta configuracion debe utilizarse exclusivamente en una red de practicas controlada.

Deten el servidor con `Ctrl + C` antes de iniciar el siguiente programa, porque ambos utilizan el puerto 8080.

### Actividad 11.1. Comprobacion del servicio

1. Identifica la IP real del Arduino UNO Q.
2. Abre la pagina desde el navegador del ordenador.
3. Comprueba una ruta inexistente y anota el codigo de estado.
4. Ejecuta `ss -ltn | grep ':8080 '` mientras el servidor esta activo.
5. Explica la diferencia entre `127.0.0.1` y la direccion IP de la red local.

**Evidencias:** captura del navegador, salida de `curl` y breve explicacion.

## 11.5. JSON y diseno de una API REST

Una **API** permite que otros programas consulten o envien datos sin depender de una interfaz grafica. En una API REST sencilla, cada ruta identifica un recurso y los metodos HTTP expresan la operacion solicitada.

Utilizaremos JSON para intercambiar informacion:

```json
{
  "equipo": "UNO-Q-JOSE",
  "estado": "OK",
  "temperatura_c": 24.5
}
```

En este ejemplo, `temperatura_c` es una **lectura simulada**: todavia no estamos conectando un sensor fisico. En el capitulo 12 conectaremos estos conceptos con la mensajeria IoT.

La API de la practica tendra estas rutas:

| Metodo | Ruta | Funcion |
|---|---|---|
| `GET` | `/` | Pagina informativa |
| `GET` | `/api/estado` | Estado del sistema |
| `GET` | `/api/lecturas` | Consultar lecturas almacenadas |
| `POST` | `/api/lecturas` | Registrar una lectura simulada |

## 11.6. Programa 2: API REST con Python

No instalaremos Flask ni otras dependencias: utilizaremos la biblioteca estandar de Python, lo que facilita reproducir la practica en Debian.

Crea el archivo:

```bash
nano ~/practicas/capitulo11/02_api_rest.py
```

Copia el programa:

```python
import json
import os
import platform
import socket
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = "0.0.0.0"
PORT = 8080
BASE = Path(__file__).resolve().parent
ARCHIVO = BASE / "datos" / "lecturas.jsonl"
MAX_BODY = 4096
LOCK = threading.Lock()


def respuesta_json(handler, codigo, objeto):
    cuerpo = json.dumps(objeto, ensure_ascii=True).encode("utf-8")
    handler.send_response(codigo)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(cuerpo)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(cuerpo)


def leer_lecturas():
    if not ARCHIVO.exists():
        return []
    with LOCK:
        with ARCHIVO.open("r", encoding="utf-8") as archivo:
            return [json.loads(linea) for linea in archivo if linea.strip()]


class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            respuesta_json(self, 200, {
                "servicio": "API Arduino UNO Q",
                "rutas": ["/api/estado", "/api/lecturas"]
            })
        elif self.path == "/api/estado":
            respuesta_json(self, 200, {
                "equipo": socket.gethostname(),
                "sistema": platform.system(),
                "arquitectura": platform.machine(),
                "pid": os.getpid(),
                "fecha_utc": datetime.now(timezone.utc).isoformat(),
                "estado": "OK"
            })
        elif self.path == "/api/lecturas":
            respuesta_json(self, 200, {"lecturas": leer_lecturas()})
        else:
            respuesta_json(self, 404, {"error": "Ruta no encontrada"})

    def do_POST(self):
        if self.path != "/api/lecturas":
            respuesta_json(self, 404, {"error": "Ruta no encontrada"})
            return

        tipo = self.headers.get("Content-Type", "").split(";")[0].strip()
        if tipo != "application/json":
            respuesta_json(self, 400, {"error": "Content-Type incorrecto"})
            return

        try:
            longitud = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            respuesta_json(self, 400, {"error": "Longitud incorrecta"})
            return

        if longitud <= 0:
            respuesta_json(self, 400, {"error": "Cuerpo vacio"})
            return
        if longitud > MAX_BODY:
            respuesta_json(self, 413, {"error": "Cuerpo demasiado grande"})
            return

        try:
            datos = json.loads(self.rfile.read(longitud).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            respuesta_json(self, 400, {"error": "JSON no valido"})
            return

        if not isinstance(datos, dict):
            respuesta_json(self, 400, {"error": "Se espera un objeto JSON"})
            return

        valor = datos.get("temperatura_c")
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            respuesta_json(self, 400, {"error": "temperatura_c debe ser numerica"})
            return
        if not -40 <= valor <= 125:
            respuesta_json(self, 400, {"error": "Valor fuera de rango"})
            return

        lectura = {
            "fecha_utc": datetime.now(timezone.utc).isoformat(),
            "temperatura_c": valor,
            "origen": "simulado"
        }
        ARCHIVO.parent.mkdir(parents=True, exist_ok=True)
        with LOCK:
            with ARCHIVO.open("a", encoding="utf-8") as archivo:
                archivo.write(json.dumps(lectura, ensure_ascii=True) + "\n")

        respuesta_json(self, 201, {"resultado": "creado", "lectura": lectura})


def main():
    servidor = ThreadingHTTPServer((HOST, PORT), APIHandler)
    print(f"API REST activa en puerto {PORT}", flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("API detenida")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
```

!!! note "Alcance de la implementacion"
    Este servidor es **didactico**. No incorpora autenticacion, autorizacion, TLS, limitacion de peticiones ni una base de datos transaccional. No debe utilizarse en produccion ni exponerse a redes no confiables. El archivo JSONL crece con cada lectura y es adecuado solo para volúmenes pequenos de laboratorio.

Comprueba y ejecuta:

```bash
cd ~/practicas/capitulo11
python3 -m py_compile 02_api_rest.py
python3 -u 02_api_rest.py
```

### Actividad 11.2. Consultar la API

En una segunda terminal SSH:

```bash
curl -i http://127.0.0.1:8080/
curl -i http://127.0.0.1:8080/api/estado
curl -i http://127.0.0.1:8080/api/lecturas
curl -i http://127.0.0.1:8080/api/no-existe
```

Comprueba los codigos `200` y `404`. Abre tambien `http://IP_DEL_ARDUINO:8080/api/estado` desde el navegador del ordenador.

### Actividad 11.3. Enviar datos mediante POST

En el Arduino:

```bash
curl -i -X POST http://127.0.0.1:8080/api/lecturas \
  -H 'Content-Type: application/json' \
  -d '{"temperatura_c":24.5}'
```

La respuesta debe incluir `201 Created` y el registro guardado.

Consulta los datos:

```bash
curl -s http://127.0.0.1:8080/api/lecturas
cat ~/practicas/capitulo11/datos/lecturas.jsonl
```

Prueba un dato incorrecto:

```bash
curl -i -X POST http://127.0.0.1:8080/api/lecturas \
  -H 'Content-Type: application/json' \
  -d '{"temperatura_c":"alta"}'
```

Debe devolver `400`.

!!! tip "Prueba desde Windows"
    En PowerShell, utiliza `curl.exe` para invocar el programa real `curl` y evitar diferencias entre versiones de PowerShell. Sustituye `IP_DEL_ARDUINO` por la IP real:

    ```powershell
    curl.exe -i http://IP_DEL_ARDUINO:8080/api/estado
    curl.exe -i -X POST http://IP_DEL_ARDUINO:8080/api/lecturas -H "Content-Type: application/json" -d '{"temperatura_c":26}'
    ```

## 11.7. Programa 3: cliente Python de la API

En este apartado, Arduino UNO Q actuara como **cliente** de su propio servicio, aunque el mismo codigo puede adaptarse a otro equipo de la red.

Crea `03_cliente_api.py`:

```python
import json
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8080/api/estado"


def main():
    try:
        with urllib.request.urlopen(URL, timeout=5) as respuesta:
            datos = json.load(respuesta)
            print(f"HTTP: {respuesta.status}")
            print(f"Equipo: {datos['equipo']}")
            print(f"Sistema: {datos['sistema']}")
            print(f"Estado: {datos['estado']}")
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as error:
        print(f"Error de consulta: {error}")


if __name__ == "__main__":
    main()
```

Con `02_api_rest.py` en ejecucion, abre otra terminal:

```bash
cd ~/practicas/capitulo11
python3 -m py_compile 03_cliente_api.py
python3 03_cliente_api.py
```

### Actividad 11.4. Cliente y servidor

1. Ejecuta la API y despues el cliente.
2. Deten la API y repite la prueba.
3. Explica por que el cliente muestra un error cuando no existe un servidor escuchando.
4. Identifica en el codigo el tiempo de espera y el tratamiento de excepciones.

## 11.8. Ejecutar la API como servicio systemd

El capitulo 9 introdujo los servicios de usuario. Reutilizaremos esa tecnica para mantener la API activa sin una terminal abierta.

**Primero**, deten la ejecucion manual de `02_api_rest.py` con `Ctrl + C`. Verifica que el puerto queda libre:

```bash
ss -ltn | grep ':8080 ' || echo 'Puerto libre'
```

Crea el directorio de unidades:

```bash
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/api-uno-q.service
```

Contenido del archivo:

```ini
[Unit]
Description=API REST de laboratorio Arduino UNO Q

[Service]
Type=simple
WorkingDirectory=/home/arduino/practicas/capitulo11
ExecStart=/usr/bin/python3 -u /home/arduino/practicas/capitulo11/02_api_rest.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

Recarga la configuracion y activa el servicio:

```bash
systemctl --user daemon-reload
systemctl --user enable --now api-uno-q.service
systemctl --user status api-uno-q.service --no-pager
```

Comprueba la respuesta:

```bash
curl -i http://127.0.0.1:8080/api/estado
journalctl --user -u api-uno-q.service -n 20 --no-pager
```

Para detenerlo o reiniciarlo:

```bash
systemctl --user stop api-uno-q.service
systemctl --user start api-uno-q.service
systemctl --user restart api-uno-q.service
```

!!! warning "Sesiones SSH y systemd de usuario"
    En el capitulo 9 aparecio el error `XDG_RUNTIME_DIR not defined`. Si vuelve a ocurrir, comprueba `systemctl status user@$(id -u).service` y la configuracion de la sesion SSH. No ejecutes indiscriminadamente los servicios con `sudo`. Para permitir que el gestor de usuario continue tras cerrar SSH, puede habilitarse `sudo loginctl enable-linger arduino`, si la politica del equipo lo permite.

### Actividad 11.5. Persistencia del servicio

1. Comprueba `active (running)`.
2. Cierra la conexion SSH y vuelve a entrar.
3. Consulta la API y el estado del servicio.
4. Reinicia el Arduino **solo con autorizacion del profesor** y comprueba el arranque automatico.
5. Recoge los registros del servicio y explica las ventajas respecto a ejecutar Python manualmente.

## 11.9. Seguridad, diagnostico y problemas frecuentes

| Sintoma | Posible causa | Comprobacion |
|---|---|---|
| `Address already in use` | Puerto 8080 ocupado | `ss -ltn | grep ':8080 '` |
| `Connection refused` | Servidor detenido o puerto incorrecto | `systemctl --user status api-uno-q.service` |
| Funciona en `127.0.0.1`, no desde Windows | IP incorrecta, aislamiento Wi-Fi o cortafuegos | `ip -brief address`, `ss -ltn` |
| `404` | Ruta inexistente | Revisar URL |
| `400` | JSON invalido o valor incorrecto | Revisar cuerpo y cabecera |
| `413` | Peticion demasiado grande | Reducir cuerpo JSON |
| Servicio reinicia continuamente | Error de Python o puerto ocupado | `journalctl --user -u api-uno-q.service -n 30` |
| `systemctl --user` no conecta | Sesion de usuario incompleta | Revisar apartado 11.8 y capitulo 9 |

Medidas basicas de seguridad:

- Trabajar en una red local de laboratorio controlada.
- No abrir el puerto 8080 en el router hacia Internet.
- No enviar contrasenas ni datos personales por HTTP.
- No ejecutar el servidor como `root`.
- Validar los datos recibidos y limitar su tamano.
- Desactivar el servicio al terminar la practica si no se necesita.
- Utilizar HTTPS y autenticacion antes de plantear un despliegue real.

Para detener y deshabilitar el servicio:

```bash
systemctl --user disable --now api-uno-q.service
```

## 11.10. Practica integradora evaluable

### Enunciado: nodo de consulta y registro HTTP

**Situacion profesional:** el departamento de sistemas necesita un servicio local que permita consultar el estado de un nodo Linux y registrar lecturas simuladas para futuras practicas IoT.

**Trabajo:** individual o por parejas, segun indique el profesor.

**Requisitos obligatorios:**

1. Identificar y documentar la IP de Arduino UNO Q y el puerto del servicio.
2. Ejecutar un servidor HTTP y demostrar el acceso desde otro equipo.
3. Publicar una API con `GET /api/estado` y `GET /api/lecturas`.
4. Registrar al menos tres lecturas mediante `POST /api/lecturas`.
5. Rechazar al menos un dato incorrecto con codigo `400`.
6. Guardar los datos en `datos/lecturas.jsonl`.
7. Configurar la API como servicio `systemd` de usuario.
8. Comprobar el estado del servicio y consultar sus registros.
9. Explicar al menos tres riesgos de seguridad y sus medidas preventivas.
10. Entregar un informe con comandos, resultados y capturas.

**Entregables:** archivos `.py`, archivo `.service`, registros JSONL de ejemplo, capturas de `curl`, salida de `systemctl`, y memoria breve en PDF o Markdown segun indique el profesor. No incluir contrasenas, tokens ni informacion privada.

### Rubrica de evaluacion (10 puntos)

| Criterio | Puntuacion |
|---|---:|
| Identificacion de IP, puerto y pruebas HTTP | 1,0 |
| Servidor HTTP accesible desde la red local | 1,0 |
| Rutas `GET` y respuestas JSON correctas | 2,0 |
| `POST`, validacion y codigos de error | 2,0 |
| Persistencia de datos en JSONL | 1,0 |
| Servicio `systemd` y comprobacion de registros | 1,5 |
| Seguridad, documentacion y presentacion | 1,5 |
| **Total** | **10,0** |

**Criterio de superacion orientativo:** al menos 5 puntos sobre 10 y demostracion funcional de la consulta de estado. La calificacion final debe seguir los criterios oficiales de la programacion del modulo.

## 11.11. Cuestionario de autoevaluacion

1. Que diferencia existe entre un cliente HTTP y un servidor HTTP?
2. Que representa el numero 8080 en una URL?
3. Por que `127.0.0.1` no sirve para acceder desde otro ordenador?
4. Que metodo HTTP utilizamos para consultar un recurso?
5. Que metodo utilizamos para enviar una lectura al servidor?
6. Que diferencia existe entre los codigos `200`, `201`, `400` y `404`?
7. Por que conviene validar los valores recibidos por una API?
8. Que ventaja ofrece `systemd` frente a ejecutar un script en una terminal SSH?
9. Que riesgos existen al publicar un servidor HTTP sin autenticacion?
10. Que diferencias hay entre JSON y una pagina HTML?

## 11.12. Resumen y continuidad

En este capitulo hemos convertido Arduino UNO Q en un servidor HTTP, desarrollado una API REST con Python, intercambiado datos JSON y automatizado su ejecucion con `systemd`. Tambien hemos comprobado respuestas, errores y medidas basicas de seguridad.

En el **capitulo 12, MQTT y comunicaciones IoT**, estudiaremos un modelo diferente: publicacion y suscripcion de mensajes mediante un broker. Compararemos las peticiones HTTP con el intercambio de eventos MQTT y prepararemos la integracion con sensores y sistemas de monitorizacion.

## 11.13. Referencias

- Python Software Foundation. Documentacion de `http.server`: <https://docs.python.org/3/library/http.server.html>.
- Python Software Foundation. Documentacion de `urllib.request`: <https://docs.python.org/3/library/urllib.request.html>.
- MDN Web Docs. HTTP: <https://developer.mozilla.org/es/docs/Web/HTTP>.
- IETF. HTTP Semantics, RFC 9110: <https://www.rfc-editor.org/rfc/rfc9110>.
- Freedesktop.org. `systemd.service`: <https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html>.
