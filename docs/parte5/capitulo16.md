# Capítulo 16. Visión artificial y reconocimiento

**Parte V — Inteligencia artificial en Arduino UNO Q**

En el capítulo 15 hemos entrenado, evaluado y medido modelos de clasificación. En este capítulo aplicaremos la misma metodología a imágenes: adquisición, preprocesamiento, extracción de características, reconocimiento y evaluación. Trabajaremos sobre el entorno Linux del Arduino UNO Q mediante Python y OpenCV. La cámara USB compatible con UVC es **opcional**: todas las prácticas esenciales pueden realizarse con imágenes de prueba generadas por los propios programas.

!!! note "Convención de codificación"
    El texto del libro utiliza tildes normalmente. **El código Python y los nombres de archivos utilizan únicamente caracteres ASCII**: sin tildes, eñes ni símbolos especiales, incluidos los símbolos de grados. Los archivos `.py` deben guardarse en UTF-8.

## 16.1. Objetivos de aprendizaje

Al finalizar el capítulo, el alumnado será capaz de:

1. Diferenciar visión artificial, procesamiento de imágenes, detección y reconocimiento.
2. Explicar cómo se representa una imagen digital mediante píxeles, canales y resolución.
3. Preparar un entorno Python aislado para trabajar con OpenCV en Linux.
4. Obtener imágenes desde archivos y, opcionalmente, desde una cámara USB.
5. Aplicar escala de grises, suavizado, umbralización y operaciones morfológicas.
6. Detectar objetos sencillos mediante contornos y describirlos con medidas geométricas.
7. Clasificar figuras por sus características y cuantificar errores.
8. Guardar evidencias y documentar las limitaciones de un sistema de visión Edge AI.

## 16.2. ¿Qué es la visión artificial?

La **visión artificial** reúne técnicas que permiten a un sistema informático obtener información útil de imágenes o vídeo. No toda visión artificial requiere aprendizaje automático: un algoritmo que detecta un objeto mediante su color o su contorno también es visión artificial.

- **Adquisición:** obtener una imagen de una cámara o archivo.
- **Preprocesamiento:** mejorar o transformar la imagen para facilitar el análisis.
- **Segmentación:** separar las regiones de interés del fondo.
- **Extracción de características:** medir área, perímetro, color, forma o textura.
- **Reconocimiento:** asignar una clase o identidad a partir de las características.
- **Decisión:** generar un resultado utilizable por otra aplicación.

!!! tip "Relación con el capítulo 15"
    El reconocimiento puede hacerse mediante reglas geométricas o mediante un modelo entrenado. En este capítulo construiremos primero una solución explicable basada en contornos. En capítulos posteriores podremos conectar sus resultados con sensores, actuadores y modelos de IA.

### 16.2.1. Imagen digital y representación

Una imagen en color puede representarse mediante una matriz de altura × anchura × canales. OpenCV suele trabajar con el orden de canales **BGR**, no RGB. En escala de grises, cada píxel se representa normalmente con un valor de 0 a 255.

| Concepto | Ejemplo | Consecuencia |
|---|---|---|
| Resolución | 640 × 480 píxeles | 307.200 píxeles por imagen |
| Escala de grises | Un canal | Menos información que en color |
| BGR | Tres canales | Hay que respetar el orden de canales |
| FPS | Fotogramas por segundo | Más FPS implica más trabajo de procesamiento |
| Latencia | Milisegundos por imagen | Condiciona la respuesta en tiempo real |

Una imagen de 640 × 480 con tres canales de 8 bits ocupa aproximadamente 921.600 bytes **sin comprimir**. Un JPEG puede ocupar mucho menos, según el contenido y la compresión.

## 16.3. Arquitectura de trabajo en Arduino UNO Q

Las prácticas de este capítulo se ejecutan en el entorno Linux de la placa. El flujo es:

```text
Imagen de archivo / Camara USB (opcional)
                  |
                  v
          Python + OpenCV
                  |
                  v
     Procesamiento y reconocimiento
                  |
                  v
      PNG + CSV + informe tecnico
```

El uso de OpenCV en Python **no implica automáticamente** que el algoritmo esté acelerado por una NPU o GPU. Las prácticas propuestas son procesamiento local en el procesador Linux. La aceleración específica requiere un entorno y modelos compatibles, que no se presuponen instalados.

!!! warning "Cámara y permisos"
    No se presupone que Arduino UNO Q tenga una cámara conectada ni que una cámara concreta sea compatible. La captura en vivo es opcional y se comprobará antes de utilizarla. No se realizarán prácticas de identificación biométrica de personas.

## 16.4. Preparación del entorno

Accede al Arduino UNO Q por SSH y ejecuta:

```bash
mkdir -p ~/practicas/capitulo16/{imagenes,resultados,datos}
cd ~/practicas/capitulo16
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy opencv-python-headless
```

La variante `opencv-python-headless` evita depender de un escritorio gráfico para las prácticas con imágenes guardadas en disco. Si `pip` no encuentra una rueda compatible o intenta compilar OpenCV, **no continúes con una compilación larga sin revisarlo**: consulta la versión de Python, la arquitectura y las dependencias disponibles. En algunos entornos Debian puede ser más conveniente instalar `python3-opencv` y `python3-numpy` mediante `apt` y usar el Python del sistema, sin mezclar ambos métodos indiscriminadamente.

Verifica:

```bash
python -c "import cv2, numpy; print('OpenCV:', cv2.__version__); print('NumPy:', numpy.__version__)"
```

!!! warning "Entorno virtual"
    Si vuelve a aparecer el error `ensurepip is not available`, instala el paquete `python3.X-venv` correspondiente a la versión real de Python y recrea `.venv`, como hicimos en el capítulo 8. No uses `sudo pip install` para modificar el Python del sistema.

### 16.4.1. Verificar espacio disponible

```bash
df -h ~
free -h
```

### 16.4.2. Organización de archivos

```text
~/practicas/capitulo16/
|-- .venv/
|-- 01_generar_imagenes.py
|-- 02_procesar_imagen.py
|-- 03_reconocer_formas.py
|-- 04_evaluar_reconocimiento.py
|-- 05_capturar_camara.py       (opcional)
|-- imagenes/
|-- resultados/
`-- datos/
```

Los archivos de programa se crearán con `nano` o se copiarán mediante SCP desde VS Code. Los comandos de Linux se escriben en la terminal; el código Python se guarda dentro de archivos `.py`.

## 16.5. Programa 1 — Generación de imágenes de prueba

Antes de conectar una cámara, crearemos imágenes reproducibles con círculos, rectángulos y triángulos. Esta estrategia permite que todos los alumnos obtengan los mismos resultados y evita depender de condiciones de iluminación.

Crea el archivo:

```bash
nano 01_generar_imagenes.py
```

```python
from pathlib import Path

import cv2
import numpy as np

BASE = Path.home() / "practicas" / "capitulo16"
IMAGENES = BASE / "imagenes"
IMAGENES.mkdir(parents=True, exist_ok=True)


def crear_lienzo():
    return np.full((480, 640, 3), 255, dtype=np.uint8)


def guardar(nombre, imagen):
    destino = IMAGENES / nombre
    if not cv2.imwrite(str(destino), imagen):
        raise RuntimeError("No se pudo guardar la imagen")
    print("Guardada:", destino)


def main():
    imagen = crear_lienzo()
    cv2.circle(imagen, (320, 240), 95, (0, 0, 0), -1)
    guardar("circulo.png", imagen)

    imagen = crear_lienzo()
    cv2.rectangle(imagen, (200, 140), (440, 340), (0, 0, 0), -1)
    guardar("rectangulo.png", imagen)

    imagen = crear_lienzo()
    vertices = np.array([[320, 110], [180, 360], [460, 360]], dtype=np.int32)
    cv2.fillPoly(imagen, [vertices], (0, 0, 0))
    guardar("triangulo.png", imagen)


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
python -m py_compile 01_generar_imagenes.py
python 01_generar_imagenes.py
ls -lh imagenes/
```

**Resultado esperado:** tres archivos PNG. Las figuras son negras sobre fondo blanco, de modo que su segmentación será sencilla.

!!! example "Actividad 16.1 — Comprender los píxeles"
    Modifica la resolución del lienzo a 800 × 600 y genera de nuevo las imágenes. Comprueba sus dimensiones con un pequeño script o mediante `file imagenes/circulo.png`. Explica cómo cambia el número total de píxeles.

## 16.6. Programa 2 — Preprocesamiento de imágenes

El preprocesamiento convierte una imagen BGR en una imagen de grises, aplica un filtro gaussiano y crea una máscara binaria. Utilizaremos un umbral automático de Otsu para no depender de un valor fijo.

```bash
nano 02_procesar_imagen.py
```

```python
from pathlib import Path

import cv2

BASE = Path.home() / "practicas" / "capitulo16"
ORIGEN = BASE / "imagenes" / "circulo.png"
SALIDA = BASE / "resultados"
SALIDA.mkdir(parents=True, exist_ok=True)


def guardar(nombre, imagen):
    if not cv2.imwrite(str(SALIDA / nombre), imagen):
        raise RuntimeError("Error al guardar la imagen")


def main():
    imagen = cv2.imread(str(ORIGEN))
    if imagen is None:
        raise FileNotFoundError(f"No se puede abrir: {ORIGEN}")

    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    suave = cv2.GaussianBlur(gris, (5, 5), 0)
    umbral, mascara = cv2.threshold(
        suave, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    limpia = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)

    guardar("01_grises.png", gris)
    guardar("02_suavizada.png", suave)
    guardar("03_mascara.png", mascara)
    guardar("04_mascara_limpia.png", limpia)
    print("Umbral Otsu:", umbral)
    print("Imagenes guardadas en:", SALIDA)


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
python -m py_compile 02_procesar_imagen.py
python 02_procesar_imagen.py
ls -lh resultados/
```

### 16.6.1. ¿Por qué invertimos el umbral?

En las imágenes generadas, la figura es negra y el fondo blanco. `THRESH_BINARY_INV` convierte la figura en blanco (255) y el fondo en negro (0), formato adecuado para detectar contornos del objeto.

### 16.6.2. Operaciones morfológicas

La apertura morfológica (`MORPH_OPEN`) ayuda a eliminar pequeñas regiones aisladas. Un kernel demasiado grande puede deformar o eliminar objetos pequeños. La elección del tamaño es una decisión técnica que debe justificarse.

!!! example "Actividad 16.2 — Comparar filtros"
    Cambia el tamaño del filtro gaussiano de `(5, 5)` a `(11, 11)` y compara las máscaras. Repite con un kernel morfológico de `(7, 7)`. Documenta qué bordes se suavizan y si se modifica la forma detectada.

## 16.7. Programa 3 — Reconocimiento de formas por contornos

Ahora implementaremos un clasificador sencillo y explicable. Se detectará el contorno principal y se aproximará mediante un polígono: tres vértices indican un triángulo; cuatro, un cuadrilátero; más vértices, una figura aproximadamente circular si su circularidad es suficiente.

La **circularidad** se calcula como:

\[
C = rac{4\pi A}{P^2}
\]

Donde \(A\) es el área y \(P\) el perímetro. Para un círculo ideal, \(C\) se aproxima a 1. En imágenes digitales, la discretización introduce diferencias.

```bash
nano 03_reconocer_formas.py
```

```python
import csv
import math
from pathlib import Path

import cv2

BASE = Path.home() / "practicas" / "capitulo16"
IMAGENES = BASE / "imagenes"
SALIDA = BASE / "resultados"
DATOS = BASE / "datos"
SALIDA.mkdir(parents=True, exist_ok=True)
DATOS.mkdir(parents=True, exist_ok=True)


def clasificar_contorno(contorno):
    area = cv2.contourArea(contorno)
    perimetro = cv2.arcLength(contorno, True)
    if area < 500 or perimetro <= 0:
        return "sin_objeto", area, 0.0

    aproximacion = cv2.approxPolyDP(contorno, 0.025 * perimetro, True)
    vertices = len(aproximacion)
    circularidad = 4.0 * math.pi * area / (perimetro * perimetro)

    if vertices == 3:
        clase = "triangulo"
    elif vertices == 4:
        clase = "rectangulo"
    elif circularidad >= 0.78:
        clase = "circulo"
    else:
        clase = "desconocido"

    return clase, area, circularidad


def reconocer(ruta):
    imagen = cv2.imread(str(ruta))
    if imagen is None:
        raise FileNotFoundError(f"No se puede abrir: {ruta}")

    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    gris = cv2.GaussianBlur(gris, (5, 5), 0)
    _, mascara = cv2.threshold(
        gris, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    contornos, _ = cv2.findContours(
        mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contornos:
        return "sin_objeto", 0.0, 0.0, imagen

    principal = max(contornos, key=cv2.contourArea)
    clase, area, circularidad = clasificar_contorno(principal)
    cv2.drawContours(imagen, [principal], -1, (0, 0, 255), 3)
    cv2.putText(
        imagen, clase, (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
        1.0, (255, 0, 0), 2
    )
    return clase, area, circularidad, imagen


def main():
    rutas = sorted(IMAGENES.glob("*.png"))
    if not rutas:
        raise RuntimeError("No hay imagenes PNG para analizar")

    registros = []
    for ruta in rutas:
        clase, area, circularidad, anotada = reconocer(ruta)
        destino = SALIDA / f"detectada_{ruta.name}"
        if not cv2.imwrite(str(destino), anotada):
            raise RuntimeError(f"No se pudo guardar: {destino}")
        registros.append([ruta.name, clase, round(area, 2), round(circularidad, 3)])
        print(ruta.name, "->", clase)

    with (DATOS / "reconocimiento.csv").open(
        "w", newline="", encoding="utf-8"
    ) as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["archivo", "clase", "area_px", "circularidad"])
        escritor.writerows(registros)

    print("Resultados:", DATOS / "reconocimiento.csv")


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
python -m py_compile 03_reconocer_formas.py
python 03_reconocer_formas.py
cat datos/reconocimiento.csv
```

**Resultado esperado:** reconocimiento de `circulo.png`, `rectangulo.png` y `triangulo.png`, y creación de tres imágenes anotadas. Las mediciones exactas dependen de la discretización de píxeles y de la versión de OpenCV.

!!! warning "Limitación del algoritmo"
    El programa identifica **un único objeto principal por imagen** y supone figuras oscuras sobre fondo claro. No reconoce objetos arbitrarios, no distingue identidades de personas y no equivale a un modelo neuronal entrenado. En un entorno real habría que gestionar iluminación, perspectiva, oclusiones y varios objetos.

!!! example "Actividad 16.3 — Análisis de errores"
    Cambia el parámetro `0.025` de `approxPolyDP` a `0.01` y a `0.06`. Compara las clases obtenidas. Explica por qué la cantidad de vértices aproximados depende de ese parámetro.

## 16.8. Programa 4 — Evaluación del reconocimiento

Un sistema de reconocimiento no debe evaluarse únicamente por una imagen que funciona. Compararemos las predicciones con las etiquetas esperadas y calcularemos la exactitud.

Para evitar confundir entrenamiento y evaluación, aquí **no entrenamos** ningún modelo: evaluamos un clasificador determinista sobre tres imágenes de referencia. La exactitud obtenida en este conjunto reducido no representa el rendimiento en imágenes reales.

```bash
nano 04_evaluar_reconocimiento.py
```

```python
import csv
from pathlib import Path

from importlib.machinery import SourceFileLoader

BASE = Path.home() / "practicas" / "capitulo16"
DATOS = BASE / "datos"
DATOS.mkdir(parents=True, exist_ok=True)

ESPERADO = {
    "circulo.png": "circulo",
    "rectangulo.png": "rectangulo",
    "triangulo.png": "triangulo",
}


def main():
    origen = DATOS / "reconocimiento.csv"
    if not origen.exists():
        raise FileNotFoundError("Ejecuta antes 03_reconocer_formas.py")

    with origen.open("r", encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))

    predicciones = {fila["archivo"]: fila["clase"] for fila in filas}
    correctas = 0
    for nombre, clase in ESPERADO.items():
        prediccion = predicciones.get(nombre, "sin_resultado")
        acierto = prediccion == clase
        correctas += int(acierto)
        print(nombre, "esperado:", clase, "obtenido:", prediccion,
              "acierto:", acierto)

    total = len(ESPERADO)
    exactitud = 100.0 * correctas / total
    print(f"Exactitud: {correctas}/{total} = {exactitud:.1f}%")

    with (DATOS / "evaluacion.csv").open(
        "w", encoding="utf-8", newline=""
    ) as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["total", "correctas", "exactitud_pct"])
        escritor.writerow([total, correctas, round(exactitud, 1)])


if __name__ == "__main__":
    main()
```

Ejecuta:

```bash
python -m py_compile 04_evaluar_reconocimiento.py
python 04_evaluar_reconocimiento.py
cat datos/evaluacion.csv
```

!!! note "Interpretación de la exactitud"
    Obtener 100 % sobre tres imágenes sintéticas solo confirma que el algoritmo funciona en ese conjunto concreto. Para una evaluación más rigurosa deben añadirse imágenes nuevas, cambios de tamaño, rotación, iluminación, ruido y fondos distintos.

!!! example "Actividad 16.4 — Robustez"
    Genera tres imágenes adicionales con objetos desplazados o girados. Añade sus etiquetas esperadas al diccionario `ESPERADO` y ejecuta nuevamente el reconocimiento y la evaluación. Presenta los errores encontrados.

## 16.9. Programa 5 (opcional) — Captura desde una cámara USB

Esta actividad requiere una cámara USB compatible, reconocida por Linux, y permisos para acceder al dispositivo. No es obligatoria para completar el capítulo.

### 16.9.1. Comprobaciones previas

Conecta la cámara y ejecuta:

```bash
ls -l /dev/video* 2>/dev/null || echo "No se detectan dispositivos de video"
```

Si dispones de la utilidad `v4l2-ctl`:

```bash
v4l2-ctl --list-devices
```

Si no está instalada, puedes consultar la disponibilidad del paquete `v4l-utils` en Debian. No instales controladores de procedencia desconocida.

### 16.9.2. Capturar un fotograma

```bash
nano 05_capturar_camara.py
```

```python
from pathlib import Path

import cv2

DESTINO = Path.home() / "practicas" / "capitulo16" / "imagenes" / "captura.png"


def main():
    camara = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not camara.isOpened():
        raise RuntimeError("No se puede abrir la camara /dev/video0")

    try:
        correcto, imagen = camara.read()
        if not correcto or imagen is None:
            raise RuntimeError("No se ha podido capturar un fotograma")
        DESTINO.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(DESTINO), imagen):
            raise RuntimeError("No se ha podido guardar la captura")
        print("Captura guardada:", DESTINO)
    finally:
        camara.release()


if __name__ == "__main__":
    main()
```

```bash
python -m py_compile 05_capturar_camara.py
python 05_capturar_camara.py
```

!!! warning "Privacidad y uso responsable"
    Captura únicamente objetos o escenas autorizadas. No grabes ni identifiques personas sin una finalidad legítima y las garantías correspondientes. La actividad se centra en figuras geométricas y objetos inanimados.

!!! example "Actividad 16.5 — Del archivo a la cámara"
    Si dispones de cámara, coloca una figura negra sobre una hoja blanca, captura la imagen y compárala con las imágenes sintéticas. Identifica sombras, ruido y diferencias de perspectiva. La detección puede fallar: explica por qué.

## 16.10. Medición del rendimiento y límites de Edge AI

En sistemas embebidos no basta con obtener un resultado: también importa el tiempo de ejecución y el consumo de recursos. Puedes medir la duración global de un programa mediante:

```bash
/usr/bin/time -f "Tiempo real: %e s | Memoria maxima: %M KB" \
    .venv/bin/python 03_reconocer_formas.py
```

El tiempo global incluye el arranque de Python, la importación de bibliotecas y el acceso al almacenamiento. **No equivale** al tiempo de inferencia de un modelo. Para medir solo una etapa, usa `time.perf_counter()` alrededor del procesamiento y repite suficientes veces.

### 16.10.1. Comparación de enfoques

| Enfoque | Ventaja | Limitación |
|---|---|---|
| Reglas geométricas | Fácil de explicar y depurar | Sensible a fondos y perspectiva |
| Clasificador entrenado | Aprende patrones de ejemplos | Necesita datos representativos |
| Red neuronal de visión | Puede reconocer patrones complejos | Mayor coste de memoria y cómputo |
| Procesamiento en la nube | Puede aprovechar servidores potentes | Depende de red, latencia y privacidad |
| Procesamiento local | Reduce dependencia de Internet | Recursos limitados del dispositivo |

### 16.10.2. Buenas prácticas

- Reducir resolución cuando sea compatible con la precisión requerida.
- Evitar cargar repetidamente archivos o modelos innecesarios.
- Registrar las versiones de Python, NumPy y OpenCV.
- Evaluar con imágenes distintas de las utilizadas para ajustar parámetros.
- Tratar los resultados como estimaciones, no como certezas absolutas.
- Mantener el procesamiento local cuando sea suficiente y respete las necesidades del proyecto.

## 16.11. Práctica integradora evaluable

### Título: Sistema de reconocimiento de figuras en Arduino UNO Q

**Modalidad:** parejas. **Duración orientativa:** 3-4 horas de taller, adaptable al calendario del módulo. **Material:** Arduino UNO Q, conexión SSH, Python, OpenCV y NumPy; cámara USB opcional.

### Situación profesional

Una empresa desea incorporar un nodo de inspección visual que clasifique piezas sencillas antes de su registro. El alumnado debe construir un prototipo capaz de analizar imágenes, asignar una clase y almacenar evidencias de sus resultados.

### Requisitos mínimos

1. Preparar el entorno de trabajo y justificar las dependencias instaladas.
2. Generar al menos tres imágenes de referencia y otras tres imágenes de prueba modificadas.
3. Aplicar preprocesamiento y conservar una máscara binaria de ejemplo.
4. Reconocer las figuras mediante contornos y generar un CSV de resultados.
5. Evaluar los aciertos sobre un conjunto de prueba y explicar al menos una limitación.
6. Medir el tiempo de ejecución y documentar el procedimiento de verificación.
7. Presentar una memoria breve con capturas o archivos de salida y conclusiones.

### Entregables

- Código fuente `.py` y listado de dependencias utilizadas.
- Carpeta `imagenes/` con imágenes originales y de prueba.
- Carpeta `resultados/` con máscaras e imágenes anotadas.
- Archivos `datos/reconocimiento.csv` y `datos/evaluacion.csv`.
- Informe técnico en PDF o Markdown con procedimiento, incidencias, pruebas y conclusiones.

### Rúbrica de evaluación

| Criterio | Puntuación máxima |
|---|---:|
| Preparación del entorno y organización de archivos | 1,0 |
| Generación y adquisición de imágenes | 1,5 |
| Preprocesamiento y explicación técnica | 1,5 |
| Detección y reconocimiento funcional | 2,0 |
| Evaluación, pruebas y análisis de errores | 2,0 |
| Medición del rendimiento y conclusiones | 1,0 |
| Calidad del código y documentación | 1,0 |
| **Total** | **10,0** |

!!! note "Evaluación competencial"
    La rúbrica es una propuesta docente. Su relación formal con los resultados de aprendizaje y criterios de evaluación del módulo debe establecerse en la programación del centro. El éxito del prototipo no sustituye la valoración del procedimiento técnico y de las evidencias.

## 16.12. Resolución de problemas

| Síntoma | Posible causa | Comprobación o solución |
|---|---|---|
| `ModuleNotFoundError: cv2` | OpenCV no instalado en el intérprete activo | Activar `.venv` y ejecutar `python -m pip show opencv-python-headless` |
| Error al crear `.venv` | Falta `ensurepip` | Instalar el paquete `python3.X-venv` correspondiente |
| `cv2.imread()` devuelve `None` | Ruta incorrecta o imagen ilegible | Revisar `ls -l imagenes/` y la ruta absoluta |
| `cv2.imwrite()` devuelve `False` | Carpeta inexistente o sin permisos | Crear directorio y revisar permisos |
| No se detectan contornos | Umbral o contraste inadecuados | Revisar la máscara guardada |
| Círculo clasificado como desconocido | Circularidad baja o contorno deformado | Ajustar iluminación, umbral y tolerancia |
| Error de cámara | Dispositivo ausente, ocupado o incompatible | Revisar `/dev/video*` y permisos |
| La ejecución es lenta | Resolución alta o recursos limitados | Reducir resolución y medir tiempos |
| Error de codificación | Archivo Python guardado en codificación no UTF-8 | Guardar como UTF-8 y mantener código ASCII |

### 16.12.1. Verificación completa de sintaxis

```bash
cd ~/practicas/capitulo16
source .venv/bin/activate
python -m py_compile 01_generar_imagenes.py
python -m py_compile 02_procesar_imagen.py
python -m py_compile 03_reconocer_formas.py
python -m py_compile 04_evaluar_reconocimiento.py
```

### 16.12.2. Secuencia completa de ejecución

```bash
python 01_generar_imagenes.py
python 02_procesar_imagen.py
python 03_reconocer_formas.py
python 04_evaluar_reconocimiento.py
cat datos/reconocimiento.csv
cat datos/evaluacion.csv
```

## 16.13. Autoevaluación

1. ¿Por qué la visión artificial no requiere siempre redes neuronales?
2. ¿Qué diferencia existe entre una imagen BGR y una imagen en escala de grises?
3. ¿Qué información proporciona una máscara binaria?
4. ¿Por qué la apertura morfológica puede eliminar ruido?
5. ¿Cómo se utiliza la circularidad para identificar formas aproximadamente circulares?
6. ¿Qué problemas aparecen al pasar de imágenes sintéticas a fotografías reales?
7. ¿Por qué una exactitud del 100 % sobre tres imágenes no garantiza un buen sistema?
8. ¿Qué diferencia hay entre tiempo total de ejecución y tiempo de inferencia?
9. ¿Qué ventajas ofrece procesar las imágenes localmente?
10. ¿Qué precauciones deben adoptarse al capturar imágenes en un entorno educativo?

## 16.14. Resumen

Hemos desarrollado un flujo completo de visión artificial: generación de imágenes, preprocesamiento, segmentación, detección de contornos, reconocimiento, evaluación y registro de resultados. El sistema funciona con archivos, sin necesidad de cámara, y puede ampliarse con captura USB cuando el hardware lo permita. También hemos identificado las limitaciones de los clasificadores basados en reglas y la importancia de evaluar la robustez antes de utilizar el sistema en condiciones reales.

**Conexión con el capítulo 17:** en *IA con sensores y actuadores* integraremos resultados de procesamiento y clasificación con decisiones sobre dispositivos, registros y servicios IoT.

## 16.15. Referencias y documentación técnica

- [Documentación oficial de OpenCV](https://docs.opencv.org/4.x/)
- [Documentación oficial de NumPy](https://numpy.org/doc/stable/)
- [Python: entornos virtuales `venv`](https://docs.python.org/3/library/venv.html)
- [OpenCV Python Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

!!! tip "Publicación con MkDocs"
    Guarda este archivo como `docs/parte5/capitulo16.md`, añade su entrada a `mkdocs.yml` dentro de la Parte V y ejecuta `mkdocs build --strict` antes de publicar con `mkdocs gh-deploy`.

