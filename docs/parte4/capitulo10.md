# Capítulo 10. Conectividad y redes en Arduino UNO Q

## 10.1. Introducción

En los capítulos anteriores hemos aprendido a utilizar Linux, programar en Python y automatizar tareas mediante `cron` y `systemd`. Ahora utilizaremos esas herramientas para configurar, analizar y diagnosticar las comunicaciones de red del **Arduino UNO Q**.

Arduino UNO Q combina un entorno Linux con un microcontrolador. En este capítulo trabajaremos **desde Linux**, utilizando la conexión de red disponible en la placa. La disponibilidad y el nombre de las interfaces dependen del firmware, los controladores y la conexión utilizada.

!!! note "Relación con el proyecto final"
    Las técnicas de este capítulo serán la base de los servidores web, las API REST, MQTT y los sistemas de monitorización que desarrollaremos en los capítulos siguientes.

### Objetivos de aprendizaje

Al finalizar el capítulo, el alumnado será capaz de:

- Identificar las interfaces de red y las direcciones IP de Arduino UNO Q.
- Explicar la función de IP, máscara/prefijo, puerta de enlace, DNS, TCP y UDP.
- Diagnosticar problemas de conectividad mediante herramientas Linux.
- Diferenciar conectividad local, salida a Internet y resolución de nombres.
- Desarrollar programas Python para comprobar conexiones TCP y consultar servicios HTTP.
- Registrar resultados de diagnóstico en archivos CSV.
- Aplicar medidas básicas de seguridad en dispositivos conectados.

### Requisitos previos

- Arduino UNO Q encendido y conectado a una red.
- Acceso a la terminal Linux mediante SSH o terminal local.
- Python 3 instalado y funcionando.
- Haber realizado los capítulos 7, 8 y 9.

!!! warning "Precaución en el aula"
    No cambies la dirección IP, las rutas o la configuración Wi-Fi de una placa a la que accedes por SSH sin disponer de una vía alternativa de acceso. Podrías perder la conexión. En este capítulo las primeras prácticas son **de observación y diagnóstico**.

## 10.2. Preparación del entorno

Conéctate por SSH al Arduino UNO Q. Comprueba el usuario y el nombre del equipo:

```bash
whoami
hostname
```

Crea el directorio de trabajo:

```bash
mkdir -p ~/practicas/capitulo10/datos
cd ~/practicas/capitulo10
```

Comprueba la versión de Python:

```bash
python3 --version
```

Comprueba si están disponibles las herramientas de diagnóstico:

```bash
command -v ip
command -v ping
command -v getent
command -v curl
command -v ss
```

Si falta alguna, consulta primero al profesor. En sistemas Debian, `ip` suele pertenecer a `iproute2`, `ping` a `iputils-ping`, `curl` a `curl` y `ss` a `iproute2`.

!!! tip "No instalar paquetes innecesarios"
    Antes de instalar software, comprueba qué herramientas existen. Una placa integrada puede tener restricciones de almacenamiento y paquetes diferentes de los de un PC convencional.

## 10.3. Fundamentos de redes aplicados a Arduino UNO Q

Una red permite que varios dispositivos intercambien información. Para que Arduino UNO Q pueda comunicarse con otros equipos necesita una interfaz activa, una dirección IP adecuada y, cuando la comunicación sale de la red local, una ruta hacia otras redes.

| Concepto | Función | Ejemplo ilustrativo |
|---|---|---|
| Dirección IPv4 | Identifica una interfaz dentro de una red | `192.168.1.49` |
| Prefijo | Delimita la parte de red de la dirección | `/24` |
| Puerta de enlace | Permite llegar a otras redes | `192.168.1.1` |
| DNS | Traduce nombres a direcciones IP | `example.com` |
| TCP | Comunicación orientada a conexión | SSH, HTTP, HTTPS |
| UDP | Comunicación sin establecimiento previo de conexión | DNS, algunas aplicaciones IoT |
| Puerto | Identifica un servicio en un equipo | SSH: `22`; HTTP: `80` |

Los valores de la tabla son ejemplos: deben sustituirse por los de cada puesto de trabajo.

### Diferencia entre IP local e IP pública

La dirección privada que recibe Arduino UNO Q en la red del aula normalmente no es una dirección pública accesible desde Internet. El router puede utilizar NAT para compartir su conexión. **Conocer la IP local no significa que el dispositivo sea accesible desde fuera del centro**.

### Modelo de comunicación

```text
Arduino UNO Q ---- Wi-Fi / red local ---- Router ---- Internet
       |                                  |
       +---- Otros equipos del aula -----+
```

## 10.4. Identificación de interfaces y direcciones

### Consultar las interfaces

```bash
ip -brief address
```

Una salida posible sería:

```text
lo        UNKNOWN    127.0.0.1/8 ::1/128
wlan0     UP         192.168.1.49/24
```

**No presupongas que tu interfaz se llama `wlan0`**: comprueba el nombre real en la salida del comando.

Para ver información detallada:

```bash
ip address show
ip link show
```

La interfaz `lo` corresponde al bucle local. Su dirección `127.0.0.1` permite que los procesos del mismo equipo se comuniquen entre sí.

### Consultar la ruta por defecto

```bash
ip route
ip route show default
```

Ejemplo:

```text
default via 192.168.1.1 dev wlan0
```

La puerta de enlace mostrada en tu placa puede ser diferente.

### Consultar los servidores DNS

```bash
cat /etc/resolv.conf
```

En algunas instalaciones el archivo puede estar gestionado automáticamente. Si existe el comando `resolvectl`, también puedes ejecutar:

```bash
resolvectl status
```

!!! note "Archivo administrado por el sistema"
    No modifiques directamente `/etc/resolv.conf` durante estas prácticas. Puede ser un enlace simbólico o un archivo generado por un servicio de red.

### Actividad 10.1. Ficha de red

Elabora una ficha con el nombre del equipo, nombre de interfaz, dirección IPv4, prefijo, puerta de enlace y servidores DNS. Adjunta capturas o transcripciones de los comandos utilizados.

## 10.5. Diagnóstico de conectividad

### Prueba 1. Pila TCP/IP local

```bash
ping -c 4 127.0.0.1
```

Esta prueba verifica el funcionamiento de la pila de red local, pero **no demuestra** que exista conectividad Wi-Fi.

### Prueba 2. Puerta de enlace

Sustituye la IP por la obtenida con `ip route show default`:

```bash
ping -c 4 192.168.1.1
```

Si la prueba falla, revisa la conexión y la configuración IP. Algunos equipos bloquean ICMP, por lo que un `ping` fallido no demuestra por sí solo que el equipo esté apagado.

### Prueba 3. Salida IP hacia Internet

```bash
ping -c 4 1.1.1.1
```

Este paso comprueba la conectividad IP hacia un destino externo que puede responder a ICMP. Su éxito no garantiza que todos los servicios de Internet estén disponibles.

### Prueba 4. Resolución DNS

```bash
getent ahostsv4 example.com
```

### Prueba 5. Conectividad HTTP/HTTPS

```bash
curl -I --max-time 10 https://example.com
```

El resultado puede variar según el servidor, el proxy y las políticas de la red. Un error de certificado o de proxy debe analizarse de forma diferenciada.

### Tabla de interpretación

| Resultado | Posible causa | Siguiente comprobación |
|---|---|---|
| Sin dirección IP | Interfaz desconectada o fallo de configuración | `ip -brief address` |
| Hay IP, pero no ruta por defecto | Falta configuración de enrutamiento | `ip route` |
| Responde la puerta de enlace, pero no una IP externa | Router, cortafuegos o salida a Internet | Revisar ruta y política de red |
| Funciona IP externa, pero falla un nombre | Problema de DNS | `getent`, `/etc/resolv.conf` |
| DNS funciona, pero falla HTTPS | Servicio, proxy, TLS o filtrado | `curl -v` con precaución |

### Actividad 10.2. Diagnóstico escalonado

Realiza las cinco pruebas, anota los resultados y redacta una conclusión razonada. Evita afirmar que existe un fallo de DNS únicamente porque `ping example.com` no recibe respuesta: el destino podría bloquear ICMP.

## 10.6. Puertos y servicios de red

En una comunicación TCP, un servidor escucha en un puerto y un cliente intenta establecer una conexión.

Ejemplos frecuentes:

| Servicio | Puerto habitual | Protocolo |
|---|---:|---|
| SSH | 22 | TCP |
| HTTP | 80 | TCP |
| HTTPS | 443 | TCP |
| MQTT | 1883 | TCP |
| MQTT con TLS | 8883 | TCP |

Para consultar los puertos TCP en escucha en Arduino UNO Q:

```bash
ss -ltn
```

Para consultar también los procesos asociados, cuando los permisos lo permitan:

```bash
sudo ss -ltnp
```

!!! warning "Seguridad"
    No abras puertos en el router, no desactives el cortafuegos y no expongas servicios de prueba a Internet. Las prácticas se realizarán dentro de la red autorizada del aula.

## 10.7. Programa 1: diagnóstico de red en Python

Crearemos `01_diagnostico_red.py`. **Todo el código fuente utiliza caracteres ASCII**, sin tildes, `ñ` ni símbolos especiales.

```bash
nano ~/practicas/capitulo10/01_diagnostico_red.py
```

```python
import platform
import shutil
import socket
import subprocess
from datetime import datetime
from pathlib import Path

BASE = Path.home() / "practicas" / "capitulo10"
DATOS = BASE / "datos"


def ejecutar(argumentos):
    try:
        proceso = subprocess.run(
            argumentos,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
        salida = proceso.stdout.strip()
        error = proceso.stderr.strip()
        return salida if proceso.returncode == 0 else f"ERROR: {error or salida}"
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"ERROR: {exc}"


def generar_informe():
    secciones = [
        "DIAGNOSTICO DE RED - ARDUINO UNO Q",
        "=" * 40,
        f"Fecha: {datetime.now().isoformat(timespec='seconds')}",
        f"Equipo: {socket.gethostname()}",
        f"Sistema: {platform.system()} {platform.release()}",
        "",
        "INTERFACES",
        ejecutar(["ip", "-brief", "address"]),
        "",
        "RUTAS",
        ejecutar(["ip", "route"]),
        "",
        "DNS",
        ejecutar(["getent", "ahostsv4", "example.com"]),
        "",
        "PUERTOS TCP EN ESCUCHA",
        ejecutar(["ss", "-ltn"]),
    ]
    return "\n".join(secciones) + "\n"


def main():
    DATOS.mkdir(parents=True, exist_ok=True)
    informe = generar_informe()
    archivo = DATOS / "informe_red.txt"
    archivo.write_text(informe, encoding="utf-8")
    print(informe)
    print(f"Informe guardado: {archivo}")


if __name__ == "__main__":
    main()
```

Comprueba sintaxis y ejecuta:

```bash
python3 -m py_compile ~/practicas/capitulo10/01_diagnostico_red.py
python3 ~/practicas/capitulo10/01_diagnostico_red.py
cat ~/practicas/capitulo10/datos/informe_red.txt
```

!!! tip "Codificacion de los programas"
    Para evitar los problemas de codificacion encontrados en el capitulo 8, los programas Python del libro emplean solamente caracteres ASCII. Los textos explicativos del libro Markdown si pueden contener tildes y otros caracteres Unicode.

### Actividad 10.3. Interpretación del informe

Localiza en el informe la interfaz utilizada, la ruta por defecto, el resultado de DNS y los puertos en escucha. Explica qué información no puede deducirse únicamente de ese informe.

## 10.8. Programa 2: comprobación de conexiones TCP

La herramienta `ping` utiliza ICMP. Para comprobar un servicio TCP resulta más apropiado intentar abrir una conexión al puerto correspondiente.

Crea el archivo:

```bash
nano ~/practicas/capitulo10/02_comprobar_tcp.py
```

```python
import socket
from datetime import datetime

PRUEBAS = [
    ("example.com", 443),
    ("example.com", 80),
]
TIEMPO_ESPERA = 4


def comprobar(host, puerto):
    try:
        with socket.create_connection((host, puerto), timeout=TIEMPO_ESPERA):
            return "OK", "Conexion establecida"
    except (OSError, socket.timeout) as exc:
        return "ERROR", str(exc)


def main():
    print("COMPROBACION DE SERVICIOS TCP")
    print(f"Fecha: {datetime.now().isoformat(timespec='seconds')}")
    for host, puerto in PRUEBAS:
        estado, detalle = comprobar(host, puerto)
        print(f"{host}:{puerto} - {estado} - {detalle}")


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
python3 -m py_compile ~/practicas/capitulo10/02_comprobar_tcp.py
python3 ~/practicas/capitulo10/02_comprobar_tcp.py
```

!!! note "Interpretacion correcta"
    Una conexion TCP correcta demuestra que se ha establecido una conexion con el puerto, pero no que la aplicacion haya respondido correctamente a una peticion HTTP o que su contenido sea valido.

### Actividad 10.4. Servicios autorizados

Modifica `PRUEBAS` para incluir la dirección IP de un servidor del aula y un puerto TCP cuyo uso haya autorizado el profesor. Compara los resultados y explica la diferencia entre `connection refused`, un tiempo de espera agotado y un error de resolución DNS.

## 10.9. Programa 3: consulta HTTP y registro CSV

El siguiente programa realizará una solicitud HTTP GET a una dirección pública de prueba y registrará la fecha, el estado y la duración de la consulta. Utilizaremos exclusivamente la biblioteca estándar de Python.

```bash
nano ~/practicas/capitulo10/03_monitor_http.py
```

```python
import csv
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

URL = "https://www.wikipedia.org/"
DESTINO = Path.home() / "practicas" / "capitulo10" / "datos" / "http.csv"


def consultar():
    inicio = time.monotonic()
    codigo = "SIN_RESPUESTA"
    estado = "ERROR"
    detalle = ""

    try:
        peticion = urllib.request.Request(
            URL,
            headers={"User-Agent": "ArduinoUNOQ-Lab/1.0"},
        )
        with urllib.request.urlopen(peticion, timeout=10) as respuesta:
            codigo = str(respuesta.status)
            estado = "OK" if 200 <= respuesta.status < 400 else "ERROR"
    except urllib.error.HTTPError as exc:
        codigo = str(exc.code)
        detalle = str(exc.reason)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        detalle = str(exc)

    duracion_ms = round((time.monotonic() - inicio) * 1000, 2)
    return {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "url": URL,
        "estado": estado,
        "codigo": codigo,
        "duracion_ms": duracion_ms,
        "detalle": detalle,
    }


def main():
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    existe = DESTINO.exists() and DESTINO.stat().st_size > 0
    resultado = consultar()

    with DESTINO.open("a", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=resultado.keys())
        if not existe:
            escritor.writeheader()
        escritor.writerow(resultado)

    print(f"Estado: {resultado['estado']}")
    print(f"Codigo HTTP: {resultado['codigo']}")
    print(f"Duracion: {resultado['duracion_ms']} ms")
    print(f"Registro: {DESTINO}")


if __name__ == "__main__":
    main()
```

Comprueba y ejecuta:

```bash
python3 -m py_compile ~/practicas/capitulo10/03_monitor_http.py
python3 ~/practicas/capitulo10/03_monitor_http.py
cat ~/practicas/capitulo10/datos/http.csv
```

Ejecuta el programa varias veces y observa cómo se añaden filas al archivo CSV.

!!! warning "Interpretacion de errores HTTPS"
    Si aparece un error de certificado TLS, no lo soluciones desactivando la validacion de certificados. Comprueba la fecha del equipo, los certificados de confianza y la configuracion de red.

## 10.10. Automatización de las comprobaciones

En el capítulo 9 configuramos tareas con `cron`. Podemos reutilizar esos conocimientos para ejecutar el monitor HTTP cada 10 minutos.

Primero verifica que el programa funciona manualmente. Después abre:

```bash
crontab -e
```

**Conserva las tareas que ya existan** y añade esta línea:

```cron
*/10 * * * * /usr/bin/python3 /home/arduino/practicas/capitulo10/03_monitor_http.py >> /home/arduino/practicas/capitulo10/datos/cron_http.log 2>&1
```

Guarda y comprueba:

```bash
crontab -l
```

Transcurrido el siguiente intervalo de 10 minutos:

```bash
tail -n 10 ~/practicas/capitulo10/datos/http.csv
cat ~/practicas/capitulo10/datos/cron_http.log
```

!!! note "Comprobacion de cron"
    Que el comando aparezca en `crontab -l` confirma que la tarea esta programada, pero no que se haya ejecutado correctamente. Para verificarlo, consulta el CSV, el archivo de errores y, si es necesario, el registro del servicio cron.

## 10.11. Seguridad básica en redes

Un dispositivo Linux conectado a la red puede ejecutar servicios accesibles desde otros equipos. Antes de publicar una aplicación conviene aplicar estas recomendaciones:

1. Utilizar contraseñas robustas y, cuando proceda, autenticación SSH mediante claves.
2. Mantener el sistema y las dependencias actualizados siguiendo el procedimiento autorizado por el centro.
3. Comprobar qué puertos están escuchando con `ss -ltn`.
4. Evitar ejecutar programas de prácticas como `root` cuando no sea necesario.
5. No incluir contraseñas, tokens o claves privadas en archivos publicados en GitHub.
6. Limitar los servicios de laboratorio a la red autorizada.
7. Utilizar HTTPS y validar certificados en las comunicaciones externas.
8. Documentar los cambios de configuración y conservar copias de seguridad.

### Actividad 10.5. Auditoría básica

Obtén una lista de puertos TCP en escucha. Investiga qué servicio corresponde a cada puerto que puedas identificar y redacta tres recomendaciones de seguridad para la placa. No detengas servicios del sistema sin autorización.

## 10.12. Práctica integradora evaluable: nodo de diagnóstico de red

### Situación profesional

El departamento de informática necesita un dispositivo capaz de verificar periódicamente la conectividad del aula y conservar evidencias para investigar interrupciones de servicio. El alumnado deberá configurar Arduino UNO Q como **nodo de diagnóstico**.

### Requisitos

- **R1.** Identificar y documentar la configuración de red real de la placa.
- **R2.** Realizar un diagnóstico escalonado de conectividad y DNS.
- **R3.** Ejecutar y explicar `01_diagnostico_red.py`.
- **R4.** Adaptar `02_comprobar_tcp.py` para comprobar un servicio autorizado.
- **R5.** Ejecutar `03_monitor_http.py` y verificar el registro CSV.
- **R6.** Programar una ejecución periódica con cron, conservando las tareas anteriores.
- **R7.** Documentar al menos una incidencia posible y su procedimiento de diagnóstico.
- **R8.** Presentar evidencias y conclusiones en un informe técnico.

### Entrega

La entrega individual o por parejas, según indique el profesor, incluirá:

```text
capitulo10/
├── 01_diagnostico_red.py
├── 02_comprobar_tcp.py
├── 03_monitor_http.py
├── datos/
│   ├── informe_red.txt
│   ├── http.csv
│   └── cron_http.log
└── informe_practica.pdf
```

El archivo PDF se elaborará fuera de la placa y deberá contener la ficha de red, pruebas, interpretación de resultados, capturas relevantes y conclusiones. El registro `cron_http.log` puede no existir hasta que cron haya ejecutado la tarea; si el programa no escribe salida, se deberá documentar esa circunstancia.

### Rúbrica de evaluación (10 puntos)

| Criterio | Puntuación máxima |
|---|---:|
| Identificación correcta de interfaces, IP, ruta y DNS | 1,5 |
| Diagnóstico escalonado e interpretación de resultados | 1,5 |
| Programa de informe de red operativo y explicado | 1,5 |
| Comprobación TCP de un servicio autorizado | 1,0 |
| Monitor HTTP y CSV correctos | 1,5 |
| Automatización con cron y evidencias de ejecución | 1,0 |
| Seguridad y procedimiento de resolución de incidencias | 1,0 |
| Calidad del informe y presentación de evidencias | 1,0 |
| **Total** | **10,0** |

!!! example "Criterio de validacion"
    No basta con presentar una captura de un comando. El alumno debe explicar que demuestra la prueba, que no demuestra y que haria si el resultado fuera distinto del esperado.

## 10.13. Resolución de problemas habituales

| Síntoma | Comprobación recomendada |
|---|---|
| `Network is unreachable` | Revisar `ip address` y `ip route` |
| `Temporary failure in name resolution` | Revisar DNS con `getent` y `/etc/resolv.conf` |
| `Connection refused` | Comprobar servicio y puerto del destino |
| `Connection timed out` | Revisar conectividad, filtrado y disponibilidad |
| `Permission denied` al guardar CSV | Comprobar propietario y permisos de `datos/` |
| `SyntaxError: Non-UTF-8 code` | Revisar codificación; mantener el código Python en ASCII |
| Cron no escribe resultados | Revisar rutas absolutas, `crontab -l` y registros |
| HTTPS falla por certificado | Revisar fecha, CA y configuración TLS sin desactivar verificación |

### Comandos de consulta rápida

```bash
ip -brief address
ip route
getent ahostsv4 example.com
ss -ltn
crontab -l
```

## 10.14. Resumen del capítulo

En este capítulo hemos utilizado Arduino UNO Q como un equipo Linux conectado a una red. Hemos identificado interfaces, direcciones, rutas y DNS; diagnosticado la conectividad; analizado puertos TCP; creado tres programas Python y automatizado la recogida de información con cron.

El siguiente capítulo, **Capítulo 11. Servidores web y API REST**, utilizará estos conocimientos para publicar un servicio HTTP accesible desde otro equipo de la red local y desarrollar una API sencilla.

## 10.15. Referencias y recursos

- Documentación oficial de Python: <https://docs.python.org/3/library/socket.html>
- Biblioteca `urllib.request`: <https://docs.python.org/3/library/urllib.request.html>
- Biblioteca `csv`: <https://docs.python.org/3/library/csv.html>
- Manual de `ip`: `man ip`
- Manual de `ss`: `man ss`
- Manual de `crontab`: `man 5 crontab`

!!! tip "Para el profesorado"
    La correspondencia de este capitulo con los resultados de aprendizaje del modulo de Hardware debe concretarse en la programacion del centro. Las actividades de conectividad y monitorizacion complementan, pero no sustituyen, las practicas de montaje, mantenimiento y recuperacion de equipos informaticos.
