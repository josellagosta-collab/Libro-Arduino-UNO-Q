# Capítulo 14. Introducción a Edge AI

## 14.1. Presentación

En los capítulos anteriores hemos utilizado Arduino UNO Q para ejecutar Linux, programar con Python, automatizar servicios, comunicar dispositivos y almacenar mediciones en InfluxDB para visualizarlas mediante Grafana. En este capítulo damos un paso más: **utilizar los datos para realizar inferencias localmente**.

La *inteligencia artificial en el borde* (*Edge AI*) consiste en ejecutar modelos de IA cerca del lugar donde se generan los datos, en lugar de enviar necesariamente todas las mediciones a un servidor remoto. Arduino UNO Q resulta especialmente interesante para introducir esta arquitectura porque combina un entorno Linux con un microcontrolador destinado a interactuar con el mundo físico.

!!! note "Alcance del capítulo"
    En este capítulo utilizaremos modelos didácticos de aprendizaje automático implementados con Python estándar. No requieren aceleradores de IA ni bibliotecas pesadas. El objetivo es comprender el ciclo completo de inferencia local antes de estudiar herramientas y modelos más avanzados en el capítulo 15. Los datos de entrenamiento serán **simulados**, no mediciones reales de sensores.

### Objetivos de aprendizaje

Al finalizar, el alumnado será capaz de:

1. Diferenciar IA, aprendizaje automático, entrenamiento e inferencia.
2. Comparar procesamiento en la nube y procesamiento en el borde.
3. Identificar las funciones del procesador Linux y del microcontrolador en un sistema IoT con IA.
4. Crear un clasificador sencillo y ejecutarlo en Arduino UNO Q.
5. Separar datos de entrenamiento y de prueba y calcular la exactitud del modelo.
6. Medir el tiempo de inferencia y registrar predicciones en CSV.
7. Diseñar un pequeño servicio de inferencia local y valorar sus limitaciones.

### Conocimientos previos

Se presupone que el alumnado ha completado los capítulos 7 a 13: terminal Linux, Python 3, archivos CSV, procesos y servicios, conectividad, API REST y almacenamiento de datos IoT.

## 14.2. ¿Qué es Edge AI?

Una aplicación IoT convencional puede seguir esta secuencia:

**Sensor → dispositivo → red → servidor → análisis → respuesta**.

En una arquitectura Edge AI, parte del análisis se traslada al dispositivo próximo al sensor:

**Sensor → dispositivo → modelo local → decisión**.

El sistema puede seguir enviando resultados o resúmenes a InfluxDB, Grafana o a un servidor central, pero no necesita enviar todos los datos para tomar cada decisión.

| Aspecto | IA en la nube | Edge AI |
|---|---|---|
| Ubicación del modelo | Servidor remoto | Dispositivo local o próximo |
| Dependencia de Internet | Habitualmente elevada | Puede funcionar sin Internet |
| Latencia | Incluye comunicación por red | Evita el viaje a la nube |
| Privacidad | Los datos pueden salir del dispositivo | Es posible procesarlos localmente |
| Recursos | Capacidad de cálculo escalable | Limitados por el hardware disponible |
| Mantenimiento | Centralizado | Requiere gestionar versiones en dispositivos |

!!! warning "Una precisión importante"
    Edge AI no significa que todo el entrenamiento se haga en el dispositivo. Es habitual **entrenar el modelo en un ordenador o servidor** y desplegar después una versión optimizada para ejecutar inferencias en el borde. En esta práctica realizaremos ambos pasos localmente porque el modelo es muy pequeño.

### 14.2.1. IA, aprendizaje automático e inferencia

- **Inteligencia artificial (IA):** conjunto de técnicas para resolver tareas que requieren percepción, predicción, clasificación o toma de decisiones.
- **Aprendizaje automático (machine learning):** técnicas que obtienen patrones a partir de ejemplos.
- **Entrenamiento:** proceso de calcular los parámetros de un modelo a partir de datos.
- **Inferencia:** uso del modelo ya entrenado para obtener una predicción sobre una nueva entrada.
- **Clasificación:** predicción de una categoría, por ejemplo `normal`, `seco` o `caluroso`.
- **Regresión:** predicción de una cantidad numérica, por ejemplo una temperatura futura.

No toda automatización es IA. Una instrucción `if temperatura > 30` es una **regla explícita**, no un modelo aprendido a partir de datos.

## 14.3. Arquitectura de Edge AI en Arduino UNO Q

En Arduino UNO Q distinguimos dos ámbitos de ejecución:

- **Procesador que ejecuta Linux:** adecuado para Python, almacenamiento de archivos, servicios, redes, bases de datos y, según el modelo y sus dependencias, inferencia de IA.
- **Microcontrolador:** adecuado para adquirir señales, controlar entradas y salidas y reaccionar ante sensores y actuadores.

Una aplicación completa podría seguir este flujo:

```text
Sensor de temperatura y humedad
             |
             v
    Adquisicion de datos
             |
             v
    Aplicacion en Linux
             |
             v
    Modelo de inferencia
             |
       +-----+-----+
       |           |
       v           v
  Accion local   Registro IoT
                   |
                   v
             InfluxDB/Grafana
```

En este capítulo simularemos la entrada de los sensores. En los capítulos siguientes podremos estudiar modelos más avanzados e integración con dispositivos reales.

!!! tip "Relación con los capítulos anteriores"
    La inferencia local puede generar un campo `estado` o `prediccion` y enviarlo a un servicio de monitorización. Antes de integrar sistemas, debemos comprobar por separado que el modelo funciona y que sus resultados son coherentes.

## 14.4. Preparación del entorno

Conéctate por SSH al Arduino UNO Q y ejecuta:

```bash
mkdir -p ~/practicas/capitulo14/datos
mkdir -p ~/practicas/capitulo14/modelos
cd ~/practicas/capitulo14
python3 --version
```

Crea un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip --version
```

Si Debian indica que falta `ensurepip`, instala el paquete `python3-venv` correspondiente a tu versión de Python, tal como hicimos en el capítulo 8. Para estas prácticas no hace falta instalar bibliotecas externas: utilizaremos la biblioteca estándar.

Comprueba que el intérprete activo pertenece al entorno virtual:

```bash
which python
```

La ruta esperada será similar a:

```text
/home/arduino/practicas/capitulo14/.venv/bin/python
```

!!! warning "Codificación de los programas"
    Todo el código Python del capítulo utiliza exclusivamente caracteres ASCII: no contiene acentos, eñes ni símbolos especiales como el signo de grados. Las explicaciones del libro sí utilizan la ortografía española habitual. Escribe el código dentro de archivos `.py`, no directamente en Bash.

## 14.5. Programa 1. Reglas frente a aprendizaje automático

### 14.5.1. Objetivo

Antes de utilizar un modelo aprendido, implementaremos un sistema de reglas. Nos servirá como referencia para comprender qué aporta el aprendizaje automático.

Crea el archivo:

```bash
nano 01_reglas.py
```

Introduce:

```python
# 01_reglas.py
# Clasificacion mediante reglas explicitas


def clasificar(temperatura, humedad):
    if temperatura >= 30:
        return "caluroso"
    if humedad < 35:
        return "seco"
    return "normal"


def main():
    ejemplos = [
        (22.0, 55.0),
        (32.0, 40.0),
        (24.0, 25.0),
        (28.0, 48.0),
    ]

    for temperatura, humedad in ejemplos:
        estado = clasificar(temperatura, humedad)
        print(
            f"Temperatura: {temperatura:.1f} C | "
            f"Humedad: {humedad:.1f} % | "
            f"Estado: {estado}"
        )


if __name__ == "__main__":
    main()
```

Guarda el archivo con `Ctrl + O`, Intro y `Ctrl + X`. Comprueba y ejecuta:

```bash
python -m py_compile 01_reglas.py
python 01_reglas.py
```

**Preguntas de reflexión:** ¿quién ha decidido los umbrales? ¿Qué sucede si el ambiente está a 29,9 C? ¿Qué dificultades aparecen cuando existen muchas variables?

!!! example "Actividad 1. Modificación de reglas"
    Cambia el umbral de humedad de 35 a 40 y observa qué predicciones se modifican. Entrega una captura del resultado y una explicación de por qué este programa no constituye aprendizaje automático.

## 14.6. Programa 2. Entrenar un clasificador sencillo

### 14.6.1. El modelo de centroides

Vamos a utilizar un **clasificador por centroide más cercano**. Durante el entrenamiento calcula, para cada clase, la media de sus ejemplos. En la inferencia asigna cada nueva observación a la clase cuyo centroide está más próximo.

Para dos variables, temperatura y humedad, calculamos la distancia euclídea:

\[
d=\sqrt{(T-T_c)^2+(H-H_c)^2}
\]

Como temperatura y humedad tienen escalas diferentes, **normalizaremos las variables** antes de calcular distancias. En este ejemplo didáctico usaremos escalas fijas de 40 C y 100 % para que las distancias sean comparables.

### 14.6.2. Crear el programa

```bash
nano 02_entrenar_modelo.py
```

```python
# 02_entrenar_modelo.py
# Modelo didactico de centroides mas cercanos

import json
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
MODELO = BASE / "modelos" / "modelo_ambiente.json"

# Datos sinteticos: temperatura, humedad, clase
ENTRENAMIENTO = [
    (20.0, 55.0, "normal"),
    (22.0, 60.0, "normal"),
    (24.0, 50.0, "normal"),
    (21.0, 65.0, "normal"),
    (25.0, 22.0, "seco"),
    (23.0, 28.0, "seco"),
    (26.0, 30.0, "seco"),
    (24.0, 25.0, "seco"),
    (32.0, 42.0, "caluroso"),
    (34.0, 48.0, "caluroso"),
    (31.0, 55.0, "caluroso"),
    (33.0, 50.0, "caluroso"),
]

ESCALAS = {"temperatura": 40.0, "humedad": 100.0}


def entrenar(datos):
    grupos = defaultdict(list)
    for temperatura, humedad, clase in datos:
        grupos[clase].append((temperatura, humedad))

    centroides = {}
    for clase, ejemplos in grupos.items():
        media_t = sum(x[0] for x in ejemplos) / len(ejemplos)
        media_h = sum(x[1] for x in ejemplos) / len(ejemplos)
        centroides[clase] = [
            media_t / ESCALAS["temperatura"],
            media_h / ESCALAS["humedad"],
        ]

    return {
        "version": 1,
        "tipo": "centroide_mas_cercano",
        "escalas": ESCALAS,
        "centroides": centroides,
        "origen_datos": "sinteticos",
    }


def main():
    modelo = entrenar(ENTRENAMIENTO)
    MODELO.parent.mkdir(parents=True, exist_ok=True)
    MODELO.write_text(
        json.dumps(modelo, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    print("Modelo entrenado correctamente")
    print(f"Archivo: {MODELO}")
    for clase, centroide in sorted(modelo["centroides"].items()):
        print(f"{clase}: {centroide}")


if __name__ == "__main__":
    main()
```

Comprueba y ejecuta:

```bash
python -m py_compile 02_entrenar_modelo.py
python 02_entrenar_modelo.py
cat modelos/modelo_ambiente.json
```

### 14.6.3. Interpretación

El archivo JSON contiene los parámetros aprendidos. **No es el programa que clasifica**, sino el resultado del entrenamiento. Esta separación permite entrenar una vez y utilizar el modelo repetidamente sin recalcular los centroides.

!!! note "Limitación del ejemplo"
    El clasificador de centroides es una técnica real de aprendizaje automático, pero muy sencilla. No es un sistema de seguridad ni un detector fiable de condiciones ambientales peligrosas. Los ejemplos y etiquetas son artificiales; las predicciones no deben utilizarse para controlar equipos críticos.

!!! example "Actividad 2. Inspección del modelo"
    Abre `modelo_ambiente.json`, identifica sus clases y explica qué representan los dos números de cada centroide. No modifiques manualmente el modelo durante esta actividad.

## 14.7. Programa 3. Inferencia local y evaluación

### 14.7.1. Separar entrenamiento e inferencia

Ahora cargaremos el archivo JSON y realizaremos predicciones sobre **datos distintos de los utilizados para entrenar**. Esto evita evaluar el modelo únicamente con los mismos ejemplos que ha memorizado o resumido.

Crea:

```bash
nano 03_inferencia_local.py
```

```python
# 03_inferencia_local.py
# Inferencia local y evaluacion con ejemplos de prueba

import json
import math
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent
MODELO = BASE / "modelos" / "modelo_ambiente.json"

# Datos sinteticos reservados para la prueba
PRUEBAS = [
    (23.0, 57.0, "normal"),
    (21.0, 52.0, "normal"),
    (25.0, 27.0, "seco"),
    (22.0, 24.0, "seco"),
    (33.0, 46.0, "caluroso"),
    (32.0, 52.0, "caluroso"),
]


def cargar_modelo():
    with MODELO.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def predecir(modelo, temperatura, humedad):
    escalas = modelo["escalas"]
    punto = (
        temperatura / escalas["temperatura"],
        humedad / escalas["humedad"],
    )

    mejor_clase = None
    mejor_distancia = float("inf")

    for clase, centroide in modelo["centroides"].items():
        distancia = math.dist(punto, centroide)
        if distancia < mejor_distancia:
            mejor_clase = clase
            mejor_distancia = distancia

    return mejor_clase


def main():
    if not MODELO.exists():
        print("Modelo no encontrado. Ejecuta 02_entrenar_modelo.py")
        return

    modelo = cargar_modelo()
    aciertos = 0
    duraciones_ms = []

    for temperatura, humedad, esperado in PRUEBAS:
        inicio = time.perf_counter()
        prediccion = predecir(modelo, temperatura, humedad)
        duracion_ms = (time.perf_counter() - inicio) * 1000
        duraciones_ms.append(duracion_ms)
        correcto = prediccion == esperado
        aciertos += int(correcto)

        print(
            f"T={temperatura:.1f} C, H={humedad:.1f} %, "
            f"Esperado={esperado}, Predicho={prediccion}, "
            f"Correcto={correcto}, Tiempo={duracion_ms:.4f} ms"
        )

    exactitud = 100 * aciertos / len(PRUEBAS)
    media_ms = sum(duraciones_ms) / len(duraciones_ms)
    print(f"Exactitud en prueba: {exactitud:.1f} %")
    print(f"Tiempo medio de inferencia: {media_ms:.4f} ms")


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
python -m py_compile 03_inferencia_local.py
python 03_inferencia_local.py
```

### 14.7.2. Métricas

La **exactitud** (*accuracy*) se calcula mediante:

\[
\text{Exactitud}=\frac{\text{predicciones correctas}}{\text{total de pruebas}}\times 100
\]

El **tiempo de inferencia** mide cuánto tarda la función `predecir` en devolver una clase. No incluye lectura de sensores, comunicación por red ni escritura de archivos. Las medidas pueden variar entre ejecuciones y, al ser el modelo muy pequeño, el tiempo registrado puede ser extremadamente bajo.

!!! warning "Interpretar la exactitud con prudencia"
    Una exactitud elevada en seis ejemplos sintéticos no demuestra que el modelo funcione bien con datos reales. Para un proyecto profesional harían falta datos representativos, más ejemplos independientes, análisis de errores y pruebas bajo condiciones reales.

!!! example "Actividad 3. Evaluación crítica"
    Anota la exactitud y el tiempo medio. Repite tres veces la ejecución y explica por qué pueden variar los tiempos. Identifica al menos dos motivos por los que estos resultados no garantizan fiabilidad en un entorno real.

## 14.8. Programa 4. Registro de predicciones en CSV

El siguiente paso consiste en registrar las predicciones, igual que hacíamos con los datos de conectividad y las mediciones IoT.

Crea:

```bash
nano 04_registrar_predicciones.py
```

```python
# 04_registrar_predicciones.py
# Guarda inferencias locales en un archivo CSV

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from importlib.machinery import SourceFileLoader

BASE = Path(__file__).resolve().parent
MODELO = BASE / "modelos" / "modelo_ambiente.json"
DESTINO = BASE / "datos" / "predicciones.csv"

# Entradas simuladas, no proceden de sensores reales
LECTURAS = [
    (22.5, 58.0),
    (25.0, 26.0),
    (33.0, 47.0),
    (24.0, 53.0),
]


def predecir(modelo, temperatura, humedad):
    escalas = modelo["escalas"]
    t = temperatura / escalas["temperatura"]
    h = humedad / escalas["humedad"]
    mejor_clase = None
    mejor_distancia = float("inf")

    for clase, centroide in modelo["centroides"].items():
        distancia_cuadrada = (
            (t - centroide[0]) ** 2 +
            (h - centroide[1]) ** 2
        )
        if distancia_cuadrada < mejor_distancia:
            mejor_clase = clase
            mejor_distancia = distancia_cuadrada

    return mejor_clase


def main():
    if not MODELO.exists():
        print("Falta el modelo. Ejecuta 02_entrenar_modelo.py")
        return

    with MODELO.open("r", encoding="utf-8") as archivo:
        modelo = json.load(archivo)

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    nuevo = not DESTINO.exists() or DESTINO.stat().st_size == 0

    with DESTINO.open("a", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        if nuevo:
            escritor.writerow([
                "fecha_utc", "temperatura_c", "humedad_pct", "prediccion"
            ])

        for temperatura, humedad in LECTURAS:
            prediccion = predecir(modelo, temperatura, humedad)
            fecha = datetime.now(timezone.utc).isoformat()
            escritor.writerow([fecha, temperatura, humedad, prediccion])
            print(
                f"T={temperatura:.1f} C, H={humedad:.1f} %, "
                f"Prediccion={prediccion}"
            )

    print(f"Archivo generado: {DESTINO}")


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
python -m py_compile 04_registrar_predicciones.py
python 04_registrar_predicciones.py
cat datos/predicciones.csv
```

!!! note "Diseño de la práctica"
    El programa escribe cuatro lecturas simuladas cada vez que se ejecuta. No debe interpretarse como una monitorización continua de sensores. Antes de conectarlo a InfluxDB, conviene decidir qué datos deben registrarse y con qué frecuencia.

!!! example "Actividad 4. Análisis del CSV"
    Ejecuta dos veces el programa, comprueba que se añaden nuevas filas sin repetir la cabecera y explica por qué se utiliza el modo de apertura `a`.

## 14.9. Del prototipo al sistema Edge AI

El flujo completo de un proyecto real puede dividirse en siete etapas:

1. **Captura:** obtener datos de sensores o de otros sistemas.
2. **Preparación:** limpiar, validar y transformar las variables.
3. **Entrenamiento:** ajustar el modelo con ejemplos representativos.
4. **Evaluación:** comprobarlo con datos no utilizados para entrenar.
5. **Despliegue:** instalar el modelo y sus dependencias en el dispositivo.
6. **Inferencia:** realizar predicciones a partir de nuevas entradas.
7. **Supervisión:** registrar resultados, detectar errores y actualizar versiones.

En nuestro caso:

| Etapa | Implementación en el capítulo |
|---|---|
| Datos | Ejemplos sintéticos de temperatura y humedad |
| Entrenamiento | `02_entrenar_modelo.py` |
| Modelo | `modelos/modelo_ambiente.json` |
| Evaluación | `03_inferencia_local.py` |
| Inferencia | Clasificación local en Python |
| Registro | `04_registrar_predicciones.py` |
| Supervisión futura | Integración con servicios, InfluxDB y Grafana |

### 14.9.1. ¿Cuándo conviene Edge AI?

Puede resultar apropiado cuando es necesario reaccionar con baja latencia, reducir tráfico, funcionar sin conexión o evitar transferir datos sensibles. No siempre es la mejor opción: los dispositivos tienen límites de memoria, energía, almacenamiento y capacidad de cálculo.

### 14.9.2. Seguridad y fiabilidad

- No ejecutes acciones peligrosas basándote únicamente en una predicción experimental.
- Mantén separados los datos de entrenamiento y los datos de evaluación.
- Registra la versión del modelo y la fecha de despliegue.
- Protege credenciales y tokens; no los incluyas en el código fuente.
- Define un comportamiento seguro si faltan datos o falla el modelo.
- Evita recopilar información personal innecesaria.

## 14.10. Actividad 5. Diseño de una aplicación Edge AI

En parejas, diseñad una aplicación de IA local para Arduino UNO Q. Elegid uno de estos escenarios:

- Detección de condiciones ambientales anómalas.
- Clasificación del estado de una máquina a partir de vibraciones simuladas.
- Detección de cambios de iluminación.
- Identificación de patrones de uso de un equipo informático.

El documento de diseño debe contener: objetivo, variables de entrada, clases de salida, origen de los datos, estrategia de evaluación, recursos necesarios, riesgos y propuesta de integración con los servicios de los capítulos 9 a 13.

!!! tip "No confundir un umbral con un modelo"
    Si la solución se limita a una secuencia de condiciones `if`, debe describirse como automatización basada en reglas. Para considerarla aprendizaje automático, el comportamiento de clasificación debe depender de parámetros calculados a partir de ejemplos.

## 14.11. Práctica integradora evaluable

### Título: Primer sistema de clasificación Edge AI en Arduino UNO Q

**Organización:** parejas, con entrega individual de la reflexión técnica.

**Objetivo:** construir, ejecutar y evaluar un clasificador local que reciba temperatura y humedad simuladas, produzca una categoría y registre las predicciones en CSV.

### Requisitos mínimos

1. Crear la estructura `~/practicas/capitulo14/` con subdirectorios `datos` y `modelos`.
2. Ejecutar y explicar el clasificador basado en reglas.
3. Entrenar el modelo de centroides y generar el archivo JSON.
4. Evaluar el modelo con ejemplos independientes.
5. Medir y documentar el tiempo medio de inferencia.
6. Generar un CSV con fecha, entradas y predicción.
7. Identificar tres limitaciones del modelo y dos ventajas potenciales de Edge AI.
8. Documentar los comandos utilizados y las incidencias resueltas.

### Entregables

- Los cuatro archivos `.py`.
- El modelo `modelo_ambiente.json`.
- El archivo `predicciones.csv`.
- Un informe breve en PDF con capturas de terminal, resultados, análisis y conclusiones.
- Una demostración del funcionamiento en Arduino UNO Q.

### Rúbrica de evaluación

| Criterio | Puntuación máxima |
|---|---:|
| Preparación correcta del entorno y estructura de archivos | 1,0 |
| Comprensión de reglas frente a aprendizaje automático | 1,0 |
| Entrenamiento y generación del modelo JSON | 2,0 |
| Inferencia y evaluación con datos de prueba | 2,0 |
| Registro correcto de predicciones en CSV | 1,5 |
| Análisis crítico de resultados y limitaciones | 1,5 |
| Documentación y demostración técnica | 1,0 |
| **Total** | **10,0** |

### Criterios de comprobación

```bash
cd ~/practicas/capitulo14
source .venv/bin/activate
python -m py_compile 01_reglas.py 02_entrenar_modelo.py 03_inferencia_local.py 04_registrar_predicciones.py
python 01_reglas.py
python 02_entrenar_modelo.py
python 03_inferencia_local.py
python 04_registrar_predicciones.py
ls -l modelos/modelo_ambiente.json datos/predicciones.csv
```

La práctica se considerará funcional cuando todos los programas terminen sin errores, el modelo exista, la evaluación muestre resultados y el CSV contenga predicciones.

## 14.12. Resolución de problemas frecuentes

| Problema | Causa posible | Solución |
|---|---|---|
| `SyntaxError: Non-UTF-8 code` | Archivo guardado con codificación incompatible | Reescribir el archivo como UTF-8 y evitar caracteres no ASCII en los programas |
| `bash: import: command not found` | Código Python pegado directamente en Bash | Guardarlo en un archivo `.py` y ejecutarlo con `python` |
| `No such file or directory` | Directorio incorrecto | Ejecutar `cd ~/practicas/capitulo14` y comprobar con `ls` |
| `Modelo no encontrado` | No se ha ejecutado el entrenamiento | Ejecutar primero `python 02_entrenar_modelo.py` |
| `Permission denied` | Permisos incorrectos | Comprobar permisos y propietario con `ls -l` |
| Predicciones poco coherentes | Datos sintéticos escasos o modelo demasiado simple | Revisar ejemplos, normalización y conjunto de prueba |
| Tiempo de inferencia variable | Carga del sistema y precisión del reloj | Repetir medidas y comparar promedios |

!!! warning "Precaución con la evaluación"
    No cambies las etiquetas del conjunto de prueba solo para mejorar la exactitud. Si modificas los datos de entrenamiento, vuelve a generar el modelo y documenta qué has cambiado.

## 14.13. Autoevaluación

1. ¿Qué diferencia existe entre entrenamiento e inferencia?
2. ¿Por qué un sistema basado en `if` no es necesariamente aprendizaje automático?
3. ¿Qué ventajas puede aportar ejecutar un modelo sin conexión a Internet?
4. ¿Por qué deben separarse los datos de entrenamiento y prueba?
5. ¿Qué información almacena nuestro archivo JSON?
6. ¿Qué significa la exactitud de un clasificador?
7. ¿Por qué no basta una exactitud elevada en seis ejemplos sintéticos?
8. ¿Qué recursos del dispositivo pueden limitar un proyecto Edge AI?
9. ¿Qué datos incluirías en un registro de predicciones?
10. ¿Cómo relacionarías el modelo con InfluxDB y Grafana?

## 14.14. Resumen del capítulo

Hemos conocido el concepto de Edge AI y sus diferencias respecto al procesamiento en la nube. Hemos distinguido las reglas explícitas de un modelo aprendido, entrenado un clasificador de centroides, separado entrenamiento y prueba, medido el tiempo de inferencia y registrado predicciones en CSV.

El ejemplo es intencionadamente sencillo: permite comprender el proceso completo sin depender de bibliotecas externas ni de un modelo de gran tamaño. En el siguiente capítulo, **Modelos de inteligencia artificial**, estudiaremos técnicas, formatos y herramientas de inferencia más avanzadas y sus requisitos de despliegue en Arduino UNO Q.

## 14.15. Referencias y ampliación

- Documentación oficial de Python: <https://docs.python.org/3/>
- Documentación de Arduino: <https://docs.arduino.cc/>
- Introducción a aprendizaje automático de Google: <https://developers.google.com/machine-learning/crash-course>
- Documentación de scikit-learn: <https://scikit-learn.org/stable/>

!!! note "Continuidad del libro"
    El capítulo 14 introduce los fundamentos y un primer prototipo verificable. No presupone que los ejemplos sintéticos representen un sensor real ni que el hardware tenga instalado un motor de inferencia específico. La integración con sensores, modelos optimizados y visión artificial se abordará progresivamente en los capítulos siguientes.
