# Capítulo 19. Implementación y pruebas

!!! info "Parte VI — Proyecto final integrador"
    En este capítulo se implementa y valida un prototipo funcional de monitorización ambiental con inferencia local en Arduino UNO Q. Se parte del diseño realizado en el capítulo 18 y se prepara la documentación del capítulo 20.

## 19.1. Objetivos y resultados de aprendizaje

Al terminar el capítulo, el alumnado será capaz de:

- Organizar un proyecto Python modular en Linux.
- Adquirir lecturas simuladas reproducibles y validar sus rangos.
- Ejecutar una clasificación local sencilla y distinguirla de un sistema basado en reglas.
- Registrar mediciones, predicciones, estados y errores en CSV.
- Publicar resultados mediante MQTT cuando exista un broker disponible.
- Comprobar el sistema con pruebas unitarias y una prueba de integración.
- Medir la latencia y documentar evidencias y limitaciones.

!!! warning "Alcance del prototipo"
    El sistema funciona inicialmente con datos simulados. No se conectan ni activan actuadores físicos. La clasificación usa un modelo k-NN entrenado con ejemplos sintéticos; sus predicciones no son una garantía de seguridad. Cualquier actuación física posterior necesita protecciones independientes del modelo.

## 19.2. Arquitectura de la implementación

El flujo previsto es:

```text
Lecturas simuladas
       |
       v
Validacion de rangos
       |
       v
Clasificador k-NN local
       |
       +-----------------> Registro CSV
       |
       +-----------------> Publicacion MQTT (opcional)
                                  |
                                  v
                         Integracion IoT existente
                         (InfluxDB / Grafana)
```

La ruta MQTT es opcional: el sistema debe funcionar y guardar evidencias incluso si el broker no está disponible. Para enviar datos a InfluxDB hace falta un consumidor MQTT o un proceso de escritura explícito; **MQTT no almacena automáticamente datos en InfluxDB**.

### Contrato de datos

Cada lectura tendrá los siguientes campos:

| Campo | Tipo | Unidad o significado |
|---|---|---|
| `timestamp` | Texto ISO 8601 UTC | Fecha y hora de la lectura |
| `temperatura` | Número real | Grados Celsius |
| `humedad` | Número real | Porcentaje relativo |
| `luminosidad` | Número real | Porcentaje simulado, 0 a 100 |
| `estado` | Texto | `normal`, `ventilar` o `revisar` |
| `origen` | Texto | `simulado` |

Los nombres de campos se mantienen en ASCII para facilitar su uso en Python, CSV y JSON.

## 19.3. Preparación del entorno en Arduino UNO Q

Conectarse por SSH o PuTTY y ejecutar:

```bash
mkdir -p ~/practicas/proyecto_final/{src,datos/entradas,datos/registros,modelos,pruebas,resultados,documentacion}
cd ~/practicas/proyecto_final
python3 --version
```

Si el proyecto del capítulo 18 ya existe, **no se debe borrar ni sobrescribir su contenido sin hacer una copia**. Se pueden integrar los programas de este capítulo en la estructura acordada.

Crear un entorno virtual si todavía no existe:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Si falta el módulo `venv`, instalar el paquete correspondiente a la versión de Python disponible (por ejemplo, `python3.13-venv`) y repetir la creación.

La implementación principal utiliza únicamente la biblioteca estándar. MQTT se incorpora después con `paho-mqtt`:

```bash
python -m pip install paho-mqtt
```

!!! tip "Codificacion"
    Los programas Python del capítulo emplean exclusivamente caracteres ASCII. El texto explicativo conserva la ortografía española habitual.

## 19.4. Programa 1: generación de lecturas

Crear `src/01_generar_lecturas.py`:

```python
from pathlib import Path
import csv
import random
from datetime import datetime, timedelta, timezone

BASE = Path(__file__).resolve().parents[1]
DESTINO = BASE / "datos" / "entradas" / "lecturas.csv"


def generar(cantidad=60, semilla=19):
    rng = random.Random(semilla)
    inicio = datetime.now(timezone.utc) - timedelta(seconds=cantidad - 1)
    filas = []
    for i in range(cantidad):
        temperatura = round(rng.uniform(18.0, 35.0), 2)
        humedad = round(rng.uniform(30.0, 85.0), 2)
        luminosidad = round(rng.uniform(10.0, 95.0), 2)
        filas.append({
            "timestamp": (inicio + timedelta(seconds=i)).isoformat(),
            "temperatura": temperatura,
            "humedad": humedad,
            "luminosidad": luminosidad,
            "origen": "simulado",
        })
    return filas


def main():
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    filas = generar()
    with DESTINO.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    print("Lecturas generadas:", len(filas))
    print("Archivo:", DESTINO)


if __name__ == "__main__":
    main()
```

Ejecutar desde la raíz del proyecto:

```bash
python src/01_generar_lecturas.py
head -n 4 datos/entradas/lecturas.csv
wc -l datos/entradas/lecturas.csv
```

**Resultado esperado:** 60 lecturas y 61 líneas contando la cabecera. Los valores serán reproducibles con la misma semilla; las marcas de tiempo cambiarán en cada ejecución.

## 19.5. Programa 2: clasificación local y registro

Se implementa un clasificador **k-NN** que utiliza ejemplos sintéticos etiquetados. Se aplica normalización para que temperatura, humedad y luminosidad contribuyan de forma comparable a la distancia. La validación de rangos es independiente del clasificador.

Crear `src/02_control_inteligente.py`:

```python
from pathlib import Path
import csv
import json
import math

BASE = Path(__file__).resolve().parents[1]
ENTRADA = BASE / "datos" / "entradas" / "lecturas.csv"
SALIDA = BASE / "datos" / "registros" / "predicciones.csv"
MODELO = BASE / "modelos" / "knn_ambiental.json"

RANGOS = {
    "temperatura": (0.0, 60.0),
    "humedad": (0.0, 100.0),
    "luminosidad": (0.0, 100.0),
}

EJEMPLOS = [
    [20, 45, 70, "normal"],
    [23, 50, 65, "normal"],
    [25, 55, 50, "normal"],
    [28, 60, 45, "normal"],
    [31, 65, 40, "ventilar"],
    [34, 70, 35, "ventilar"],
    [36, 75, 30, "ventilar"],
    [30, 80, 25, "ventilar"],
    [18, 85, 10, "revisar"],
    [19, 90, 15, "revisar"],
    [22, 88, 20, "revisar"],
    [24, 92, 25, "revisar"],
]


def validar(lectura):
    for campo, (minimo, maximo) in RANGOS.items():
        valor = float(lectura[campo])
        if not math.isfinite(valor) or not minimo <= valor <= maximo:
            raise ValueError("Valor fuera de rango: " + campo)
    return True


def distancia(a, b):
    escalas = [60.0, 100.0, 100.0]
    return math.sqrt(sum(((x - y) / escala) ** 2
                         for x, y, escala in zip(a, b, escalas)))


def predecir(valores, ejemplos, k=3):
    vecinos = sorted(
        ((distancia(valores, fila[:3]), fila[3]) for fila in ejemplos),
        key=lambda elemento: elemento[0],
    )[:k]
    votos = {}
    for _, etiqueta in vecinos:
        votos[etiqueta] = votos.get(etiqueta, 0) + 1
    return sorted(votos, key=lambda etiqueta: (-votos[etiqueta], etiqueta))[0]


def procesar(filas):
    resultados = []
    for fila in filas:
        resultado = dict(fila)
        try:
            validar(fila)
            valores = [float(fila[c]) for c in RANGOS]
            resultado["estado"] = predecir(valores, EJEMPLOS)
            resultado["error"] = ""
        except (ValueError, KeyError) as exc:
            resultado["estado"] = "revisar"
            resultado["error"] = str(exc)
        resultados.append(resultado)
    return resultados


def main():
    with ENTRADA.open(newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    if not filas:
        raise SystemExit("No hay lecturas para procesar")
    MODELO.parent.mkdir(parents=True, exist_ok=True)
    MODELO.write_text(json.dumps({"k": 3, "ejemplos": EJEMPLOS}, indent=2),
                      encoding="utf-8")
    resultados = procesar(filas)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    columnas = list(resultados[0])
    with SALIDA.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(resultados)
    for estado in ("normal", "ventilar", "revisar"):
        print(estado, sum(f["estado"] == estado for f in resultados))
    print("Archivo:", SALIDA)


if __name__ == "__main__":
    main()
```

Ejecutar:

```bash
python src/02_control_inteligente.py
head -n 5 datos/registros/predicciones.csv
cat modelos/knn_ambiental.json
```

!!! note "Interpretacion del modelo"
    Los ejemplos etiquetados son didácticos, no mediciones de un entorno real. El archivo JSON guarda los ejemplos y el parámetro `k`; no es un modelo validado para controlar equipos. La acción `ventilar` es solo una recomendación simulada.

## 19.6. Programa 3: pruebas automáticas

Una implementación no se considera terminada solo porque no produzca errores visibles. Debemos comprobar casos normales, entradas inválidas y consistencia del clasificador.

Crear `pruebas/test_control.py`:

```python
from pathlib import Path
import importlib.util
import unittest

RUTA = Path(__file__).resolve().parents[1] / "src" / "02_control_inteligente.py"
ESPEC = importlib.util.spec_from_file_location("control_inteligente", RUTA)
MODULO = importlib.util.module_from_spec(ESPEC)
ESPEC.loader.exec_module(MODULO)


class PruebasControl(unittest.TestCase):
    def test_lectura_valida(self):
        lectura = {"temperatura": "24", "humedad": "55", "luminosidad": "60"}
        self.assertTrue(MODULO.validar(lectura))

    def test_humedad_invalida(self):
        lectura = {"temperatura": "24", "humedad": "110", "luminosidad": "60"}
        with self.assertRaises(ValueError):
            MODULO.validar(lectura)

    def test_nan_rechazado(self):
        lectura = {"temperatura": "nan", "humedad": "50", "luminosidad": "60"}
        with self.assertRaises(ValueError):
            MODULO.validar(lectura)

    def test_prediccion_conocida(self):
        resultado = MODULO.predecir([34, 70, 35], MODULO.EJEMPLOS)
        self.assertEqual(resultado, "ventilar")

    def test_fallo_se_registra(self):
        filas = [{"timestamp": "2026-01-01T00:00:00+00:00",
                  "temperatura": "25", "humedad": "-1",
                  "luminosidad": "50", "origen": "simulado"}]
        resultado = MODULO.procesar(filas)
        self.assertEqual(resultado[0]["estado"], "revisar")
        self.assertNotEqual(resultado[0]["error"], "")


if __name__ == "__main__":
    unittest.main()
```

Ejecutar:

```bash
python -m unittest discover -s pruebas -p 'test_*.py' -v
```

**Criterio de aceptación:** deben finalizar cinco pruebas sin fallos. Si una prueba falla, se corrige el código antes de continuar.

## 19.7. Programa 4: publicación MQTT opcional

Este programa envía cada predicción como JSON a un broker MQTT existente. No crea el broker ni configura InfluxDB. Se utiliza una variable de entorno para la dirección y se establece un tiempo de espera para evitar bloqueos prolongados.

Crear `src/03_publicar_mqtt.py`:

```python
from pathlib import Path
import csv
import json
import os
import time
import paho.mqtt.client as mqtt

BASE = Path(__file__).resolve().parents[1]
ENTRADA = BASE / "datos" / "registros" / "predicciones.csv"
BROKER = os.environ.get("MQTT_HOST", "127.0.0.1")
PUERTO = int(os.environ.get("MQTT_PORT", "1883"))
TOPICO = os.environ.get("MQTT_TOPIC", "unoq/proyecto_final/ambiente")


def main():
    with ENTRADA.open(newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    usuario = os.environ.get("MQTT_USER")
    clave = os.environ.get("MQTT_PASSWORD")
    if usuario:
        cliente.username_pw_set(usuario, clave)
    cliente.connect(BROKER, PUERTO, keepalive=30)
    cliente.loop_start()
    try:
        for fila in filas:
            mensaje = json.dumps(fila, ensure_ascii=True)
            resultado = cliente.publish(TOPICO, mensaje, qos=1)
            resultado.wait_for_publish(timeout=5)
            if not resultado.is_published():
                raise TimeoutError("Publicacion MQTT sin confirmar")
            print("Publicado:", fila["timestamp"], fila["estado"])
            time.sleep(0.1)
    finally:
        cliente.loop_stop()
        cliente.disconnect()


if __name__ == "__main__":
    main()
```

Antes de ejecutarlo, configurar la dirección real del broker, por ejemplo:

```bash
export MQTT_HOST=192.168.250.250
export MQTT_PORT=1883
export MQTT_TOPIC=unoq/proyecto_final/ambiente
python src/03_publicar_mqtt.py
```

La dirección anterior es **solo un ejemplo de infraestructura**: debe sustituirse por el broker realmente accesible desde Arduino UNO Q. Si el broker requiere autenticación, definir `MQTT_USER` y `MQTT_PASSWORD` sin escribir credenciales en el código. Para redes no confiables, utilizar TLS y un puerto/configuración adecuados; este ejemplo presupone una red de laboratorio controlada.

Para verificar la recepción, usar un suscriptor MQTT conectado al mismo broker y tópico. En un equipo con Mosquitto Clients instalado:

```bash
mosquitto_sub -h 192.168.250.250 -t 'unoq/proyecto_final/ambiente' -v
```

!!! warning "Publicacion de datos"
    El ejemplo publica todas las lecturas históricas al ejecutar el programa. No debe confundirse con un sistema de streaming en tiempo real. Para producción se requiere control de duplicados, reconexión, identificadores de mensajes y políticas de retención.

## 19.8. Programa 5: medición del rendimiento

Crear `src/04_medir_rendimiento.py`:

```python
from pathlib import Path
import csv
import importlib.util
import statistics
import time

BASE = Path(__file__).resolve().parents[1]
RUTA = BASE / "src" / "02_control_inteligente.py"
ESPEC = importlib.util.spec_from_file_location("control_inteligente", RUTA)
MODULO = importlib.util.module_from_spec(ESPEC)
ESPEC.loader.exec_module(MODULO)
DESTINO = BASE / "resultados" / "latencias.csv"


def main():
    muestra = [29.0, 65.0, 45.0]
    for _ in range(100):
        MODULO.predecir(muestra, MODULO.EJEMPLOS)
    tiempos = []
    for _ in range(1000):
        inicio = time.perf_counter_ns()
        MODULO.predecir(muestra, MODULO.EJEMPLOS)
        tiempos.append((time.perf_counter_ns() - inicio) / 1_000_000)
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    with DESTINO.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["prueba", "latencia_ms"])
        escritor.writerows((i + 1, valor) for i, valor in enumerate(tiempos))
    print("Media (ms):", round(statistics.mean(tiempos), 4))
    print("Mediana (ms):", round(statistics.median(tiempos), 4))
    print("Maximo (ms):", round(max(tiempos), 4))
    print("Archivo:", DESTINO)


if __name__ == "__main__":
    main()
```

Ejecutar:

```bash
python src/04_medir_rendimiento.py
head -n 5 resultados/latencias.csv
```

La medición refleja únicamente la llamada al clasificador en el equipo utilizado. No incluye adquisición del sensor, transmisión MQTT ni actualización de Grafana. Repetir la prueba si hay procesos de fondo que puedan alterar los resultados.

## 19.9. Secuencia completa de integración

Desde la raíz del proyecto:

```bash
source .venv/bin/activate
python src/01_generar_lecturas.py
python src/02_control_inteligente.py
python -m unittest discover -s pruebas -p 'test_*.py' -v
python src/04_medir_rendimiento.py
```

La publicación MQTT se realiza únicamente después de comprobar la conectividad y los parámetros del broker:

```bash
python src/03_publicar_mqtt.py
```

### Lista de verificación

- [ ] Se han creado 60 lecturas simuladas.
- [ ] Existe el CSV con predicciones y estados.
- [ ] El modelo se ha guardado en JSON.
- [ ] Las cinco pruebas unitarias se completan correctamente.
- [ ] Existe el CSV con 1000 medidas de latencia.
- [ ] Se registra si la prueba MQTT se ha realizado, omitido o ha fallado.
- [ ] Se han guardado capturas o registros de ejecución como evidencias.

## 19.10. Integración con InfluxDB y Grafana

En el capítulo 13 ya se trabajó con InfluxDB y Grafana. Aquí se reutiliza esa infraestructura **solo si existe un flujo de ingestión configurado**.

El mensaje MQTT contiene `timestamp`, `temperatura`, `humedad`, `luminosidad`, `estado` y `origen`. Para representarlo en Grafana se necesita que un servicio intermedio lo escriba en InfluxDB, por ejemplo Node-RED, Telegraf con entrada MQTT o un programa Python con `influxdb-client`.

Un posible esquema de almacenamiento es:

| Elemento | Propuesta |
|---|---|
| Bucket | `iot` |
| Measurement | `proyecto_final` |
| Campos numéricos | `temperatura`, `humedad`, `luminosidad` |
| Etiquetas | `origen`, `estado` |
| Tiempo | `timestamp` de la lectura |

!!! warning "Evitar confusiones"
    No se debe afirmar que Grafana recibe los datos hasta comprobar el proceso de ingestión, la escritura en InfluxDB y la consulta del bucket. El hecho de recibir un mensaje MQTT no prueba que haya sido almacenado.

Una consulta Flux de comprobación, una vez confirmada la escritura, sería:

```flux
from(bucket: "iot")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "proyecto_final")
  |> filter(fn: (r) => r._field == "temperatura")
```

## 19.11. Plan de pruebas del proyecto

| ID | Tipo | Procedimiento | Resultado esperado |
|---|---|---|---|
| P01 | Funcional | Generar lecturas | 60 filas de datos |
| P02 | Funcional | Procesar lecturas | 60 estados registrados |
| P03 | Validación | Introducir humedad 110 | Rechazo y estado `revisar` |
| P04 | Validación | Introducir temperatura `nan` | Rechazo y estado `revisar` |
| P05 | Unitaria | Ejecutar `unittest` | 5 pruebas correctas |
| P06 | Rendimiento | Ejecutar benchmark | CSV de 1000 latencias |
| P07 | Comunicación | Publicar MQTT | Mensajes recibidos por suscriptor |
| P08 | Integración | Consultar InfluxDB | Datos visibles si hay ingestión |
| P09 | Visualización | Abrir Grafana | Gráfica con datos reales del proyecto |

En P07–P09, indicar **No realizado** cuando no se disponga de la infraestructura, en lugar de marcar la prueba como superada.

## 19.12. Actividades guiadas

### Actividad 1. Estructura y ejecución

Preparar las carpetas, ejecutar el generador y justificar por qué el programa utiliza rutas relativas al archivo y no al directorio actual de la terminal.

### Actividad 2. Validación de datos

Modificar una copia de `lecturas.csv` para incluir una humedad de `110`. Ejecutar el clasificador y localizar el registro rechazado. Explicar por qué el sistema asigna `revisar`.

### Actividad 3. Experimentación con k-NN

Cambiar el valor de `k` de 3 a 1 y comparar las predicciones. Restaurar el valor original. Explicar cómo puede afectar `k` a la sensibilidad del clasificador.

### Actividad 4. Pruebas automatizadas

Añadir un caso unitario que compruebe el rechazo de una luminosidad negativa. Ejecutar la batería completa y conservar el resultado.

### Actividad 5. Rendimiento y comunicaciones

Medir la latencia en tres ejecuciones. Si existe broker MQTT, publicar y capturar al menos cinco mensajes; si no existe, describir la prueba pendiente y el motivo.

## 19.13. Práctica integradora evaluable

**Enunciado.** Implementar y verificar en Arduino UNO Q un prototipo de monitorización ambiental inteligente. El sistema debe generar lecturas, validarlas, clasificarlas con un modelo local, registrar resultados y producir evidencias de pruebas. La publicación MQTT y la integración con Grafana se valorarán cuando la infraestructura esté disponible.

**Entregables:**

1. Código fuente de los programas y pruebas.
2. Archivo CSV de lecturas y predicciones.
3. Archivo JSON del modelo.
4. Resultados de las pruebas automáticas y benchmark.
5. Memoria breve con arquitectura, incidencias y conclusiones.
6. Evidencias de MQTT/Grafana si se ha realizado la integración.

### Rúbrica (10 puntos)

| Criterio | Puntuación |
|---|---:|
| Organización del proyecto y ejecución reproducible | 1,0 |
| Generación y formato de lecturas | 1,5 |
| Validación y tratamiento de errores | 1,5 |
| Clasificación local y explicación del modelo | 2,0 |
| Pruebas automáticas y evidencias | 2,0 |
| Medición de rendimiento | 1,0 |
| Comunicación de resultados y documentación | 1,0 |
| **Total** | **10,0** |

La integración MQTT/Grafana puede aportarse como evidencia adicional en el último criterio, pero no es obligatoria si el centro no dispone de broker o canal de ingestión operativo.

## 19.14. Resolución de problemas

| Problema | Causa probable | Solución |
|---|---|---|
| `No such file or directory` | No se ejecutó el generador | Ejecutar primero `01_generar_lecturas.py` |
| `ModuleNotFoundError: paho` | Falta la dependencia opcional | Instalar `paho-mqtt` en el entorno activo |
| `Connection refused` | Broker MQTT inaccesible | Verificar IP, puerto y servicio |
| `Not authorized` | Credenciales MQTT incorrectas | Revisar usuario, contraseña y permisos |
| `No data` en Grafana | No existe ingestión o rango temporal erróneo | Comprobar escritura, bucket y período |
| Fallo en prueba unitaria | Cambio de comportamiento | Revisar la función y el caso de prueba |
| Latencia muy variable | Carga de CPU o procesos de fondo | Repetir y comparar mediana |

## 19.15. Autoevaluación

1. ¿Qué diferencia existe entre una regla fija y una predicción k-NN?
2. ¿Por qué se deben validar las lecturas antes de clasificarlas?
3. ¿Qué información guarda el archivo JSON del modelo?
4. ¿Por qué se utilizan pruebas automáticas además de pruebas manuales?
5. ¿Qué mide exactamente el benchmark propuesto?
6. ¿Por qué publicar MQTT no implica almacenar datos en InfluxDB?
7. ¿Qué evidencias demostrarían una integración correcta con Grafana?
8. ¿Qué medidas serían necesarias antes de activar un actuador real?

## 19.16. Conclusiones y continuidad

El capítulo ha desarrollado una implementación modular y comprobable de Edge AI en Arduino UNO Q. El prototipo genera datos simulados, realiza inferencia local, registra decisiones y permite probar comunicaciones MQTT. La integración con InfluxDB y Grafana requiere verificar el flujo completo de ingestión.

En el **capítulo 20, Documentación y presentación del proyecto**, se prepararán la memoria técnica, el manual de instalación, los resultados de pruebas y la defensa del proyecto final.
