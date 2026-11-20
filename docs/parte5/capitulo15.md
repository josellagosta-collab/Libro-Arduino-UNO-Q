# Capítulo 15. Modelos de inteligencia artificial

## 15.1. Presentación

En el capítulo 14 aprendimos a distinguir las reglas programadas de los modelos entrenados y construimos un clasificador de centroides para interpretar datos ambientales simulados. Ahora avanzaremos hacia el **ciclo de vida de un modelo de inteligencia artificial**: preparar datos, seleccionar un algoritmo, entrenar, evaluar, guardar una versión, desplegarla y medir su rendimiento en Arduino UNO Q.

En este capítulo trabajaremos con **datos sintéticos de temperatura y humedad**. No afirmaremos que las predicciones procedan de sensores reales. Para que las prácticas puedan ejecutarse en el entorno Debian de Arduino UNO Q sin instalaciones pesadas, implementaremos un clasificador **k vecinos más próximos (k-NN)** con la biblioteca estándar de Python. Estudiaremos también las diferencias con redes neuronales, modelos preentrenados y motores de inferencia optimizados, que podrán incorporarse en prácticas posteriores.

!!! note "Criterio técnico"
    Un algoritmo k-NN es un modelo de aprendizaje automático válido, aunque su fase de entrenamiento consista principalmente en almacenar los ejemplos. La inferencia se realiza en Linux y no requiere asumir que existe un acelerador de IA configurado. El uso de bibliotecas como scikit-learn, ONNX Runtime o motores específicos depende de la compatibilidad de versiones y arquitectura; no son requisitos para completar este capítulo.

### Objetivos de aprendizaje

Al finalizar, el alumnado será capaz de:

1. Distinguir clasificación, regresión y detección de anomalías.
2. Identificar las fases de preparación, entrenamiento, validación y despliegue de un modelo.
3. Explicar el funcionamiento de k-NN y la necesidad de normalizar variables.
4. Evitar la fuga de información entre entrenamiento y prueba.
5. Calcular exactitud y matriz de confusión sobre ejemplos no utilizados para entrenar.
6. Guardar y recuperar un modelo en JSON con metadatos y versión.
7. Medir tiempos de inferencia y reconocer limitaciones de memoria, latencia y generalización.
8. Preparar una aplicación de inferencia local reproducible y documentada.

### Conocimientos previos

Capítulos 7 a 14: Linux, Python, archivos CSV y JSON, entornos virtuales, servicios, redes, IoT y conceptos básicos de Edge AI.

## 15.2. Tipos de modelos y tareas

| Tarea | Entrada | Salida | Ejemplo de aplicación |
|---|---|---|---|
| Clasificación | Temperatura y humedad | Etiqueta | `normal`, `seco`, `caluroso` |
| Regresión | Mediciones históricas | Valor numérico | Temperatura estimada |
| Detección de anomalías | Lecturas y comportamiento habitual | Normal o atípico | Detección de sensor defectuoso |
| Visión artificial | Imagen o fotograma | Clase, posición o máscara | Detección de objetos |
| Procesamiento del lenguaje | Texto | Clasificación o texto | Análisis de incidencias |

La **clasificación** será nuestra tarea principal. Un modelo de clasificación no sustituye a un sistema de seguridad: las salidas deben interpretarse como predicciones y pueden ser erróneas.

### 15.2.1. Entrenamiento e inferencia

```text
DATOS DE EJEMPLO
       |
       v
Separacion entrenamiento/prueba
       |
       +---------------------------+
       |                           |
       v                           v
ENTRENAMIENTO                  PRUEBA RESERVADA
       |                           |
       v                           |
Modelo + normalizacion             |
       |                           |
       v                           v
   INFERENCIA ----------------> EVALUACION
       |
       v
  DESPLIEGUE LOCAL
```

!!! warning "Evitar la fuga de datos"
    Las medias y desviaciones utilizadas para normalizar deben calcularse **solo con el conjunto de entrenamiento**. Utilizar datos de prueba para preparar el modelo produce una evaluación artificialmente optimista.

## 15.3. Algoritmos y formatos de despliegue

| Técnica | Ventajas | Limitaciones |
|---|---|---|
| Reglas explícitas | Simples y explicables | No aprenden de ejemplos |
| Centroides (cap. 14) | Poco almacenamiento | Fronteras de decisión simples |
| k-NN | Fácil de comprender; no requiere entrenamiento complejo | Conserva ejemplos; la inferencia crece con el conjunto |
| Árbol de decisión | Interpretable en muchos casos | Puede sobreajustarse |
| Redes neuronales | Modelan relaciones complejas | Requieren más datos, cálculo y herramientas |

Un modelo puede guardarse como JSON didáctico, como archivo propio de una biblioteca o en formatos de intercambio como **ONNX**. No basta con cambiar la extensión del archivo: el motor de inferencia debe ser compatible con las operaciones, versiones y arquitectura del dispositivo.

!!! tip "Por qué utilizaremos JSON"
    El modelo k-NN del capítulo puede almacenarse con `json` de Python, sin dependencias externas. Evitamos cargar archivos serializados de procedencia desconocida y podemos inspeccionar sus parámetros. **No se deben cargar modelos no confiables con `pickle`.**

## 15.4. Preparación del entorno en Arduino UNO Q

Desde PuTTY o una sesión SSH:

```bash
mkdir -p ~/practicas/capitulo15/datos
mkdir -p ~/practicas/capitulo15/modelos
mkdir -p ~/practicas/capitulo15/resultados
cd ~/practicas/capitulo15
python3 --version
```

Crearemos un entorno virtual para mantener la continuidad con el capítulo 8, aunque los programas no necesiten paquetes de terceros:

```bash
python3 -m venv .venv
source .venv/bin/activate
python --version
```

Si aparece `ensurepip is not available`, hay que instalar el paquete `python3.X-venv` que corresponda exactamente a la versión de Python del sistema. En el entorno que hemos utilizado anteriormente fue `python3.13-venv`:

```bash
sudo apt update
sudo apt install python3.13-venv
```

No instalaremos bibliotecas adicionales. Los cuatro programas se escribirán mediante `nano` en la carpeta `~/practicas/capitulo15`. **El código se pega dentro de `nano`, no directamente en Bash.**

!!! warning "Codificación"
    Todo el código Python de este capítulo usa únicamente caracteres ASCII. Los textos explicativos del libro sí incluyen tildes y signos ortográficos normales. No introduzcas en los programas símbolos como el grado de temperatura o caracteres copiados desde procesadores de texto.

## 15.5. Programa 1. Generación de un conjunto de datos

### 15.5.1. Objetivo

Crear un CSV reproducible con lecturas ambientales **simuladas** y etiquetas. Emplearemos una semilla fija para obtener los mismos datos en cada ejecución. El programa reserva un conjunto de prueba independiente, que no utilizaremos para normalizar ni entrenar.

Crea el archivo:

```bash
nano 01_generar_datos.py
```

```python
import csv
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATOS = BASE / "datos"
DATOS.mkdir(parents=True, exist_ok=True)
RNG = random.Random(150)

CENTROS = {
    "normal": (23.0, 55.0),
    "seco": (23.0, 28.0),
    "caluroso": (34.0, 52.0),
}


def crear_ejemplos(n_por_clase):
    filas = []
    for etiqueta, (temp, hum) in CENTROS.items():
        for _ in range(n_por_clase):
            filas.append({
                "temperatura": round(RNG.gauss(temp, 1.8), 2),
                "humedad": round(max(0.0, min(100.0, RNG.gauss(hum, 5.0))), 2),
                "etiqueta": etiqueta,
            })
    RNG.shuffle(filas)
    return filas


def guardar(nombre, filas):
    destino = DATOS / nombre
    with destino.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(
            archivo, fieldnames=["temperatura", "humedad", "etiqueta"]
        )
        escritor.writeheader()
        escritor.writerows(filas)
    print("Archivo:", destino, "Registros:", len(filas))


def main():
    guardar("entrenamiento.csv", crear_ejemplos(30))
    guardar("prueba.csv", crear_ejemplos(10))


if __name__ == "__main__":
    main()
```

Guarda el archivo con `Ctrl + O`, Intro y `Ctrl + X`. Ejecuta:

```bash
python -m py_compile 01_generar_datos.py
python 01_generar_datos.py
head -n 5 datos/entrenamiento.csv
wc -l datos/*.csv
```

**Resultado esperado:** 90 registros de entrenamiento y 30 de prueba, más una línea de cabecera en cada CSV. La etiqueta de cada registro se deriva del grupo sintético que lo generó; las clases pueden solaparse y no representan una verdad física universal.

!!! example "Actividad 1"
    Comprueba cuántas filas hay en cada CSV y explica por qué no debemos utilizar el archivo `prueba.csv` para calcular la normalización.

## 15.6. Programa 2. Entrenar y guardar un modelo k-NN

### 15.6.1. Fundamento

Para clasificar una lectura, k-NN calcula su distancia a los ejemplos de entrenamiento y elige la etiqueta más frecuente entre los **k vecinos más próximos**. Utilizaremos `k=5` y distancia euclídea sobre variables estandarizadas.

Para cada variable:

\[
z = \frac{x - \mu_{entrenamiento}}{\sigma_{entrenamiento}}
\]

Esto evita que la humedad domine la distancia solo por tener una escala numérica diferente de la temperatura.

Crea el archivo:

```bash
nano 02_entrenar_knn.py
```

```python
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
ENTRADA = BASE / "datos" / "entrenamiento.csv"
SALIDA = BASE / "modelos" / "modelo_knn.json"
CAMPOS = ["temperatura", "humedad"]


def leer_datos(ruta):
    with ruta.open("r", newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    if not filas:
        raise ValueError("El CSV no contiene ejemplos")
    return filas


def calcular_estadisticas(filas):
    estadisticas = {}
    for campo in CAMPOS:
        valores = [float(fila[campo]) for fila in filas]
        media = sum(valores) / len(valores)
        varianza = sum((x - media) ** 2 for x in valores) / len(valores)
        desviacion = math.sqrt(varianza)
        if desviacion == 0:
            desviacion = 1.0
        estadisticas[campo] = {"media": media, "desviacion": desviacion}
    return estadisticas


def normalizar(fila, estadisticas):
    return [
        (float(fila[campo]) - estadisticas[campo]["media"])
        / estadisticas[campo]["desviacion"]
        for campo in CAMPOS
    ]


def main():
    filas = leer_datos(ENTRADA)
    estadisticas = calcular_estadisticas(filas)
    ejemplos = [
        {"x": normalizar(fila, estadisticas), "etiqueta": fila["etiqueta"]}
        for fila in filas
    ]
    modelo = {
        "formato": "knn_ambiente_v1",
        "version": "1.0",
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "campos": CAMPOS,
        "k": 5,
        "estadisticas": estadisticas,
        "ejemplos": ejemplos,
        "etiquetas": sorted(set(fila["etiqueta"] for fila in filas)),
    }
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(modelo, indent=2), encoding="utf-8")
    print("Modelo guardado:", SALIDA)
    print("Ejemplos:", len(ejemplos))
    print("Vecinos k:", modelo["k"])
    print("Clases:", ", ".join(modelo["etiquetas"]))


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
python -m py_compile 02_entrenar_knn.py
python 02_entrenar_knn.py
ls -lh modelos/modelo_knn.json
```

El archivo JSON contiene los ejemplos normalizados, los parámetros de escalado, el valor de `k` y los metadatos de versión. No es un modelo de red neuronal; es la representación completa del clasificador k-NN.

!!! example "Actividad 2"
    Abre el JSON con `less modelos/modelo_knn.json`. Identifica `k`, `estadisticas`, `etiquetas` y `version`. Explica qué ocurriría si cambiaras las medias del modelo sin volver a entrenarlo.

## 15.7. Programa 3. Inferencia y evaluación del modelo

Crearemos un programa que cargue el modelo, prediga etiquetas para las 30 lecturas de prueba y calcule la exactitud y una matriz de confusión. El programa también permitirá clasificar una lectura introducida desde la terminal.

Crea el archivo:

```bash
nano 03_evaluar_knn.py
```

```python
import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
MODELO = BASE / "modelos" / "modelo_knn.json"
PRUEBA = BASE / "datos" / "prueba.csv"


def cargar_modelo():
    modelo = json.loads(MODELO.read_text(encoding="utf-8"))
    if modelo.get("formato") != "knn_ambiente_v1":
        raise ValueError("Formato de modelo incompatible")
    if not modelo.get("ejemplos") or int(modelo.get("k", 0)) < 1:
        raise ValueError("Modelo incompleto")
    return modelo


def predecir(modelo, temperatura, humedad):
    valores = {"temperatura": temperatura, "humedad": humedad}
    vector = []
    for campo in modelo["campos"]:
        parametros = modelo["estadisticas"][campo]
        vector.append(
            (valores[campo] - parametros["media"]) / parametros["desviacion"]
        )
    distancias = []
    for ejemplo in modelo["ejemplos"]:
        distancia = math.sqrt(sum(
            (a - b) ** 2 for a, b in zip(vector, ejemplo["x"])
        ))
        distancias.append((distancia, ejemplo["etiqueta"]))
    vecinos = sorted(distancias, key=lambda item: item[0])[:modelo["k"]]
    votos = Counter(etiqueta for _, etiqueta in vecinos)
    max_votos = max(votos.values())
    candidatos = [et for et, n in votos.items() if n == max_votos]
    # Resolve ties using the closest neighbor among tied labels.
    etiqueta = next(et for _, et in vecinos if et in candidatos)
    return etiqueta, max_votos / len(vecinos)


def evaluar(modelo):
    with PRUEBA.open("r", newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    if not filas:
        raise ValueError("No hay datos de prueba")
    clases = modelo["etiquetas"]
    matriz = {real: {pred: 0 for pred in clases} for real in clases}
    aciertos = 0
    for fila in filas:
        real = fila["etiqueta"]
        prediccion, _ = predecir(
            modelo, float(fila["temperatura"]), float(fila["humedad"])
        )
        matriz[real][prediccion] += 1
        aciertos += int(real == prediccion)
    print("Ejemplos de prueba:", len(filas))
    print("Aciertos:", aciertos)
    print("Exactitud: {:.2f}%".format(100 * aciertos / len(filas)))
    print("Matriz de confusion (filas reales, columnas predichas):")
    print("real/pred", *clases, sep="\t")
    for real in clases:
        print(real, *(matriz[real][pred] for pred in clases), sep="\t")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--temperatura", type=float)
    parser.add_argument("--humedad", type=float)
    args = parser.parse_args()
    modelo = cargar_modelo()
    if (args.temperatura is None) != (args.humedad is None):
        parser.error("Indica temperatura y humedad juntas")
    if args.temperatura is not None:
        if not math.isfinite(args.temperatura) or not math.isfinite(args.humedad):
            parser.error("Los valores deben ser finitos")
        if not 0 <= args.humedad <= 100:
            parser.error("La humedad debe estar entre 0 y 100")
        etiqueta, votos = predecir(modelo, args.temperatura, args.humedad)
        print("Prediccion:", etiqueta)
        print("Fraccion de votos:", round(votos, 2))
        print("La fraccion de votos no es una probabilidad calibrada")
    else:
        evaluar(modelo)


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
python -m py_compile 03_evaluar_knn.py
python 03_evaluar_knn.py
python 03_evaluar_knn.py --temperatura 24 --humedad 56
python 03_evaluar_knn.py --temperatura 22 --humedad 25
```

!!! note "Interpretación de la exactitud"
    Una exactitud elevada sobre 30 ejemplos **simulados** no demuestra que el sistema funcione con sensores reales. El modelo solo ha aprendido patrones del generador de datos. Además, la fracción de votos entre vecinos no debe presentarse como una probabilidad calibrada.

### 15.7.1. La matriz de confusión

Cada fila representa una clase real y cada columna una clase predicha. Los valores de la diagonal principal son los aciertos. Los valores fuera de la diagonal muestran los tipos de confusión del modelo.

!!! example "Actividad 3"
    Anota la exactitud y la matriz de confusión obtenidas. Identifica si existe alguna confusión entre clases y explica por qué un resultado perfecto tampoco garantizaría un buen comportamiento con datos reales.

## 15.8. Programa 4. Medir latencia y registrar inferencias

En Edge AI importa no solo la exactitud, sino también el tiempo de respuesta, la memoria y la continuidad del servicio. Mediremos la inferencia repetidamente, sin incluir la carga inicial del JSON, y guardaremos un resumen en CSV.

Crea el archivo:

```bash
nano 04_benchmark_knn.py
```

```python
import csv
import json
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from importlib.util import module_from_spec, spec_from_file_location

BASE = Path(__file__).resolve().parent
RUTA_MODELO = BASE / "modelos" / "modelo_knn.json"
SALIDA = BASE / "resultados" / "rendimiento.csv"


def cargar_predictor():
    ruta = BASE / "03_evaluar_knn.py"
    spec = spec_from_file_location("evaluador_knn", ruta)
    modulo = module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo.predecir


def main():
    modelo = json.loads(RUTA_MODELO.read_text(encoding="utf-8"))
    predecir = cargar_predictor()
    lecturas = [(23.0, 54.0), (24.0, 26.0), (35.0, 50.0)]
    tiempos_ms = []
    for _ in range(20):
        for temperatura, humedad in lecturas:
            inicio = time.perf_counter_ns()
            etiqueta, votos = predecir(modelo, temperatura, humedad)
            duracion = (time.perf_counter_ns() - inicio) / 1000000.0
            tiempos_ms.append(duracion)
    resumen = {
        "fecha_utc": datetime.now(timezone.utc).isoformat(),
        "modelo": modelo["version"],
        "inferencias": len(tiempos_ms),
        "media_ms": round(statistics.mean(tiempos_ms), 4),
        "min_ms": round(min(tiempos_ms), 4),
        "max_ms": round(max(tiempos_ms), 4),
    }
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    existe = SALIDA.exists() and SALIDA.stat().st_size > 0
    with SALIDA.open("a", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(resumen))
        if not existe:
            escritor.writeheader()
        escritor.writerow(resumen)
    print("Inferencias:", resumen["inferencias"])
    print("Tiempo medio (ms):", resumen["media_ms"])
    print("Tiempo maximo (ms):", resumen["max_ms"])
    print("Registro:", SALIDA)


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
python -m py_compile 04_benchmark_knn.py
python 04_benchmark_knn.py
cat resultados/rendimiento.csv
```

!!! warning "Medidas de rendimiento"
    Los tiempos dependen de la carga de Linux, del número de ejemplos y de la resolución del reloj. La prueba no mide consumo energético ni rendimiento de aceleradores de IA. Para comparar dos modelos, utiliza las mismas entradas y condiciones de ejecución.

!!! example "Actividad 4"
    Ejecuta tres veces el benchmark y compara los tiempos medios. ¿Son idénticos? Razona cómo afectaría al tiempo de inferencia aumentar de 90 a 9.000 ejemplos de entrenamiento.

## 15.9. Comparación de modelos y criterios de selección

El modelo más complejo no siempre es el más apropiado para un dispositivo de borde. Para seleccionar una solución debemos valorar:

- **Calidad de predicción:** métricas sobre datos representativos y no vistos.
- **Latencia:** tiempo máximo aceptable para reaccionar.
- **Memoria:** tamaño del modelo y memoria durante la ejecución.
- **Consumo energético:** relevante en sistemas alimentados por batería.
- **Disponibilidad:** capacidad de funcionar sin conexión a Internet.
- **Mantenibilidad:** versión, procedencia y actualización de modelos.
- **Seguridad y privacidad:** tratamiento de datos y acceso a servicios.

| Caso | Técnica orientativa | Motivo |
|---|---|---|
| Tres estados ambientales con pocos datos | Centroides o k-NN | Prototipo sencillo y explicable |
| Predicción numérica | Regresión | Salida continua |
| Detección de objetos en cámara | Modelo de visión | Trabaja con imágenes |
| Texto y lenguaje | Modelo especializado | Requiere procesamiento lingüístico |

No hay un único modelo óptimo para todos los casos. La elección depende de la tarea, los datos disponibles y los recursos del dispositivo.

## 15.10. Modelos preentrenados y despliegue en Arduino UNO Q

En aplicaciones profesionales es habitual entrenar un modelo en un ordenador con más recursos y desplegarlo en el dispositivo para realizar inferencias. El procedimiento general es:

1. Definir el problema y las métricas.
2. Obtener y etiquetar datos representativos.
3. Separar entrenamiento, validación y prueba.
4. Entrenar y seleccionar un modelo.
5. Exportarlo en un formato compatible con el motor de inferencia.
6. Comprobar la compatibilidad con Linux y la arquitectura del equipo.
7. Medir memoria, latencia, temperatura y estabilidad.
8. Versionar el modelo y prever una recuperación ante fallos.

### 15.10.1. ¿Qué es la cuantización?

La cuantización representa parámetros o activaciones con menor precisión numérica, por ejemplo enteros de 8 bits en lugar de números de coma flotante de 32 bits. Puede reducir el tamaño y acelerar ciertas operaciones **si el motor y el hardware las soportan**, pero también puede afectar a la calidad de predicción.

### 15.10.2. ¿Qué comprobaremos antes de instalar un motor de IA?

```bash
uname -m
cat /etc/os-release
python3 --version
free -h
df -h ~
```

Estos comandos permiten conocer la arquitectura, distribución, versión de Python y recursos disponibles. **No instalaremos automáticamente paquetes pesados ni descargaremos modelos grandes**, porque su compatibilidad y requisitos deben verificarse primero.

!!! note "Relación con los siguientes capítulos"
    El capítulo 16 abordará la visión artificial y el capítulo 17 la integración de IA con sensores y actuadores. Aquí nos centramos en comprender, guardar, evaluar y ejecutar un modelo local reproducible.

## 15.11. Actividad 5. Cambiar el valor de k

Realiza una copia del modelo:

```bash
cp modelos/modelo_knn.json modelos/modelo_knn_original.json
```

Abre `modelos/modelo_knn.json` con `nano` y cambia únicamente `"k": 5` por `"k": 1`. Ejecuta de nuevo:

```bash
python 03_evaluar_knn.py
python 04_benchmark_knn.py
```

Después prueba `k=9`. Compara la exactitud y los tipos de error. Finalmente, restaura el modelo original:

```bash
cp modelos/modelo_knn_original.json modelos/modelo_knn.json
```

!!! warning "Control de versiones"
    Cambiar `k` modifica el comportamiento del modelo. En un proyecto real habría que registrar el cambio, volver a validar y actualizar su versión antes del despliegue.

## 15.12. Práctica integradora evaluable

### Título: Selección y validación de un modelo Edge AI

**Situación profesional:** un equipo técnico debe elegir un clasificador para supervisar las condiciones ambientales de una instalación. Se solicita un prototipo local que funcione en Arduino UNO Q sin depender de servicios externos.

**Trabajo:** individual o por parejas, según indique el profesor.

### Requisitos mínimos

1. Generar un conjunto reproducible de entrenamiento y otro de prueba.
2. Entrenar un clasificador k-NN y guardar su configuración en JSON.
3. Realizar inferencias sobre lecturas nuevas.
4. Evaluar el modelo mediante exactitud y matriz de confusión.
5. Comparar al menos dos valores de `k`.
6. Medir y registrar tiempos de inferencia.
7. Documentar por qué los resultados con datos simulados no equivalen a una validación con sensores reales.
8. Proponer una mejora para el futuro sistema IoT.

### Entregables

- Cuatro archivos `.py` funcionales.
- `datos/entrenamiento.csv` y `datos/prueba.csv`.
- `modelos/modelo_knn.json`.
- `resultados/rendimiento.csv`.
- Informe PDF o Markdown con pruebas, resultados, comparación y conclusiones.
- Demostración en Arduino UNO Q.

### Rúbrica de evaluación

| Criterio | Puntuación |
|---|---:|
| Generación correcta de datos y separación de conjuntos | 1,5 |
| Entrenamiento, normalización y guardado del modelo | 2,0 |
| Inferencia y evaluación con matriz de confusión | 2,0 |
| Comparación razonada de valores de `k` | 1,5 |
| Medición y registro del rendimiento | 1,5 |
| Documentación, análisis crítico y demostración | 1,5 |
| **Total** | **10,0** |

### Comprobación final

```bash
cd ~/practicas/capitulo15
source .venv/bin/activate
python -m py_compile 01_generar_datos.py 02_entrenar_knn.py 03_evaluar_knn.py 04_benchmark_knn.py
python 01_generar_datos.py
python 02_entrenar_knn.py
python 03_evaluar_knn.py
python 03_evaluar_knn.py --temperatura 25 --humedad 55
python 04_benchmark_knn.py
ls -lh datos/*.csv modelos/*.json resultados/*.csv
```

## 15.13. Resolución de problemas frecuentes

| Incidencia | Causa probable | Solución |
|---|---|---|
| `SyntaxError: Non-UTF-8 code` | Archivo guardado con codificación incorrecta | Guardar como UTF-8 y evitar caracteres no ASCII en el código |
| `bash: import: command not found` | Código Python pegado en Bash | Crear el archivo con `nano` y ejecutarlo con Python |
| `FileNotFoundError` | No se ejecutaron los programas anteriores | Ejecutar primero `01_generar_datos.py` y `02_entrenar_knn.py` |
| `No module named ...` | Entorno o dependencias incorrectos | Confirmar el intérprete; los ejemplos solo usan biblioteca estándar |
| `Formato de modelo incompatible` | JSON modificado o modelo de otro programa | Regenerar el JSON con `02_entrenar_knn.py` |
| Exactitud diferente de la esperada | Cambios en datos o en `k` | Revisar la semilla y el archivo del modelo |
| Resultados poco realistas | Datos sintéticos y clases simplificadas | Validar con mediciones reales en una fase posterior |
| Tiempos variables | Carga del sistema | Repetir pruebas y comparar promedios |

!!! tip "Diagnóstico rápido"
    Ante un error, comprueba el directorio actual con `pwd`, los archivos con `ls -l`, la sintaxis con `python -m py_compile` y el contenido del modelo con `python -m json.tool modelos/modelo_knn.json`.

## 15.14. Autoevaluación

1. ¿Qué diferencia existe entre clasificación y regresión?
2. ¿Qué almacena un modelo k-NN?
3. ¿Por qué es importante normalizar temperatura y humedad?
4. ¿Por qué calculamos la normalización solo con datos de entrenamiento?
5. ¿Qué significa una celda fuera de la diagonal de la matriz de confusión?
6. ¿Qué efecto puede tener modificar el valor de `k`?
7. ¿Por qué la fracción de votos no es una probabilidad calibrada?
8. ¿Por qué una buena exactitud con datos sintéticos no garantiza funcionamiento real?
9. ¿Qué diferencia existe entre el formato de un modelo y su motor de inferencia?
10. ¿Qué factores debemos medir antes de desplegar IA en un dispositivo de borde?

## 15.15. Resumen del capítulo

Hemos avanzado desde el primer clasificador de centroides del capítulo 14 hasta un modelo k-NN reproducible y versionado. Hemos generado conjuntos independientes de entrenamiento y prueba, normalizado correctamente las variables, evaluado predicciones con una matriz de confusión, medido la latencia y registrado resultados.

También hemos identificado los límites de los datos simulados y los requisitos para desplegar modelos más complejos en Arduino UNO Q. En el **capítulo 16, Visión artificial**, aplicaremos los conceptos de inferencia a imágenes y estudiaremos sus requisitos de adquisición y procesamiento.

## 15.16. Referencias y ampliación

- Documentación de Python: <https://docs.python.org/3/>
- Documentación de Arduino: <https://docs.arduino.cc/>
- Introducción a aprendizaje automático de Google: <https://developers.google.com/machine-learning/crash-course>
- Guía de scikit-learn sobre vecinos próximos: <https://scikit-learn.org/stable/modules/neighbors.html>
- Documentación de ONNX: <https://onnx.ai/>

!!! note "Continuidad del libro"
    Los ejemplos se han diseñado para ejecutarse con Python estándar sobre Linux, sin presuponer bibliotecas de IA, controladores especiales ni aceleradores configurados. La compatibilidad de herramientas de inferencia más avanzadas se estudiará antes de instalarlas.
