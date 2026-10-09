from pathlib import Path
import sys

ROOT = Path.cwd()
if not (ROOT / "mkdocs.yml").is_file() or not (ROOT / "docs" / "index.md").is_file():
    sys.exit("ERROR: Ejecuta este script desde la raíz de tu proyecto MkDocs (donde están mkdocs.yml y docs/index.md).")

TITLES = ['Arquitectura y características de Arduino UNO Q', 'Preparación del entorno de desarrollo', 'Primeros programas y pruebas', 'Entradas y salidas digitales', 'Sensores y actuadores', 'Comunicación entre procesadores y aplicaciones', 'Introducción al entorno Linux de Arduino UNO Q', 'Programación con Python', 'Automatización y servicios', 'Conectividad y servicios de red', 'Servidores web y API REST', 'MQTT y comunicaciones IoT', 'InfluxDB y Grafana', 'Introducción a Edge AI', 'Modelos de inteligencia artificial', 'Visión artificial y reconocimiento', 'Integración de IA con sensores y actuadores', 'Diseño del proyecto final', 'Implementación y pruebas', 'Documentación y presentación']
PARTS = ['Introducción a Arduino UNO Q', 'Programación y electrónica', 'Linux y Python', 'Redes e IoT', 'Inteligencia artificial', 'Proyecto final']
BOUNDS = [(1, 3), (4, 6), (7, 9), (10, 13), (14, 17), (18, 20)]

for part, (start, end) in enumerate(BOUNDS, 1):
    folder = ROOT / "docs" / f"parte{part}"
    folder.mkdir(parents=True, exist_ok=True)
    (ROOT / "docs" / "assets" / "images" / f"parte{part}").mkdir(parents=True, exist_ok=True)
    for number in range(start, end + 1):
        file = folder / f"capitulo{number:02}.md"
        if not file.exists():
            file.write_text(f"# Capítulo {number}. {TITLES[number - 1]}\n\n!!! info \"En preparación\"\n    Este capítulo se desarrollará próximamente.\n", encoding="utf-8")

(ROOT / "programas").mkdir(exist_ok=True)
(ROOT / "requirements.txt").write_text("mkdocs\nmkdocs-material\n", encoding="utf-8") if not (ROOT / "requirements.txt").exists() else None

config = [
    "site_name: Arduino UNO Q - 2º ASIX",
    "site_description: Libro tutorial de Arduino UNO Q",
    "site_author: José Aguilera Molina",
    "theme:",
    "  name: material",
    "  language: es",
    "  palette:",
    "    - scheme: default",
    "      primary: blue",
    "      accent: amber",
    "  features:",
    "    - navigation.sections",
    "    - navigation.footer",
    "    - content.code.copy",
    "    - search.suggest",
    "    - search.highlight",
    "markdown_extensions:",
    "  - admonition",
    "  - pymdownx.details",
    "  - pymdownx.superfences",
    "  - pymdownx.highlight",
    "  - attr_list",
    "  - tables",
    "  - toc:",
    "      permalink: true",
    "nav:",
    "  - Inicio: index.md",
]
for i, (start, end) in enumerate(BOUNDS, 1):
    config.append(f"  - 'Parte {i}. {PARTS[i-1]}':")
    for number in range(start, end+1):
        config.append(f"      - 'Capítulo {number}. {TITLES[number-1]}': parte{i}/capitulo{number:02}.md")

config_path = ROOT / "mkdocs.yml"
backup_path = ROOT / "mkdocs.yml.bak"
if not backup_path.exists():
    backup_path.write_bytes(config_path.read_bytes())
config_path.write_text("\n".join(config) + "\n", encoding="utf-8")
print("Estructura creada: 20 capítulos, 6 partes, carpetas de imágenes y navegación MkDocs.")
print("Portada docs/index.md conservada. Configuración anterior: mkdocs.yml.bak")
