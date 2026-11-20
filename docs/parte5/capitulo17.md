# Capítulo 17. Integración de IA con sensores y actuadores

!!! info "Parte V — Inteligencia artificial en Arduino UNO Q"
    En este capítulo construiremos un sistema de decisión Edge AI que recibe lecturas ambientales, realiza inferencia local y propone acciones de control. Empezaremos en **modo simulación**, sin activar salidas físicas, para poder reproducir las pruebas en cualquier Arduino UNO Q.

## 17.1. Objetivos de aprendizaje

Al finalizar este capítulo, el alumnado será capaz de:

- Explicar el flujo **sensor → adquisición → preprocesamiento → modelo → decisión → actuador**.
- Distinguir la predicción de un modelo de la activación real de un dispositivo.
- Generar datos de prueba y crear un modelo k-NN sencillo en Python.
- Ejecutar inferencia local sin depender de servicios en la nube.
- Registrar decisiones y tiempos de respuesta para analizarlos.
- Aplicar medidas de seguridad antes de controlar hardware real.
- Relacionar el sistema con MQTT, InfluxDB y Grafana, estudiados en los capítulos 12 y 13.

## 17.2. De los modelos de IA al control de dispositivos

En el capítulo 15 entrenamos y evaluamos modelos; en el 16 analizamos imágenes. Ahora conectaremos las predicciones con decisiones que podrían afectar al mundo físico.

Un **sensor** transforma una magnitud física (temperatura, humedad, luz, movimiento) en una señal o un dato digital. Un **actuador** ejecuta una acción: encender un ventilador, mover un servomotor, activar un relé o iluminar un LED.

El modelo de IA se sitúa entre la adquisición y la decisión. En lugar de enviar los datos a un servidor remoto, **Edge AI** realiza la inferencia en el propio equipo. Esto puede reducir la latencia, el tráfico de red y la exposición de datos, aunque no garantiza por sí mismo un sistema seguro.

```text
Sensores → Lectura y validación → Normalización → Modelo IA
                                                  ↓
Registro CSV / MQTT / InfluxDB ← Decisión segura ← Predicción
                                                  ↓
                                         Actuador (opcional)
```

!!! warning "Predicción no equivale a control seguro"
    Ningún programa de este capítulo conecta automáticamente un motor, un relé o una carga eléctrica. Antes de controlar un actuador real hay que verificar tensiones, corrientes, alimentación, aislamiento, estado inicial, parada de emergencia y comportamiento ante fallos. No se deben conectar cargas de potencia directamente a los pines de la placa.

### 17.2.1. Dos procesadores, dos responsabilidades

Arduino UNO Q combina un entorno Linux, adecuado para ejecutar Python y tareas de IA, con un microcontrolador destinado a la interacción con entradas y salidas. El intercambio entre ambos debe diseñarse de acuerdo con las interfaces y herramientas efectivamente disponibles en la versión instalada del sistema.

En esta práctica utilizaremos **Python en Linux** para simular lecturas y generar decisiones. La conexión posterior con sensores y actuadores físicos será una ampliación guiada, no un requisito para completar la práctica.

### 17.2.2. Reglas frente a modelos aprendidos

Una regla como `temperatura >= 27` es programación convencional. Un clasificador k-NN compara una lectura nueva con ejemplos etiquetados y decide según sus vecinos. **Si las etiquetas se generan mediante una regla, el modelo solo aprende a imitar esa regla**: no descubre por sí mismo la temperatura óptima ni constituye un control industrial certificado.

Para un proyecto real necesitaríamos lecturas auténticas, etiquetas fiables, separación entre entrenamiento y prueba, métricas y supervisión humana.

## 17.3. Arquitectura de la práctica

Construiremos un prototipo de ventilación inteligente con tres variables:

| Variable | Unidad | Uso |
|---|---|---|
| Temperatura | °C | Principal indicador térmico |
| Humedad relativa | % | Variable ambiental complementaria |
| Luz | % (escala simulada) | Contexto adicional para el modelo |

La salida será una **propuesta**: `0 = ventilacion apagada` o `1 = ventilacion encendida`. El sistema no activa físicamente ningún ventilador.

El flujo consta de cuatro programas:

1. `01_generar_lecturas.py`: crea 120 muestras ambientales simuladas.
2. `02_entrenar_modelo.py`: construye un modelo k-NN y lo guarda en JSON.
3. `03_control_edge.py`: ejecuta inferencia local y registra las decisiones.
4. `04_validar_seguridad.py`: comprueba rangos y cuenta cambios de estado.

!!! note "Alcance didáctico"
    Los datos son sintéticos y las etiquetas del entrenamiento se calculan con una regla de referencia. La práctica demuestra la integración de un modelo con una cadena de decisión, pero **no valida su precisión con datos reales independientes**. Tampoco implementa histéresis ni protección eléctrica para un actuador físico.

## 17.4. Preparación del entorno

Conecta mediante SSH o PuTTY al Arduino UNO Q. El prompt puede tener este aspecto:

```bash
arduino@UNO-Q-JOSE:~$
```

Crea la estructura de carpetas:

```bash
mkdir -p ~/practicas/capitulo17/{datos,modelos,resultados}
cd ~/practicas/capitulo17
```

Comprueba la versión de Python:

```bash
python3 --version
```

Los ejemplos emplean **solo la biblioteca estándar de Python**: `csv`, `json`, `math`, `random`, `pathlib` y `time`. Por tanto, no necesitan instalar paquetes externos. Si deseas mantener un entorno aislado, puedes crearlo así:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Si falla la creación del entorno virtual por ausencia de `ensurepip`, utiliza la solución que aplicamos en capítulos anteriores (`python3.13-venv` para Python 3.13), o ejecuta los programas directamente con `python3`.

!!! tip "Cómo crear los archivos"
    Sitúate en `~/practicas/capitulo17`, ejecuta `nano nombre_del_archivo.py`, pega el programa correspondiente, guarda con `Ctrl + O`, confirma con `Enter` y sal con `Ctrl + X`. Los programas Python de este capítulo contienen únicamente caracteres ASCII para evitar problemas de codificación; el texto explicativo mantiene la ortografía española.

## 17.5. Programa 1: adquisición de lecturas simuladas

En un sistema real, las lecturas llegarían de sensores físicos o de un servicio MQTT. Para empezar, generaremos una secuencia reproducible de temperaturas, humedades y niveles de luz.

El programa fija una semilla aleatoria, crea un fichero CSV con cabecera y guarda 120 muestras. Los valores cambian suavemente para representar un entorno variable.

**Archivo:** `01_generar_lecturas.py`

```python
from pathlib import Path
import csv
import math
import random

BASE = Path(__file__).resolve().parent
DESTINO = BASE / "datos" / "lecturas.csv"
DESTINO.parent.mkdir(parents=True, exist_ok=True)
random.seed(17)

with DESTINO.open("w", newline="", encoding="utf-8") as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow(["instante", "temperatura", "humedad", "luz"])
    for i in range(120):
        temperatura = 23 + 5 * math.sin(i / 14) + random.uniform(-0.7, 0.7)
        humedad = 56 - 9 * math.sin(i / 14) + random.uniform(-2, 2)
        luz = 55 + 35 * math.sin(i / 11) + random.uniform(-5, 5)
        escritor.writerow([i, round(temperatura, 2), round(humedad, 2), round(max(0, min(100, luz)), 2)])

print("Archivo generado:", DESTINO)
print("Lecturas simuladas: 120")
```

**Ejecución:**

```bash
python3 01_generar_lecturas.py
```

**Comprobación:**

```bash
head -n 6 datos/lecturas.csv
wc -l datos/lecturas.csv
```

El archivo debe contener 121 líneas: una cabecera y 120 lecturas.


## 17.6. Programa 2: entrenamiento del modelo

El clasificador **k-NN** conserva ejemplos etiquetados. En la inferencia calcula distancias normalizadas, selecciona los cinco vecinos más cercanos y decide por mayoría. La normalización impide que una variable con escala numérica grande domine la distancia. El archivo JSON incluye ejemplos, escalas, etiquetas y el origen de las etiquetas.

**Archivo:** `02_entrenar_modelo.py`

```python
from pathlib import Path
import csv
import json

BASE = Path(__file__).resolve().parent
ORIGEN = BASE / "datos" / "lecturas.csv"
DESTINO = BASE / "modelos" / "modelo_ventilacion.json"
DESTINO.parent.mkdir(parents=True, exist_ok=True)

with ORIGEN.open(newline="", encoding="utf-8") as archivo:
    filas = list(csv.DictReader(archivo))

if not filas:
    raise SystemExit("No hay lecturas para entrenar")

# Modelo simple basado en ejemplos etiquetados por una regla de referencia.
# Este entrenamiento NO aprende una politica distinta de dicha regla.
ejemplos = []
for fila in filas:
    t = float(fila["temperatura"])
    h = float(fila["humedad"])
    luz = float(fila["luz"])
    etiqueta = 1 if t >= 27 or (t >= 25 and h >= 65) else 0
    ejemplos.append({"x": [t, h, luz], "y": etiqueta})

modelo = {
    "tipo": "knn",
    "k": 5,
    "escalas": [10.0, 40.0, 100.0],
    "etiquetas": {"0": "apagado", "1": "encendido"},
    "ejemplos": ejemplos,
    "origen_etiquetas": "regla_de_referencia"
}
DESTINO.write_text(json.dumps(modelo, indent=2), encoding="utf-8")
print("Modelo guardado:", DESTINO)
print("Ejemplos:", len(ejemplos))
```

**Ejecución:**

```bash
python3 02_entrenar_modelo.py
```

**Comprobación:**

```bash
ls -lh modelos/modelo_ventilacion.json
```

El modelo debe existir y contener 120 ejemplos. No se trata de un modelo neuronal: es un clasificador k-NN sencillo y transparente.


## 17.7. Programa 3: inferencia local y decisiones

Este programa lee las muestras, carga el modelo JSON, calcula una predicción para cada lectura y mide la duración de la inferencia con `time.perf_counter()`. **No controla GPIO ni envía órdenes a un actuador**: solo muestra decisiones y las registra en un CSV.

**Archivo:** `03_control_edge.py`

```python
from pathlib import Path
import csv
import json
import math
import time

BASE = Path(__file__).resolve().parent
MODELO = BASE / "modelos" / "modelo_ventilacion.json"
LECTURAS = BASE / "datos" / "lecturas.csv"
REGISTRO = BASE / "resultados" / "decisiones.csv"
REGISTRO.parent.mkdir(parents=True, exist_ok=True)

modelo = json.loads(MODELO.read_text(encoding="utf-8"))
escalas = modelo["escalas"]
k = modelo["k"]


def predecir(valores):
    distancias = []
    for ejemplo in modelo["ejemplos"]:
        distancia = math.sqrt(sum(
            ((a - b) / escala) ** 2
            for a, b, escala in zip(valores, ejemplo["x"], escalas)
        ))
        distancias.append((distancia, ejemplo["y"]))
    vecinos = sorted(distancias, key=lambda par: par[0])[:k]
    votos = sum(etiqueta for _, etiqueta in vecinos)
    return 1 if votos > k / 2 else 0


# Modo seguro: solo registra decisiones, no acciona hardware.
with LECTURAS.open(newline="", encoding="utf-8") as entrada,         REGISTRO.open("w", newline="", encoding="utf-8") as salida:
    lector = csv.DictReader(entrada)
    escritor = csv.writer(salida)
    escritor.writerow(["instante", "temperatura", "humedad", "luz", "prediccion", "latencia_ms"])
    for fila in lector:
        valores = [float(fila[c]) for c in ("temperatura", "humedad", "luz")]
        inicio = time.perf_counter()
        prediccion = predecir(valores)
        latencia_ms = (time.perf_counter() - inicio) * 1000
        escritor.writerow([fila["instante"], *valores, prediccion, round(latencia_ms, 4)])
        print("t=", fila["instante"], "ventilacion=", "ON" if prediccion else "OFF")

print("Registro guardado:", REGISTRO)
```

**Ejecución:**

```bash
python3 03_control_edge.py
```

**Comprobación:**

```bash
head -n 6 resultados/decisiones.csv
wc -l resultados/decisiones.csv
```

Se esperan 121 líneas. La columna `latencia_ms` contiene una medida local orientativa; su valor depende de la carga del equipo.


## 17.8. Programa 4: validación básica

Antes de conectar dispositivos físicos revisamos si existen lecturas fuera de rango y cuántas veces cambia la salida propuesta. Un número elevado de cambios puede indicar oscilaciones y desgaste si en el futuro se emplea un relé.

**Archivo:** `04_validar_seguridad.py`

```python
from pathlib import Path
import csv

BASE = Path(__file__).resolve().parent
ORIGEN = BASE / "resultados" / "decisiones.csv"
TOTAL = 0
CAMBIOS = 0
ANOMALIAS = 0
anterior = None

with ORIGEN.open(newline="", encoding="utf-8") as archivo:
    for fila in csv.DictReader(archivo):
        TOTAL += 1
        t = float(fila["temperatura"])
        h = float(fila["humedad"])
        luz = float(fila["luz"])
        accion = int(fila["prediccion"])
        if not (-10 <= t <= 60 and 0 <= h <= 100 and 0 <= luz <= 100):
            ANOMALIAS += 1
        if anterior is not None and accion != anterior:
            CAMBIOS += 1
        anterior = accion

print("Muestras:", TOTAL)
print("Cambios de estado:", CAMBIOS)
print("Valores fuera de rango:", ANOMALIAS)
if ANOMALIAS:
    print("AVISO: revisar los datos antes de conectar actuadores")
else:
    print("Validacion basica de rangos: OK")
```

**Ejecución:**

```bash
python3 04_validar_seguridad.py
```

**Comprobación:** el programa debe mostrar el número de muestras, los cambios de estado y los valores fuera de rango. Un resultado de cero anomalías solo significa que los valores cumplen estos límites básicos, no que el sistema sea seguro para uso industrial.

## 17.9. Interpretación de resultados

Una vez ejecutados los cuatro programas, examina los archivos generados:

```bash
ls -lh datos modelos resultados
head -n 5 resultados/decisiones.csv
```

Analiza las siguientes preguntas:

- ¿En qué instantes propone encender el ventilador?
- ¿Hay diferencias entre las decisiones del modelo y la regla que generó las etiquetas?
- ¿Cuánto tarda cada inferencia? ¿Es comparable ese tiempo con el intervalo de muestreo?
- ¿Qué ocurre si la temperatura se aproxima a un umbral de decisión?
- ¿Por qué no sería seguro accionar directamente un relé con cada cambio de predicción?

!!! example "Ejemplo de análisis"
    Si la predicción cambia rápidamente entre 0 y 1, el actuador físico podría encenderse y apagarse repetidamente. Para evitarlo, un diseño real debe añadir una política de control independiente del modelo: histéresis, tiempo mínimo entre maniobras, límites de seguridad y un estado seguro ante fallos.

### 17.9.1. Modelo, política de control y actuador

Conviene separar tres responsabilidades:

| Capa | Responsabilidad | Ejemplo |
|---|---|---|
| Modelo | Estimar un estado o necesidad | «Conviene ventilar» |
| Política de control | Autorizar o rechazar la acción | «Solo activar si el sensor es válido y han pasado 30 s» |
| Actuador | Ejecutar la orden autorizada | Activar un módulo de control adecuado |

Esta separación facilita las pruebas, la depuración y la seguridad.

## 17.10. Integración opcional con sensores y actuadores reales

El paso de simulación a hardware debe realizarse únicamente después de identificar los módulos concretos y verificar su compatibilidad con Arduino UNO Q.

### 17.10.1. Adquisición de datos reales

El sistema podría recibir valores de:

- Un sensor de temperatura y humedad conectado a una interfaz compatible.
- Un sensor de luminosidad mediante un bus o una entrada apropiada.
- Un microcontrolador que publique lecturas por MQTT.
- Una API REST que proporcione medidas ambientales.

Antes de modificar los programas, hay que documentar: modelo de sensor, tensión de alimentación, pines o bus utilizado, biblioteca necesaria, frecuencia de muestreo y formato de datos.

### 17.10.2. Salida física segura

Para accionar un ventilador o motor **no se debe utilizar directamente un pin de la placa como fuente de potencia**. Se requiere una etapa de control adecuada, alimentación compatible y protección frente a cargas inductivas cuando corresponda. En una primera ampliación es preferible emplear un LED indicador o una simulación de actuador.

!!! warning "Seguridad eléctrica"
    No conectar tensión de red a una protoboard ni manipular cargas de 230 V en esta práctica. Si se emplea un módulo de relé o controlador de motor, el docente debe comprobar su esquema, alimentación, aislamiento y requisitos de protección antes de autorizar las conexiones.

### 17.10.3. Comunicación con el microcontrolador

En una ampliación posterior, la aplicación Linux podría enviar comandos a un programa del microcontrolador mediante una interfaz soportada por el entorno instalado. El microcontrolador debería validar la orden, aplicar límites y pasar a un estado seguro si deja de recibir mensajes.

No incluimos aquí código de pines o librerías de comunicación no verificadas, porque dependen del firmware, las bibliotecas y el hardware conectado.

## 17.11. Relación con MQTT, InfluxDB y Grafana

La arquitectura del proyecto puede reutilizar lo aprendido en capítulos anteriores:

```text
Lecturas → Modelo local → Decisión → Registro CSV
    |                         |
    +------> MQTT ------------+
                 |
              InfluxDB
                 |
              Grafana
```

Una implementación ampliada podría publicar por MQTT el instante, las tres lecturas, la predicción y la latencia de inferencia. Después, InfluxDB almacenaría la serie temporal y Grafana mostraría la evolución y los cambios de estado.

**Importante:** los cuatro programas proporcionados no publican por MQTT ni escriben en InfluxDB. Esta integración se propone como actividad de ampliación y debe aprovechar la configuración ya probada en los capítulos 12 y 13.

## 17.12. Actividades guiadas

### Actividad 1. Verificar el conjunto de datos

Ejecuta `01_generar_lecturas.py`, abre `datos/lecturas.csv` y comprueba el número de filas, los nombres de columnas y los rangos de temperatura, humedad y luz. Explica por qué son datos simulados y no medidas físicas.

### Actividad 2. Modificar la regla de etiquetado

En `02_entrenar_modelo.py`, modifica el umbral `t >= 27` por `t >= 26`. Vuelve a entrenar el modelo y ejecuta de nuevo `03_control_edge.py`. Compara el número de decisiones de encendido.

### Actividad 3. Estudiar el número de vecinos

Cambia `"k": 5` por `"k": 3` y después por `"k": 9` en el entrenamiento. Genera cada modelo, realiza inferencia y describe las diferencias observadas. Guarda una copia de cada CSV para comparar los resultados.

### Actividad 4. Medir el rendimiento

Ejecuta varias veces `03_control_edge.py`. Compara las latencias registradas e identifica posibles variaciones debidas a la carga del sistema. Explica por qué una inferencia rápida no garantiza por sí sola una respuesta de control segura.

### Actividad 5. Diseñar una ampliación con MQTT

Dibuja el flujo de mensajes que permitiría enviar las lecturas y decisiones a InfluxDB mediante el sistema MQTT trabajado anteriormente. Propón los nombres de los temas, los campos de los mensajes y dos paneles para Grafana. No es necesario conectar hardware nuevo.

## 17.13. Práctica integradora evaluable

### Título: Prototipo de control ambiental con inferencia local

**Organización:** individual o por parejas, según indique el docente.  
**Entorno:** Arduino UNO Q con Linux y Python.  
**Duración orientativa:** 2-3 sesiones de taller.  
**Material:** Arduino UNO Q, ordenador con SSH/PuTTY, editor de texto y archivos de este capítulo. No se requieren sensores ni actuadores físicos.

### Enunciado

Desarrolla y documenta un prototipo que genere lecturas ambientales simuladas, entrene un modelo k-NN, ejecute inferencia local, registre las decisiones y analice sus riesgos antes de controlar un actuador real.

### Requisitos de entrega

1. Los cuatro programas Python funcionando en `~/practicas/capitulo17`.
2. El CSV de lecturas y el archivo JSON del modelo.
3. El CSV de decisiones con tiempos de inferencia.
4. Una tabla comparativa con dos valores diferentes de `k`.
5. Una breve memoria en PDF o Markdown con capturas, resultados, conclusiones y medidas de seguridad.
6. Una demostración al profesor de la ejecución completa.

### Rúbrica de evaluación

| Criterio | Puntuación máxima |
|---|---:|
| Organización del proyecto y ejecución de programas | 1,5 |
| Generación y validación de datos | 1,5 |
| Entrenamiento y explicación del modelo k-NN | 2,0 |
| Inferencia, registro y medición de latencias | 2,0 |
| Análisis de seguridad y limitaciones | 2,0 |
| Documentación y demostración | 1,0 |
| **Total** | **10,0** |

!!! note "Condición de seguridad"
    La demostración se realizará en modo simulación. La conexión de un actuador físico requerirá una práctica específica, un esquema revisado y autorización del docente.

## 17.14. Resolución de problemas frecuentes

| Problema | Causa probable | Solución |
|---|---|---|
| `FileNotFoundError` al entrenar | No existe `datos/lecturas.csv` | Ejecutar primero `01_generar_lecturas.py` |
| `FileNotFoundError` al inferir | Falta el JSON del modelo | Ejecutar `02_entrenar_modelo.py` |
| Error al validar | Falta `resultados/decisiones.csv` | Ejecutar `03_control_edge.py` |
| No aparecen archivos | Ejecución desde otra carpeta | Los programas guardan rutas relativas a su propio archivo; revisar `~/practicas/capitulo17` |
| Predicciones inesperadas | Datos simulados, etiquetas de referencia o elección de `k` | Revisar los ejemplos y el origen de las etiquetas |
| Latencias diferentes entre ejecuciones | Carga variable del sistema | Repetir medidas y comparar distribuciones |
| Cambios frecuentes de estado | Ausencia de política de control con histéresis | Mantener modo simulación y diseñar protecciones antes de conectar hardware |

## 17.15. Autoevaluación

1. ¿Qué diferencia existe entre una lectura de sensor y una predicción de IA?
2. ¿Por qué es conveniente ejecutar la inferencia localmente en ciertos sistemas IoT?
3. ¿Qué función cumple el archivo JSON del modelo?
4. ¿Cómo decide el algoritmo k-NN la clase de una lectura nueva?
5. ¿Por qué se normalizan las variables antes de calcular distancias?
6. ¿Qué limitación tiene entrenar con etiquetas obtenidas de una regla programada?
7. ¿Por qué debemos separar modelo y política de control?
8. ¿Qué información registramos en `decisiones.csv`?
9. ¿Qué medidas añadirías antes de controlar un ventilador real?
10. ¿Cómo aprovecharías MQTT, InfluxDB y Grafana para supervisar este sistema?

## 17.16. Conclusiones

En este capítulo hemos integrado adquisición de datos, entrenamiento, inferencia y evaluación de decisiones en un prototipo **Edge AI** que funciona localmente en Arduino UNO Q. Hemos comprobado que el modelo puede proponer acciones, pero también que un sistema físico necesita una capa independiente de validación y seguridad.

En el **capítulo 18 — Diseño del proyecto final**, utilizaremos los conocimientos adquiridos para planificar una solución completa, definir requisitos, seleccionar componentes y organizar las fases de desarrollo.

### Referencias de consulta

- [Documentación de Python](https://docs.python.org/3/)
- [Arduino — documentación oficial](https://docs.arduino.cc/)
- [MQTT — sitio oficial](https://mqtt.org/)
- [InfluxDB — documentación](https://docs.influxdata.com/)
- [Grafana — documentación](https://grafana.com/docs/)
