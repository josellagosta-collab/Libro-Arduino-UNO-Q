# Capítulo 7. Introducción al entorno Linux de Arduino UNO Q

## Objetivos de aprendizaje

Al finalizar este capítulo, el alumnado será capaz de:

- Explicar qué funciones desempeña Linux dentro de la arquitectura dual de Arduino UNO Q.
- Diferenciar el entorno Linux del programa que ejecuta el microcontrolador STM32.
- Acceder de forma segura a la terminal Linux de la placa, localmente o mediante SSH.
- Identificar el usuario, el nombre del equipo, la versión del sistema y su arquitectura.
- Navegar por el sistema de archivos utilizando rutas absolutas y relativas.
- Crear, consultar, copiar, mover y eliminar archivos y directorios.
- Interpretar permisos y propietarios de archivos Linux.
- Consultar procesos, memoria, almacenamiento e interfaces de red.
- Utilizar comandos de diagnóstico sin modificar la configuración del sistema.
- Elaborar un informe técnico reproducible sobre el estado de la placa.

## 1. Introducción

En los capítulos anteriores hemos trabajado con el microcontrolador STM32 de Arduino UNO Q. Hemos programado entradas y salidas digitales, conectado sensores y actuadores y utilizado el mecanismo de comunicación entre los dos procesadores.

A partir de este capítulo comenzamos la **Parte 3. Linux y programación con Python**. Nuestro objetivo será aprender a administrar el entorno Linux que ejecuta el procesador Qualcomm de la placa.

Arduino UNO Q no funciona como un Arduino UNO tradicional. Además de su microcontrolador, dispone de un procesador capaz de ejecutar un sistema operativo Linux, aplicaciones Python, servicios de red y otras herramientas habituales en sistemas informáticos.

Esta característica resulta especialmente interesante en el ámbito de **Administración de Sistemas Informáticos en Red (ASIX)**, porque permite estudiar Linux sobre un dispositivo físico que también puede interactuar con componentes electrónicos.

!!! info "Relación con el capítulo 6"

    En el capítulo anterior, Python ejecutaba operaciones en el entorno Linux y podía comunicarse con el STM32 mediante Bridge y RPC.

    En este capítulo estudiaremos el sistema operativo en el que se ejecutan esas aplicaciones Python.

## 2. Arquitectura dual: Linux y microcontrolador

Arduino UNO Q combina dos entornos de ejecución con funciones diferentes:

| Componente | Entorno | Funciones habituales |
|---|---|---|
| Qualcomm QRB2210 | Debian GNU/Linux | Aplicaciones Python, red, archivos, procesos y servicios |
| STM32U585 | Entorno de microcontrolador con Zephyr y API Arduino | Lectura de sensores, control de GPIO y tareas de hardware |

El procesador Qualcomm puede ejecutar varios procesos y administrar recursos del sistema. El STM32 está orientado a tareas de control y a la interacción con periféricos.

### 2.1. ¿Por qué utilizar Linux en Arduino UNO Q?

Linux aporta herramientas que permiten:

- Administrar archivos y directorios.
- Ejecutar programas en distintos lenguajes.
- Establecer conexiones de red.
- Acceder a otros equipos mediante SSH.
- Consultar procesos y servicios.
- Registrar datos y eventos.
- Ejecutar aplicaciones de automatización e IoT.

### 2.2. ¿Qué tareas corresponden al STM32?

El microcontrolador resulta apropiado para leer pulsadores y sensores, controlar LED y actuadores y realizar tareas que requieren un control preciso de los periféricos.

!!! warning "No confundir los dos entornos"

    Un comando escrito en la terminal Linux se ejecuta en el procesador Qualcomm, no en el STM32.

    Del mismo modo, un sketch Arduino no se convierte automáticamente en un comando Linux.

    Para intercambiar información entre ambos entornos utilizaremos los mecanismos de comunicación estudiados en el capítulo 6.

## 3. Material y preparación del entorno

### 3.1. Material necesario

- Una placa Arduino UNO Q.
- Un ordenador con Windows 11.
- Cable USB-C adecuado para datos.
- Arduino App Lab instalado y operativo.
- Conexión a la misma red local para el ordenador y la placa, si se utilizará SSH por Wi-Fi o Ethernet.
- Terminal de Windows, PowerShell o PuTTY.

### 3.2. Comprobaciones previas

1. Alimenta la placa y espera a que el sistema termine de arrancar.
2. Abre Arduino App Lab.
3. Comprueba que la placa aparece conectada y que puedes acceder a su entorno.
4. Identifica el nombre de usuario Linux y la dirección IP de la placa.
5. Conserva esos datos para las prácticas posteriores.

!!! tip "Datos de nuestra instalación"

    En nuestras pruebas anteriores hemos trabajado con una placa cuyo nombre de usuario era `arduino` y cuyo nombre de equipo era `UNO-Q-JOSE`.

    Los ejemplos de este capítulo utilizan ese usuario como referencia, pero **cada alumno debe sustituirlo por el nombre configurado en su propia placa**.

## 4. Acceso a la terminal Linux

La terminal permite introducir comandos que el sistema operativo interpreta y ejecuta. En Linux es habitual utilizar un intérprete de comandos o *shell*, como Bash.

### 4.1. Acceso desde el entorno de la placa

Si la instalación de Arduino App Lab o el sistema de la placa ofrece una terminal Linux, podemos utilizarla directamente para realizar las primeras comprobaciones.

El aspecto habitual de una línea de comandos es:

```text
arduino@UNO-Q-JOSE:~$
```

Los elementos indican:

| Elemento | Significado |
|---|---|
| `arduino` | Usuario que ha iniciado la sesión |
| `UNO-Q-JOSE` | Nombre del equipo |
| `~` | Directorio personal del usuario |
| `$` | Sesión de usuario sin privilegios de administrador |

### 4.2. Acceso remoto mediante SSH

SSH (*Secure Shell*) permite acceder a una terminal remota a través de una conexión cifrada.

Desde PowerShell en Windows 11, el formato general es:

```powershell
ssh usuario@direccion_ip
```

Por ejemplo, **si la IP actual de la placa fuera `192.168.1.49`**:

```powershell
ssh arduino@192.168.1.49
```

La IP es un ejemplo tomado de una configuración anterior: debe verificarse antes de utilizarla.

En la primera conexión, SSH puede solicitar la confirmación de la clave de identidad del servidor. Antes de aceptarla, debemos comprobar que la dirección y la identidad corresponden a nuestra placa.

Después se solicitará la contraseña del usuario Linux, si la autenticación está configurada mediante contraseña.

!!! warning "Requisitos de SSH"

    Para que la conexión funcione, la placa debe estar accesible en la red y disponer de un servidor SSH habilitado.

    Si aparece `Connection refused`, no significa necesariamente que la IP sea incorrecta: el servicio SSH puede no estar activo.

    No debemos modificar servicios del sistema sin autorización del profesor.

### 4.3. Acceso mediante PuTTY

PuTTY es una alternativa gráfica para conectarse desde Windows.

1. Abre PuTTY.
2. Introduce la dirección IP de la placa en **Host Name**.
3. Selecciona **SSH** y el puerto **22**, salvo que se haya configurado otro.
4. Pulsa **Open**.
5. Comprueba la identidad del servidor si es la primera conexión.
6. Introduce el usuario y la contraseña.

### 4.4. Cerrar la sesión

Para finalizar una sesión SSH de forma ordenada, ejecuta:

```bash
exit
```

## 5. Programa práctico 1. Identificación del sistema Linux

### 5.1. Objetivo

Obtener información básica sobre el sistema operativo y el equipo donde se ejecuta.

### 5.2. Comandos

Ejecuta los siguientes comandos, uno a uno:

```bash
whoami
hostname
pwd
uname -a
cat /etc/os-release
```

### 5.3. Análisis

| Comando | Información obtenida |
|---|---|
| `whoami` | Usuario actual |
| `hostname` | Nombre del equipo |
| `pwd` | Directorio de trabajo actual |
| `uname -a` | Información del núcleo Linux y arquitectura |
| `cat /etc/os-release` | Identificación de la distribución Linux |

El archivo `/etc/os-release` contiene información sobre el sistema operativo. No debemos confundir la versión de Debian con la versión del núcleo Linux, que puede consultarse con `uname`.

Para consultar únicamente la arquitectura, ejecuta:

```bash
uname -m
```

Para conocer el tiempo transcurrido desde el último arranque:

```bash
uptime
```

!!! example "Actividad 7.1. Ficha de identificación"

    Elabora una tabla con los siguientes datos reales de tu placa:

    - Nombre de usuario.
    - Nombre del equipo.
    - Distribución Linux y versión.
    - Arquitectura del procesador.
    - Versión del núcleo Linux.
    - Tiempo de funcionamiento.

    Incorpora una captura de la terminal como evidencia.

## 6. Organización del sistema de archivos Linux

Linux utiliza una estructura jerárquica de directorios cuyo punto de partida es `/`, denominado **directorio raíz**.

| Directorio | Función general |
|---|---|
| `/` | Raíz del sistema de archivos |
| `/home` | Directorios personales de usuarios |
| `/etc` | Archivos de configuración del sistema |
| `/usr` | Programas, bibliotecas y recursos compartidos |
| `/var` | Datos variables, registros y otros archivos |
| `/tmp` | Archivos temporales |
| `/dev` | Representación de dispositivos |
| `/proc` | Información virtual sobre procesos y núcleo |
| `/sys` | Información e interfaces del núcleo y dispositivos |

### 6.1. Rutas absolutas y relativas

Una **ruta absoluta** comienza en `/`:

```text
/home/arduino/practicas
```

Una **ruta relativa** se interpreta desde el directorio actual:

```text
practicas/capitulo07
```

Símbolos importantes:

| Símbolo | Significado |
|---|---|
| `.` | Directorio actual |
| `..` | Directorio superior |
| `~` | Directorio personal del usuario |
| `/` | Separador de directorios |

### 6.2. Comandos de navegación

```bash
pwd
ls
ls -l
ls -la
cd ~
```

`ls -l` muestra información detallada y `ls -la` incluye también los archivos ocultos.

!!! example "Actividad 7.2. Exploración del sistema"

    1. Accede a tu directorio personal con `cd ~`.
    2. Muestra su contenido mediante `ls -la`.
    3. Accede a `/etc` y consulta sus nombres de archivo con `ls`.
    4. Regresa a tu directorio personal.
    5. Explica la diferencia entre una ruta absoluta y una relativa.

## 7. Programa práctico 2. Gestión de archivos y directorios

### 7.1. Objetivo

Crear un espacio de trabajo propio y utilizar comandos básicos de gestión de archivos.

**Todas las operaciones de escritura se realizarán dentro del directorio personal del alumno.**

### 7.2. Crear el espacio de trabajo

Ejecuta:

```bash
cd ~
mkdir -p practicas/capitulo07
cd practicas/capitulo07
pwd
```

El comando `mkdir -p` permite crear los directorios intermedios que todavía no existen.

### 7.3. Crear y consultar un archivo

```bash
printf 'Arduino UNO Q\nPractica Linux\n' > datos.txt
cat datos.txt
```

El operador `>` crea el archivo o sustituye su contenido anterior. Debemos utilizarlo con cuidado.

Para añadir una nueva línea sin borrar las anteriores:

```bash
printf 'Capitulo 7\n' >> datos.txt
cat datos.txt
```

El operador `>>` añade contenido al final.

### 7.4. Copiar, renombrar y organizar

```bash
cp datos.txt copia_datos.txt
mv copia_datos.txt respaldo.txt
mkdir documentos
mv respaldo.txt documentos/
ls -l
ls -l documentos
```

Los comandos utilizados son:

| Comando | Función |
|---|---|
| `mkdir` | Crear directorios |
| `cp` | Copiar archivos |
| `mv` | Mover o renombrar |
| `cat` | Mostrar contenido |
| `ls` | Listar archivos |

### 7.5. Consultar el contenido y eliminar un archivo de prueba

```bash
cat documentos/respaldo.txt
rm documentos/respaldo.txt
ls -l documentos
```

!!! warning "Precaución con rm"

    `rm` elimina archivos y no los envía a una papelera de reciclaje.

    No utilices `rm -r` o `rm -rf` sobre rutas del sistema. En estas prácticas solo eliminaremos archivos de prueba creados por nosotros.

### 7.6. Resultado esperado

Al finalizar, el directorio tendrá esta estructura:

```text
practicas/
└── capitulo07/
    ├── datos.txt
    └── documentos/
```

!!! example "Actividad 7.3. Gestión documental"

    Crea un directorio llamado `informes` y, dentro de él, un archivo `equipo.txt` con el nombre del equipo y la fecha de la práctica.

    Haz una copia denominada `equipo_backup.txt` y comprueba que ambos archivos contienen la misma información.

## 8. Usuarios, grupos y permisos

Linux es un sistema multiusuario. Cada archivo tiene un propietario y unos permisos que determinan qué operaciones pueden realizarse sobre él.

### 8.1. Identificación del usuario

```bash
whoami
id
```

El comando `id` muestra el identificador del usuario y los grupos a los que pertenece.

### 8.2. Interpretación de permisos

Ejecuta:

```bash
cd ~/practicas/capitulo07
ls -l datos.txt
```

Una línea de salida puede tener este aspecto:

```text
-rw-r--r-- 1 arduino arduino 38 nov 18 19:00 datos.txt
```

La cadena `-rw-r--r--` indica:

- `-`: archivo ordinario.
- `rw-`: el propietario puede leer y escribir.
- `r--`: el grupo puede leer.
- `r--`: otros usuarios pueden leer.

Las letras más habituales son `r` (lectura), `w` (escritura) y `x` (ejecución).

### 8.3. Modificar permisos de un archivo propio

Para permitir que únicamente el propietario lea y escriba un archivo:

```bash
chmod 600 datos.txt
ls -l datos.txt
```

Para recuperar permisos de lectura para el grupo y otros usuarios:

```bash
chmod 644 datos.txt
ls -l datos.txt
```

!!! warning "Privilegios de administrador"

    El comando `sudo` permite ejecutar determinadas órdenes con privilegios elevados si el usuario está autorizado.

    En este capítulo no es necesario utilizar `sudo`. Evita cambiar permisos de archivos del sistema, usuarios o servicios.

!!! example "Actividad 7.4. Seguridad de archivos"

    Explica qué diferencia existe entre los permisos `600`, `644` y `755`.

    Aplica `600` y `644` únicamente a un archivo de prueba de tu directorio personal y registra el resultado de `ls -l`.

## 9. Programa práctico 3. Diagnóstico de recursos del sistema

### 9.1. Objetivo

Consultar el estado del procesador, la memoria y el almacenamiento de la placa utilizando comandos de solo lectura.

### 9.2. Información de memoria

```bash
free -h
```

Este comando muestra memoria total, utilizada y disponible. La opción `-h` utiliza unidades fáciles de interpretar.

### 9.3. Almacenamiento disponible

```bash
df -h
```

El comando `df` muestra el espacio utilizado y disponible en los sistemas de archivos montados.

Para consultar el tamaño de nuestro directorio de prácticas:

```bash
du -sh ~/practicas
```

### 9.4. Procesos del sistema

```bash
ps -ef
```

Para consultar los procesos de forma interactiva:

```bash
top
```

Pulsa `q` para salir de `top`.

### 9.5. Tiempo de funcionamiento

```bash
uptime
```

Este comando muestra, entre otros datos, el tiempo de funcionamiento y la carga media del sistema.

!!! info "Interpretación de los resultados"

    La memoria disponible, el espacio libre y la carga del sistema cambian durante el funcionamiento normal de la placa.

    No existe un resultado numérico único para toda la clase: cada alumno debe registrar los valores obtenidos en su dispositivo.

!!! example "Actividad 7.5. Informe de recursos"

    Registra la memoria total, memoria disponible, espacio disponible en el sistema de archivos principal y tiempo de funcionamiento.

    Explica qué comandos has utilizado y qué significa cada valor.

## 10. Programa práctico 4. Diagnóstico de conectividad

### 10.1. Objetivo

Identificar las interfaces de red y comprobar la conectividad del sistema Linux.

### 10.2. Consultar direcciones IP

```bash
ip -br addr
```

Este comando muestra un resumen de las interfaces y sus direcciones.

Para consultar las rutas configuradas:

```bash
ip route
```

La ruta por defecto, si existe, indica la puerta de enlace utilizada para alcanzar redes externas.

### 10.3. Comprobar conectividad

Primero identifica la dirección de la puerta de enlace en `ip route`. Después ejecuta `ping` hacia esa dirección.

Por ejemplo, **solo si la puerta de enlace de tu red es `192.168.1.1`**:

```bash
ping -c 4 192.168.1.1
```

Para comprobar conectividad IP hacia Internet, cuando esté permitido por la red del centro:

```bash
ping -c 4 1.1.1.1
```

Para comprobar también la resolución de nombres:

```bash
getent hosts example.com
```

!!! note "No confundir conectividad con DNS"

    Si un ping a una dirección IP funciona, pero la resolución de nombres falla, es posible que exista un problema de DNS.

    Si el destino no responde a ping, tampoco podemos concluir automáticamente que no exista conectividad: algunos equipos bloquean ICMP.

### 10.4. Comprobar servicios en escucha

```bash
ss -ltn
```

Este comando permite consultar los puertos TCP en estado de escucha sin necesidad de privilegios de administrador.

En prácticas anteriores utilizamos servicios web publicados en puertos concretos. La salida de `ss` nos ayudará a comprender qué significa que un servicio esté escuchando en una dirección y un puerto.

!!! example "Actividad 7.6. Diagnóstico de red"

    Identifica la IP de tu placa, la puerta de enlace y las interfaces activas.

    Comprueba la conectividad con la puerta de enlace y registra los resultados.

    Indica si el equipo dispone de resolución DNS funcional.

## 11. Programa práctico 5. Generar un informe automático

### 11.1. Objetivo

Reunir los principales comandos aprendidos en un archivo de texto que sirva como informe de diagnóstico.

Este ejemplo utiliza un pequeño script de Bash. No sustituye el aprendizaje de Python del siguiente capítulo, sino que muestra cómo Linux permite automatizar tareas administrativas sencillas.

### 11.2. Crear el script

Accede a nuestro directorio de prácticas:

```bash
cd ~/practicas/capitulo07
```

Crea el archivo mediante el siguiente comando. Copia el bloque completo, incluida la última línea `EOF`:

```bash
cat > diagnostico.sh <<'EOF'
#!/usr/bin/env bash

set -u

SALIDA="$HOME/practicas/capitulo07/informe_linux.txt"

{
    echo "INFORME DE ARDUINO UNO Q"
    echo "========================"
    echo "Fecha: $(date)"
    echo "Usuario: $(whoami)"
    echo "Equipo: $(hostname)"
    echo
    echo "SISTEMA OPERATIVO"
    cat /etc/os-release
    echo
    echo "ARQUITECTURA"
    uname -m
    echo
    echo "TIEMPO DE FUNCIONAMIENTO"
    uptime
    echo
    echo "MEMORIA"
    free -h
    echo
    echo "ALMACENAMIENTO"
    df -h
    echo
    echo "RED"
    ip -br addr
    echo
    echo "RUTAS"
    ip route
} > "$SALIDA"

echo "Informe generado en: $SALIDA"
EOF
```

### 11.3. Ejecutar el script

No es necesario modificar los permisos de ejecución si lo iniciamos explícitamente con Bash:

```bash
bash diagnostico.sh
```

Para consultar el informe:

```bash
cat informe_linux.txt
```

Para mostrar únicamente las primeras líneas:

```bash
head -n 15 informe_linux.txt
```

### 11.4. Análisis

En este programa hemos utilizado:

| Elemento | Función |
|---|---|
| `#!/usr/bin/env bash` | Identifica el intérprete previsto |
| `SALIDA=...` | Guarda una ruta en una variable |
| `$(comando)` | Inserta la salida de un comando |
| `{ ... } > archivo` | Redirige la salida de un bloque completo |
| `echo` | Escribe texto |
| `date` | Muestra la fecha y hora |
| `head` | Muestra las primeras líneas de un archivo |

!!! tip "Privacidad del informe"

    Un informe de diagnóstico puede contener nombres de equipo, usuarios, direcciones IP y otros datos de la red.

    Antes de publicarlo en GitHub o compartirlo fuera del aula, revisa y oculta la información que no deba hacerse pública.

!!! example "Actividad 7.7. Ampliación del script"

    Modifica el script para incorporar:

    1. La versión del núcleo Linux mediante `uname -r`.
    2. El espacio ocupado por el directorio de prácticas.
    3. Un encabezado con el nombre del alumno.
    4. Una línea final que indique que el informe ha terminado.

    Ejecuta el script y comprueba el archivo resultante.

## 12. Errores habituales y resolución de problemas

| Síntoma | Posible causa | Comprobación recomendada |
|---|---|---|
| SSH no conecta | IP incorrecta o placa desconectada | Comprobar IP y conexión de red |
| `Connection refused` | Servicio SSH no disponible | Verificar que SSH está habilitado |
| `Permission denied` | Credenciales o permisos incorrectos | Revisar usuario y autenticación |
| `command not found` | Comando mal escrito o no instalado | Revisar sintaxis y disponibilidad |
| `No such file or directory` | Ruta inexistente | Utilizar `pwd` y `ls` |
| `Permission denied` al escribir | Directorio protegido | Trabajar dentro de `~/practicas` |
| Un archivo queda vacío | Redirección `>` accidental | Revisar antes de sobrescribir |
| No responde `ping` | Filtro ICMP o problema de red | Comprobar rutas y otros servicios |
| Un comando tarda demasiado | Proceso interactivo o bloqueo | Utilizar `Ctrl+C` si procede |

### 12.1. Buenas prácticas de administración

- Ejecutar primero comandos de consulta antes de modificar configuraciones.
- Trabajar en el directorio personal del usuario.
- Documentar los cambios y resultados.
- Evitar ejecutar comandos desconocidos copiados de Internet.
- No compartir contraseñas ni claves privadas.
- No instalar paquetes o cambiar servicios sin autorización.
- Mantener separadas las tareas del procesador Linux y las del STM32.

## 13. Práctica evaluable. Auditoría básica del entorno Linux

### 13.1. Enunciado

Una empresa desea utilizar Arduino UNO Q como nodo de supervisión en una red local. Antes de instalar las aplicaciones, el departamento de sistemas necesita un informe que identifique el dispositivo y compruebe sus recursos y conectividad.

El alumnado actuará como técnico de sistemas y realizará una **auditoría básica no invasiva** de la placa.

### 13.2. Requisitos obligatorios

El trabajo deberá incluir:

1. Acceso correcto a la terminal Linux, preferentemente mediante SSH.
2. Identificación del usuario, nombre de equipo, distribución y arquitectura.
3. Creación de un directorio de trabajo dentro del directorio personal.
4. Creación, copia, renombrado y consulta de archivos.
5. Interpretación de los permisos de un archivo.
6. Consulta de memoria, almacenamiento y procesos.
7. Identificación de la dirección IP y de la puerta de enlace.
8. Prueba documentada de conectividad.
9. Ejecución de un script que genere un informe de diagnóstico.
10. Explicación de los resultados obtenidos.

### 13.3. Desarrollo recomendado

**Paso 1.** Accede a la placa y verifica la identidad del sistema.

**Paso 2.** Crea la carpeta `~/practicas/capitulo07`.

**Paso 3.** Realiza las operaciones de gestión de archivos solicitadas.

**Paso 4.** Consulta los permisos de un archivo y explica su significado.

**Paso 5.** Registra memoria, almacenamiento y tiempo de funcionamiento.

**Paso 6.** Identifica la configuración IP y comprueba la conectividad.

**Paso 7.** Ejecuta el script de diagnóstico y revisa su salida.

**Paso 8.** Prepara la documentación y las evidencias.

### 13.4. Ampliación voluntaria

Incorpora al script una comprobación que indique si existe una ruta por defecto y un apartado que liste los puertos TCP en escucha.

No es necesario abrir puertos ni modificar servicios.

### 13.5. Entrega

Cada alumno entregará:

- Un documento PDF con portada, objetivos, procedimiento, comandos y resultados.
- Capturas de terminal que acrediten las operaciones realizadas.
- El archivo `diagnostico.sh`.
- El archivo `informe_linux.txt`, revisado para evitar divulgar datos sensibles.
- Un apartado final de incidencias y conclusiones.

### 13.6. Rúbrica de evaluación

| Criterio | Puntuación |
|---|---:|
| Acceso a Linux e identificación del sistema | 1,5 puntos |
| Navegación y gestión de archivos | 2 puntos |
| Interpretación de usuarios y permisos | 1 punto |
| Diagnóstico de recursos | 1,5 puntos |
| Diagnóstico de red | 1,5 puntos |
| Script de informe y comprobación | 1,5 puntos |
| Calidad de la documentación | 1 punto |
| **Total** | **10 puntos** |

## 14. Resumen del capítulo

En este capítulo hemos comenzado a administrar el entorno Linux de Arduino UNO Q. Hemos aprendido a acceder a la terminal, identificar el sistema operativo, navegar por directorios y gestionar archivos.

También hemos interpretado permisos, consultado procesos y recursos, diagnosticado la conectividad de red y generado un informe automático mediante Bash.

Estas herramientas constituyen la base para desarrollar aplicaciones y servicios sobre el procesador Qualcomm. En el siguiente capítulo, **Programación con Python**, utilizaremos este entorno para escribir programas que interactúen con archivos, procesos y otros recursos de la placa.

## Documentación de referencia

- [Arduino UNO Q — Documentación oficial](https://docs.arduino.cc/hardware/uno-q/)
- [Arduino UNO Q — Manual de usuario](https://docs.arduino.cc/tutorials/uno-q/user-manual/)
- [Arduino App Lab — Documentación oficial](https://docs.arduino.cc/software/app-lab/)
- [Debian — Documentación](https://www.debian.org/doc/)
- [GNU Bash — Manual de referencia](https://www.gnu.org/software/bash/manual/)
- [OpenSSH — Manuales](https://www.openssh.com/manual.html)
