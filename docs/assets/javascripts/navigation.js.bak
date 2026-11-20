
document.addEventListener("DOMContentLoaded", () => {

    const capitulos = {
        1: [
            "Arquitectura y características",
            "Entorno de desarrollo",
            "Primeros programas"
        ],
        2: [
            "Entradas y salidas digitales",
            "Sensores y actuadores",
            "Comunicación entre procesadores"
        ],
        3: [
            "Linux en Arduino UNO Q",
            "Programación con Python",
            "Automatización y servicios"
        ],
        4: [
            "Conectividad y redes",
            "Servidores web y API REST",
            "MQTT y comunicaciones IoT",
            "InfluxDB y Grafana"
        ],
        5: [
            "Introducción a Edge AI",
            "Modelos de inteligencia artificial",
            "Visión artificial",
            "IA con sensores y actuadores"
        ],
        6: [
            "Diseño del proyecto",
            "Implementación y pruebas",
            "Documentación y presentación"
        ]
    };

    const inicio = {
        1: 1,
        2: 4,
        3: 7,
        4: 10,
        5: 14,
        6: 18
    };

    const tabs = document.querySelectorAll(".md-tabs__item");

    // Obtener la URL base del libro
    const script = [...document.scripts].find(s =>
        s.src.includes("assets/javascripts/navigation.js")
    );

    if (!script) return;

    const base = new URL("../../", script.src);

    // Crear los menus fuera de los contenedores de Material
    const contenedor = document.createElement("div");
    contenedor.id = "monlau-menu-container";

    // Estilos esenciales independientes del CSS externo
    Object.assign(contenedor.style, {
        position: "fixed",
        top: "0",
        left: "0",
        width: "0",
        height: "0",
        zIndex: "99999",
        pointerEvents: "none"
    });

    document.body.appendChild(contenedor);

    let menuActivo = null;
    let pestañaActiva = null;
    let temporizador = null;

    function cerrarMenu() {
        if (menuActivo) {
            menuActivo.style.display = "none";
        }
        menuActivo = null;
        pestañaActiva = null;
    }

    function programarCierre() {
        clearTimeout(temporizador);
        temporizador = setTimeout(cerrarMenu, 180);
    }

    tabs.forEach(tab => {

        const enlace = tab.querySelector(".md-tabs__link");
        if (!enlace) return;

        const texto = enlace.textContent.trim();
        const coincidencia = texto.match(/Parte\s+([1-6])/i);
        if (!coincidencia) return;

        const parte = Number(coincidencia[1]);

        const menu = document.createElement("div");
        menu.className = "monlau-menu-flotante";

        // Estilos esenciales para garantizar que sea flotante
        Object.assign(menu.style, {
            display: "none",
            position: "fixed",
            width: "330px",
            maxWidth: "calc(100vw - 20px)",
            backgroundColor: "#ffffff",
            borderTop: "4px solid #f5c400",
            boxShadow: "0 8px 24px rgba(0,0,0,0.25)",
            borderRadius: "0 0 6px 6px",
            padding: "8px 0",
            maxHeight: "70vh",
            overflowY: "auto",
            zIndex: "99999",
            pointerEvents: "auto"
        });

        capitulos[parte].forEach((titulo, indice) => {

            const numero = inicio[parte] + indice;
            const link = document.createElement("a");

            link.textContent = `Capítulo ${numero}. ${titulo}`;

            link.href = new URL(
                `parte${parte}/capitulo${String(numero).padStart(2, "0")}/`,
                base
            ).href;

            Object.assign(link.style, {
                display: "block",
                padding: "11px 16px",
                color: "#00549f",
                fontSize: "13px",
                lineHeight: "1.5",
                textDecoration: "none"
            });

            link.addEventListener("mouseenter", () => {
                link.style.backgroundColor = "#eef4fa";
            });

            link.addEventListener("mouseleave", () => {
                link.style.backgroundColor = "transparent";
            });

            menu.appendChild(link);
        });

        contenedor.appendChild(menu);

        function abrirMenu() {

            clearTimeout(temporizador);

            if (menuActivo && menuActivo !== menu) {
                menuActivo.style.display = "none";
            }

            const rect = tab.getBoundingClientRect();

            menu.style.display = "block";

            const ancho = menu.getBoundingClientRect().width;

            menu.style.left = Math.max(
                10,
                Math.min(rect.left, window.innerWidth - ancho - 10)
            ) + "px";

            menu.style.top = rect.bottom + "px";

            menuActivo = menu;
            pestañaActiva = tab;
        }

        tab.addEventListener("mouseenter", abrirMenu);
        tab.addEventListener("mouseleave", programarCierre);

        enlace.addEventListener("focus", abrirMenu);

        menu.addEventListener("mouseenter", () => {
            clearTimeout(temporizador);
        });

        menu.addEventListener("mouseleave", programarCierre);
    });

    document.addEventListener("keydown", event => {
        if (event.key === "Escape") {
            clearTimeout(temporizador);
            cerrarMenu();
        }
    });

    document.addEventListener("click", event => {
        if (
            !event.target.closest(".monlau-menu-flotante") &&
            !event.target.closest(".md-tabs__item")
        ) {
            cerrarMenu();
        }
    });

    window.addEventListener("scroll", cerrarMenu);
    window.addEventListener("resize", cerrarMenu);

});
