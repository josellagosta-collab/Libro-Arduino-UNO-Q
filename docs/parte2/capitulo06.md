# Capítulo 6. Comunicación entre procesadores de Arduino UNO Q

## Objetivos de aprendizaje

Al finalizar el capítulo, el alumnado será capaz de:

- Diferenciar las funciones del microprocesador Qualcomm QRB2210 y del microcontrolador STM32U585.
- Explicar por qué una aplicación necesita intercambiar información entre Linux y el microcontrolador.
- Identificar el papel de **Arduino Router**, **Bridge** y las llamadas **RPC**.
- Crear una aplicación de Arduino App Lab con código Python y un sketch Arduino.
- Publicar una función del microcontrolador para invocarla desde Python.
- Intercambiar órdenes y valores numéricos entre ambos procesadores.
- Consultar los registros de ejecución y diagnosticar errores de comunicación.
- Diseñar y documentar una aplicación híbrida sencilla.

## 1. Una placa, dos entornos de ejecución

Arduino UNO Q combina dos procesadores con tareas diferentes:

| Componente | Entorno | Funciones principales |
|---|---|---|
| Qualcomm QRB2210 (MPU) | Debian Linux | Python, red, servicios, procesamiento de datos y aplicaciones complejas |
| STM32U585 (MCU) | Zephyr y entorno Arduino | Lectura de sensores, control de GPIO, temporización y actuación sobre hardware |

En los capítulos 3, 4 y 5 hemos trabajado principalmente con programas Arduino ejecutados en el STM32. En este capítulo incorporaremos **Python en Linux** y aprenderemos a coordinar ambos entornos.

!!! info "Idea fundamental"

    No estamos ejecutando Python directamente en el STM32 ni accediendo a los GPIO del STM32 desde Linux como si fueran pines locales. Cada procesador ejecuta su propio código y ambos se comunican mediante un mecanismo de intercambio de mensajes.

### 1.1. Ejemplo de aplicación híbrida

Imaginemos un sistema que debe recibir órdenes desde una futura página web y encender un LED:

1. Una aplicación Python en Linux recibe o genera una orden.
2. Python envía la orden al microcontrolador.
3. El STM32 cambia el estado de una salida digital.
4. El LED se enciende o se apaga.

Esta separación es especialmente útil en aplicaciones de IoT, automatización industrial y Edge AI.

## 2. Bridge, Arduino Router y RPC

**RPC** significa *Remote Procedure Call*, o llamada a procedimiento remoto. Permite invocar una función que se ejecuta en otro proceso o procesador.

En Arduino UNO Q, la biblioteca **Bridge** ofrece una interfaz de programación para estas llamadas. El servicio Linux **arduino-router** se encarga de encaminar los mensajes entre los participantes.

```text
                ARDUINO UNO Q
┌───────────────────────────────┐
│ Qualcomm QRB2210             │
│ Debian Linux                 │
│                               │
│ python/main.py               │
│ Bridge.call("set_led", True)  │
│             │                 │
│       arduino-router          │
└─────────────┼─────────────────┘
              │ RPC
┌─────────────▼─────────────────┐
│ STM32U585                     │
│ Zephyr + Arduino              │
│                               │
│ sketch/sketch.ino             │
│ Bridge.provide_safe(...)      │
│             │                 │
│       Salida digital          │
└───────────────────────────────┘
```

*Figura 6.1. Esquema conceptual de una llamada RPC entre Linux y STM32.*

### 2.1. Funciones principales

| Función | Entorno | Utilidad |
|---|---|---|
| `Bridge.begin()` | Arduino | Inicializa la comunicación del sketch |
| `Bridge.provide_safe(nombre, función)` | Arduino | Publica una función del STM32 y la ejecuta de forma segura en el contexto del bucle principal |
| `Bridge.provide(nombre, función)` | Arduino | Publica una función que puede ejecutarse en el hilo de comunicación; requiere especial cuidado con la concurrencia |
| `Bridge.call(nombre, argumentos...)` | Python | Invoca una función remota y espera su respuesta |
| `Bridge.notify(nombre, argumentos...)` | API Bridge cuando esté disponible | Envía una notificación sin esperar resultado |

!!! warning "Seguridad de ejecución"

    Cuando la función remota utiliza `digitalWrite()`, `Serial` u otras API habituales de Arduino, emplearemos `Bridge.provide_safe()`.

    Evitaremos llamadas recursivas de comunicación desde funciones registradas con `Bridge.provide()`, porque pueden producir bloqueos.

## 3. Preparación del entorno

### Material necesario

- Una placa Arduino UNO Q.
- Ordenador con Windows 11 y Arduino App Lab instalado.
- Cable USB-C de **datos** y alimentación adecuada.
- Conexión a la placa configurada en Arduino App Lab.

**No es necesario utilizar protoboard:** las primeras pruebas emplean el LED integrado controlado por el STM32.

### Procedimiento

1. Conecta Arduino UNO Q al ordenador.
2. Abre Arduino App Lab.
3. Comprueba que la placa aparece como dispositivo disponible.
4. Crea una aplicación nueva con el nombre `06_01_bridge_led`.
5. Localiza los archivos `python/main.py` y `sketch/sketch.ino`.
6. Comprueba que puedes editar ambos archivos desde la misma aplicación.

!!! tip "Dos archivos, dos procesadores"

    `python/main.py` se ejecuta en Debian Linux, mientras que `sketch/sketch.ino` se compila para el microcontrolador STM32.

    Pulsar **Run** en Arduino App Lab permite preparar y ejecutar los componentes de la aplicación.

## 4. Programa 1. Encender y apagar un LED desde Python

### Objetivo

Enviar periódicamente una orden desde Python al STM32 para encender y apagar un LED integrado.

Este primer programa adapta el ejemplo de comunicación RPC del manual oficial de Arduino UNO Q.

### 4.1. Código Arduino: `sketch/sketch.ino`

```cpp
#include <Arduino.h>
#include "Arduino_RouterBridge.h"

// Función invocada desde Python.
// LED_BUILTIN corresponde al LED integrado usado por el ejemplo oficial.
void set_led_state(bool encendido)
{
    // En el LED integrado, LOW significa encendido.
    digitalWrite(LED_BUILTIN, encendido ? LOW : HIGH);
}

void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);

    Bridge.begin();

    // La función usa digitalWrite: registro seguro.
    Bridge.provide_safe("set_led_state", set_led_state);
}

void loop()
{
    // Bridge gestiona la recepción de llamadas remotas.
}
```

### 4.2. Código Python: `python/main.py`

```python
from arduino.app_utils import *
import time

led_encendido = False


def loop():
    global led_encendido

    time.sleep(1)
    led_encendido = not led_encendido

    Bridge.call("set_led_state", led_encendido)
    print(f"Orden enviada al STM32: {led_encendido}")


App.run(user_loop=loop)
```

### 4.3. Ejecución

1. Guarda los dos archivos.
2. Pulsa **Run**.
3. Espera a que se compile el sketch y se inicie el componente Python.
4. Observa el LED integrado del STM32.
5. Abre la consola **Main (Python)** y comprueba los mensajes.

**Resultado esperado:** el LED cambia de estado aproximadamente cada segundo.

!!! example "Actividad 6.1"

    Modifica el programa Python para que el LED permanezca encendido dos segundos y apagado medio segundo. No cambies el sketch Arduino.

    Explica por qué el comportamiento puede modificarse desde Linux sin cambiar la lógica de control del GPIO.

## 5. Análisis de la comunicación

### 5.1. Publicar una función

La instrucción:

```cpp
Bridge.provide_safe("set_led_state", set_led_state);
```

registra un nombre remoto (`"set_led_state"`) y lo asocia con una función C++.

### 5.2. Invocar la función

La instrucción Python:

```python
Bridge.call("set_led_state", True)
```

solicita al STM32 que ejecute la función registrada, pasando un valor booleano.

### 5.3. Correspondencia de tipos

En nuestras primeras aplicaciones utilizaremos tipos sencillos:

| Python | C++ | Ejemplo |
|---|---|---|
| `bool` | `bool` | `True` → encender |
| `int` | `int` | `2` → seleccionar color |
| `str` | Requiere una firma compatible | Texto de diagnóstico |

!!! warning "Compatibilidad de parámetros"

    El nombre RPC y los parámetros deben coincidir entre el emisor y la función registrada. Para evitar problemas, empezaremos con valores booleanos y enteros sencillos.

## 6. Programa 2. Seleccionar el color RGB desde Linux

### Objetivo

Enviar un número desde Python y utilizarlo en el STM32 para seleccionar un color del LED RGB 3.

| Valor enviado | Resultado |
|---|---|
| 0 | LED apagado |
| 1 | Rojo |
| 2 | Verde |
| 3 | Azul |
| 4 | Amarillo |

### 6.1. Código Arduino: `sketch/sketch.ino`

```cpp
#include <Arduino.h>
#include "Arduino_RouterBridge.h"

void set_color(int color)
{
    // Todos los canales apagados (lógica activa en LOW).
    digitalWrite(LED3_R, HIGH);
    digitalWrite(LED3_G, HIGH);
    digitalWrite(LED3_B, HIGH);

    switch (color)
    {
        case 1: // Rojo
            digitalWrite(LED3_R, LOW);
            break;

        case 2: // Verde
            digitalWrite(LED3_G, LOW);
            break;

        case 3: // Azul
            digitalWrite(LED3_B, LOW);
            break;

        case 4: // Amarillo
            digitalWrite(LED3_R, LOW);
            digitalWrite(LED3_G, LOW);
            break;

        default: // Apagado
            break;
    }
}

void setup()
{
    pinMode(LED3_R, OUTPUT);
    pinMode(LED3_G, OUTPUT);
    pinMode(LED3_B, OUTPUT);

    set_color(0);

    Bridge.begin();
    Bridge.provide_safe("set_color", set_color);
}

void loop()
{
}
```

### 6.2. Código Python: `python/main.py`

```python
from arduino.app_utils import *
import time

COLORES = [1, 2, 3, 4, 0]
NOMBRES = {
    0: "Apagado",
    1: "Rojo",
    2: "Verde",
    3: "Azul",
    4: "Amarillo",
}

indice = 0


def loop():
    global indice

    color = COLORES[indice]
    Bridge.call("set_color", color)
    print(f"Color solicitado: {NOMBRES[color]} ({color})")

    indice = (indice + 1) % len(COLORES)
    time.sleep(1)


App.run(user_loop=loop)
```

### 6.3. Comprobación

1. Crea una nueva aplicación `06_02_bridge_rgb`.
2. Copia los dos archivos anteriores.
3. Ejecuta la aplicación.
4. Comprueba que el LED recorre los colores de la tabla.
5. Observa los mensajes en la consola Python.

!!! example "Actividad 6.2"

    Añade los colores cian, magenta y blanco.

    Amplía la tabla de códigos y modifica ambos programas. Documenta los nuevos valores que viajan desde Linux al STM32.

## 7. Programa 3. Enviar un estado calculado en Python

Hasta ahora Python ha enviado órdenes de forma secuencial. En una aplicación real, la orden puede depender de un cálculo o de una condición.

### Objetivo

Simular una medida de temperatura en Linux y comunicar al STM32 si debe activarse una alarma visual.

**Esta práctica utiliza datos simulados.** No hay todavía un sensor físico de temperatura conectado.

### 7.1. Sketch Arduino

```cpp
#include <Arduino.h>
#include "Arduino_RouterBridge.h"

void set_alarm(bool alarma)
{
    // Rojo cuando hay alarma; verde en estado normal.
    digitalWrite(LED3_R, alarma ? LOW : HIGH);
    digitalWrite(LED3_G, alarma ? HIGH : LOW);
    digitalWrite(LED3_B, HIGH);
}

void setup()
{
    pinMode(LED3_R, OUTPUT);
    pinMode(LED3_G, OUTPUT);
    pinMode(LED3_B, OUTPUT);

    digitalWrite(LED3_R, HIGH);
    digitalWrite(LED3_G, HIGH);
    digitalWrite(LED3_B, HIGH);

    Bridge.begin();
    Bridge.provide_safe("set_alarm", set_alarm);
}

void loop()
{
}
```

### 7.2. Programa Python

```python
from arduino.app_utils import *
import time

TEMPERATURAS = [22, 25, 29, 31, 35, 27, 23]
UMBRAL = 30
indice = 0


def loop():
    global indice

    temperatura = TEMPERATURAS[indice]
    alarma = temperatura >= UMBRAL

    Bridge.call("set_alarm", alarma)
    print(
        f"Temperatura simulada: {temperatura} °C | "
        f"Alarma: {'ACTIVA' if alarma else 'INACTIVA'}"
    )

    indice = (indice + 1) % len(TEMPERATURAS)
    time.sleep(2)


App.run(user_loop=loop)
```

### 7.3. Resultado esperado

- Si la temperatura simulada es inferior a 30 °C, el LED aparece verde.
- Si la temperatura simulada alcanza o supera los 30 °C, aparece rojo.
- La consola Python muestra la temperatura y el estado de la alarma.

!!! example "Actividad 6.3"

    Cambia el umbral a 28 °C. Después añade un tercer estado: amarillo cuando la temperatura esté entre 26 y 27 °C, ambos incluidos.

    Decide qué información debe calcular Python y qué debe ejecutar el STM32. Justifica tu diseño.

## 8. Supervisión y resolución de problemas

Arduino App Lab dispone de registros diferenciados para el arranque de la aplicación, Python y el sketch del microcontrolador.

| Panel | Qué comprobar |
|---|---|
| **Start-up** | Compilación, despliegue e inicio de la aplicación |
| **Main (Python)** | Mensajes de `print()` y excepciones Python |
| **Sketch (Microcontroller)** | Mensajes de `Serial.println()` del STM32 |

### Errores frecuentes

| Síntoma | Posible causa | Comprobación |
|---|---|---|
| La aplicación no inicia | Error de compilación | Revisar **Start-up** |
| Python muestra una excepción RPC | Nombre de función incorrecto | Comparar `Bridge.call()` y `Bridge.provide_safe()` |
| El LED no cambia | Se está usando el LED o canal incorrecto | Verificar `LED_BUILTIN`, `LED3_R`, `LED3_G` y `LED3_B` |
| El LED muestra el estado contrario | Lógica activa en nivel bajo | Revisar `LOW` y `HIGH` |
| La orden no llega al STM32 | Bridge no inicializado o componente detenido | Revisar `Bridge.begin()` y los registros |
| La aplicación se bloquea | Uso inadecuado de callbacks o llamadas anidadas | Mantener cortas las funciones RPC y usar `provide_safe()` para GPIO |

!!! tip "Método de diagnóstico"

    1. Comprueba que la placa está conectada.
    2. Revisa primero los mensajes de arranque.
    3. Comprueba que Python se está ejecutando.
    4. Verifica que el nombre RPC coincide exactamente.
    5. Comprueba el tipo de dato enviado.
    6. Ejecuta de nuevo una versión mínima del programa.

## 9. Buenas prácticas de diseño

En proyectos con dos procesadores conviene repartir las responsabilidades:

- **Linux/Python:** interfaz de usuario, redes, almacenamiento, análisis de datos y lógica de alto nivel.
- **STM32/Arduino:** lectura y escritura de GPIO, temporización y actuación sobre periféricos.
- **Bridge/RPC:** intercambio de órdenes y resultados entre ambos entornos.

Evita enviar órdenes repetidas sin necesidad. En aplicaciones reales, define qué ocurre si Linux se reinicia o deja de comunicarse: por ejemplo, apagar una salida mediante un mecanismo de seguridad implementado en el microcontrolador.

!!! warning "Aplicaciones críticas"

    Las prácticas de este capítulo son educativas. Un sistema de seguridad industrial no debe depender únicamente de una orden RPC ni de un LED de diagnóstico. Debe incorporar protecciones y mecanismos independientes adecuados al riesgo.

## 10. Práctica evaluable: panel de control híbrido

### Enunciado

Desarrolla una aplicación de Arduino UNO Q que permita controlar el LED RGB 3 desde un programa Python que se ejecuta en Linux.

### Requisitos funcionales

1. La aplicación tendrá un archivo Python y un sketch Arduino.
2. Python enviará al menos **cinco códigos de estado** distintos.
3. El STM32 interpretará los códigos y mostrará un color diferente para cada estado (se permite incluir apagado).
4. La comunicación utilizará `Bridge.call()` y `Bridge.provide_safe()`.
5. Los cambios de estado se realizarán automáticamente cada dos segundos.
6. Python mostrará en consola el código y el nombre del estado enviado.
7. El código incluirá comentarios y constantes con nombres descriptivos.
8. Se documentarán al menos tres pruebas de funcionamiento.

### Ampliación voluntaria

Añade un estado de alarma intermitente gestionado por el STM32 sin bloquear el procesamiento de las órdenes entrantes. Para ello puedes utilizar `millis()` en `loop()`.

### Entrega

El alumnado entregará:

- Los archivos `python/main.py` y `sketch/sketch.ino`.
- Un PDF con portada, objetivo, arquitectura de la aplicación, explicación de las llamadas RPC, capturas de las consolas, resultados de las pruebas y conclusiones.
- Una demostración del funcionamiento sobre la placa.

### Rúbrica de evaluación

| Criterio | Puntuación |
|---|---:|
| Aplicación con los dos componentes correctamente configurados | 1 |
| Inicialización y registro RPC correctos | 2 |
| Envío y recepción de los cinco estados | 2 |
| Control correcto del LED RGB | 2 |
| Mensajes y diagnóstico | 1 |
| Claridad y organización del código | 1 |
| Documentación y pruebas | 1 |
| **Total** | **10** |

## 11. Resumen

En este capítulo hemos aprendido a comunicar los dos procesadores de Arduino UNO Q. Hemos utilizado Python en Debian Linux para generar órdenes y un sketch Arduino en el STM32 para controlar hardware.

El mecanismo **Bridge/RPC** permite combinar las ventajas de ambos entornos sin mezclar sus responsabilidades. Este conocimiento será fundamental para los capítulos de Linux, Python, redes, servicios e inteligencia artificial.

En el **capítulo 7** comenzaremos a explorar Debian Linux en Arduino UNO Q.

## Documentación de referencia

- [Arduino UNO Q — Manual oficial y comunicación Bridge/RPC](https://docs.arduino.cc/tutorials/uno-q/user-manual/)
- [Arduino UNO Q — Características y recursos oficiales](https://docs.arduino.cc/hardware/uno-q)
- [Arduino UNO Q — Introducción a Debian Linux](https://docs.arduino.cc/tutorials/uno-q/debian-guide/)
- [Arduino App Lab — Ejemplos oficiales](https://docs.arduino.cc/software/app-lab/tutorials/examples/)
