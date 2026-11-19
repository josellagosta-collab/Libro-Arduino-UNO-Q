# Capítulo 8. Programación con Python en Arduino UNO Q

## Objetivos de aprendizaje

Al finalizar este capítulo, el alumnado será capaz de:

- Explicar dónde se ejecutan los programas Python dentro de la arquitectura de Arduino UNO Q.
- Comprobar la disponibilidad de Python 3 en Debian Linux.
- Crear, guardar y ejecutar scripts Python desde la terminal.
- Utilizar variables, tipos de datos, operadores, condicionales, bucles y funciones.
- Gestionar archivos de texto y datos CSV en el directorio personal.
- Obtener información del sistema utilizando bibliotecas estándar de Python.
- Ejecutar comandos Linux de forma controlada mediante `subprocess`.
- Registrar eventos mediante el módulo `logging`.
- Organizar un proyecto Python y utilizar un entorno virtual cuando sea necesario.
- Desarrollar una aplicación de diagnóstico y generación de informes.
- Documentar y comprobar los resultados de las prácticas.

## 1. Introducción

En el capítulo 7 hemos aprendido a trabajar con Debian Linux en Arduino UNO Q: acceder mediante SSH, utilizar la terminal, administrar archivos, consultar procesos y diagnosticar la red.

Ahora utilizaremos esos conocimientos para **automatizar tareas mediante Python**. En lugar de escribir manualmente varios comandos, podremos desarrollar programas que los ejecuten, interpreten sus resultados y generen informes.

Python es un lenguaje de programación de alto nivel, interpretado y de propósito general. Se utiliza en administración de sistemas, automatización, desarrollo web, análisis de datos, inteligencia artificial e Internet de las cosas (IoT).

En Arduino UNO Q, Python se ejecuta en el **procesador Qualcomm QRB2210**, bajo Debian Linux. El microcontrolador STM32U585 mantiene sus propias funciones de control de hardware.

!!! info "Relación con los capítulos anteriores"

    En el capítulo 6 utilizamos Python junto con Arduino App Lab y el mecanismo Bridge para comunicarnos con el STM32.

    En este capítulo nos centraremos en **Python como herramienta de administración y automatización de Linux**. Los programas serán scripts independientes, ejecutados desde la terminal, sin necesidad de utilizar Bridge.

### 1.1. Aplicaciones de Python en ASIX

Entre sus usos más habituales destacan:

- Consultar el estado de un servidor o dispositivo Linux.
- Comprobar la conectividad de red.
- Automatizar copias y tratamiento de archivos.
- Procesar registros de funcionamiento.
- Generar informes de diagnóstico.
- Ejecutar tareas repetitivas de administración.
- Preparar aplicaciones que posteriormente utilizarán sensores, bases de datos o servicios web.

## 2. Preparación del entorno

### 2.1. Material necesario

- Arduino UNO Q con Debian Linux operativo.
- Ordenador con Windows 11.
- Cable USB-C para datos y alimentación.
- Acceso a la placa mediante Arduino App Lab, terminal o SSH.
- Editor de texto disponible en Linux, por ejemplo `nano`.
- Conocimientos básicos de los comandos del capítulo 7.

### 2.2. Conexión a la placa

Accede a la terminal Linux de Arduino UNO Q como hicimos en el capítulo anterior. Si utilizas SSH desde PowerShell o PuTTY, sustituye la dirección IP por la de tu placa:

```powershell
ssh arduino@192.168.1.49
```

La dirección `192.168.1.49` es únicamente un ejemplo de una configuración utilizada durante las pruebas del proyecto. Puede haber cambiado.

Comprueba el usuario y el directorio actual:

```bash
whoami
pwd
```

!!! warning "Trabajar sin privilegios de administrador"

    Realizaremos las prácticas dentro del directorio personal del usuario. No es necesario utilizar `sudo` para crear o ejecutar los programas.

    No modificaremos archivos de configuración del sistema ni instalaremos paquetes globales sin una necesidad justificada.

### 2.3. Comprobar Python 3

Ejecuta:

```bash
python3 --version
```

La respuesta mostrará la versión de Python 3 instalada, que puede variar según la imagen de Debian.

Comprueba la ubicación del intérprete:

```bash
command -v python3
```

Para conocer más información:

```bash
python3 -c 'import sys; print(sys.version); print(sys.executable)'
```

!!! tip "¿Python o Python 3?"

    En Debian utilizaremos `python3` para ejecutar los scripts. El comando `python` puede no existir o depender de la configuración del sistema.

### 2.4. Crear el directorio de prácticas

```bash
mkdir -p ~/practicas/capitulo08
cd ~/practicas/capitulo08
pwd
```

Todos los archivos de este capítulo se guardarán en ese directorio.

## 3. Primer programa Python

### 3.1. Crear el archivo

Abre el editor:

```bash
nano 01_hola_python.py
```

Introduce:

```python
# Programa 1: Primer programa Python
# Arduino UNO Q - Debian Linux

print("Hola desde Python en Arduino UNO Q")
print("Este programa se ejecuta en el procesador Qualcomm")
```

Guarda con `Ctrl + O`, confirma con `Intro` y sal de `nano` con `Ctrl + X`.

### 3.2. Ejecutar el programa

```bash
python3 01_hola_python.py
```

Resultado esperado:

```text
Hola desde Python en Arduino UNO Q
Este programa se ejecuta en el procesador Qualcomm
```

### 3.3. Interpretación del código

La función `print()` muestra información en la salida estándar de la terminal.

Los comentarios comienzan por `#` y permiten documentar el código sin ejecutarse.

La extensión `.py` identifica habitualmente un archivo de código fuente Python.

!!! example "Actividad 8.1"

    Modifica el programa para mostrar tu nombre, el grupo de clase y el nombre de la placa.

    Ejecuta el archivo y realiza una captura del resultado.

## 4. Variables, tipos de datos y operadores

Una variable permite almacenar información que el programa utilizará durante su ejecución.

### 4.1. Tipos de datos básicos

| Tipo | Ejemplo | Utilidad |
|---|---|---|
| `str` | `"Arduino UNO Q"` | Texto |
| `int` | `42` | Número entero |
| `float` | `23.5` | Número decimal |
| `bool` | `True` | Valor lógico |
| `list` | `[10, 20, 30]` | Colección ordenada |
| `dict` | `{"estado": "OK"}` | Datos asociados a claves |

Crea el archivo:

```bash
nano 02_variables.py
```

```python
# Programa 2: Variables y operaciones

nombre = "Arduino UNO Q"
temperatura_simulada = 24.5
umbral = 30.0
muestras = [23.8, 24.5, 25.1]

media = sum(muestras) / len(muestras)
alarma = temperatura_simulada >= umbral

print(f"Dispositivo: {nombre}")
print(f"Temperatura simulada: {temperatura_simulada:.1f} °C")
print(f"Media de las muestras: {media:.2f} °C")
print(f"Alarma activada: {alarma}")
```

Ejecuta:

```bash
python3 02_variables.py
```

!!! note "Datos simulados"

    Los valores de temperatura del ejemplo son **simulados**. No estamos leyendo un sensor físico. La lectura de sensores reales y su comunicación con otros componentes se abordará en capítulos posteriores.

### 4.2. Operadores habituales

| Operador | Significado | Ejemplo |
|---|---|---|
| `+` | Suma | `a + b` |
| `-` | Resta | `a - b` |
| `*` | Multiplicación | `a * b` |
| `/` | División | `a / b` |
| `==` | Igualdad | `a == b` |
| `!=` | Desigualdad | `a != b` |
| `>` | Mayor que | `a > b` |
| `>=` | Mayor o igual | `a >= b` |
| `and` | Y lógico | `a > 0 and b > 0` |
| `or` | O lógico | `a > 0 or b > 0` |

!!! example "Actividad 8.2"

    Cambia el valor de `temperatura_simulada` a `35.0` y comprueba cómo cambia la variable `alarma`.

    Añade una cuarta muestra a la lista y calcula de nuevo la media.

## 5. Estructuras de control y funciones

### 5.1. Condicionales

La estructura `if` permite ejecutar instrucciones cuando se cumple una condición:

```python
uso_cpu_simulado = 78

if uso_cpu_simulado >= 90:
    print("Estado crítico")
elif uso_cpu_simulado >= 70:
    print("Advertencia")
else:
    print("Estado normal")
```

Python utiliza la **indentación** para delimitar bloques. En nuestros programas emplearemos cuatro espacios.

### 5.2. Bucles

El bucle `for` permite recorrer una secuencia:

```python
for numero in range(1, 6):
    print(f"Comprobación {numero}")
```

El bucle `while` repite instrucciones mientras una condición sea verdadera:

```python
contador = 0

while contador < 3:
    print("Sistema activo")
    contador += 1
```

!!! warning "Evitar bucles infinitos"

    Un bucle `while` debe disponer de una condición de salida cuando no se pretenda ejecutar permanentemente. Si un programa queda bloqueado en la terminal, normalmente puede interrumpirse con `Ctrl + C`.

### 5.3. Funciones

Una función agrupa instrucciones para reutilizarlas:

```python
def evaluar_temperatura(valor, umbral=30.0):
    if valor >= umbral:
        return "ALERTA"
    return "NORMAL"

print(evaluar_temperatura(22.5))
print(evaluar_temperatura(34.2))
```

!!! example "Actividad 8.3"

    Escribe una función llamada `evaluar_memoria()` que reciba un porcentaje de uso.

    La función devolverá `NORMAL` si el valor es inferior al 80 %, y `ALERTA` en caso contrario.

    Prueba la función con los valores 45, 79 y 92.

## 6. Programa 3. Gestión de archivos con Python

En el capítulo 7 hemos utilizado comandos como `cat`, `cp` y `ls`. Python también permite crear y gestionar archivos desde un programa.

### 6.1. La biblioteca pathlib

El módulo `pathlib` facilita el manejo de rutas y directorios de forma portable.

Crea:

```bash
nano 03_archivos.py
```

```python
# Programa 3: Escritura y lectura de archivos
from pathlib import Path
from datetime import datetime

carpeta = Path.home() / "practicas" / "capitulo08" / "datos"
carpeta.mkdir(parents=True, exist_ok=True)

archivo = carpeta / "registro.txt"
fecha = datetime.now().isoformat(timespec="seconds")

with archivo.open("a", encoding="utf-8") as fichero:
    fichero.write(f"{fecha} - Programa ejecutado correctamente\n")

print(f"Archivo: {archivo}")
print("Contenido del registro:")
print(archivo.read_text(encoding="utf-8"))
```

Ejecuta:

```bash
python3 03_archivos.py
```

Comprueba el archivo con Linux:

```bash
cat ~/practicas/capitulo08/datos/registro.txt
```

### 6.2. Conceptos utilizados

- `Path.home()` obtiene el directorio personal del usuario.
- `mkdir()` crea directorios.
- `open("a")` abre un archivo para añadir contenido sin borrar lo anterior.
- `with` garantiza el cierre del archivo al finalizar el bloque.
- `read_text()` permite leer un archivo de texto.
- `datetime.now()` obtiene la fecha y hora del sistema.

!!! example "Actividad 8.4"

    Ejecuta el programa tres veces y comprueba que el registro conserva las entradas anteriores.

    Modifica el mensaje para incluir tu grupo de clase.

## 7. Programa 4. Tratamiento de datos CSV

El formato CSV permite almacenar información tabular de manera sencilla. Es útil para intercambiar datos entre programas, hojas de cálculo y sistemas de monitorización.

### 7.1. Generar un CSV

Crea:

```bash
nano 04_csv.py
```

```python
# Programa 4: Registro y análisis de datos CSV
import csv
from pathlib import Path
from statistics import mean

carpeta = Path.home() / "practicas" / "capitulo08" / "datos"
carpeta.mkdir(parents=True, exist_ok=True)
archivo = carpeta / "temperaturas_simuladas.csv"

muestras = [22.8, 23.4, 24.1, 23.9, 25.0]

with archivo.open("w", newline="", encoding="utf-8") as fichero:
    escritor = csv.writer(fichero)
    escritor.writerow(["muestra", "temperatura_c"])
    for indice, valor in enumerate(muestras, start=1):
        escritor.writerow([indice, valor])

lecturas = []
with archivo.open("r", newline="", encoding="utf-8") as fichero:
    lector = csv.DictReader(fichero)
    for fila in lector:
        lecturas.append(float(fila["temperatura_c"]))

print(f"Archivo creado: {archivo}")
print(f"Número de muestras: {len(lecturas)}")
print(f"Mínima: {min(lecturas):.1f} °C")
print(f"Máxima: {max(lecturas):.1f} °C")
print(f"Media: {mean(lecturas):.2f} °C")
```

Ejecuta:

```bash
python3 04_csv.py
```

Consulta el contenido:

```bash
cat ~/practicas/capitulo08/datos/temperaturas_simuladas.csv
```

!!! note "Diferencia entre modos de apertura"

    El modo `"w"` sobrescribe el contenido anterior. El modo `"a"` añade nuevas líneas. Debemos elegir el modo adecuado para evitar perder información.

!!! example "Actividad 8.5"

    Amplía la lista a diez muestras simuladas.

    Calcula cuántas superan 24 °C y muestra el resultado en pantalla.

## 8. Programa 5. Diagnóstico del sistema mediante Python

Python puede obtener información de Debian sin instalar bibliotecas externas. Utilizaremos `platform`, `shutil`, `os`, `socket` y `subprocess`.

### 8.1. Ejecutar comandos con subprocess

El módulo `subprocess` permite iniciar procesos y recoger su salida.

```python
import subprocess

resultado = subprocess.run(
    ["uname", "-r"],
    capture_output=True,
    text=True,
    timeout=5,
    check=False
)

print(resultado.stdout.strip())
```

Los argumentos principales son:

| Parámetro | Función |
|---|---|
| `capture_output=True` | Captura salida estándar y errores |
| `text=True` | Devuelve texto en lugar de bytes |
| `timeout=5` | Limita el tiempo de ejecución a cinco segundos |
| `check=False` | Permite examinar el código de salida sin lanzar una excepción por un error del comando |
| `returncode` | Código de finalización del proceso; normalmente `0` indica éxito |
| `stdout` | Salida estándar |
| `stderr` | Mensajes de error |

!!! warning "Seguridad al ejecutar comandos"

    Pasaremos los comandos como listas de argumentos y evitaremos `shell=True`.

    No construiremos comandos del sistema concatenando texto introducido por usuarios. Esto reduce el riesgo de ejecutar instrucciones no deseadas.

### 8.2. Crear el programa completo

```bash
nano 05_diagnostico.py
```

```python
# Programa 5: Diagnóstico básico de Arduino UNO Q
import os
import platform
import shutil
import socket
import subprocess
from datetime import datetime
from pathlib import Path


def ejecutar_comando(argumentos):
    try:
        resultado = subprocess.run(
            argumentos,
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
        if resultado.returncode != 0:
            return f"No disponible: {resultado.stderr.strip()}"
        return resultado.stdout.strip()
    except (OSError, subprocess.TimeoutExpired) as error:
        return f"No disponible: {error}"


def generar_informe():
    memoria = ejecutar_comando(["free", "-h"])
    ruta = ejecutar_comando(["ip", "route", "show", "default"])
    interfaces = ejecutar_comando(["ip", "-brief", "address"])
    disco = shutil.disk_usage(Path.home())

    lineas = [
        "INFORME DE DIAGNÓSTICO - ARDUINO UNO Q",
        "=" * 46,
        f"Fecha: {datetime.now().isoformat(timespec='seconds')}",
        f"Usuario: {os.getlogin() if os.isatty(0) else os.environ.get('USER', 'desconocido')}",
        f"Equipo: {socket.gethostname()}",
        f"Sistema: {platform.system()}",
        f"Arquitectura: {platform.machine()}",
        f"Kernel: {platform.release()}",
        f"Python: {platform.python_version()}",
        f"Espacio libre en HOME: {disco.free / (1024 ** 3):.2f} GiB",
        "",
        "MEMORIA",
        memoria,
        "",
        "INTERFACES DE RED",
        interfaces,
        "",
        "RUTA POR DEFECTO",
        ruta or "No se ha encontrado una ruta por defecto",
    ]
    return "\n".join(lineas) + "\n"


def main():
    carpeta = Path.home() / "practicas" / "capitulo08" / "informes"
    carpeta.mkdir(parents=True, exist_ok=True)
    destino = carpeta / "diagnostico_python.txt"

    informe = generar_informe()
    destino.write_text(informe, encoding="utf-8")

    print(informe)
    print(f"Informe guardado en: {destino}")


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
python3 05_diagnostico.py
```

Consulta el informe:

```bash
cat ~/practicas/capitulo08/informes/diagnostico_python.txt
```

### 8.3. Interpretación de resultados

El programa recopila:

- Fecha de ejecución.
- Usuario y nombre del equipo.
- Sistema operativo, arquitectura y versión del kernel.
- Versión de Python.
- Espacio libre en el sistema de archivos del directorio personal.
- Información de memoria.
- Interfaces y direcciones IP.
- Ruta por defecto.

Los valores dependerán de la configuración real de la placa.

!!! warning "Privacidad de los informes"

    Los informes pueden incluir nombres de usuario, direcciones IP y otros datos internos de la red del centro. Antes de publicarlos en GitHub o compartirlos fuera del aula, elimina o anonimiza esa información.

!!! example "Actividad 8.6"

    Compara la información del informe con la obtenida manualmente en el capítulo 7 mediante `uname`, `free`, `df` e `ip`.

    Explica qué ventajas tiene automatizar estas consultas con Python.

## 9. Registro de eventos con logging

El módulo `logging` permite guardar mensajes de funcionamiento y errores sin depender únicamente de `print()`.

Crea:

```bash
nano 06_logging.py
```

```python
# Programa 6: Registro de eventos
import logging
from pathlib import Path

carpeta = Path.home() / "practicas" / "capitulo08" / "logs"
carpeta.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=carpeta / "aplicacion.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

logging.info("Aplicación iniciada")

valor_simulado = 85
if valor_simulado >= 80:
    logging.warning("Uso simulado superior al umbral")
else:
    logging.info("Estado simulado normal")

logging.info("Aplicación finalizada")
print("Registro creado correctamente")
```

Ejecuta:

```bash
python3 06_logging.py
cat ~/practicas/capitulo08/logs/aplicacion.log
```

### 9.1. Niveles de registro

| Nivel | Utilidad |
|---|---|
| `DEBUG` | Detalles para depuración |
| `INFO` | Funcionamiento normal |
| `WARNING` | Situaciones que requieren atención |
| `ERROR` | Fallos de una operación |
| `CRITICAL` | Errores graves |

!!! example "Actividad 8.7"

    Modifica el programa para que registre un mensaje `ERROR` cuando un valor simulado supere 95.

    Ejecuta varias pruebas y comprueba el archivo de registro.

## 10. Organización de proyectos y entornos virtuales

Cuando un programa crece, conviene separar código, datos, registros e informes.

### 10.1. Estructura recomendada

```text
capitulo08/
├── 01_hola_python.py
├── 02_variables.py
├── 03_archivos.py
├── 04_csv.py
├── 05_diagnostico.py
├── 06_logging.py
├── datos/
│   ├── registro.txt
│   └── temperaturas_simuladas.csv
├── informes/
│   └── diagnostico_python.txt
└── logs/
    └── aplicacion.log
```

Los archivos de datos, registros e informes se generan durante la ejecución. No es necesario crearlos manualmente.

### 10.2. Entornos virtuales

Un entorno virtual permite aislar las dependencias Python de un proyecto y evitar modificaciones innecesarias en el Python del sistema.

Comprueba primero si está disponible el módulo `venv`:

```bash
python3 -m venv --help
```

Si está instalado, crea el entorno:

```bash
cd ~/practicas/capitulo08
python3 -m venv .venv
source .venv/bin/activate
python --version
```

Para salir:

```bash
deactivate
```

!!! note "Instalación de dependencias"

    Todos los ejemplos de este capítulo utilizan bibliotecas estándar y no requieren instalar paquetes mediante `pip`.

    Si `venv` no está disponible, el profesor deberá revisar los paquetes necesarios para la versión de Debian instalada. No utilizaremos `sudo pip install` para modificar el Python del sistema.

### 10.3. Comprobar la sintaxis

Python permite compilar el código a bytecode para detectar errores de sintaxis:

```bash
python3 -m py_compile 05_diagnostico.py
```

Este comando no sustituye a las pruebas funcionales: un programa puede tener una sintaxis correcta y producir resultados incorrectos.

## 11. Errores habituales y resolución de problemas

| Problema | Posible causa | Comprobación o solución |
|---|---|---|
| `python3: command not found` | Python 3 no está disponible en el entorno | Comprobar `command -v python3` |
| `SyntaxError` | Error de sintaxis | Revisar la línea indicada |
| `IndentationError` | Sangrado incorrecto | Utilizar cuatro espacios por nivel |
| `FileNotFoundError` | Ruta inexistente | Comprobar `pwd` y la ruta del archivo |
| `PermissionError` | Falta de permisos | Trabajar dentro de `~/practicas` |
| `ModuleNotFoundError` | Módulo no instalado o nombre incorrecto | Comprobar el intérprete y las dependencias |
| `TimeoutExpired` | Comando externo demasiado lento | Revisar el comando y el tiempo límite |
| No se genera el informe | Error durante la ejecución | Revisar la salida de la terminal |
| Resultados de red vacíos | Interfaz desconectada o comando no disponible | Consultar `ip address` e `ip route` |

### 11.1. Procedimiento de diagnóstico

1. Comprueba el directorio actual con `pwd`.
2. Verifica que el archivo existe mediante `ls -l`.
3. Ejecuta el programa con `python3 nombre.py`.
4. Lee el mensaje de error completo, especialmente la última línea.
5. Comprueba la sintaxis y la indentación.
6. Introduce mensajes `print()` o registros `logging` para localizar el problema.
7. Corrige un único aspecto cada vez y vuelve a ejecutar.

!!! tip "Buenas prácticas"

    Utiliza nombres descriptivos, funciones pequeñas, rutas construidas con `pathlib`, gestión de excepciones y comentarios que expliquen las decisiones importantes.

    No incluyas contraseñas, tokens ni claves privadas dentro de los scripts.

## 12. Práctica evaluable: monitor de diagnóstico Linux con Python

### 12.1. Contexto profesional

El departamento de sistemas de una empresa utiliza varias placas Arduino UNO Q como dispositivos de automatización e IoT.

Antes de poner una placa en servicio, el técnico debe ejecutar un programa Python que identifique el equipo, compruebe sus recursos y genere un informe para el responsable de sistemas.

El alumnado desarrollará una aplicación de diagnóstico que pueda ejecutarse desde una terminal SSH sin intervención manual.

### 12.2. Material necesario

- Arduino UNO Q operativo.
- Ordenador con Windows 11.
- Acceso SSH o terminal Linux.
- Python 3.
- Editor de texto.

### 12.3. Requisitos obligatorios

1. Crear una carpeta de proyecto llamada `practica_monitor_python` dentro de `~/practicas/capitulo08`.
2. Desarrollar un archivo principal llamado `monitor.py`.
3. Utilizar al menos **tres funciones propias**.
4. Identificar el nombre del equipo, el sistema operativo, el kernel y la versión de Python.
5. Consultar la memoria y el almacenamiento disponible.
6. Obtener las interfaces de red y la ruta por defecto.
7. Guardar un informe de texto con fecha y hora.
8. Registrar en un archivo de log el inicio y el final de la ejecución.
9. Gestionar correctamente los posibles errores de los comandos externos.
10. Documentar el funcionamiento y demostrar que la aplicación se ejecuta correctamente.

### 12.4. Desarrollo recomendado

**Paso 1.** Accede a Arduino UNO Q mediante SSH.

**Paso 2.** Crea el directorio de trabajo:

```bash
mkdir -p ~/practicas/capitulo08/practica_monitor_python
cd ~/practicas/capitulo08/practica_monitor_python
```

**Paso 3.** Diseña las funciones del programa. Por ejemplo:

```python
def obtener_identidad():
    pass


def obtener_recursos():
    pass


def obtener_red():
    pass
```

**Paso 4.** Implementa cada función y comprueba su resultado por separado.

**Paso 5.** Construye el informe utilizando los datos obtenidos.

**Paso 6.** Guarda el informe en un directorio `informes`.

**Paso 7.** Añade un registro de eventos en un directorio `logs`.

**Paso 8.** Ejecuta la aplicación y verifica que los archivos se han creado correctamente.

**Paso 9.** Realiza una segunda ejecución para comprobar que el programa sigue funcionando.

**Paso 10.** Documenta las pruebas, incidencias y conclusiones.

### 12.5. Ampliación voluntaria

Incorpora una opción para generar también un archivo JSON con la información recopilada. Utiliza la biblioteca estándar `json`.

Como segunda ampliación, permite que el usuario indique mediante un argumento la carpeta donde se guardarán los informes, utilizando `argparse`.

### 12.6. Entrega

Cada alumno entregará:

- Un documento PDF con portada, objetivos, procedimiento y conclusiones.
- El código fuente completo de `monitor.py`.
- Capturas de la ejecución en la terminal Linux.
- Un informe de diagnóstico generado por el programa.
- Un archivo de registro de eventos.
- Explicación de al menos dos pruebas realizadas y de sus resultados.

Los informes deberán revisarse para eliminar información sensible antes de compartirlos.

### 12.7. Rúbrica de evaluación

| Criterio | Puntuación |
|---|---:|
| Preparación del entorno y ejecución correcta | 1 punto |
| Organización del código y funciones propias | 1,5 puntos |
| Identificación del sistema | 1 punto |
| Diagnóstico de memoria y almacenamiento | 1,5 puntos |
| Diagnóstico de red | 1 punto |
| Generación del informe | 1 punto |
| Registro de eventos y gestión de errores | 1 punto |
| Pruebas y documentación técnica | 2 puntos |
| **Total** | **10 puntos** |

## 13. Resumen del capítulo

En este capítulo hemos aprendido a desarrollar y ejecutar programas Python en el entorno Debian Linux de Arduino UNO Q.

Hemos utilizado variables, condicionales, bucles y funciones, y hemos trabajado con archivos de texto y CSV. También hemos obtenido información del sistema operativo, ejecutado comandos Linux mediante `subprocess` y registrado eventos con `logging`.

Finalmente, hemos integrado estos conocimientos en una aplicación de diagnóstico que genera informes técnicos de la placa.

En el siguiente capítulo, **Automatización y servicios**, utilizaremos Python para ejecutar tareas de manera programada, gestionar procesos y estudiar cómo mantener aplicaciones en funcionamiento en Linux.

## Documentación de referencia

- [Arduino UNO Q — Documentación oficial](https://docs.arduino.cc/hardware/uno-q/)
- [Arduino UNO Q — Manual de usuario](https://docs.arduino.cc/tutorials/uno-q/user-manual/)
- [Python 3 — Tutorial oficial](https://docs.python.org/3/tutorial/)
- [Python — Biblioteca estándar](https://docs.python.org/3/library/)
- [Python — pathlib](https://docs.python.org/3/library/pathlib.html)
- [Python — subprocess](https://docs.python.org/3/library/subprocess.html)
- [Python — logging](https://docs.python.org/3/library/logging.html)
- [Debian — Documentación](https://www.debian.org/doc/)
