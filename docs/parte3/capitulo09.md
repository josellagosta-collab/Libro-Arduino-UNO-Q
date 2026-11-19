# Capítulo 9. Automatización y servicios en Arduino UNO Q

## Objetivos de aprendizaje

Al finalizar este capítulo, el alumnado será capaz de:

- Explicar las diferencias entre un script, un proceso, un servicio y una tarea programada.
- Ejecutar programas Python desde la terminal de Debian Linux.
- Crear scripts Bash sencillos para automatizar tareas repetitivas.
- Utilizar `subprocess`, `pathlib` y `logging` para desarrollar herramientas de administración.
- Programar tareas periódicas mediante `cron` y conocer sus limitaciones.
- Crear y administrar un servicio de usuario con `systemd`.
- Consultar el estado y los registros de un servicio mediante `systemctl` y `journalctl`.
- Detectar y corregir errores habituales de rutas, permisos y entornos Python.
- Desarrollar un monitor periódico de Arduino UNO Q que guarde resultados y pueda ejecutarse como servicio.
- Documentar y verificar una solución de automatización con criterios profesionales.

## 1. Introducción

En el capítulo 7 aprendimos a administrar Debian Linux desde la terminal de Arduino UNO Q. En el capítulo 8 desarrollamos programas Python para gestionar archivos, ejecutar comandos y generar informes de diagnóstico.

En este capítulo daremos un paso más: **conseguiremos que esos programas se ejecuten automáticamente**, sin tener que iniciar cada uno de ellos manualmente.

Esta capacidad es fundamental en administración de sistemas. Un dispositivo Linux puede recopilar datos, comprobar servicios, registrar incidencias o ejecutar tareas de mantenimiento mientras está funcionando.

En Arduino UNO Q, estas tareas se ejecutan en el entorno **Debian Linux del procesador Qualcomm**, de forma independiente de los programas que controla el microcontrolador STM32.

!!! info "Relación con los capítulos anteriores"

    Aprovecharemos Python, Bash, SSH, archivos de texto y comandos de diagnóstico que ya hemos utilizado. En este capítulo no es necesario conectar sensores ni modificar el programa del STM32.

### 1.1. Aplicaciones profesionales

- Generar un informe de estado cada cierto tiempo.
- Registrar si un dispositivo de la red responde.
- Guardar el uso de memoria y almacenamiento para analizar tendencias.
- Iniciar automáticamente una aplicación al arrancar el sistema.
- Consultar errores de una aplicación que se ejecuta en segundo plano.
- Preparar servicios que posteriormente enviarán datos mediante MQTT o HTTP.

## 2. Preparación del entorno

### 2.1. Material necesario

- Arduino UNO Q con Debian Linux operativo.
- Ordenador Windows 11 con acceso SSH o PuTTY.
- Usuario `arduino` con acceso a su directorio personal.
- Python 3 y los comandos Linux utilizados en los capítulos 7 y 8.
- Conexión a la placa mediante red local o terminal disponible.

Accedemos por SSH utilizando la IP real de nuestra placa:

```powershell
ssh arduino@192.168.1.49
```

La dirección anterior es un ejemplo del entorno de prácticas: si ha cambiado, debemos sustituirla.

### 2.2. Comprobar el sistema

```bash
whoami
hostname
python3 --version
systemctl --version
```

Creamos el directorio de trabajo:

```bash
mkdir -p ~/practicas/capitulo09
cd ~/practicas/capitulo09
pwd
```

En este capítulo utilizaremos la ruta:

```text
/home/arduino/practicas/capitulo09/
```

!!! warning "Seguridad y permisos"

    Trabajaremos dentro del directorio personal del usuario `arduino`. No ejecutaremos los scripts Python como `root` ni modificaremos servicios críticos del sistema. Antes de instalar paquetes o cambiar configuraciones, comprobaremos si realmente es necesario.

## 3. Conceptos básicos: procesos, tareas y servicios

Un **proceso** es un programa que se está ejecutando. Un **script** es un archivo que contiene instrucciones que podemos ejecutar cuando queramos. Una **tarea programada** se inicia en momentos definidos. Un **servicio** es un programa administrado por un gestor de servicios, que puede arrancar, detenerse y registrar su actividad.

| Concepto | Ejemplo | Herramienta |
|---|---|---|
| Script | Generar un informe | `python3` |
| Proceso | Python en ejecución | `ps`, `pgrep` |
| Tarea periódica | Ejecutar un informe cada 5 minutos | `cron` |
| Servicio | Monitor continuo en segundo plano | `systemd` |
| Registro | Consultar incidencias del monitor | `journalctl` |

### 3.1. Consultar procesos

```bash
ps -ef | grep '[p]ython'
```

Para identificar el proceso que ejecuta un programa concreto:

```bash
pgrep -af monitor_servicio.py
```

Si no aparece ninguna línea, es posible que el programa no se esté ejecutando.

## 4. Programa 1. Automatizar un diagnóstico con Bash

Bash permite encadenar comandos Linux sin repetirlos manualmente.

Creamos un archivo:

```bash
nano 01_diagnostico.sh
```

Introducimos el siguiente contenido:

```bash
#!/usr/bin/env bash
set -eu

CARPETA="$HOME/practicas/capitulo09/informes"
mkdir -p "$CARPETA"

FECHA=$(date +%Y%m%d_%H%M%S)
ARCHIVO="$CARPETA/diagnostico_${FECHA}.txt"

{
    echo "DIAGNOSTICO ARDUINO UNO Q"
    echo "Fecha: $(date -Is)"
    echo "Usuario: $(whoami)"
    echo "Equipo: $(hostname)"
    echo ""
    echo "MEMORIA"
    free -h
    echo ""
    echo "DISCO"
    df -h "$HOME"
    echo ""
    echo "RED"
    ip -brief address
} > "$ARCHIVO"

echo "Informe guardado en: $ARCHIVO"
```

Guardamos con `Ctrl + O`, Intro y `Ctrl + X`.

Comprobamos la sintaxis y ejecutamos:

```bash
bash -n 01_diagnostico.sh
bash 01_diagnostico.sh
```

Mostramos los archivos creados:

```bash
ls -lh ~/practicas/capitulo09/informes
```

### 4.1. Interpretación del programa

- `#!/usr/bin/env bash` identifica el intérprete.
- `set -eu` interrumpe el script ante ciertos errores o variables sin definir.
- `mkdir -p` crea el directorio si no existe.
- `date +%Y%m%d_%H%M%S` crea una marca temporal para el nombre del archivo.
- `{ ... } > "$ARCHIVO"` redirige varias salidas al mismo informe.
- Las comillas protegen las rutas que pudieran contener espacios.

!!! example "Actividad 1. Ampliar el informe"

    Modifica el script para añadir la versión del kernel mediante `uname -r` y el tiempo de actividad con `uptime`. Ejecuta el programa dos veces y comprueba que genera archivos distintos.

## 5. Programa 2. Comprobar conectividad con Python

Vamos a crear una herramienta que compruebe si una dirección IP responde a `ping` y guarde el resultado en un archivo CSV. Utilizaremos `subprocess.run()` con una lista de argumentos, sin ejecutar comandos a través de un intérprete de shell.

Creamos:

```bash
nano 02_comprobar_red.py
```

```python
import csv
import subprocess
from datetime import datetime
from pathlib import Path

DESTINO = "192.168.1.1"
CARPETA = Path.home() / "practicas" / "capitulo09" / "datos"
ARCHIVO = CARPETA / "conectividad.csv"


def comprobar_red(destino):
    try:
        resultado = subprocess.run(
            ["ping", "-c", "1", "-W", "2", destino],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            check=False,
        )
        return resultado.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def main():
    CARPETA.mkdir(parents=True, exist_ok=True)
    nuevo = not ARCHIVO.exists() or ARCHIVO.stat().st_size == 0
    disponible = comprobar_red(DESTINO)
    estado = "OK" if disponible else "ERROR"

    with ARCHIVO.open("a", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        if nuevo:
            escritor.writerow(["fecha", "destino", "estado"])
        escritor.writerow([
            datetime.now().isoformat(timespec="seconds"),
            DESTINO,
            estado,
        ])

    print(f"Destino: {DESTINO} - Estado: {estado}")
    print(f"Registro: {ARCHIVO}")


if __name__ == "__main__":
    main()
```

!!! note "Dirección de destino"

    La IP `192.168.1.1` es solo un ejemplo. Sustitúyela por la dirección del router o de un equipo que responda a ICMP en tu red. Algunos equipos bloquean `ping` aunque estén funcionando correctamente.

Ejecutamos:

```bash
python3 -m py_compile 02_comprobar_red.py
python3 02_comprobar_red.py
cat ~/practicas/capitulo09/datos/conectividad.csv
```

### 5.1. Comprobación

El CSV debe contener una cabecera y al menos una fila:

```text
fecha,destino,estado
2026-11-19T10:00:00,192.168.1.1,OK
```

Los datos mostrados son ilustrativos: el resultado real dependerá de la conectividad.

!!! example "Actividad 2. Comprobación repetida"

    Ejecuta el programa tres veces. Comprueba que conserva la cabecera y añade una fila por ejecución. Cambia temporalmente el destino por una IP de prueba sin respuesta y explica el resultado.

## 6. Programar tareas periódicas con cron

`cron` es un servicio clásico de Linux que ejecuta comandos según una programación temporal. Cada usuario puede disponer de su propia tabla de tareas, denominada **crontab**.

### 6.1. Comprobar disponibilidad

```bash
command -v crontab
systemctl status cron --no-pager
```

Si `crontab` no existe o el servicio no está disponible, no debemos suponer que está instalado. En una instalación Debian donde se permita administrar paquetes, el profesor puede valorar instalarlo mediante:

```bash
sudo apt update
sudo apt install cron
```

La instalación modifica el sistema y solo debe realizarse cuando sea necesaria y esté autorizada.

### 6.2. Crear una tarea cada cinco minutos

Abrimos el editor de tareas del usuario:

```bash
crontab -e
```

Añadimos esta línea, utilizando la ruta absoluta del usuario:

```cron
*/5 * * * * /usr/bin/python3 /home/arduino/practicas/capitulo09/02_comprobar_red.py >> /home/arduino/practicas/capitulo09/cron.log 2>&1
```

El formato de cron tiene cinco campos temporales:

| Campo | Significado | Valor utilizado |
|---|---|---|
| Minuto | Minutos de la hora | `*/5` |
| Hora | Hora del día | `*` |
| Día del mes | Día | `*` |
| Mes | Mes | `*` |
| Día de la semana | Día | `*` |

La tarea se ejecutará aproximadamente en los minutos 0, 5, 10, 15, etc. de cada hora, **si la placa está encendida y cron está funcionando**.

!!! warning "Evitar duplicados"

    Antes de añadir una nueva línea, revisa la tabla con `crontab -l`. Si ya existe una entrada equivalente, no la dupliques. Las tareas periódicas pueden seguir ejecutándose después de terminar la práctica.

### 6.3. Verificar y retirar la tarea

```bash
crontab -l
cat ~/practicas/capitulo09/cron.log
cat ~/practicas/capitulo09/datos/conectividad.csv
```

El archivo `cron.log` puede estar vacío si el programa no produce errores y su salida se redirige; nuestro programa sí muestra mensajes de ejecución.

Para detener la programación, ejecuta `crontab -e` y elimina **solo la línea añadida**. No utilices `crontab -r`, ya que borraría todas las tareas del usuario.

!!! example "Actividad 3. Verificación de cron"

    Programa la comprobación de conectividad, espera al menos seis minutos y demuestra que se han añadido filas al CSV. Después elimina la tarea y documenta la operación.

## 7. Introducción a systemd

`systemd` es el gestor de servicios utilizado habitualmente por Debian. Permite definir cómo se inicia una aplicación, cuándo debe reiniciarse y dónde consultar sus registros.

En esta práctica crearemos un **servicio de usuario**, sin modificar `/etc/systemd/system` ni ejecutar Python como administrador.

| Herramienta | Función |
|---|---|
| `systemctl --user` | Administrar servicios del usuario |
| `journalctl --user` | Consultar registros del usuario |
| `systemctl --user status` | Consultar el estado de una unidad |
| `systemctl --user start` | Iniciar una unidad |
| `systemctl --user stop` | Detener una unidad |

!!! note "Sesiones de usuario y arranque"

    Un servicio `systemd --user` normalmente funciona mientras existe una sesión de usuario. Para permitir que continúe sin una sesión abierta puede ser necesario habilitar `linger`, operación que requiere autorización administrativa. No debemos confundir iniciar un servicio al entrar por SSH con iniciarlo automáticamente al encender la placa.

## 8. Programa 3. Monitor continuo en Python

Vamos a crear un monitor que registre periódicamente el uso de memoria y el espacio disponible en el directorio personal. Usaremos exclusivamente bibliotecas estándar de Python y comandos Linux ya conocidos.

Creamos el archivo:

```bash
nano 03_monitor_servicio.py
```

```python
import logging
import shutil
import signal
import subprocess
import time
from pathlib import Path

CARPETA = Path.home() / "practicas" / "capitulo09" / "datos"
INTERVALO = 30
activo = True


def detener(signum, frame):
    global activo
    activo = False


def memoria_disponible_mib():
    try:
        resultado = subprocess.run(
            ["free", "-m"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            check=True,
        )
        for linea in resultado.stdout.splitlines():
            if linea.startswith("Mem:"):
                columnas = linea.split()
                return int(columnas[6])
    except (OSError, ValueError, IndexError,
            subprocess.SubprocessError):
        pass
    return None


def main():
    CARPETA.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    signal.signal(signal.SIGTERM, detener)
    signal.signal(signal.SIGINT, detener)

    logging.info("Monitor iniciado")

    while activo:
        libre_gib = shutil.disk_usage(Path.home()).free / (1024 ** 3)
        memoria_mib = memoria_disponible_mib()
        memoria_texto = (
            str(memoria_mib) if memoria_mib is not None else "N/D"
        )
        logging.info(
            "Memoria disponible: %s MiB; disco libre: %.2f GiB",
            memoria_texto,
            libre_gib,
        )

        for _ in range(INTERVALO):
            if not activo:
                break
            time.sleep(1)

    logging.info("Monitor detenido")


if __name__ == "__main__":
    main()
```

**Nota técnica:** `free -m` presenta los datos de memoria en MiB, aunque la opción se denomine `-m`. En distribuciones habituales, la columna `available` ocupa la séptima posición de la fila `Mem:`; si el formato de la herramienta cambia, la función devolverá `N/D`.

### 8.1. Prueba manual

```bash
python3 -m py_compile 03_monitor_servicio.py
python3 03_monitor_servicio.py
```

El programa mostrará una línea aproximadamente cada 30 segundos. Para detenerlo, pulsa `Ctrl + C`.

!!! example "Actividad 4. Monitorización manual"

    Ejecuta el monitor durante al menos un minuto. Anota dos lecturas y explica por qué la memoria disponible y el espacio libre pueden variar.

## 9. Crear un servicio de usuario con systemd

### 9.1. Preparar el archivo de unidad

Creamos el directorio de unidades personales:

```bash
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/arduino-monitor.service
```

Contenido del archivo:

```ini
[Unit]
Description=Monitor de recursos Arduino UNO Q

[Service]
Type=simple
WorkingDirectory=/home/arduino/practicas/capitulo09
ExecStart=/usr/bin/python3 -u /home/arduino/practicas/capitulo09/03_monitor_servicio.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

La opción `-u` evita que la salida estándar de Python se quede retenida en un búfer. En este ejemplo, `logging` escribe en la salida de error y `journalctl` la recoge.

Si el usuario de tu placa no es `arduino`, adapta ambas rutas antes de continuar.

### 9.2. Activar y arrancar el servicio

```bash
systemctl --user daemon-reload
systemctl --user enable --now arduino-monitor.service
```

Comprobamos el estado:

```bash
systemctl --user status arduino-monitor.service --no-pager
```

Si todo funciona, deberíamos ver `active (running)`.

### 9.3. Consultar los registros

```bash
journalctl --user -u arduino-monitor.service -n 20 --no-pager
```

Para seguir los mensajes en tiempo real:

```bash
journalctl --user -u arduino-monitor.service -f
```

Salimos del seguimiento con `Ctrl + C`, sin detener el servicio.

### 9.4. Detener y desactivar

```bash
systemctl --user stop arduino-monitor.service
systemctl --user disable arduino-monitor.service
```

Comprueba el resultado:

```bash
systemctl --user status arduino-monitor.service --no-pager
```

El estado puede aparecer como `inactive (dead)`; esto es normal después de detenerlo.

!!! warning "Si aparece Failed to connect to bus"

    Puede que la sesión no disponga de un gestor `systemd --user` operativo. Comprueba `echo "$XDG_RUNTIME_DIR"` y `loginctl user-status "$USER"`. No ejecutes `sudo systemctl --user` como sustitución: administraría otro contexto de usuario. Si la plataforma no proporciona este servicio, realiza la práctica manual y consulta al profesor antes de cambiar la configuración del sistema.

!!! example "Actividad 5. Gestión de servicios"

    Inicia el servicio, consulta su estado, captura tres mensajes del registro, detén el servicio y demuestra que ya no sigue registrando lecturas.

## 10. Ejecución automática al arrancar

La orden `enable` configura el servicio para que se inicie cuando arranque el gestor de servicios del usuario. **No garantiza por sí sola que se inicie tras encender la placa sin que nadie abra una sesión**.

Para comprobar si el usuario tiene habilitado `linger`:

```bash
loginctl show-user "$USER" -p Linger
```

Si devuelve `Linger=no`, el gestor de usuario puede terminar cuando se cierre la última sesión.

En un entorno administrado y con autorización, puede habilitarse la persistencia mediante:

```bash
sudo loginctl enable-linger arduino
```

!!! warning "Cambio administrativo opcional"

    No habilites `linger` en un equipo compartido sin permiso. Mantener servicios activos sin sesión aumenta el consumo de recursos y puede afectar a otras aplicaciones. Para la práctica básica basta con iniciar y comprobar el servicio durante una sesión SSH.

### 10.1. Diferencias entre cron y systemd

| Característica | cron | Servicio systemd |
|---|---|---|
| Ejecución periódica | Sí | Con temporizadores o lógica del programa |
| Proceso continuo | No es su uso principal | Sí |
| Reinicio tras un fallo | No directamente | `Restart=on-failure` |
| Registro centralizado | Según redirecciones y sistema | `journalctl` |
| Dependencia de sesiones | Depende de la configuración | En servicios de usuario, puede depender de la sesión |

!!! note "Temporizadores systemd"

    `systemd` también dispone de unidades `.timer` para tareas periódicas. Las estudiaremos como ampliación; no es necesario configurar simultáneamente cron y un temporizador para la misma tarea.

## 11. Diagnóstico y resolución de problemas

| Problema | Causa posible | Comprobación o solución |
|---|---|---|
| `Permission denied` | Permisos insuficientes | Comprobar `ls -l` y ejecutar con `python3` o `bash` |
| `python3: command not found` | Ruta incorrecta | Consultar `command -v python3` |
| `No such file or directory` | Ruta equivocada | Comprobar `pwd` y `ls` |
| El servicio no arranca | Error de Python o unidad | `journalctl --user -u arduino-monitor.service` |
| `Failed to connect to bus` | Sin gestor de usuario accesible | Comprobar sesión y `XDG_RUNTIME_DIR` |
| cron no ejecuta la tarea | Servicio ausente o ruta incorrecta | `systemctl status cron` y rutas absolutas |
| No aparecen registros | Programa no iniciado o sin salida | `systemctl --user status` y `journalctl` |
| `SyntaxError: Non-UTF-8 code` | Archivo con codificación incorrecta | Guardar como UTF-8 y evitar caracteres especiales en el código |

### 11.1. Comandos de diagnóstico

```bash
python3 -m py_compile 02_comprobar_red.py
python3 -m py_compile 03_monitor_servicio.py
systemctl --user status arduino-monitor.service --no-pager
journalctl --user -u arduino-monitor.service -n 30 --no-pager
```

Para revisar el archivo de unidad:

```bash
systemd-analyze --user verify ~/.config/systemd/user/arduino-monitor.service
```

Si el comando no está disponible en la instalación, puede omitirse; la comprobación funcional del servicio sigue siendo necesaria.

### 11.2. Precauciones con la codificación

Todos los ejemplos Python del capítulo utilizan **solo caracteres ASCII dentro del código fuente**. Los textos explicativos del libro pueden contener tildes, pero no debemos copiar texto con codificación incompatible al editor de la placa.

Si más adelante necesitamos representar una temperatura en grados Celsius, podemos escribir:

```python
print(f"Temperatura: {25.5} \u00b0C")
```

De este modo, el archivo fuente no necesita contener el símbolo de grado directamente. La secuencia `\u00b0` se interpreta en Python como el carácter `°`.

## 12. Práctica evaluable: servicio de monitorización de Arduino UNO Q

### 12.1. Contexto profesional

Una empresa necesita supervisar de forma continua un dispositivo Linux que participa en una instalación IoT. El equipo técnico debe desarrollar una herramienta de monitorización y dejarla funcionando como servicio de usuario, con registros consultables.

Cada alumno realizará la práctica individualmente y entregará evidencias de su funcionamiento.

### 12.2. Material necesario

- Arduino UNO Q operativo y acceso SSH.
- Python 3.
- Terminal Linux y editor `nano`.
- Acceso al directorio personal del usuario.
- Gestor `systemd --user` funcional para la parte de servicio.

### 12.3. Requisitos obligatorios

1. Crear el directorio `~/practicas/capitulo09/proyecto_final`.
2. Desarrollar un programa Python que consulte memoria disponible y espacio libre.
3. Registrar una lectura cada 30 segundos.
4. Mostrar fecha y hora en cada lectura.
5. Guardar las lecturas en un archivo CSV con cabecera, sin borrar las anteriores.
6. Registrar errores mediante `logging`.
7. Detener el programa correctamente mediante `Ctrl + C` o `SIGTERM`.
8. Crear una unidad `systemd --user` con rutas absolutas.
9. Demostrar inicio, estado, registros y parada del servicio.
10. Elaborar un informe técnico con pruebas y capturas de pantalla.

!!! note "Alternativa si systemd de usuario no está disponible"

    Si la imagen Debian de la placa no permite utilizar `systemd --user`, el profesor podrá autorizar una ejecución manual supervisada del programa y evaluar por separado la definición de la unidad. No deben realizarse cambios administrativos improvisados para completar la actividad.

### 12.4. Desarrollo recomendado

**Fase 1. Preparación.** Crear el directorio de trabajo y comprobar la versión de Python.

**Fase 2. Programación.** Adaptar el programa 3 para añadir almacenamiento CSV. Utilizar rutas de `pathlib` y escritura con `encoding="utf-8"`.

**Fase 3. Validación.** Ejecutar el programa durante dos minutos. Comprobar que se han generado varias filas con marcas temporales diferentes.

**Fase 4. Servicio.** Crear y activar la unidad de usuario. Consultar su estado y sus registros.

**Fase 5. Cierre.** Detener y desactivar el servicio para no dejar procesos de prácticas funcionando innecesariamente.

### 12.5. Ampliación voluntaria

- Registrar también el porcentaje de ocupación del disco.
- Incorporar una comprobación de conectividad.
- Configurar el intervalo de muestreo mediante una variable de entorno.
- Añadir rotación o limitación de tamaño de los archivos de registro.
- Investigar las unidades `systemd.timer` como alternativa a cron.

### 12.6. Entrega

El alumnado entregará:

- Archivo Python del proyecto final.
- Archivo de unidad `.service`.
- CSV con al menos cuatro lecturas reales.
- Capturas de `systemctl --user status` y `journalctl --user`.
- Breve informe en PDF que explique el funcionamiento, las pruebas realizadas y las incidencias detectadas.

### 12.7. Rúbrica de evaluación

| Criterio | Puntuación |
|---|---:|
| Organización de archivos y rutas correctas | 1 punto |
| Obtención correcta de memoria y almacenamiento | 2 puntos |
| Registro periódico y generación de CSV | 2 puntos |
| Gestión de errores y parada controlada | 1 punto |
| Configuración y comprobación del servicio | 2 puntos |
| Evidencias, documentación y presentación | 2 puntos |
| **Total** | **10 puntos** |

## 13. Resumen del capítulo

En este capítulo hemos aprendido a transformar programas ejecutados manualmente en herramientas de automatización para Debian Linux en Arduino UNO Q.

Hemos creado un script Bash, desarrollado una comprobación de conectividad con Python, programado tareas mediante cron y administrado un servicio de usuario con systemd. También hemos aprendido a consultar registros, detectar fallos y detener correctamente los procesos.

Estos conocimientos preparan el siguiente bloque del libro, dedicado a **conectividad y redes**, donde construiremos aplicaciones que se comunicarán con otros dispositivos y servicios.

## Documentación de referencia

- [Python 3: biblioteca estándar](https://docs.python.org/3/library/)
- [Python: subprocess](https://docs.python.org/3/library/subprocess.html)
- [Python: logging](https://docs.python.org/3/library/logging.html)
- [Debian: cron](https://manpages.debian.org/cron)
- [systemd: systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)
- [systemd: systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)
- [systemd: journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)
