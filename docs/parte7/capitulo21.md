# Capítulo 21. Creación, verificación y restauración de imágenes de equipos

!!! info "Parte VII — Actividades complementarias imprescindibles · RA3 · 8 horas"
    Esta práctica amplía el libro Arduino UNO Q con una competencia propia del mantenimiento de equipos informáticos: **crear una imagen, verificarla y restaurarla**. El trabajo se realiza en un **PC de laboratorio**, no en el Arduino UNO Q, y exclusivamente con equipos y discos autorizados por el profesorado.

## 21.1. Objetivos y resultados esperados

Al finalizar, el alumnado podrá identificar el origen y destino de una imagen, distinguir copia de archivos de imagen de disco, preparar un medio de recuperación, crear una imagen, comprobar su integridad, restaurarla en un equipo de pruebas y documentar la recuperación.

**Duración total: 8 horas**, organizadas en cuatro sesiones de dos horas.

| Sesión | Duración | Trabajo | Evidencia |
|---|---:|---|---|
| 1 | 2 h | Inventario, seguridad y medio de arranque | Ficha de equipo y fotografía del medio |
| 2 | 2 h | Captura de imagen | Registro de origen, destino y nombre de imagen |
| 3 | 2 h | Verificación de integridad y plan de recuperación | Resultado de verificación y lista de comprobación |
| 4 | 2 h | Restauración controlada y prueba de arranque | Acta de restauración y capturas de pruebas |

## 21.2. Fundamentos técnicos

Una **imagen de disco** conserva información necesaria para reconstruir una instalación: particiones, sistemas de archivos y, según la herramienta y el modo empleado, metadatos de arranque. No equivale a copiar una carpeta de documentos. Una **copia de seguridad** protege información; una **imagen de recuperación** permite recuperar un estado del equipo con mayor rapidez, aunque no sustituye por sí sola a una estrategia completa de copias.

Conceptos que deben dominarse:

- **Origen:** disco del equipo cuya instalación se captura.
- **Destino de almacenamiento:** unidad externa o recurso de red donde se guarda la imagen.
- **Disco de restauración:** disco que recibirá la imagen y cuyo contenido anterior puede desaparecer.
- **UEFI y GPT:** firmware y tabla de particiones habituales en equipos actuales.
- **Integridad:** comprobación de que la imagen puede leerse y no presenta errores detectables.
- **Recuperación:** reconstrucción del sistema seguida de pruebas funcionales documentadas.

!!! danger "Riesgo de pérdida irreversible de datos"
    Restaurar una imagen **sobrescribe información del disco de destino**. Está prohibido utilizar ordenadores de producción, discos con datos personales o dispositivos no autorizados. Antes de confirmar la restauración, el docente debe comprobar físicamente el identificador, capacidad y número de serie del disco de destino. No se ejecutarán comandos destructivos de clonación directa en esta práctica.

## 21.3. Material necesario

- Un PC de laboratorio con instalación de prueba y permiso expreso para modificarlo.
- Un segundo disco de pruebas compatible, o un entorno virtual con discos virtuales diferenciados.
- Una unidad externa con espacio suficiente para la imagen.
- Un USB de arranque con **Clonezilla Live** preparado por el centro.
- Una hoja de inventario, un registro de incidencias y acceso a la documentación oficial.

!!! tip "Alternativa sin equipos físicos"
    Puede realizarse íntegramente con dos discos virtuales y una máquina virtual autorizada. Esta modalidad es especialmente recomendable para practicar restauraciones sin riesgo sobre el inventario del centro.

## 21.4. Sesión 1: inventario y preparación (2 h)

1. Identifica el equipo de laboratorio, su etiqueta de inventario y la autorización para intervenir.
2. Registra fabricante, modelo, memoria, disco, capacidad, esquema de particiones y tipo de arranque.
3. Diferencia claramente el **disco origen**, el **almacenamiento de la imagen** y el **disco destino de restauración**.
4. Comprueba que la unidad de almacenamiento dispone de espacio suficiente.
5. Arranca el equipo con el USB de recuperación autorizado y verifica que reconoce los discos.
6. **No inicies todavía ninguna operación de escritura.** Solicita al docente que valide la identificación de unidades.

### Plantilla de inventario

| Campo | Valor observado |
|---|---|
| Equipo e identificador de inventario | |
| Fecha y responsable | |
| Disco origen: modelo, serie y capacidad | |
| Esquema de particiones / arranque | |
| Almacenamiento de imagen: modelo y capacidad | |
| Disco destino de pruebas: modelo y serie | |
| Autorización docente | |

## 21.5. Sesión 2: creación de imagen (2 h)

En Clonezilla Live, la terminología puede variar según la versión. Consulta las pantallas que realmente aparezcan y documenta las opciones elegidas.

1. Selecciona el idioma y el teclado apropiados.
2. Inicia Clonezilla y escoge el modo **device-image** para guardar una imagen en un dispositivo de almacenamiento.
3. Selecciona **local_dev** si la imagen se guardará en una unidad externa; también puede utilizarse un destino de red previamente preparado por el docente.
4. Identifica el dispositivo donde **se almacenará la imagen**. Comprueba su capacidad y contenido antes de montarlo.
5. Selecciona el directorio de almacenamiento y el modo de guardar el disco completo (**savedisk**), cuando sea el modo previsto por el docente.
6. Selecciona el disco **origen** de la instalación de prueba. Verifica de nuevo su modelo y capacidad.
7. Asigna un nombre descriptivo, por ejemplo `aula_pc07_2026-11-20`, adaptado a la fecha real.
8. Revisa la pantalla de resumen con el docente y solo entonces confirma la captura.
9. Espera a que termine y registra mensajes, duración y ubicación de la imagen.

!!! warning "No confundir operaciones"
    `savedisk` crea una imagen del disco; `restoredisk` restaura una imagen sobre un disco. Seleccionar la segunda opción por error puede destruir información. Si hay cualquier duda sobre la pantalla o los identificadores, cancela el procedimiento.

## 21.6. Sesión 3: verificación y plan de recuperación (2 h)

Una imagen creada no se considera válida hasta comprobarla.

1. Utiliza la función de **comprobación/verificación de imagen** de Clonezilla disponible en la versión instalada.
2. Registra el nombre de la imagen, la ubicación y el resultado literal de la comprobación.
3. Comprueba que el almacenamiento externo puede desconectarse y volver a montarse correctamente.
4. Prepara un plan de recuperación: equipo autorizado, disco destino, responsable, fecha y pruebas posteriores.
5. Define criterios de aceptación: arranque correcto, acceso al sistema, particiones esperadas y funcionamiento de red y periféricos básicos.

### Integridad mediante SHA-256 (complementaria)

En un sistema Linux puede calcularse el resumen de un **archivo concreto**:

```bash
sha256sum archivo_de_prueba.img
```

La comparación solo es útil si se dispone de un valor de referencia fiable obtenido previamente. En una imagen Clonezilla compuesta por varios archivos, **un hash de un solo archivo no verifica la imagen completa**; utiliza la comprobación integrada de Clonezilla para la validación del conjunto.

## 21.7. Sesión 4: restauración y pruebas (2 h)

!!! danger "Punto de control obligatorio"
    El docente debe aprobar por escrito el disco destino antes de restaurar. La restauración se realiza **únicamente en un disco o máquina virtual de pruebas**, nunca en el disco de trabajo del alumnado.

1. Confirma que la imagen ha superado la verificación.
2. Arranca el entorno de recuperación y localiza el almacenamiento de la imagen.
3. Escoge el procedimiento de restauración del disco (**restoredisk**) siguiendo las pantallas de Clonezilla.
4. Selecciona la imagen correcta.
5. Identifica el disco destino mediante modelo, serie y capacidad. Solicita validación docente.
6. Lee las advertencias y confirma solo cuando el destino sea inequívoco.
7. Espera a que termine, apaga de forma segura y retira el medio de arranque.
8. Inicia el equipo restaurado y ejecuta las pruebas previstas.

### Plan de pruebas posterior

| ID | Prueba | Criterio de aceptación | Resultado | Evidencia |
|---|---|---|---|---|
| P01 | Arranque | El sistema inicia sin errores críticos | | |
| P02 | Particiones | Estructura coherente con la imagen | | |
| P03 | Usuario de pruebas | Inicio de sesión correcto | | |
| P04 | Red | Conectividad local comprobada | | |
| P05 | Aplicaciones | Programa de prueba operativo | | |
| P06 | Recuperación | Incidencias y tiempo documentados | | |

## 21.8. Actividades guiadas

1. Dibuja el flujo **equipo origen → imagen → verificación → equipo restaurado** e identifica los puntos de riesgo.
2. Completa la ficha de inventario y señala qué datos evitan confundir discos.
3. Captura la imagen y documenta los parámetros realmente utilizados.
4. Verifica la imagen y explica la diferencia entre integridad y funcionamiento del sistema restaurado.
5. Restaura en el destino autorizado y ejecuta las seis pruebas del plan.

## 21.9. Práctica integradora evaluable

**Enunciado:** documenta la recuperación completa de un PC de laboratorio desde una imagen verificada. La entrega será individual, aunque las operaciones físicas puedan realizarse por parejas y bajo supervisión.

| Criterio | Puntos |
|---|---:|
| Inventario y distinción inequívoca de discos | 2 |
| Creación de la imagen y registro del proceso | 2 |
| Verificación y explicación de resultados | 2 |
| Restauración autorizada y segura | 2 |
| Pruebas funcionales y memoria con evidencias | 2 |
| **Total** | **10** |

**Entrega:** inventario, capturas pertinentes sin datos personales, resultado de verificación, autorización del destino, tabla de pruebas y conclusión sobre la recuperabilidad.

## 21.10. Incidencias frecuentes

- **No aparece el disco externo:** comprueba conexión, alimentación y compatibilidad del puerto; no selecciones otro disco por aproximación.
- **No hay espacio suficiente:** detén el proceso y solicita otro almacenamiento.
- **La imagen no supera la verificación:** no la utilices para restaurar; revisa el registro y repite la captura si procede.
- **El equipo restaurado no arranca:** documenta el error y revisa compatibilidad UEFI/BIOS, particiones y orden de arranque sin modificar discos ajenos.
- **El destino es más pequeño que el origen:** no fuerces la restauración; consulta las limitaciones de la herramienta y utiliza un disco de pruebas adecuado.

## 21.11. Autoevaluación y cierre

1. ¿Qué diferencia existe entre una copia de archivos y una imagen de disco?
2. ¿Por qué debe verificarse una imagen antes de restaurarla?
3. ¿Qué información permite identificar un disco sin ambigüedad?
4. ¿Qué demuestra una restauración que arranca correctamente? ¿Qué no demuestra?
5. ¿Por qué las evidencias deben excluir información personal?

!!! success "RA3 — Evidencia final"
    La actividad se considera completada cuando existe una **imagen verificada**, una **restauración autorizada** y un **registro de pruebas reales**, no solo una captura de pantalla de la herramienta.

**Referencia técnica:** documentación oficial de Clonezilla: <https://clonezilla.org/clonezilla-live.php>.
