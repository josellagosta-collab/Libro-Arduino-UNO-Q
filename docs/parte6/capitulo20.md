# Capítulo 20. Documentación y presentación del proyecto

!!! info "Parte VI — Proyecto final integrador"
    Este capítulo cierra el libro **Arduino UNO Q**. El alumnado elaborará una memoria técnica reproducible, organizará las evidencias de las pruebas, preparará una demostración y defenderá las decisiones adoptadas. La documentación debe describir **lo que realmente se ha implementado y comprobado**, diferenciándolo de las funciones previstas o simuladas.

## 20.1. Objetivos de aprendizaje

Al finalizar este capítulo, el alumnado será capaz de:

- Organizar la documentación de un proyecto de IoT y Edge AI de manera profesional.
- Explicar la arquitectura y el flujo de información entre Arduino UNO Q, Python, MQTT, InfluxDB y Grafana.
- Documentar la instalación, configuración, ejecución y recuperación del sistema.
- Presentar resultados verificables y reconocer sus limitaciones.
- Registrar evidencias de pruebas funcionales, de integración y de rendimiento.
- Preparar una presentación oral y una demostración técnica controlada.
- Entregar un proyecto reproducible y evaluable por otra persona.

!!! note "Continuidad con los capítulos anteriores"
    En el capítulo 18 se definió el diseño del sistema y en el capítulo 19 se abordó su implementación y las pruebas. En este capítulo se reutilizará la carpeta `~/practicas/proyecto_final` y se documentarán **los archivos y resultados que realmente existan**. No se deben inventar capturas, métricas ni pruebas superadas.

## 20.2. ¿Por qué es imprescindible documentar?

Un proyecto puede funcionar correctamente en el ordenador de su autor y resultar imposible de reproducir en otro equipo. Una documentación de calidad permite:

1. Comprender qué problema resuelve el sistema.
2. Identificar los requisitos y las decisiones de diseño.
3. Repetir la instalación y las pruebas.
4. Detectar errores y realizar mantenimiento.
5. Transferir el proyecto a otro equipo de trabajo.
6. Evaluar los resultados con criterios objetivos.

La documentación no consiste en copiar fragmentos de código sin explicarlos. Debe conectar cada decisión con una necesidad técnica y cada resultado con una evidencia.

### 20.2.1. Documentación técnica y documentación de usuario

| Documento | Destinatario | Contenido principal |
|---|---|---|
| Memoria técnica | Profesorado y equipo técnico | Objetivos, arquitectura, implementación, pruebas y conclusiones |
| Guía de instalación | Personal técnico | Dependencias, configuración y comandos de puesta en marcha |
| Manual de uso | Usuario final | Operación normal, indicadores y solución de incidencias habituales |
| Registro de pruebas | Equipo de validación | Casos de prueba, resultados, fecha y evidencias |
| Presentación | Tribunal o grupo clase | Problema, solución, demostración, resultados y mejoras |

## 20.3. Estructura de entrega del proyecto final

Trabajaremos sobre la estructura utilizada en los capítulos 18 y 19, incorporando la documentación y los resultados de evaluación.

```text
proyecto_final/
├── configuracion/
├── datos/
│   ├── entradas/
│   └── registros/
├── modelos/
├── src/
├── pruebas/
├── resultados/
│   ├── evidencias/
│   └── informes/
├── documentacion/
│   ├── README.md
│   ├── memoria_tecnica.md
│   ├── instalacion.md
│   ├── manual_usuario.md
│   ├── registro_pruebas.csv
│   └── presentacion.md
└── .gitignore
```

!!! warning "Seguridad de la información"
    No se incluirán contraseñas, claves de API, tokens de InfluxDB, credenciales MQTT ni archivos `.env` con secretos. Las capturas de pantalla también deben revisarse antes de compartirlas.

### 20.3.1. Crear los directorios

Conéctate al Arduino UNO Q mediante SSH o PuTTY:

```bash
cd ~/practicas/proyecto_final
mkdir -p documentacion resultados/evidencias resultados/informes
```

Comprueba el contenido disponible:

```bash
find . -maxdepth 3 -type f | sort
```

El listado obtenido será el punto de partida de la documentación. Los nombres exactos de los programas pueden variar según la implementación realizada en el capítulo 19.

## 20.4. Elaboración de la memoria técnica

La memoria técnica debe ser comprensible sin necesidad de consultar todo el historial de desarrollo. Se recomienda la siguiente estructura.

### 20.4.1. Portada y ficha del proyecto

Incluir:

- Título del proyecto.
- Nombre del alumno o equipo.
- Curso y módulo.
- Centro educativo.
- Profesor responsable.
- Fecha y versión del documento.

### 20.4.2. Resumen ejecutivo

Redactar entre 150 y 250 palabras para responder:

- ¿Qué problema se quiere resolver?
- ¿Qué dispositivos y tecnologías se utilizan?
- ¿Qué función cumple el modelo de IA?
- ¿Qué resultados se han obtenido?
- ¿Qué limitaciones se han detectado?

### 20.4.3. Requisitos y alcance

Separar los requisitos funcionales de los no funcionales.

| Identificador | Tipo | Requisito | Verificación |
|---|---|---|---|
| RF-01 | Funcional | Obtener lecturas ambientales o simuladas | Archivo de entradas o salida de consola |
| RF-02 | Funcional | Ejecutar inferencia local | Registro de predicciones |
| RF-03 | Funcional | Publicar resultados por MQTT, si está habilitado | Mensaje recibido por un suscriptor |
| RF-04 | Funcional | Consultar históricos en InfluxDB y Grafana, si están configurados | Consulta y captura del panel |
| RNF-01 | No funcional | Evitar publicar credenciales | Revisión de archivos de entrega |
| RNF-02 | No funcional | Documentar el tiempo de inferencia | Informe de rendimiento |

!!! tip "Trazabilidad"
    Para cada requisito se indicará una prueba concreta. Un requisito sin comprobación debe figurar como **pendiente**, nunca como validado.

### 20.4.4. Arquitectura del sistema

El esquema lógico general es:

```text
+----------------------+       +-----------------------+
| Sensor o simulador   | ----> | Arduino UNO Q         |
| de datos ambientales |       | Linux + Python        |
+----------------------+       | Modelo de Edge AI     |
                               +-----------+-----------+
                                           |
                                  Prediccion / decision
                                           |
                        +------------------+------------------+
                        |                                     |
                 Registro local                         MQTT opcional
                        |                                     |
                   CSV / JSON                          Consumidor IoT
                                                              |
                                                      InfluxDB / Grafana
                                                       (si configurados)
```

Explicar qué componentes se ejecutan en el Arduino UNO Q y cuáles están desplegados en otros servicios o equipos. **No asumir que todos los servicios están instalados en el mismo dispositivo.**

### 20.4.5. Modelo de inteligencia artificial

Documentar, como mínimo:

1. Problema de clasificación o predicción.
2. Variables de entrada y sus unidades.
3. Origen y cantidad de los datos.
4. Algoritmo utilizado, por ejemplo k-NN.
5. Parámetros elegidos y criterio de selección.
6. Separación entre entrenamiento y prueba.
7. Métricas calculadas y limitaciones de los datos simulados.
8. Comportamiento previsto ante entradas inválidas.

!!! warning "Interpretación de resultados"
    Una exactitud elevada sobre datos sintéticos no demuestra automáticamente que el modelo funcione bien con sensores reales. Deben describirse las condiciones de prueba y las posibles diferencias con el entorno de producción.

### 20.4.6. Resultados y conclusiones

Para cada resultado, incluir la evidencia correspondiente. Las conclusiones deben responder a los objetivos iniciales, identificar problemas resueltos y proponer mejoras realistas.

## 20.5. Documentar la instalación y la puesta en marcha

Una guía de instalación debe permitir que otra persona reproduzca el sistema.

### 20.5.1. Identificación del entorno

En el Arduino UNO Q, ejecuta:

```bash
uname -a
python3 --version
hostname
pwd
```

Para consultar paquetes Python instalados en el entorno activo:

```bash
python3 -m pip list
```

Si se utiliza un entorno virtual, actívalo antes de ejecutar el último comando. No instales paquetes de nuevo solo para documentar versiones.

### 20.5.2. Dependencias

Crear un archivo de dependencias únicamente con las bibliotecas realmente utilizadas. Por ejemplo, si el proyecto utiliza `paho-mqtt` y `influxdb-client`, pueden figurar en `requirements.txt`; si no se usan, no deben añadirse.

Para exportar las dependencias del entorno virtual activo:

```bash
python -m pip freeze > documentacion/requirements_instalados.txt
```

Este listado refleja el entorno actual y puede incluir bibliotecas ajenas al proyecto. Revisarlo antes de convertirlo en el archivo definitivo de instalación.

### 20.5.3. Variables de configuración

Documentar el nombre y la función de cada variable, **sin revelar su valor secreto**.

| Variable de ejemplo | Finalidad | ¿Se puede publicar su valor? |
|---|---|---|
| `MQTT_HOST` | Dirección del broker | Depende de la red |
| `MQTT_PORT` | Puerto de comunicación | Generalmente sí |
| `INFLUX_URL` | URL de InfluxDB | Depende del despliegue |
| `INFLUX_ORG` | Organización de InfluxDB | Revisar |
| `INFLUX_BUCKET` | Bucket de datos | Revisar |
| `INFLUX_TOKEN` | Token de acceso | **No** |

### 20.5.4. Procedimiento de arranque

En `documentacion/instalacion.md`, registrar los comandos reales para:

1. Acceder al directorio del proyecto.
2. Activar el entorno Python, si existe.
3. Iniciar el generador de datos o leer los sensores.
4. Ejecutar el programa de inferencia.
5. Activar los servicios externos que correspondan.
6. Consultar los registros y detener el sistema de forma segura.

No copiar comandos de ejemplo que no se hayan probado en el equipo.

## 20.6. Preparar un README profesional

El archivo `README.md` será la puerta de entrada al proyecto. Debe incluir:

- Descripción breve y finalidad.
- Requisitos de hardware y software.
- Árbol de directorios.
- Instalación y ejecución.
- Resultados esperados y ubicación de los registros.
- Limitaciones conocidas.
- Referencias a la memoria y al manual de usuario.

### Programa 1. Generar una plantilla de README

Crea `documentacion/01_generar_readme.py`:

```python
from pathlib import Path

base = Path.home() / "practicas" / "proyecto_final"
docs = base / "documentacion"
docs.mkdir(parents=True, exist_ok=True)

contenido = """# Proyecto final Arduino UNO Q

## Descripcion
Sistema de monitorizacion ambiental con inferencia local.

## Objetivos
- Obtener datos ambientales o simulados.
- Ejecutar un modelo de IA local.
- Registrar y visualizar resultados cuando corresponda.

## Requisitos
Completar con el hardware, el sistema y las versiones reales.

## Instalacion
Consultar instalacion.md.

## Ejecucion
Completar con los comandos comprobados en el equipo.

## Resultados
Consultar resultados/ y documentacion/registro_pruebas.csv.

## Limitaciones
Indicar sensores simulados, servicios opcionales y pruebas pendientes.

## Documentacion
- memoria_tecnica.md
- instalacion.md
- manual_usuario.md
"""

destino = docs / "README.md"
if destino.exists():
    print("El archivo ya existe. No se sobrescribe:", destino)
else:
    destino.write_text(contenido, encoding="utf-8")
    print("Plantilla creada:", destino)
```

Ejecútalo desde el directorio del proyecto:

```bash
cd ~/practicas/proyecto_final
python3 documentacion/01_generar_readme.py
cat documentacion/README.md
```

!!! note "Comprobación"
    El programa crea una plantilla, **no una memoria terminada**. Cada apartado debe completarse con la información real del proyecto. Si el archivo ya existe, el programa lo conserva.

## 20.7. Registrar las pruebas y las evidencias

Una prueba verificable debe indicar qué se esperaba, qué ocurrió y cómo se demuestra.

### 20.7.1. Ficha de prueba

| Campo | Descripción |
|---|---|
| Identificador | Código único, por ejemplo `P-01` |
| Fecha | Día de ejecución |
| Componente | Módulo o servicio evaluado |
| Procedimiento | Pasos ejecutados |
| Resultado esperado | Comportamiento previsto |
| Resultado observado | Comportamiento realmente obtenido |
| Estado | `OK`, `FALLO` o `PENDIENTE` |
| Evidencia | Ruta de captura, registro o archivo |
| Observaciones | Incidencias y correcciones |

### Programa 2. Registrar una prueba desde la terminal

Crea `documentacion/02_registrar_prueba.py`:

```python
import csv
from datetime import datetime
from pathlib import Path

base = Path.home() / "practicas" / "proyecto_final"
destino = base / "documentacion" / "registro_pruebas.csv"
destino.parent.mkdir(parents=True, exist_ok=True)

campos = [
    "fecha", "id", "componente", "esperado", "observado",
    "estado", "evidencia", "observaciones"
]

print("Registro de pruebas del proyecto final")
identificador = input("ID de prueba: ").strip()
componente = input("Componente: ").strip()
esperado = input("Resultado esperado: ").strip()
observado = input("Resultado observado: ").strip()
estado = input("Estado (OK/FALLO/PENDIENTE): ").strip().upper()
evidencia = input("Ruta de evidencia (opcional): ").strip()
observaciones = input("Observaciones: ").strip()

if not identificador or not componente:
    raise SystemExit("ERROR: ID y componente son obligatorios")
if estado not in {"OK", "FALLO", "PENDIENTE"}:
    raise SystemExit("ERROR: estado no valido")

nuevo = not destino.exists() or destino.stat().st_size == 0
with destino.open("a", newline="", encoding="utf-8") as archivo:
    escritor = csv.DictWriter(archivo, fieldnames=campos)
    if nuevo:
        escritor.writeheader()
    escritor.writerow({
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "id": identificador,
        "componente": componente,
        "esperado": esperado,
        "observado": observado,
        "estado": estado,
        "evidencia": evidencia,
        "observaciones": observaciones,
    })

print("Prueba registrada en:", destino)
```

Ejecuta:

```bash
python3 documentacion/02_registrar_prueba.py
```

Introduce una prueba que hayas realizado realmente. Después consulta el archivo:

```bash
head -n 5 documentacion/registro_pruebas.csv
```

!!! warning "Integridad de las evidencias"
    El registro es una declaración de resultados introducida por el usuario. No verifica automáticamente que la prueba haya ocurrido ni que la evidencia exista. El profesor deberá contrastar los registros con los archivos y la demostración.

### 20.7.2. Pruebas mínimas propuestas

| ID | Prueba | Evidencia recomendada |
|---|---|---|
| P-01 | Generación o captura de lecturas | CSV y salida de consola |
| P-02 | Inferencia local | Predicciones y entradas asociadas |
| P-03 | Rechazo de datos inválidos | Registro de error o prueba unitaria |
| P-04 | Publicación MQTT, si se usa | Mensaje recibido |
| P-05 | Escritura en InfluxDB, si se usa | Consulta de puntos |
| P-06 | Visualización en Grafana, si se usa | Captura del dashboard |
| P-07 | Rendimiento del modelo | Informe con tiempos y condiciones |
| P-08 | Reinicio y recuperación | Registro de procedimiento |

Los servicios opcionales no utilizados se marcarán como **no aplicables** en la memoria; no se contabilizarán como pruebas realizadas.

## 20.8. Informe automático del estado de las pruebas

### Programa 3. Resumir el registro CSV

Crea `documentacion/03_resumen_pruebas.py`:

```python
import csv
from collections import Counter
from pathlib import Path

base = Path.home() / "practicas" / "proyecto_final"
origen = base / "documentacion" / "registro_pruebas.csv"
destino = base / "resultados" / "informes" / "resumen_pruebas.txt"

if not origen.exists():
    raise SystemExit("ERROR: no existe el registro de pruebas")

with origen.open("r", newline="", encoding="utf-8") as archivo:
    filas = list(csv.DictReader(archivo))

conteos = Counter(fila.get("estado", "").upper() for fila in filas)
lineas = [
    "RESUMEN DE PRUEBAS",
    "Total de registros: " + str(len(filas)),
    "OK: " + str(conteos["OK"]),
    "FALLO: " + str(conteos["FALLO"]),
    "PENDIENTE: " + str(conteos["PENDIENTE"]),
]

destino.parent.mkdir(parents=True, exist_ok=True)
destino.write_text("\n".join(lineas) + "\n", encoding="utf-8")
print("\n".join(lineas))
print("Informe guardado en:", destino)
```

Ejecuta:

```bash
python3 documentacion/03_resumen_pruebas.py
cat resultados/informes/resumen_pruebas.txt
```

!!! tip "Cómo interpretar el informe"
    El programa cuenta **registros**, no pruebas únicas. Si repites una misma prueba varias veces, cada ejecución registrada se contabilizará. En la memoria debes explicar las repeticiones y distinguir los resultados iniciales de los definitivos.

## 20.9. Preparar el manual de usuario

El manual debe explicar cómo utilizar el proyecto sin necesidad de conocer su código fuente.

### 20.9.1. Contenido recomendado

1. Descripción general del sistema.
2. Requisitos previos y conexión al Arduino UNO Q.
3. Procedimiento de inicio.
4. Lectura e interpretación de los resultados.
5. Significado de los estados de la IA.
6. Procedimiento de parada.
7. Mensajes de error habituales.
8. Contacto de mantenimiento o responsable.

### 20.9.2. Tabla de incidencias

| Síntoma | Causa posible | Comprobación |
|---|---|---|
| No se generan lecturas | Programa detenido o ruta incorrecta | Revisar proceso y directorio |
| No aparece el modelo | Archivo no generado o ruta errónea | Verificar `modelos/` |
| Fallan las predicciones | Datos incompletos o formato incompatible | Revisar entradas y registro |
| MQTT no recibe mensajes | Broker inaccesible o configuración incorrecta | Comprobar red y suscriptor |
| Grafana no muestra datos | Rango temporal o consulta incorrecta | Revisar bucket, campo y tiempo |
| El programa no inicia | Dependencia o entorno Python incorrecto | Revisar versión y bibliotecas |

## 20.10. Preparar la presentación oral

Una buena presentación no debe reproducir toda la memoria. Debe destacar las decisiones y los resultados más importantes.

### 20.10.1. Propuesta de ocho diapositivas

| Diapositiva | Contenido | Tiempo orientativo |
|---|---|---|
| 1 | Título, autores y objetivo | 1 min |
| 2 | Problema y requisitos | 1 min |
| 3 | Arquitectura del sistema | 2 min |
| 4 | Datos y modelo de IA | 2 min |
| 5 | Implementación y tecnologías | 2 min |
| 6 | Demostración | 3 min |
| 7 | Resultados, pruebas y limitaciones | 2 min |
| 8 | Conclusiones y mejoras | 2 min |

Duración orientativa total: **15 minutos**. El profesor puede adaptarla a la organización del grupo.

### 20.10.2. Recomendaciones de comunicación

- Utilizar esquemas sencillos y capturas legibles.
- Explicar las siglas antes de emplearlas.
- Distinguir entre funcionalidades reales y simuladas.
- Presentar métricas con sus unidades y condiciones de medición.
- Evitar mostrar contraseñas o tokens durante la demostración.
- Repartir las intervenciones si el proyecto es en equipo.
- Reservar tiempo para preguntas.

## 20.11. Preparar una demostración técnica fiable

La demostración debe ser breve, reproducible y resistente a fallos previsibles.

### 20.11.1. Guion de demostración

1. Mostrar la estructura de directorios y explicar los componentes.
2. Enseñar una entrada ambiental real o simulada.
3. Ejecutar el programa de inferencia local.
4. Mostrar la predicción y explicar su significado.
5. Abrir el registro generado.
6. Si están configurados, comprobar MQTT e InfluxDB/Grafana.
7. Mostrar el registro de pruebas y las limitaciones conocidas.

### 20.11.2. Plan de contingencia

Antes de la defensa:

- Comprobar alimentación, conexión de red y acceso SSH.
- Verificar que los servicios necesarios están disponibles.
- Preparar un conjunto de datos de prueba reproducible.
- Conservar capturas de ejecuciones anteriores **identificadas como evidencias históricas**, no como demostración en directo.
- Preparar una explicación de los componentes opcionales que no estén conectados.

!!! warning "Demostraciones con actuadores"
    Si se han incorporado actuadores reales, comprobar límites eléctricos, estados seguros y posibilidad de desconexión antes de la presentación. No ejecutar acciones físicas potencialmente peligrosas como parte de una demostración improvisada.

## 20.12. Entrega y control de versiones

### 20.12.1. Archivos que deben entregarse

- Código fuente desarrollado.
- Configuración de ejemplo sin secretos.
- Modelo y datos de prueba permitidos.
- Memoria técnica y manual de usuario.
- Instrucciones de instalación.
- Registro de pruebas y evidencias.
- Presentación o guion de defensa.
- Lista de limitaciones y mejoras.

### 20.12.2. Archivo `.gitignore`

En el directorio raíz del proyecto puede utilizarse:

```gitignore
.venv/
__pycache__/
*.pyc
.env
.env.*
!.env.example
*.token
*.key
```

!!! warning "Revisión antes de publicar"
    Un `.gitignore` evita incorporar ciertos archivos nuevos, pero **no elimina secretos ya incluidos en el historial de Git**. Revisar `git status`, los archivos preparados para el commit y el historial si previamente se publicaron credenciales.

### 20.12.3. Sincronización con GitHub

Si el proyecto final dispone de un repositorio Git independiente y configurado, pueden utilizarse:

```bash
git status
git add .
git commit -m "Documentar proyecto final Arduino UNO Q"
git push origin main
```

Estos comandos deben ejecutarse **dentro del repositorio correspondiente**. No es necesario crear un repositorio independiente para completar la práctica.

La publicación del **libro MkDocs**, en cambio, se realizará desde VS Code en Windows, dentro de `F:\proyectos_SDD\Libro-Arduino-UNO-Q`, siguiendo el procedimiento habitual con `mkdocs build --strict`, `git push` y `mkdocs gh-deploy`.

## 20.13. Actividades guiadas

### Actividad 1. Inventario documental

1. Ejecuta `find . -maxdepth 3 -type f | sort`.
2. Identifica código, datos, modelos, registros y documentación.
3. Marca qué archivos deben entregarse y cuáles contienen información sensible.
4. Redacta una tabla con la función de cada archivo principal.

**Evidencia:** inventario incluido en la memoria.

### Actividad 2. README reproducible

1. Ejecuta `01_generar_readme.py`.
2. Completa todos los apartados de la plantilla.
3. Añade los comandos de ejecución realmente comprobados.
4. Pide a un compañero que siga las instrucciones y anota las dificultades encontradas.

**Evidencia:** `documentacion/README.md` revisado.

### Actividad 3. Registro de pruebas

1. Selecciona tres pruebas realizadas en el capítulo 19.
2. Regístralas con `02_registrar_prueba.py`.
3. Añade referencias a evidencias existentes.
4. Ejecuta `03_resumen_pruebas.py`.
5. Explica las diferencias entre registros correctos, fallidos y pendientes.

**Evidencia:** CSV y resumen TXT.

### Actividad 4. Preparación de la defensa

1. Crea una presentación de ocho diapositivas.
2. Incluye un diagrama de arquitectura.
3. Presenta al menos una métrica real de prueba.
4. Explica una limitación técnica detectada.
5. Ensaya una exposición de aproximadamente 15 minutos.

**Evidencia:** presentación y guion.

### Actividad 5. Ensayo de demostración

1. Reinicia la aplicación siguiendo la guía de instalación.
2. Ejecuta una inferencia local.
3. Muestra su registro.
4. Comprueba los servicios externos que se hayan incorporado.
5. Documenta un fallo posible y su recuperación.

**Evidencia:** acta breve de ensayo y capturas pertinentes.

## 20.14. Práctica final integradora: entrega y defensa del sistema Edge AI

### Enunciado

El alumnado entregará y defenderá el proyecto final desarrollado en los capítulos 18 y 19. El sistema debe contar con documentación suficiente para que una tercera persona comprenda su arquitectura, reproduzca sus funciones principales y evalúe sus resultados.

La entrega incluirá una memoria técnica, una guía de instalación, un manual de usuario, un registro de pruebas, evidencias verificables y una presentación oral con demostración.

### Condiciones de realización

- Trabajo individual o en equipo, según la organización del profesor.
- Se permite el uso de datos simulados, siempre que se identifiquen como tales.
- Los componentes no implementados deben marcarse como pendientes u opcionales.
- Las métricas deben proceder de ejecuciones reales y documentadas.
- No se publicarán secretos, credenciales ni datos personales innecesarios.

### Entregables

1. Carpeta del proyecto con código y configuración segura.
2. `documentacion/README.md` completo.
3. `documentacion/memoria_tecnica.md`.
4. `documentacion/instalacion.md` y `manual_usuario.md`.
5. `documentacion/registro_pruebas.csv` y evidencias.
6. Presentación y demostración del proyecto.

### Rúbrica de evaluación (10 puntos)

| Criterio | Puntuación máxima |
|---|---:|
| Memoria técnica: claridad, arquitectura y requisitos | 2,0 |
| Reproducibilidad de la instalación y del uso | 1,5 |
| Calidad del registro de pruebas y evidencias | 2,0 |
| Explicación del modelo de IA y sus limitaciones | 1,0 |
| Presentación oral y organización de contenidos | 1,5 |
| Demostración técnica y respuesta a preguntas | 1,5 |
| Seguridad documental y control de versiones | 0,5 |
| **Total** | **10,0** |

!!! example "Criterios de calidad"
    La máxima puntuación exige documentación coherente con el sistema implementado, pruebas contrastables y una defensa que explique las decisiones técnicas. No se penalizará la ausencia de hardware opcional si el alcance aprobado del proyecto contempla simulación y esta se documenta correctamente.

## 20.15. Lista de comprobación antes de entregar

- [ ] La memoria explica el problema, los objetivos y la arquitectura.
- [ ] Se identifica el hardware utilizado y el software instalado.
- [ ] Se distinguen los datos reales de los simulados.
- [ ] El modelo de IA está descrito con sus entradas y limitaciones.
- [ ] El README contiene comandos comprobados.
- [ ] El manual de usuario explica el funcionamiento normal.
- [ ] Existe un registro de pruebas con resultados observados.
- [ ] Las evidencias corresponden a ejecuciones reales.
- [ ] No se incluyen contraseñas ni tokens.
- [ ] La presentación tiene una duración adecuada.
- [ ] La demostración se ha ensayado.
- [ ] Se han documentado incidencias y mejoras futuras.

## 20.16. Autoevaluación

1. ¿Qué diferencia existe entre una memoria técnica y un manual de usuario?
2. ¿Por qué es importante documentar las versiones del software?
3. ¿Qué información mínima debe contener un caso de prueba?
4. ¿Qué riesgo supone publicar un token de InfluxDB?
5. ¿Por qué no basta con afirmar que un modelo tiene una exactitud elevada?
6. ¿Cómo debe documentarse una función todavía no implementada?
7. ¿Qué debe hacerse si una demostración en directo falla?
8. ¿Qué ventajas aporta un README bien estructurado?
9. ¿Qué limitaciones presenta una prueba realizada solo con datos sintéticos?
10. ¿Qué relación existe entre requisitos, pruebas y evidencias?

## 20.17. Resolución de problemas

### El archivo de registro de pruebas no existe

Ejecuta primero `02_registrar_prueba.py` y guarda al menos una prueba válida. Después vuelve a ejecutar el programa de resumen.

### No se encuentra la carpeta del proyecto

Comprueba:

```bash
ls -la ~/practicas
ls -la ~/practicas/proyecto_final
```

Si tu implementación utiliza otra ruta, modifica las variables `base` de los programas para que apunten a la carpeta real.

### El README ya existe

El primer programa evita sobrescribirlo. Edita el documento existente o haz una copia de seguridad antes de crear una nueva plantilla.

### El informe muestra más pruebas de las esperadas

Cada ejecución registrada produce una fila. Revisa si has registrado varias veces el mismo identificador y explica las repeticiones.

### No aparecen datos nuevos en Grafana

Comprueba el intervalo temporal, la consulta Flux, el bucket y que el programa responsable de escribir los datos esté funcionando. Las capturas antiguas no sustituyen a una comprobación actual.

### La demostración depende de Internet

Documenta las dependencias externas y prepara una ejecución local con datos de prueba. No atribuyas al sistema funciones que no puedan comprobarse durante la defensa.

## 20.18. Conclusiones del capítulo y cierre del libro

Con este capítulo se completa el recorrido del libro **Arduino UNO Q**: desde los primeros programas y la interacción con hardware hasta Linux, Python, comunicaciones IoT, almacenamiento de datos, visualización y aplicaciones de inteligencia artificial en el borde de la red.

El proyecto final reúne tres competencias esenciales: **diseñar**, **implementar y comprobar**, y **documentar y comunicar** una solución técnica. Un resultado profesional no se limita a que el programa funcione; también exige que sea comprensible, verificable, seguro y mantenible.

!!! success "Libro completado"
    Tras validar las actividades y la defensa del proyecto, habremos finalizado los **20 capítulos** del libro Arduino UNO Q. Como trabajo de cierre, conviene revisar los enlaces, la navegación de MkDocs y la publicación final en GitHub Pages.
