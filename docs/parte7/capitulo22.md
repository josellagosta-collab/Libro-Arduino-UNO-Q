# Capítulo 22. Infraestructura y mantenimiento de un CPD

!!! info "Parte VII — Actividades complementarias imprescindibles · RA4 · 3 horas"
    Actividad práctica de reconocimiento de infraestructura de centros de procesamiento de datos (CPD): servidores, racks, redundancia, almacenamiento y mantenimiento. Se trabaja con equipos del taller, fotografías autorizadas o un inventario simulado.

## 22.1. Objetivos y planificación

Al finalizar, el alumnado identificará componentes de un CPD, describirá sus funciones, reconocerá puntos únicos de fallo y elaborará una propuesta básica de mantenimiento.

| Bloque | Tiempo | Producto |
|---|---:|---|
| Reconocimiento de equipos y rack | 60 min | Plano e inventario |
| Redundancia y almacenamiento | 60 min | Diagrama y análisis de fallos |
| Mantenimiento y defensa | 60 min | Checklist e informe |

## 22.2. Elementos de un CPD

- **Rack:** armario o bastidor normalizado que organiza equipos; la altura se expresa habitualmente en unidades `U`.
- **Servidor:** equipo dedicado a ejecutar servicios, aplicaciones o máquinas virtuales.
- **Switch:** interconecta dispositivos en la red local; pueden existir enlaces y equipos redundantes.
- **SAI/UPS:** proporciona alimentación temporal y facilita un apagado controlado ante fallos eléctricos.
- **PDU:** distribuye la energía dentro del rack; no equivale a un SAI.
- **Almacenamiento NAS/SAN:** proporciona almacenamiento compartido mediante arquitecturas y protocolos diferentes.
- **Ventilación y climatización:** mantienen las condiciones ambientales de operación.
- **Cableado y etiquetado:** permiten localizar puertos, equipos y circuitos con rapidez.

### RAID y copias de seguridad

RAID puede mejorar disponibilidad o rendimiento, según su nivel, pero **no sustituye una copia de seguridad**. Un borrado accidental o un ransomware pueden afectar simultáneamente a varios discos de un conjunto RAID.

| Solución | Finalidad | Limitación |
|---|---|---|
| RAID 1 | Espejo entre discos | No protege contra borrados lógicos |
| RAID 5/6 | Paridad y tolerancia a fallos de discos | Reconstrucción y riesgo de fallos adicionales |
| Copia externa | Recuperación de datos | Depende de periodicidad y pruebas de restauración |
| Dos fuentes de alimentación | Redundancia eléctrica del servidor | No sirve si ambas dependen del mismo punto de fallo |
| Dos enlaces de red | Mayor disponibilidad | Requiere configuración correcta de red |

## 22.3. Actividad 1: reconocimiento del rack (60 min)

1. Observa un rack del centro o una fotografía proporcionada por el docente.
2. Identifica servidores, switches, paneles de parcheo, PDU, SAI, ventilación y organizadores de cable.
3. Elabora un esquema frontal de posiciones, sin mover ni desconectar dispositivos.
4. Completa el inventario y anota los elementos que no puedas identificar con certeza.

| Posición / U | Equipo | Función | Conexiones visibles | Observaciones |
|---|---|---|---|---|
| | | | | |
| | | | | |
| | | | | |

!!! warning "Trabajo en infraestructura real"
    La actividad es **visual y documental**. No se abrirán servidores, SAI ni cuadros eléctricos, ni se desconectarán cables o fuentes de alimentación. Las intervenciones físicas requieren autorización y personal competente.

## 22.4. Actividad 2: redundancia y almacenamiento (60 min)

Diseña una infraestructura de ejemplo para alojar una aplicación y sus datos. Incluye:

1. Un servidor principal y una estrategia de recuperación.
2. Almacenamiento y copias de seguridad.
3. Alimentación eléctrica y apagado seguro.
4. Conectividad de red.
5. Dos posibles puntos únicos de fallo y una mejora para cada uno.

### Matriz de disponibilidad

| Componente | Fallo previsto | Consecuencia | Medida preventiva o de recuperación |
|---|---|---|---|
| Disco | Avería física | Pérdida de acceso a datos | RAID adecuado + copias verificadas |
| Fuente eléctrica | Corte de suministro | Parada del servicio | SAI y apagado controlado |
| Switch | Avería de equipo | Pérdida de conectividad | Redundancia cuando esté justificada |
| Temperatura | Refrigeración insuficiente | Sobrecalentamiento | Monitorización y alarmas |

## 22.5. Actividad 3: mantenimiento del CPD (60 min)

Elabora una lista de comprobación de mantenimiento **no invasivo**. Cada verificación debe tener responsable, frecuencia y evidencia.

| Comprobación | Frecuencia propuesta | Evidencia | Responsable |
|---|---|---|---|
| Estado de alarmas de hardware | | | |
| Temperatura y ventilación | | | |
| Capacidad de almacenamiento | | | |
| Estado de copias y restauraciones de prueba | | | |
| Etiquetado e inventario | | | |
| Alertas del SAI | | | |
| Registros y actualizaciones planificadas | | | |

Presenta en cinco minutos el esquema del rack, los dos principales riesgos identificados y el plan de mantenimiento. Distingue las comprobaciones que puedes realizar como observador de las que requieren autorización técnica.

## 22.6. Práctica evaluable

**Enunciado:** realiza una auditoría documental básica de un rack o CPD de ejemplo y entrega un informe con inventario, esquema, riesgos y mantenimiento.

| Criterio | Puntos |
|---|---:|
| Identificación de equipos y funciones | 3 |
| Esquema y organización del rack | 2 |
| Redundancia, RAID y copias diferenciados | 2 |
| Plan de mantenimiento razonado | 2 |
| Claridad de la exposición y evidencias | 1 |
| **Total** | **10** |

## 22.7. Incidencias y autoevaluación

Si una etiqueta es ilegible, registra la incertidumbre: **no inventes modelos ni conexiones**. Si no se dispone de rack real, trabaja con imágenes autorizadas y especifica que el inventario es simulado.

1. ¿Por qué una PDU no sustituye a un SAI?
2. ¿Qué diferencia existe entre redundancia y copia de seguridad?
3. ¿Qué representa una unidad U en un rack?
4. ¿Qué comprobaciones pueden hacerse sin manipular equipos?
5. ¿Qué información debe contener una ficha de mantenimiento?

!!! success "RA4 — Evidencia final"
    El alumnado entrega un **inventario del rack**, un **diagrama de redundancia** y una **lista de mantenimiento documentada**.
