
# Capítulo 2. Preparación del entorno de desarrollo

## Objetivos de aprendizaje

Al finalizar este capítulo, el alumnado será capaz de:

- Identificar las herramientas de desarrollo compatibles con Arduino UNO Q.
- Instalar Arduino App Lab en Windows 11.
- Conectar Arduino UNO Q al ordenador mediante USB-C.
- Realizar la configuración inicial de la placa.
- Comprender la estructura de una aplicación de Arduino App Lab.
- Ejecutar un ejemplo para verificar el funcionamiento.
- Identificar los entornos Linux y STM32.
- Reconocer las posibilidades de VS Code y Arduino IDE.
- Resolver los problemas más habituales de conexión.

## 1. Introducción al entorno de desarrollo

Arduino UNO Q combina dos sistemas de procesamiento:

- Un microprocesador Qualcomm que ejecuta Debian Linux.
- Un microcontrolador STM32 que ejecuta programas Arduino sobre Zephyr.

Por este motivo, el desarrollo de aplicaciones requiere herramientas capaces de trabajar con ambos sistemas.

En este capítulo aprenderemos a preparar el entorno de desarrollo utilizando un ordenador con Windows 11.

El objetivo será disponer de un sistema preparado para crear, ejecutar y depurar aplicaciones.

### 1.1. Herramientas de desarrollo

Podemos utilizar diferentes herramientas para programar Arduino UNO Q.

| Herramienta | Función principal |
|---|---|
| Arduino App Lab | Desarrollo de aplicaciones para Linux y STM32 |
| Arduino IDE | Programación del microcontrolador STM32 |
| Visual Studio Code | Edición de código, Python y desarrollo avanzado |
| PowerShell | Ejecución de comandos desde Windows |
| SSH | Administración remota del sistema Linux |
| Python | Desarrollo de aplicaciones y automatización |

La herramienta principal que utilizaremos será **Arduino App Lab**.

Más adelante incorporaremos VS Code, Python y herramientas de administración de Linux.

!!! info "Arduino App Lab"

    Arduino App Lab es un entorno de desarrollo que permite integrar programas Arduino, aplicaciones Python y servicios Linux dentro de un mismo proyecto.

    Facilita la comunicación entre los dos procesadores de Arduino UNO Q.

## 2. Instalación de Arduino App Lab

### 2.1. Requisitos previos

Antes de comenzar, necesitaremos:

- Un ordenador con Windows 11.
- Una placa Arduino UNO Q.
- Un cable USB-C compatible con transferencia de datos.
- Conexión a Internet.
- Permisos para instalar aplicaciones en Windows.

!!! warning "Importante: cable USB-C"

    Algunos cables USB-C permiten únicamente la carga eléctrica.

    Para configurar Arduino UNO Q desde el ordenador necesitaremos un cable que también permita transferir datos.

    Si la placa recibe alimentación pero no aparece en Arduino App Lab, debemos comprobar el cable.

### 2.2. Descargar Arduino App Lab

**Paso 1.** Abre el navegador web.

**Paso 2.** Accede a la página oficial de Arduino:

https://www.arduino.cc/en/software/

**Paso 3.** Localiza el apartado correspondiente a **Arduino App Lab**.

**Paso 4.** Selecciona la versión compatible con Windows.

**Paso 5.** Descarga el instalador.

!!! tip "Software oficial"

    Descarga Arduino App Lab desde la página oficial de Arduino.

    Evita utilizar instaladores obtenidos de páginas de terceros.

### 2.3. Instalar Arduino App Lab

**Paso 1.** Localiza el archivo descargado.

**Paso 2.** Ejecuta el instalador.

**Paso 3.** Acepta las condiciones y permisos que solicite el instalador, después de revisarlos.

**Paso 4.** Sigue las instrucciones del asistente.

**Paso 5.** Finaliza la instalación.

**Paso 6.** Abre Arduino App Lab desde el menú Inicio de Windows.

Si el sistema solicita permisos de administrador y el usuario no dispone de ellos, será necesario contactar con el responsable informático del centro.

### 2.4. Primera ejecución

Al iniciar Arduino App Lab, aparecerá su interfaz principal.

La aplicación permite:

- Detectar placas compatibles.
- Acceder a ejemplos.
- Crear aplicaciones.
- Editar programas.
- Ejecutar proyectos.
- Consultar mensajes y registros.

En este momento todavía no es necesario escribir ningún programa.

Primero comprobaremos la comunicación con la placa.

## 3. Conexión de Arduino UNO Q al ordenador

### 3.1. Conexión física

**Paso 1.** Coloca Arduino UNO Q sobre una superficie limpia, estable y no conductora.

**Paso 2.** Comprueba que no existen cables o componentes conectados incorrectamente.

**Paso 3.** Conecta un extremo del cable USB-C al conector de Arduino UNO Q.

**Paso 4.** Conecta el otro extremo al ordenador.

**Paso 5.** Espera mientras la placa inicia su sistema.

Arduino UNO Q necesita arrancar el sistema Linux, por lo que la detección inicial puede tardar más que en un Arduino tradicional.

!!! warning "Alimentación"

    Utiliza una conexión y una fuente de alimentación que cumplan los requisitos eléctricos oficiales de Arduino UNO Q.

    Evita conectar simultáneamente fuentes de alimentación externas sin haber comprobado previamente su compatibilidad.

### 3.2. Detección desde Arduino App Lab

**Paso 1.** Abre Arduino App Lab.

**Paso 2.** Accede al apartado de selección o conexión de dispositivos.

**Paso 3.** Espera a que aparezca Arduino UNO Q.

**Paso 4.** Selecciona la placa detectada.

**Paso 5.** Sigue las indicaciones de configuración que aparezcan.

Durante la primera configuración, el sistema puede solicitar actualizaciones de software.

Si existen actualizaciones oficiales disponibles, seguiremos el procedimiento indicado por Arduino App Lab.

!!! tip "Si no aparece la placa"

    Comprueba que el cable USB-C permite transferir datos.

    Prueba otro puerto USB del ordenador.

    Espera a que finalice el arranque de Linux.

    Reinicia Arduino App Lab y vuelve a conectar la placa si fuera necesario.

## 4. Configuración inicial de Arduino UNO Q

Durante el primer uso, Arduino App Lab puede solicitar información para configurar el sistema Linux.

Entre los datos habituales se encuentran:

- Nombre del dispositivo.
- Contraseña del sistema.
- Configuración de red Wi-Fi.

### 4.1. Nombre del dispositivo

En un entorno docente es recomendable utilizar nombres que permitan identificar cada placa.

Por ejemplo:

| Grupo | Nombre propuesto |
|---|---|
| Grupo 1 | unoq-asix-01 |
| Grupo 2 | unoq-asix-02 |
| Grupo 3 | unoq-asix-03 |
| Grupo 4 | unoq-asix-04 |

El nombre debe ser único dentro de la red cuando se utilice para identificar el equipo.

### 4.2. Contraseña del sistema

La contraseña permite proteger el acceso al sistema Linux.

Debe cumplir los requisitos de seguridad indicados durante la configuración.

!!! warning "Seguridad"

    No utilices contraseñas compartidas públicamente.

    No incluyas contraseñas en capturas de pantalla ni en los documentos de entrega.

    Conserva las credenciales siguiendo las indicaciones del profesor y las normas del centro.

### 4.3. Configuración de Wi-Fi

Si el asistente solicita una red inalámbrica, seleccionaremos una red autorizada para los dispositivos del taller.

Será necesario conocer:

- Nombre de la red (SSID).
- Contraseña.
- Requisitos de autenticación.
- Posibles restricciones de acceso.

!!! info "Redes del centro educativo"

    Algunas redes educativas utilizan autenticación empresarial, aislamiento de clientes o restricciones de acceso.

    Estas configuraciones pueden impedir que Arduino App Lab descubra automáticamente la placa mediante la red.

    Durante la primera instalación utilizaremos preferentemente USB-C.

## 5. Conocer Arduino App Lab

Arduino App Lab organiza el desarrollo mediante aplicaciones o *Apps*.

Una App puede incluir diferentes componentes.

### 5.1. Componentes de una aplicación

| Componente | Función | Sistema de ejecución |
|---|---|---|
| Arduino Sketch | Control electrónico | STM32 |
| Python | Lógica de aplicación | Debian Linux |
| Bricks | Servicios y funcionalidades adicionales | Debian Linux |
| Bridge | Comunicación entre procesadores | Linux y STM32 |

No todas las aplicaciones necesitan utilizar todos estos componentes.

Por ejemplo, una aplicación sencilla puede contener únicamente un programa Arduino.

Una aplicación más avanzada puede combinar Arduino, Python y servicios de red.

### 5.2. Arduino Sketch

Un *sketch* es un programa desarrollado utilizando el entorno de programación Arduino.

Normalmente incluye dos funciones principales:

- `setup()`: se ejecuta durante la inicialización.
- `loop()`: se ejecuta repetidamente.

Ejemplo de estructura:

```cpp
void setup()
{
    // Inicialización
}

void loop()
{
    // Código que se repite
}
```

En Arduino UNO Q, estos programas se ejecutan en el microcontrolador STM32.

### 5.3. Python

Python permite desarrollar aplicaciones de alto nivel sobre Debian Linux.

Por ejemplo:

```python
print("Hola desde Arduino UNO Q")
```

Más adelante utilizaremos Python para:

- Procesar datos.
- Crear servidores web.
- Realizar peticiones HTTP.
- Gestionar archivos.
- Automatizar tareas.
- Comunicarnos con servicios de red.

### 5.4. Bricks

Los Bricks son componentes preparados para incorporar determinadas funcionalidades a una aplicación.

Dependiendo de la versión de Arduino App Lab y de los componentes disponibles, pueden facilitar la integración de servicios y modelos de inteligencia artificial.

No será necesario utilizarlos durante nuestra primera prueba.

## 6. Primera prueba de funcionamiento

Para comprobar el entorno ejecutaremos un ejemplo oficial incluido en Arduino App Lab.

Utilizaremos el ejemplo **Blink**.

Este programa enciende y apaga periódicamente un LED integrado en la placa.

### 6.1. Abrir el ejemplo

**Paso 1.** Comprueba que Arduino UNO Q aparece conectada en Arduino App Lab.

**Paso 2.** Accede al apartado **Examples**.

**Paso 3.** Busca el ejemplo **Blink**.

**Paso 4.** Abre el ejemplo.

**Paso 5.** Examina su descripción y los archivos que lo componen.

### 6.2. Ejecutar el ejemplo

**Paso 1.** Pulsa el botón **Run**.

**Paso 2.** Espera mientras Arduino App Lab prepara y ejecuta la aplicación.

**Paso 3.** Observa los LED de la placa.

**Paso 4.** Comprueba que el LED rojo integrado parpadea periódicamente.

**Paso 5.** Consulta los mensajes de ejecución que aparecen en Arduino App Lab.

!!! success "Resultado esperado"

    El LED rojo integrado se enciende durante aproximadamente un segundo y se apaga durante otro segundo.

    Este comportamiento se repite continuamente.

    La ejecución correcta confirma que Arduino App Lab puede comunicarse con la placa y ejecutar el programa en el STM32.

### 6.3. ¿Qué hemos comprobado?

Con esta prueba hemos verificado:

1. Que Arduino UNO Q recibe alimentación.
2. Que el ordenador puede comunicarse con la placa.
3. Que Arduino App Lab detecta el dispositivo.
4. Que el entorno puede preparar y ejecutar una aplicación.
5. Que el microcontrolador STM32 responde correctamente.

En el capítulo siguiente analizaremos el código y aprenderemos a modificarlo.

## 7. Herramientas complementarias

Aunque Arduino App Lab será nuestro entorno principal, utilizaremos otras herramientas durante el curso.

### 7.1. Visual Studio Code

Visual Studio Code es un editor de código que permite trabajar con numerosos lenguajes de programación.

Lo utilizaremos especialmente para:

- Programación Python.
- Edición de archivos de configuración.
- Desarrollo de aplicaciones web.
- Gestión de proyectos.
- Control de versiones con Git.
- Administración remota mediante SSH.

Página oficial:

https://code.visualstudio.com/

!!! info "VS Code y Arduino UNO Q"

    VS Code no sustituye automáticamente a Arduino App Lab.

    Para programar el STM32 desde herramientas externas es necesario utilizar un flujo de compilación y carga compatible con Arduino UNO Q.

    En nuestro curso comenzaremos utilizando Arduino App Lab y posteriormente estudiaremos herramientas avanzadas.

### 7.2. Arduino IDE

Arduino IDE también permite programar el microcontrolador STM32 de Arduino UNO Q.

Para ello se necesita instalar el núcleo específico de la placa.

Sin embargo, Arduino IDE no proporciona por sí solo el entorno completo para desarrollar las aplicaciones Linux de Arduino UNO Q.

Por esta razón utilizaremos Arduino App Lab como herramienta principal.

### 7.3. PowerShell

PowerShell es una consola de comandos incluida en Windows.

Nos permitirá ejecutar comandos relacionados con:

- Redes.
- Conectividad.
- Archivos.
- Procesos.
- SSH.
- Herramientas de desarrollo.

Ejemplo:

```powershell
ping 127.0.0.1
```

Este comando permite comprobar el funcionamiento básico de la pila TCP/IP local de Windows.

### 7.4. SSH

SSH significa *Secure Shell*.

Es un protocolo que permite acceder de forma segura a la consola de otro equipo.

Más adelante utilizaremos SSH para administrar Debian Linux en Arduino UNO Q.

La conexión tendrá una estructura similar a:

```powershell
ssh usuario@direccion_ip
```

Sustituiremos `usuario` y `direccion_ip` por los valores correspondientes a nuestra placa.

Para utilizar SSH necesitaremos que el servicio esté habilitado y que exista conectividad entre el ordenador y Arduino UNO Q.

## 8. Resolución de problemas habituales

Durante la instalación pueden aparecer diferentes incidencias.

| Problema | Posible causa | Solución |
|---|---|---|
| La placa no aparece | Cable USB sin datos | Utilizar otro cable |
| La placa no aparece | Puerto USB incorrecto o defectuoso | Probar otro puerto |
| La conexión tarda | Arranque de Linux | Esperar a que finalice |
| App Lab no se instala | Permisos insuficientes | Solicitar ayuda al administrador |
| No aparece por Wi-Fi | Red aislada o firewall | Comprobar red y mDNS |
| No se ejecuta Blink | Problema de comunicación o configuración | Revisar mensajes de App Lab |
| Fallan las actualizaciones | Conectividad insuficiente | Comprobar acceso a Internet |

!!! warning "Actualización del sistema"

    No desconectes la alimentación durante una actualización del firmware o del sistema operativo.

    Una interrupción puede impedir el arranque correcto de la placa.

### 8.1. Diagnóstico desde Windows

Si Arduino UNO Q no aparece, podemos comprobar si Windows detecta algún dispositivo USB nuevo.

**Paso 1.** Pulsa `Windows + X`.

**Paso 2.** Abre el **Administrador de dispositivos**.

**Paso 3.** Observa los dispositivos disponibles.

**Paso 4.** Conecta y desconecta Arduino UNO Q para identificar posibles cambios.

**Paso 5.** Comprueba si Windows muestra algún dispositivo con problemas de controlador.

!!! info "Puertos COM"

    Arduino UNO Q no debe tratarse necesariamente como una placa Arduino clásica que siempre aparece como un puerto COM.

    La conexión utilizada por Arduino App Lab puede emplear otros mecanismos de comunicación USB.

    La ausencia de un puerto COM no demuestra por sí sola que exista una avería.

## 9. Práctica: preparación del puesto de desarrollo

### Objetivo

Instalar y configurar el entorno necesario para trabajar con Arduino UNO Q y verificar su funcionamiento mediante un ejemplo oficial.

### Material necesario

- Ordenador con Windows 11.
- Arduino UNO Q.
- Cable USB-C de datos.
- Acceso a Internet.
- Arduino App Lab.

### Desarrollo

**Actividad 1. Instalación**

1. Accede a la web oficial de Arduino.
2. Descarga Arduino App Lab.
3. Instala la aplicación.
4. Comprueba que se inicia correctamente.
5. Realiza una captura de la ventana principal.

**Actividad 2. Conexión**

1. Conecta Arduino UNO Q mediante USB-C.
2. Espera a que finalice el arranque.
3. Comprueba que Arduino App Lab detecta la placa.
4. Completa la configuración inicial.
5. Anota el nombre asignado al dispositivo.

**Actividad 3. Primera ejecución**

1. Abre el ejemplo Blink.
2. Examina su contenido.
3. Ejecuta la aplicación.
4. Comprueba el parpadeo del LED.
5. Realiza una captura de los mensajes de ejecución.

**Actividad 4. Identificación de herramientas**

Completa la tabla:

| Herramienta | Instalación o disponibilidad | Función |
|---|---|---|
| Arduino App Lab | | |
| VS Code | | |
| PowerShell | | |
| Arduino IDE | | |
| SSH | | |

**Actividad 5. Cuestiones**

Responde:

1. ¿Por qué Arduino UNO Q necesita un entorno diferente al de Arduino UNO R3?
2. ¿Qué procesador ejecuta los programas Arduino?
3. ¿Qué procesador ejecuta Python?
4. ¿Qué función tiene Arduino App Lab?
5. ¿Qué es un Brick?
6. ¿Para qué sirve Bridge?
7. ¿Qué utilidad tiene SSH?
8. ¿Por qué puede no aparecer Arduino UNO Q como puerto COM?
9. ¿Qué precaución debemos tomar durante una actualización?
10. ¿Qué hemos comprobado al ejecutar Blink?

### Entrega

El alumnado entregará un documento PDF que incluya:

- Portada.
- Captura de Arduino App Lab.
- Nombre asignado a la placa.
- Captura de la ejecución del ejemplo.
- Tabla de herramientas completada.
- Respuestas a las cuestiones.
- Conclusiones.

## 10. Resumen del capítulo

Arduino UNO Q dispone de una arquitectura dual que combina Linux y un microcontrolador STM32.

Arduino App Lab es el entorno principal para desarrollar aplicaciones que integran ambos sistemas.

Durante este capítulo hemos preparado el ordenador, conectado la placa, realizado su configuración inicial y ejecutado el ejemplo Blink.

También hemos identificado otras herramientas que utilizaremos durante el curso, como VS Code, PowerShell y SSH.

En el próximo capítulo comenzaremos a desarrollar nuestros primeros programas y aprenderemos a modificar el comportamiento de Arduino UNO Q.

## Documentación de referencia

- [Arduino UNO Q - Manual oficial](https://docs.arduino.cc/tutorials/uno-q/user-manual/)
- [Arduino UNO Q - Documentación de hardware](https://docs.arduino.cc/hardware/uno-q/)
- [Arduino App Lab - Ejemplos](https://docs.arduino.cc/software/app-lab/tutorials/examples/)
- [Arduino - Descargas de software](https://www.arduino.cc/en/software/)
- [Visual Studio Code](https://code.visualstudio.com/)
