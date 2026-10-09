
# Capítulo 3. Primeros programas con Arduino UNO Q

## Objetivos de aprendizaje

Al finalizar este capítulo, el alumnado será capaz de:

- Crear una aplicación en Arduino App Lab.
- Identificar la estructura de un programa Arduino.
- Comprender el funcionamiento de `setup()` y `loop()`.
- Declarar constantes y variables.
- Configurar salidas digitales.
- Controlar los LED RGB integrados de Arduino UNO Q.
- Utilizar temporizadores mediante `delay()`.
- Crear funciones para organizar un programa.
- Utilizar la comunicación serie para depurar.
- Modificar y comprobar el funcionamiento de un programa.

## 1. Introducción a la programación de Arduino UNO Q

En el capítulo anterior instalamos Arduino App Lab y comprobamos el funcionamiento de la placa mediante el ejemplo Blink.

Ahora comenzaremos a desarrollar nuestros propios programas.

Arduino UNO Q dispone de dos procesadores:

- **Qualcomm QRB2210:** ejecuta Debian Linux y aplicaciones Python.
- **STM32U585:** ejecuta programas Arduino sobre Zephyr.

En este capítulo trabajaremos principalmente con el microcontrolador STM32U585.

Utilizaremos el lenguaje de programación Arduino, basado en C++.

!!! info "Nuestro primer objetivo"

    Aprenderemos a controlar los LED RGB integrados en Arduino UNO Q.

    De esta manera podremos realizar nuestras primeras prácticas sin necesidad de conectar componentes externos.

## 2. Estructura de un programa Arduino

Un programa Arduino, denominado habitualmente *sketch*, utiliza dos funciones principales:

```cpp
void setup()
{
    // Código de inicialización
}

void loop()
{
    // Código que se repite
}
```

### 2.1. La función setup()

La función `setup()` se ejecuta una vez cuando comienza el programa.

Se utiliza para configurar el funcionamiento de la placa.

Por ejemplo:

```cpp
void setup()
{
    pinMode(LED3_R, OUTPUT);
}
```

La instrucción `pinMode()` configura un pin como entrada o salida.

En este ejemplo configuramos el canal rojo del LED RGB 3 como salida digital.

### 2.2. La función loop()

La función `loop()` se ejecuta repetidamente mientras el programa está funcionando.

Ejemplo:

```cpp
void loop()
{
    digitalWrite(LED3_R, LOW);
    delay(1000);

    digitalWrite(LED3_R, HIGH);
    delay(1000);
}
```

Este programa enciende y apaga el LED rojo periódicamente.

### 2.3. Conceptos básicos

| Elemento | Descripción |
|---|---|
| `void` | Indica que una función no devuelve un valor |
| `setup()` | Función de inicialización |
| `loop()` | Función de ejecución repetitiva |
| `{ }` | Delimitan un bloque de instrucciones |
| `;` | Finaliza una instrucción |
| `//` | Introduce un comentario de una línea |
| `pinMode()` | Configura un pin |
| `digitalWrite()` | Establece el nivel lógico de una salida |
| `delay()` | Introduce una pausa en milisegundos |

!!! tip "Comentarios"

    Los comentarios permiten documentar el funcionamiento de un programa.

    No se ejecutan y no modifican el comportamiento del circuito.

## 3. Los LED RGB integrados

Arduino UNO Q incorpora cuatro LED RGB.

Cada LED RGB dispone de tres canales de color:

- Rojo (R).
- Verde (G).
- Azul (B).

Combinando estos canales podemos obtener diferentes colores.

Los LED RGB están distribuidos entre los dos procesadores.

| LED | Procesador que lo controla |
|---|---|
| RGB 1 | Qualcomm, Linux |
| RGB 2 | Qualcomm, Linux |
| RGB 3 | STM32 |
| RGB 4 | STM32 |

En este capítulo utilizaremos el LED RGB 3.

Sus canales se identifican mediante:

```cpp
LED3_R
LED3_G
LED3_B
```

Estas constantes están definidas por el entorno de programación de Arduino UNO Q.

### 3.1. Lógica activa a nivel bajo

Los LED RGB controlados por el STM32 utilizan lógica activa a nivel bajo.

Esto significa:

| Valor | Estado del canal |
|---|---|
| `LOW` | Encendido |
| `HIGH` | Apagado |

!!! warning "Importante"

    En estos LED integrados, `LOW` enciende el canal y `HIGH` lo apaga.

    Este comportamiento es diferente del que utilizaremos normalmente al conectar un LED externo entre una salida digital y GND.

## 4. Programa 1. Encender el LED rojo

### Objetivo

Encender permanentemente el canal rojo del LED RGB 3.

### Preparación

1. Conecta Arduino UNO Q al ordenador.
2. Abre Arduino App Lab.
3. Comprueba que la placa está disponible.
4. Accede a **My Apps**.
5. Selecciona **Create new app**.
6. Asigna el nombre `01_led_rojo`.
7. Abre el archivo `sketch/sketch.ino`.

Sustituye su contenido por el siguiente programa:

```cpp
// Programa 1: LED rojo
// Arduino UNO Q - STM32

void setup()
{
    pinMode(LED3_R, OUTPUT);
    pinMode(LED3_G, OUTPUT);
    pinMode(LED3_B, OUTPUT);

    // Apagar inicialmente los tres canales
    digitalWrite(LED3_R, HIGH);
    digitalWrite(LED3_G, HIGH);
    digitalWrite(LED3_B, HIGH);

    // Encender solamente el canal rojo
    digitalWrite(LED3_R, LOW);
}

void loop()
{
    // No es necesario repetir ninguna operación
}
```

### Ejecución

1. Guarda el programa.
2. Pulsa **Run**.
3. Espera a que finalice la preparación de la aplicación.
4. Observa el LED RGB 3.

### Resultado esperado

El LED RGB 3 permanece encendido en color rojo.

### Análisis

La función `setup()` configura los tres canales como salidas.

Posteriormente apaga los tres canales y enciende únicamente el rojo.

La función `loop()` está vacía porque no necesitamos modificar el estado del LED.

!!! example "Actividad 3.1"

    Modifica el programa para que el LED permanezca encendido en color verde.

    Después realiza una segunda modificación para que permanezca encendido en azul.

    Anota qué instrucciones has cambiado.

## 5. Programa 2. Parpadeo del LED

### Objetivo

Encender y apagar periódicamente el LED rojo.

Crea una nueva aplicación llamada `02_led_parpadeo`.

Introduce el siguiente programa:

```cpp
// Programa 2: Parpadeo del LED rojo
// Arduino UNO Q - STM32

void setup()
{
    pinMode(LED3_R, OUTPUT);
    pinMode(LED3_G, OUTPUT);
    pinMode(LED3_B, OUTPUT);

    digitalWrite(LED3_R, HIGH);
    digitalWrite(LED3_G, HIGH);
    digitalWrite(LED3_B, HIGH);
}

void loop()
{
    // Encender rojo
    digitalWrite(LED3_R, LOW);

    // Esperar un segundo
    delay(1000);

    // Apagar rojo
    digitalWrite(LED3_R, HIGH);

    // Esperar un segundo
    delay(1000);
}
```

### 5.1. La función delay()

La instrucción `delay()` detiene temporalmente la ejecución del sketch.

El tiempo se expresa en milisegundos.

| Instrucción | Tiempo |
|---|---|
| `delay(100)` | 0,1 segundos |
| `delay(250)` | 0,25 segundos |
| `delay(500)` | 0,5 segundos |
| `delay(1000)` | 1 segundo |
| `delay(2000)` | 2 segundos |

### 5.2. Modificar la velocidad

Modifica los dos valores de `delay()` para que el LED parpadee cada medio segundo.

Después utiliza:

```cpp
delay(200);
```

Observa cómo cambia la frecuencia de parpadeo.

!!! example "Actividad 3.2"

    Programa el LED para que:

    1. Permanezca encendido durante dos segundos.
    2. Permanezca apagado durante medio segundo.
    3. Repita continuamente esta secuencia.

    Explica por qué los tiempos de encendido y apagado son diferentes.

## 6. Programa 3. Secuencia de colores

### Objetivo

Programar una secuencia que encienda sucesivamente los canales rojo, verde y azul.

Crea una aplicación llamada `03_secuencia_rgb`.

```cpp
// Programa 3: Secuencia RGB
// Arduino UNO Q - STM32

void setup()
{
    pinMode(LED3_R, OUTPUT);
    pinMode(LED3_G, OUTPUT);
    pinMode(LED3_B, OUTPUT);

    // Estado inicial: todos apagados
    digitalWrite(LED3_R, HIGH);
    digitalWrite(LED3_G, HIGH);
    digitalWrite(LED3_B, HIGH);
}

void loop()
{
    // ROJO
    digitalWrite(LED3_R, LOW);
    digitalWrite(LED3_G, HIGH);
    digitalWrite(LED3_B, HIGH);

    delay(1000);

    // VERDE
    digitalWrite(LED3_R, HIGH);
    digitalWrite(LED3_G, LOW);
    digitalWrite(LED3_B, HIGH);

    delay(1000);

    // AZUL
    digitalWrite(LED3_R, HIGH);
    digitalWrite(LED3_G, HIGH);
    digitalWrite(LED3_B, LOW);

    delay(1000);
}
```

### Resultado esperado

El LED RGB 3 muestra la siguiente secuencia:

1. Rojo durante un segundo.
2. Verde durante un segundo.
3. Azul durante un segundo.
4. Repetición de la secuencia.

### 6.1. Combinación de colores

Un LED RGB permite obtener otros colores encendiendo simultáneamente varios canales.

| Color | Rojo | Verde | Azul |
|---|---|---|---|
| Rojo | LOW | HIGH | HIGH |
| Verde | HIGH | LOW | HIGH |
| Azul | HIGH | HIGH | LOW |
| Amarillo | LOW | LOW | HIGH |
| Cian | HIGH | LOW | LOW |
| Magenta | LOW | HIGH | LOW |
| Blanco | LOW | LOW | LOW |
| Apagado | HIGH | HIGH | HIGH |

!!! example "Actividad 3.3"

    Modifica el programa para que la secuencia sea:

    Rojo → Amarillo → Verde → Cian → Azul → Magenta → Blanco.

    Cada color deberá permanecer encendido durante 500 milisegundos.

## 7. Programa 4. Utilización de funciones

Cuando un programa aumenta de tamaño, resulta conveniente dividirlo en funciones.

Una función permite agrupar instrucciones que realizan una tarea concreta.

Vamos a crear una función que reciba los estados de los tres canales del LED.

### 7.1. Definición de una función

```cpp
void establecerColor(int rojo, int verde, int azul)
{
    digitalWrite(LED3_R, rojo);
    digitalWrite(LED3_G, verde);
    digitalWrite(LED3_B, azul);
}
```

Esta función recibe tres parámetros.

Cada parámetro representa el estado de un canal del LED.

Por ejemplo:

```cpp
establecerColor(LOW, HIGH, HIGH);
```

Enciende el LED rojo.

### 7.2. Programa completo

Crea una aplicación llamada `04_funciones_rgb`.

```cpp
// Programa 4: Control RGB mediante funciones
// Arduino UNO Q - STM32

const int TIEMPO = 1000;

// Funcion para establecer un color
void establecerColor(int rojo, int verde, int azul)
{
    digitalWrite(LED3_R, rojo);
    digitalWrite(LED3_G, verde);
    digitalWrite(LED3_B, azul);
}

// Funcion de inicializacion
void setup()
{
    pinMode(LED3_R, OUTPUT);
    pinMode(LED3_G, OUTPUT);
    pinMode(LED3_B, OUTPUT);

    establecerColor(HIGH, HIGH, HIGH);
}

// Funcion principal
void loop()
{
    // Rojo
    establecerColor(LOW, HIGH, HIGH);
    delay(TIEMPO);

    // Verde
    establecerColor(HIGH, LOW, HIGH);
    delay(TIEMPO);

    // Azul
    establecerColor(HIGH, HIGH, LOW);
    delay(TIEMPO);

    // Amarillo
    establecerColor(LOW, LOW, HIGH);
    delay(TIEMPO);

    // Apagado
    establecerColor(HIGH, HIGH, HIGH);
    delay(TIEMPO);
}
```

### 7.3. Ventajas de utilizar funciones

La utilización de funciones permite:

- Reducir la repetición de instrucciones.
- Facilitar la lectura del código.
- Simplificar las modificaciones.
- Detectar errores con mayor facilidad.
- Reutilizar código en diferentes programas.

### 7.4. Constantes y variables

En el programa anterior hemos utilizado:

```cpp
const int TIEMPO = 1000;
```

La palabra `const` indica que el valor no debe modificarse durante la ejecución.

El tipo `int` permite almacenar números enteros.

El identificador `TIEMPO` representa la duración de las pausas.

Si queremos cambiar la velocidad de toda la secuencia, únicamente tendremos que modificar esta constante.

!!! example "Actividad 3.4"

    Modifica el programa para que:

    - La duración de cada color sea de 300 ms.
    - Se incorporen los colores cian y magenta.
    - La secuencia termine con el LED apagado durante dos segundos.

    Utiliza funciones y evita repetir instrucciones innecesariamente.

## 8. Depuración mediante comunicación serie

Durante el desarrollo de programas es importante disponer de herramientas que permitan conocer qué está ocurriendo.

Una técnica habitual consiste en enviar mensajes de diagnóstico mediante comunicación serie.

### 8.1. Inicializar la comunicación

La instrucción:

```cpp
Serial.begin(9600);
```

Inicializa la comunicación serie a 9600 bits por segundo.

### 8.2. Enviar mensajes

La instrucción:

```cpp
Serial.println("Programa iniciado");
```

Envía un mensaje de texto y añade un salto de línea.

### 8.3. Ejemplo completo

Crea una aplicación llamada `05_monitor_serie`.

```cpp
// Programa 5: Depuracion serie
// Arduino UNO Q - STM32

void setup()
{
    Serial.begin(9600);

    pinMode(LED3_R, OUTPUT);
    pinMode(LED3_G, OUTPUT);
    pinMode(LED3_B, OUTPUT);

    digitalWrite(LED3_R, HIGH);
    digitalWrite(LED3_G, HIGH);
    digitalWrite(LED3_B, HIGH);

    Serial.println("Programa iniciado");
}

void loop()
{
    Serial.println("LED encendido");

    digitalWrite(LED3_R, LOW);
    delay(1000);

    Serial.println("LED apagado");

    digitalWrite(LED3_R, HIGH);
    delay(1000);
}
```

### 8.4. Consultar los mensajes

1. Ejecuta la aplicación desde Arduino App Lab.
2. Abre el panel de consola.
3. Selecciona la sección correspondiente al sketch o microcontrolador.
4. Comprueba que aparecen los mensajes.

Resultado esperado:

```text
Programa iniciado
LED encendido
LED apagado
LED encendido
LED apagado
...
```

!!! info "Consola de Arduino App Lab"

    Arduino App Lab permite consultar los mensajes de las aplicaciones.

    Los mensajes generados mediante `Serial.println()` en el sketch
    pueden consultarse en la consola correspondiente al microcontrolador.

    La salida de los programas Python se consulta por separado.

## 9. Errores habituales de programación

Durante las primeras prácticas pueden aparecer errores de compilación o ejecución.

| Error | Causa habitual |
|---|---|
| Falta `;` | Instrucción sin punto y coma |
| Llaves incorrectas | Bloque de código mal delimitado |
| Nombre incorrecto | Variable o constante no reconocida |
| LED apagado | Estado lógico incorrecto |
| Color incorrecto | Canales RGB mal configurados |
| Parpadeo inesperado | Tiempo de `delay()` incorrecto |
| No aparecen mensajes | Consola incorrecta o comunicación no inicializada |

### 9.1. Diferencia entre compilación y ejecución

La compilación transforma el código fuente en instrucciones ejecutables por el microcontrolador.

Si existen errores de sintaxis, la compilación puede detenerse.

Una vez compilado, el programa se ejecuta en la placa.

También pueden aparecer errores de funcionamiento aunque la compilación haya finalizado correctamente.

Por ejemplo, un programa puede compilar sin errores y encender un LED de color diferente al esperado.

!!! tip "Método de resolución de problemas"

    Cuando un programa no funcione:

    1. Comprueba los mensajes de compilación.
    2. Revisa los nombres de las constantes.
    3. Verifica los estados HIGH y LOW.
    4. Comprueba los tiempos.
    5. Introduce mensajes de diagnóstico.
    6. Realiza cambios pequeños y vuelve a ejecutar.

## 10. Práctica evaluable: semáforo RGB

### Objetivo

Desarrollar un programa que simule el funcionamiento de un semáforo utilizando el LED RGB 3 integrado en Arduino UNO Q.

### Material necesario

- Arduino UNO Q.
- Ordenador con Windows 11.
- Cable USB-C.
- Arduino App Lab.

### Requisitos funcionales

El programa deberá cumplir las siguientes condiciones:

1. Encender el LED rojo durante cinco segundos.
2. Encender el LED verde durante cuatro segundos.
3. Encender el LED amarillo durante dos segundos.
4. Apagar el LED durante un segundo.
5. Repetir continuamente la secuencia.

Además, deberá:

- Utilizar una función para establecer los colores.
- Utilizar constantes para definir los tiempos.
- Enviar mensajes a la consola serie.
- Incluir comentarios explicativos.

### Desarrollo

**Paso 1.** Crea una aplicación llamada `practica_semaforo`.

**Paso 2.** Configura los tres canales RGB como salidas.

**Paso 3.** Crea una función para establecer el color del LED.

**Paso 4.** Define las constantes de tiempo.

**Paso 5.** Programa la secuencia del semáforo.

**Paso 6.** Incorpora mensajes mediante `Serial.println()`.

**Paso 7.** Ejecuta y comprueba el funcionamiento.

**Paso 8.** Corrige los posibles errores.

### Ampliación voluntaria

Modifica el programa para que el LED verde parpadee tres veces antes de pasar al amarillo.

Cada parpadeo deberá incluir:

- 300 ms encendido.
- 300 ms apagado.

### Entrega

El alumnado entregará un documento PDF con:

- Portada identificativa.
- Objetivo de la práctica.
- Código fuente completo.
- Explicación de las funciones utilizadas.
- Captura de Arduino App Lab.
- Captura de los mensajes de consola.
- Descripción de las pruebas realizadas.
- Conclusiones.

También entregará el código fuente del programa según las indicaciones del profesor.

### Criterios de evaluación

| Criterio | Puntuación |
|---|---:|
| Configuración correcta de los LED | 1 punto |
| Secuencia y tiempos correctos | 3 puntos |
| Utilización de funciones | 2 puntos |
| Utilización de constantes | 1 punto |
| Mensajes de depuración | 1 punto |
| Comentarios y claridad del código | 1 punto |
| Documentación de la práctica | 1 punto |
| **Total** | **10 puntos** |

## 11. Resumen del capítulo

En este capítulo hemos desarrollado nuestros primeros programas con Arduino UNO Q.

Hemos aprendido a utilizar las funciones `setup()` y `loop()`, configurar salidas digitales y controlar los LED RGB integrados.

También hemos utilizado constantes, funciones y mensajes de depuración mediante comunicación serie.

Estos conocimientos constituyen la base para desarrollar programas más complejos.

En el siguiente capítulo comenzaremos a trabajar con entradas y salidas digitales y conectaremos componentes externos mediante una protoboard.

## Documentación de referencia

- [Arduino UNO Q - Manual oficial](https://docs.arduino.cc/tutorials/uno-q/user-manual/)
- [Arduino App Lab - Ejemplos](https://docs.arduino.cc/software/app-lab/tutorials/examples/)
- [Arduino - Ejemplo Blink](https://docs.arduino.cc/built-in-examples/basics/Blink)
- [Arduino - Blink Without Delay](https://docs.arduino.cc/built-in-examples/digital/BlinkWithoutDelay/)
