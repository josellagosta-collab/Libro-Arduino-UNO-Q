# Capítulo 5. Sensores y actuadores

## Objetivos de aprendizaje

Al finalizar este capítulo, el alumnado será capaz de:

- Distinguir sensores y actuadores e identificar sus señales de entrada y salida.
- Interpretar una señal analógica y diferenciarla de una señal digital.
- Conectar un potenciómetro a una entrada analógica de Arduino UNO Q.
- Obtener medidas con `analogRead()` y convertirlas a magnitudes útiles.
- Construir un divisor de tensión con una resistencia LDR.
- Regular el brillo de un LED mediante PWM y `analogWrite()`.
- Implementar un sistema de control que relacione un sensor y un actuador.
- Documentar el montaje, el código, las pruebas y las medidas obtenidas.

## 1. Introducción

En el capítulo anterior utilizamos entradas y salidas digitales para controlar LED y leer pulsadores. Ahora aprenderemos a conectar **sensores**, que obtienen información del entorno, y **actuadores**, que producen una respuesta física.

Un sistema de control sencillo sigue este esquema:

**Entorno → Sensor → Arduino UNO Q → Actuador → Entorno**

Por ejemplo, un sensor puede detectar que disminuye la iluminación y Arduino puede aumentar el brillo de un LED.

En estas prácticas ejecutaremos el código en el **STM32U585** de Arduino UNO Q. La programación se realizará con Arduino App Lab, siguiendo el procedimiento del capítulo 3.

!!! warning "Seguridad eléctrica"

    Los GPIO del STM32 trabajan con lógica de **3,3 V**. Según el pinout oficial, algunas entradas son tolerantes a 5 V, pero **A0 y A1 no lo son**. Nunca conectes 5 V a A0 o A1.

    Alimentaremos los sensores analógicos de este capítulo desde **3V3**, no desde 5 V. Conecta y desconecta los circuitos con la placa sin alimentación.

    Un GPIO no debe alimentar directamente motores, relés, tiras LED ni otras cargas de potencia. Esas aplicaciones necesitan una etapa de potencia y, normalmente, alimentación independiente.

## 2. Sensores, actuadores y tipos de señales

### 2.1. Sensores

Un sensor convierte una magnitud física en una señal que puede interpretar un sistema electrónico.

| Sensor | Magnitud medida | Señal habitual |
|---|---|---|
| Pulsador | Accionamiento | Digital |
| Potenciómetro | Posición del mando | Analógica |
| LDR con divisor | Iluminación aproximada | Analógica |
| DHT11/DHT22 | Temperatura y humedad | Digital, con protocolo |
| HC-SR04 | Distancia | Pulsos digitales |

En este capítulo utilizaremos **potenciómetro y LDR**. Los sensores con protocolos específicos se estudiarán posteriormente.

### 2.2. Actuadores

Un actuador transforma una orden eléctrica en una acción observable.

| Actuador | Acción | Consideración |
|---|---|---|
| LED | Emite luz | Necesita resistencia limitadora |
| Zumbador activo | Emite sonido | Verificar tensión y corriente; puede requerir transistor |
| Servomotor | Mueve un eje | Requiere alimentación adecuada y control por pulsos |
| Motor DC | Produce giro | Necesita controlador de motor |
| Relé | Conmuta una carga | Necesita módulo/controlador y protección |

Por seguridad, nuestras primeras prácticas de actuación utilizarán **un LED externo**.

### 2.3. Señales digitales y analógicas

Una señal digital presenta estados discretos, como `LOW` y `HIGH`. Una señal analógica puede adoptar múltiples niveles de tensión dentro de un intervalo.

En el STM32, el conversor analógico-digital (ADC) transforma la tensión de entrada en un número. La resolución que obtiene un sketch depende de la configuración de `analogReadResolution()`.

## 3. Material necesario

Por pareja de alumnos:

- Arduino UNO Q, cable USB-C y ordenador con Arduino App Lab.
- Protoboard y cables de conexión.
- Potenciómetro de **10 kΩ**.
- LDR (fotorresistencia).
- Resistencia fija de **10 kΩ** para el divisor de tensión.
- Un LED externo y una resistencia de **330 Ω** (220 Ω también puede servir si se comprueba la corriente).
- Multímetro, si está disponible.
- Pinout oficial de Arduino UNO Q utilizado en el capítulo 1.

!!! tip "Identificación de pines"

    Antes de cablear, localiza físicamente **3V3**, **GND**, **A0** y **D9** en el pinout oficial. Comprueba que no confundes 3V3 con 5V ni A0 con otra posición del conector.

## 4. Lectura de señales analógicas

### 4.1. El conversor ADC

La función `analogRead(pin)` devuelve una lectura digital proporcional a la tensión aplicada a una entrada analógica.

En nuestros ejemplos fijaremos explícitamente una resolución de **12 bits**:

```cpp
analogReadResolution(12);
```

Con esta configuración, el intervalo nominal de lectura es de **0 a 4095**. Para una entrada cuya escala de medida corresponde a 0–3,3 V, la conversión aproximada es:

\[
V \approx \frac{\text{lectura} \times 3,3}{4095}
\]

La tensión real puede presentar errores por tolerancias, referencia, ruido y características del ADC. No utilizaremos estas medidas como instrumentos de precisión.

!!! info "Resolución frente a exactitud"

    Tener 4096 niveles posibles no significa que la tensión medida sea exacta. La resolución describe el número de niveles; la exactitud depende de otros factores eléctricos.

## 5. Programa 1. Lectura de un potenciómetro

### 5.1. Objetivo

Leer la posición de un potenciómetro y mostrar su valor en la consola del sketch.

### 5.2. Conexiones

Con la placa desconectada:

1. Inserta el potenciómetro de 10 kΩ en la protoboard.
2. Conecta uno de sus **terminales exteriores** a **3V3**.
3. Conecta el otro terminal exterior a **GND**.
4. Conecta el **terminal central (cursor)** a **A0**.
5. Revisa el cableado y conecta la placa.

| Potenciómetro | Arduino UNO Q |
|---|---|
| Terminal exterior 1 | 3V3 |
| Terminal central | A0 |
| Terminal exterior 2 | GND |

Si intercambias los dos terminales exteriores, se invierte el sentido de crecimiento de la lectura; no es un fallo.

!!! warning "No utilizar 5 V"

    La entrada **A0 no es tolerante a 5 V**. El potenciómetro debe conectarse entre **3V3 y GND**.

### 5.3. Programa completo

Crea una aplicación llamada `01_potenciometro` y escribe en `sketch/sketch.ino`:

```cpp
#include <Arduino.h>

const int PIN_POTENCIOMETRO = A0;

void setup()
{
    Serial.begin(9600);
    analogReadResolution(12);
    Serial.println("Lectura del potenciometro");
}

void loop()
{
    int lectura = analogRead(PIN_POTENCIOMETRO);
    float voltios = lectura * 3.3f / 4095.0f;

    Serial.print("ADC: ");
    Serial.print(lectura);
    Serial.print(" | Tension aproximada: ");
    Serial.print(voltios, 2);
    Serial.println(" V");

    delay(250);
}
```

### 5.4. Comprobación

1. Ejecuta la aplicación desde Arduino App Lab.
2. Abre la consola correspondiente al sketch del microcontrolador.
3. Gira lentamente el potenciómetro.
4. Comprueba que las lecturas cambian de forma progresiva.
5. Anota tres lecturas: mínimo, posición central y máximo.

Ejemplo **orientativo**, no valores garantizados:

```text
ADC: 25 | Tension aproximada: 0.02 V
ADC: 2038 | Tension aproximada: 1.64 V
ADC: 4080 | Tension aproximada: 3.29 V
```

!!! example "Actividad 5.1. Medidas analógicas"

    Registra una tabla con cinco posiciones del potenciómetro, lectura ADC y tensión calculada. Explica por qué los valores reales pueden diferir ligeramente de 0, 2048 y 4095.

## 6. Programa 2. Porcentaje de apertura

Podemos transformar una lectura analógica en un valor más intuitivo, por ejemplo, un porcentaje de 0 a 100.

\[
\text{porcentaje} = \frac{\text{lectura} \times 100}{4095}
\]

Crea la aplicación `02_potenciometro_porcentaje`:

```cpp
#include <Arduino.h>

const int PIN_POTENCIOMETRO = A0;

void setup()
{
    Serial.begin(9600);
    analogReadResolution(12);
}

void loop()
{
    int lectura = analogRead(PIN_POTENCIOMETRO);
    int porcentaje = (lectura * 100L) / 4095;

    Serial.print("Posicion: ");
    Serial.print(porcentaje);
    Serial.println(" %");

    delay(200);
}
```

La expresión `100L` realiza la multiplicación con un entero largo, evitando desbordamientos en plataformas con enteros pequeños y haciendo el ejemplo más portable.

!!! example "Actividad 5.2. Conversión de unidades"

    Modifica el programa para mostrar también una escala de 0 a 10. Explica qué sucede cuando el potenciómetro está aproximadamente a la mitad de su recorrido.

## 7. Modulación por ancho de pulso (PWM)

### 7.1. ¿Qué es PWM?

PWM (*Pulse Width Modulation*) permite modificar la proporción de tiempo que una señal digital permanece activa dentro de un ciclo.

En una salida PWM, la tensión alterna rápidamente entre niveles digitales. No es una salida analógica continua. Un LED puede percibirse más o menos brillante según el **ciclo de trabajo**.

| Ciclo de trabajo | Interpretación aproximada |
|---|---|
| 0 % | Siempre apagado |
| 25 % | Encendido una cuarta parte del tiempo |
| 50 % | Encendido la mitad del tiempo |
| 75 % | Encendido tres cuartas partes del tiempo |
| 100 % | Siempre encendido |

Utilizaremos **D9**, marcado con capacidad PWM en el pinout oficial.

### 7.2. Conexión del LED externo

Con la placa desconectada:

1. Coloca un LED en la protoboard.
2. Conecta **D9** a una resistencia de **330 Ω**.
3. Conecta el otro extremo de la resistencia al **ánodo** del LED (pata larga, normalmente).
4. Conecta el **cátodo** del LED (pata corta y lado plano del encapsulado) a **GND**.
5. Comprueba polaridad y conexiones antes de alimentar.

**Circuito:** `D9 → resistencia 330 Ω → ánodo LED → cátodo LED → GND`.

!!! info "Diferencia con el LED RGB integrado"

    El LED externo de este montaje se enciende cuando la salida proporciona un nivel alto. No debe confundirse con los LED RGB integrados del capítulo 3, que utilizaban lógica activa a nivel bajo.

## 8. Programa 3. Regulación del brillo de un LED

### 8.1. Objetivo

Modificar progresivamente el brillo de un LED conectado a D9.

Crea una aplicación llamada `03_led_pwm`:

```cpp
#include <Arduino.h>

const int PIN_LED = 9;

void setup()
{
    pinMode(PIN_LED, OUTPUT);
    analogWriteResolution(8); // Valores entre 0 y 255
}

void loop()
{
    // Aumentar brillo
    for (int brillo = 0; brillo <= 255; brillo += 5)
    {
        analogWrite(PIN_LED, brillo);
        delay(30);
    }

    // Disminuir brillo
    for (int brillo = 255; brillo >= 0; brillo -= 5)
    {
        analogWrite(PIN_LED, brillo);
        delay(30);
    }
}
```

### 8.2. Análisis

- `analogWriteResolution(8)` selecciona una escala de 8 bits.
- `analogWrite(PIN_LED, 0)` corresponde a un ciclo de trabajo mínimo.
- `analogWrite(PIN_LED, 255)` corresponde al máximo.
- El bucle `for` recorre una serie de valores de brillo.

!!! example "Actividad 5.3. Efecto de respiración"

    Modifica los incrementos y las pausas para conseguir una transición de brillo más lenta y uniforme. Describe qué ocurre si aumentas `delay(30)` a `delay(80)`.

## 9. Programa 4. Control del brillo mediante potenciómetro

### 9.1. Objetivo

Combinar un **sensor** (potenciómetro) y un **actuador** (LED) en un mismo programa.

### 9.2. Conexiones

Mantén los dos circuitos de los apartados anteriores:

| Elemento | Conexión |
|---|---|
| Potenciómetro, extremo 1 | 3V3 |
| Potenciómetro, cursor | A0 |
| Potenciómetro, extremo 2 | GND |
| D9 | Resistencia de 330 Ω y ánodo del LED |
| Cátodo del LED | GND |

Todos los elementos deben compartir la referencia **GND**.

### 9.3. Programa completo

Crea la aplicación `04_potenciometro_led`:

```cpp
#include <Arduino.h>

const int PIN_POTENCIOMETRO = A0;
const int PIN_LED = 9;

void setup()
{
    Serial.begin(9600);
    analogReadResolution(12);
    analogWriteResolution(8);
    pinMode(PIN_LED, OUTPUT);
}

void loop()
{
    int lectura = analogRead(PIN_POTENCIOMETRO);

    // Escalar 0-4095 a 0-255
    int brillo = (lectura * 255L) / 4095;

    analogWrite(PIN_LED, brillo);

    Serial.print("ADC: ");
    Serial.print(lectura);
    Serial.print(" | PWM: ");
    Serial.println(brillo);

    delay(100);
}
```

### 9.4. Pruebas

1. Gira el potenciómetro al mínimo y observa el LED.
2. Sitúalo a media escala.
3. Gíralo al máximo.
4. Comprueba que el valor PWM aumenta con la lectura.
5. Verifica en la consola la correspondencia entre sensor y actuador.

!!! example "Actividad 5.4. Control inverso"

    Modifica el programa para que el LED tenga el brillo máximo cuando el potenciómetro esté al mínimo, y viceversa.

    Pista: calcula `255 - brillo` antes de escribir la salida PWM.

## 10. Sensores resistivos: la LDR

Una **LDR** (*Light Dependent Resistor*) es una resistencia cuyo valor cambia con la iluminación. En muchas LDR habituales, la resistencia disminuye cuando reciben más luz.

Arduino no mide directamente resistencia con `analogRead()`: mide una tensión. Por ello utilizaremos un **divisor de tensión**.

### 10.1. Divisor de tensión

Conecta:

**3V3 → LDR → punto de medida (A0) → resistencia 10 kΩ → GND**

| Elemento | Conexión |
|---|---|
| Extremo 1 de LDR | 3V3 |
| Extremo 2 de LDR | A0 y un extremo de la resistencia de 10 kΩ |
| Otro extremo de la resistencia de 10 kΩ | GND |

Con esta disposición, el valor medido en A0 **suele aumentar al iluminar la LDR** y disminuir al taparla. La sensibilidad depende de la LDR y de la resistencia fija.

La relación ideal es:

\[
V_{A0} = 3,3\;\frac{R_{fija}}{R_{LDR}+R_{fija}}
\]

!!! warning "Comprobar el montaje"

    La LDR no tiene polaridad. El punto A0 debe estar conectado a la unión entre la LDR y la resistencia fija, **nunca directamente a 5 V**. Si obtienes lecturas casi constantes, revisa que ambas resistencias formen realmente un divisor de tensión.

## 11. Programa 5. Medición de luz con una LDR

Crea la aplicación `05_ldr`:

```cpp
#include <Arduino.h>

const int PIN_LDR = A0;

void setup()
{
    Serial.begin(9600);
    analogReadResolution(12);
    Serial.println("Sensor LDR iniciado");
}

void loop()
{
    int luz = analogRead(PIN_LDR);

    Serial.print("Lectura de luz: ");
    Serial.println(luz);

    delay(300);
}
```

### 11.1. Calibración experimental

1. Coloca la LDR bajo la iluminación habitual del aula.
2. Registra la lectura.
3. Tápala con la mano sin tocar el circuito.
4. Registra la lectura.
5. Ilumínala con una linterna a una distancia prudente.
6. Registra la lectura.
7. Compara los resultados.

| Condición | Lectura ADC obtenida |
|---|---|
| LDR tapada | Por medir |
| Luz ambiente | Por medir |
| Luz intensa | Por medir |

!!! info "La LDR no mide lux directamente"

    La lectura ADC permite comparar niveles relativos de iluminación. Para obtener lux con fiabilidad haría falta calibrar el sistema o utilizar un sensor diseñado para medir iluminancia.

## 12. Programa 6. Encendido automático por oscuridad

### 12.1. Objetivo

Encender un LED cuando la iluminación sea inferior a un umbral.

Mantén la LDR conectada a A0 y añade el LED externo con resistencia de 330 Ω en D9, como en el apartado 7.

### 12.2. Determinar el umbral

Antes de ejecutar el siguiente programa, consulta las lecturas del apartado 11 y selecciona un valor intermedio entre la lectura con luz y la lectura en oscuridad.

El valor **2000** del ejemplo es únicamente un punto de partida y **debe ajustarse a cada montaje**.

### 12.3. Programa completo

Crea la aplicación `06_luz_automatica`:

```cpp
#include <Arduino.h>

const int PIN_LDR = A0;
const int PIN_LED = 9;
const int UMBRAL = 2000; // Ajustar tras medir el sensor

void setup()
{
    Serial.begin(9600);
    analogReadResolution(12);
    pinMode(PIN_LED, OUTPUT);
    digitalWrite(PIN_LED, LOW);
}

void loop()
{
    int lectura = analogRead(PIN_LDR);

    if (lectura < UMBRAL)
    {
        digitalWrite(PIN_LED, HIGH);
        Serial.print("Oscuridad - LED encendido | ADC: ");
    }
    else
    {
        digitalWrite(PIN_LED, LOW);
        Serial.print("Luz suficiente - LED apagado | ADC: ");
    }

    Serial.println(lectura);
    delay(200);
}
```

### 12.4. Análisis

La estructura `if ... else` permite tomar una decisión en función de una condición.

- Si `lectura < UMBRAL`, encendemos el LED.
- En caso contrario, lo apagamos.

Con el divisor propuesto, una menor iluminación suele producir una lectura inferior.

!!! example "Actividad 5.5. Evitar oscilaciones"

    Observa qué ocurre cuando la luz ambiental se mantiene cerca del umbral. Investiga el concepto de **histéresis** y propone dos umbrales distintos: uno para encender y otro para apagar.

## 13. Diagnóstico de problemas

| Síntoma | Posible causa | Comprobación |
|---|---|---|
| El ADC siempre muestra 0 | Cursor desconectado o entrada a GND | Revisar A0 y cableado |
| El ADC siempre muestra el máximo | Entrada conectada a 3V3 o divisor incorrecto | Revisar protoboard |
| La lectura cambia bruscamente | Conexión floja o entrada flotante | Verificar masa y conexiones |
| El LED externo no se enciende | Polaridad invertida o cableado incorrecto | Revisar ánodo, cátodo y resistencia |
| No varía el brillo | Pin sin PWM o resolución/configuración errónea | Usar D9 y revisar `analogWrite()` |
| La LDR responde al revés | Divisor conectado en orden inverso | Revisar posición de LDR y resistencia |
| El LED oscila cerca del umbral | Variación de luz y falta de histéresis | Ajustar umbrales |
| No aparecen mensajes | Consola equivocada o fallo de ejecución | Abrir la consola del sketch |

!!! tip "Método de depuración"

    Comprueba por separado el sensor y el actuador antes de combinarlos. Primero mide valores con `Serial.println()`, después prueba el LED con un programa mínimo y finalmente integra ambos elementos.

## 14. Práctica evaluable: sistema de iluminación inteligente

### 14.1. Enunciado

Desarrolla un **sistema automático de iluminación** utilizando Arduino UNO Q, una LDR y un LED externo. El sistema deberá aumentar la iluminación artificial cuando disminuya la luz ambiental.

### 14.2. Requisitos obligatorios

1. Montar una LDR y una resistencia de 10 kΩ como divisor de tensión en A0.
2. Conectar un LED a D9 mediante una resistencia de 330 Ω.
3. Configurar la lectura analógica a 12 bits.
4. Configurar la salida PWM a 8 bits.
5. Medir la iluminación relativa y mostrar la lectura ADC por consola.
6. Transformar la lectura en un valor PWM **inverso**: más oscuridad, más brillo.
7. Definir constantes para los pines utilizados.
8. Documentar y justificar el funcionamiento del circuito.

### 14.3. Orientación para el desarrollo

Con el divisor del apartado 10, la luz suele aumentar la lectura ADC. Una fórmula sencilla para invertir el brillo es:

```cpp
int brillo = 255 - (lectura * 255L) / 4095;
```

Después se puede aplicar:

```cpp
analogWrite(PIN_LED, brillo);
```

La respuesta exacta depende del sensor y de la iluminación del aula. No es necesario que la relación entre luz real y brillo sea lineal.

### 14.4. Ampliación voluntaria

Implementa alguna de las siguientes mejoras:

- **Promedio de lecturas:** calcular la media de diez medidas para reducir fluctuaciones.
- **Zona muerta:** evitar cambios de brillo cuando la variación es muy pequeña.
- **Umbrales:** apagar totalmente el LED cuando haya suficiente luz.
- **Modo manual:** incorporar un pulsador para activar o desactivar el control automático.

### 14.5. Entrega

Cada pareja entregará:

- Archivo fuente `sketch.ino`.
- Documento PDF con portada, objetivos y relación de materiales.
- Tabla de conexiones y fotografía clara del circuito.
- Explicación del programa y de la fórmula de control.
- Capturas de las lecturas serie en al menos tres condiciones de iluminación.
- Tabla de pruebas con resultados obtenidos.
- Incidencias, soluciones y conclusiones.

### 14.6. Criterios de evaluación

| Criterio | Puntuación |
|---|---:|
| Montaje correcto y seguro | 2 puntos |
| Lectura analógica de la LDR | 2 puntos |
| Regulación PWM del LED | 2 puntos |
| Relación inversa entre luz y brillo | 1,5 puntos |
| Depuración y pruebas documentadas | 1 punto |
| Claridad del código y documentación | 1,5 puntos |
| **Total** | **10 puntos** |

## 15. Resumen del capítulo

Hemos aprendido a diferenciar sensores y actuadores, leer señales analógicas con el ADC del STM32, transformar lecturas en porcentajes, utilizar PWM para regular un LED y construir un divisor de tensión con una LDR.

También hemos desarrollado dos ejemplos de control: un LED regulado por potenciómetro y un sistema que responde a la iluminación ambiental.

En el **capítulo 6** estudiaremos la comunicación entre los dos procesadores de Arduino UNO Q y cómo combinar las capacidades del microcontrolador con las aplicaciones que se ejecutan en Linux.

## Documentación de referencia

- [Arduino UNO Q: documentación oficial](https://docs.arduino.cc/hardware/uno-q/)
- [Arduino UNO Q: manual de usuario](https://docs.arduino.cc/tutorials/uno-q/user-manual/)
- [Referencia Arduino: analogRead()](https://docs.arduino.cc/language-reference/en/functions/analog-io/analogRead/)
- [Referencia Arduino: analogWrite()](https://docs.arduino.cc/language-reference/en/functions/analog-io/analogWrite/)
- [Referencia Arduino: analogReadResolution()](https://docs.arduino.cc/language-reference/en/functions/zero-due-mkr-family/analogReadResolution/)

!!! info "Fuente del pinout"

    Para verificar las conexiones de A0, D9, 3V3 y GND, utiliza el documento oficial de Arduino UNO Q **ABX00162, Full Pinout**, actualizado el 17 de febrero de 2026, incorporado como figura en el capítulo 1.
