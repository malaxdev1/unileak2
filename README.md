```
██████╗  █████╗ ██████╗ ██╗  ██╗██╗    ██╗ █████╗ ██╗     ██╗
██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝██║    ██║██╔══██╗██║     ██║
██║  ██║███████║██████╔╝█████╔╝ ██║ █╗ ██║███████║██║     ██║
██║  ██║██╔══██║██╔══██╗██╔═██╗ ██║███╗██║██╔══██║██║     ██║
██████╔╝██║  ██║██║  ██║██║  ██╗╚███╔███╔╝██║  ██║███████╗███████╗
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝

██╗      █████╗ ██████╗ ███████╗    ██████╗  ██████╗ ██████╗  ██████╗        ██╗
██║     ██╔══██╗██╔══██╗██╔════╝    ╚════██╗██╔═████╗╚════██╗██╔════╝       ███║
██║     ███████║██████╔╝███████╗     █████╔╝██║██╔██║ █████╔╝███████╗ █████╗╚██║
██║     ██╔══██║██╔══██╗╚════██║    ██╔═══╝ ████╔╝██║██╔═══╝ ██╔═══██╗╚════╝ ██║
███████╗██║  ██║██████╔╝███████║    ███████╗╚██████╔╝███████╗╚██████╔╝       ██║
╚══════╝╚═╝  ╚═╝╚═════╝ ╚══════╝    ╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝        ╚═╝

                        Universidad de Medellín
                        UNILEAK - Laboratorio 2026
```

"Solo estaba mirando..."

---

## Descripción

UniLeak es un laboratorio educativo de seguridad ofensiva que simula un sistema universitario con vulnerabilidades intencionales. El participante asume el rol de un estudiante que explora el sistema; las fallas de diseño permiten una escalada progresiva sin necesidad de exploits complejos ni herramientas avanzadas.

El laboratorio está pensado como una cadena de descubrimientos: cada hallazgo conduce al siguiente, en un flujo narrativo que refleja cómo pequeñas debilidades se combinan en un entorno real.

**Advertencia:** Todas las vulnerabilidades son intencionales. Uso exclusivamente educativo. No utilizar estas técnicas en sistemas reales sin autorización explícita.

---

## Requisitos

- Python 3.8 o superior
- pip
- Navegador moderno (Chrome, Firefox o Edge) con DevTools (F12)

Opcional para algunas pruebas: CyberChef, AperiSolve, editor de cookies o Burp Suite.

---

## Instalación y ejecución

1. Clonar o descargar el proyecto.

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Generar la imagen con esteganografía (carnet universitario y pista oculta):
   ```bash
   python create_stego_image.py
   ```

4. Colocar la foto del profesor en `static/uploads/professor.jpg` y, si aplica, configurar sus metadatos según `static/uploads/INSTRUCCIONES_FOTO_PROFESOR.txt`.

5. Ejecutar la aplicación:
   ```bash
   python app.py
   ```
   Alternativa en Windows: `run.bat`

6. Acceder en el navegador a: `http://localhost:5000`

---

## Credenciales de acceso

| Rol           | Usuario  | Clave     |
|---------------|----------|-----------|
| Estudiante    | 20261001 | 12051998  |
| Estudiante    | 20261002 | 23071999  |
| Estudiante    | 20261003 | 15031997  |
| Monitor       | 10011234 | admin2026 |
| Coordinador   | 10021234 | coord2026 |

Para seguir el flujo del laboratorio se suele comenzar con el estudiante 20261001.

---

## Estructura del proyecto

```
labdarkwall2026/
├── app.py                      # Aplicación Flask (rutas y lógica)
├── create_stego_image.py       # Genera imagen con esteganografía LSB
├── decode_stego.py             # Decodifica mensaje en profile_card.png
├── requirements.txt
├── run.bat                     # Arranque rápido (Windows)
├── README.md                   # Este archivo
├── SOLUCION.md                 # Solución completa (spoilers)
├── data/
│   ├── usuarios.csv
│   ├── notas.csv
│   ├── materias.csv
│   ├── deudas.csv
│   └── revisiones.csv
├── templates/
│   ├── login.html
│   ├── panel_estudiante.html
│   ├── panel_monitor.html
│   ├── panel_academico.html
│   ├── secreto_profesor.html
│   ├── boveda.html
│   ├── cambiar_clave.html
│   └── olvido_clave.html
└── static/
    ├── css/style.css
    └── uploads/
        ├── profile_card.png    # Imagen con esteganografía
        ├── professor.jpg       # Foto del profesor (metadatos; el usuario la aporta)
        └── INSTRUCCIONES_FOTO_PROFESOR.txt
```

---

## Objetivos de aprendizaje

El laboratorio trabaja, entre otros, los siguientes conceptos:

- Esteganografía (LSB en imágenes) y gestión de información oculta
- Information disclosure (endpoints de debug expuestos)
- Bypass de validación solo en cliente
- Insecure Direct Object Reference (IDOR)
- Broken Access Control y escalada de privilegios
- Manejo inseguro de tokens (p. ej. Base64 sin firma)
- Falta de autorización en APIs y paneles
- Exposición de información en metadatos (EXIF/comentarios en imágenes)

---

## Flujo del laboratorio

El participante inicia como estudiante, explora el panel y la imagen del carnet, descubre endpoints internos y debilidades de validación, y puede acabar modificando notas, accediendo a paneles de monitor y coordinación, ajustando estado académico y financiero, y obteniendo la última pista desde los metadatos de la foto del profesor. La fase final consiste en calcular el SHA1 de las ocho flags (en orden alfabético) e introducirlo en la bóveda para completar el lab.

Hay 8 flags en total. La documentación detallada de cada paso y la solución completa se encuentran en **SOLUCION.md**.

---

## Tecnologías

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript
- Datos: CSV (simulación de base de datos)
- Imágenes: Pillow (PIL) para generación y decodificación de esteganografía

---

## Documentación adicional

- **SOLUCION.md:** Guía paso a paso con la solución completa de todos los actos, flags, rutas y hash final de la bóveda. Contiene spoilers; conviene consultarlo solo tras intentar el lab o para verificación.

---

## Aviso legal

Este proyecto es un entorno de aprendizaje controlado. Las vulnerabilidades son intencionales y están documentadas. El acceso no autorizado a sistemas informáticos es un delito; estas prácticas deben limitarse a entornos propios o autorizados. El conocimiento adquirido ha de usarse de forma responsable.

Universidad de Medellín – DarkWall Lab 2026. Fines educativos y de demostración.
