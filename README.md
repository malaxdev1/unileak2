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

## Sistema Multi-Usuario

UniLeak soporta múltiples usuarios simultáneos sin interferencias entre sí, adecuado para despliegues en la nube donde varios estudiantes pueden trabajar al mismo tiempo.

### Características

- Registro de usuarios individual
- Aislamiento total de datos por usuario
- Progreso independiente (notas, deudas, flags)
- Sin sabotaje entre participantes
- Persistencia en Vercel KV (Redis)

### Despliegue en Vercel

Para desplegar en producción con múltiples usuarios:

- [Inicio rápido (5 minutos)](docs/deployment/QUICKSTART.md)
- [Configuración completa](docs/deployment/SETUP_VERCEL.md)

```bash
git push origin main
```

Luego en vercel.com: importar el repositorio, crear base de datos KV en Storage y conectar al proyecto.

---

## Requisitos

### Uso local

- Python 3.8 o superior
- pip
- Navegador moderno (Chrome, Firefox o Edge) con DevTools (F12)

### Despliegue en Vercel

- Cuenta de Vercel (gratuita)
- Vercel KV habilitado (incluido en plan gratuito)

Opcional para algunas pruebas: CyberChef, AperiSolve, editor de cookies o Burp Suite.

---

## Instalación y ejecución

1. Clonar o descargar el proyecto.

2. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Generar la imagen con esteganografía (carnet universitario y pista oculta). Desde la raíz del proyecto:

   ```bash
   python scripts/create_stego_image.py
   ```

4. Colocar la foto del profesor en `static/uploads/professor.jpg` y, si aplica, configurar sus metadatos según `static/uploads/INSTRUCCIONES_FOTO_PROFESOR.txt`.

5. Ejecutar la aplicación:

   ```bash
   python app.py
   ```

6. Acceder en el navegador a: `http://localhost:5000`

---

## Credenciales de acceso

### Usuarios demo (preconfigurados)

| Rol         | Usuario  | Clave     |
| ----------- | -------- | --------- |
| Estudiante  | 20261001 | 12051998  |
| Estudiante  | 20261002 | 23071999  |
| Estudiante  | 20261003 | 15031997  |
| Monitor     | 10011234 | admin2026 |
| Coordinador | 10021234 | coord2026 |

Para seguir el flujo del laboratorio se suele comenzar con el estudiante 20261001.

### Registro de nuevos usuarios

En el despliegue con Vercel KV, cada participante puede registrarse desde "¿No tienes cuenta? Regístrate aquí" y trabajar con su propio conjunto de datos aislado.

---

## Estructura del proyecto

```
unileak2/
├── app.py                 # Aplicación Flask (rutas y lógica)
├── wsgi.py                # Entry point para Vercel
├── vercel.json            # Configuración de despliegue
├── requirements.txt
├── .env.example
│
├── api/                   # Endpoint serverless (Vercel)
│   └── index.py
│
├── scripts/               # Utilidades (ejecutar desde raíz)
│   ├── create_stego_image.py
│   └── decode_stego.py
│
├── data/                  # Datos base (CSV, solo lectura)
│   ├── usuarios.csv
│   ├── notas.csv
│   ├── materias.csv
│   ├── deudas.csv
│   └── revisiones.csv
│
├── templates/             # Plantillas HTML
├── static/
│   ├── css/
│   └── uploads/           # Imágenes del lab (profile_card, professor, etc.)
│
└── docs/                  # Documentación
    ├── README.md          # Índice de documentación
    ├── deployment/        # Guías de despliegue
    ├── architecture/      # Implementación KV y flujos
    ├── lab/               # Solución del laboratorio (spoilers)
    └── development/       # Changelog y resumen de cambios
```

---

## Objetivos de aprendizaje

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

Hay 8 flags en total. La solución detallada está en [docs/lab/SOLUCION.md](docs/lab/SOLUCION.md).

---

## Tecnologías

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Datos:** CSV (datos base) + Vercel KV/Redis (progreso de usuarios)
- **Imágenes:** Pillow (PIL) para esteganografía
- **Despliegue:** Vercel con KV para multi-usuario

---

## Documentación

Toda la documentación está en la carpeta [docs/](docs/README.md):

- **Despliegue:** [Inicio rápido](docs/deployment/QUICKSTART.md), [Setup Vercel](docs/deployment/SETUP_VERCEL.md)
- **Arquitectura:** [Implementación KV](docs/architecture/IMPLEMENTACION_KV.md), [Flujos del sistema](docs/architecture/FLUJOS.md)
- **Laboratorio:** [Solución completa](docs/lab/SOLUCION.md) (spoilers)
- **Desarrollo:** [Resumen de cambios](docs/development/RESUMEN_CAMBIOS.md)

---

## Aviso legal

Este proyecto es un entorno de aprendizaje controlado. Las vulnerabilidades son intencionales y están documentadas. El acceso no autorizado a sistemas informáticos es un delito; estas prácticas deben limitarse a entornos propios o autorizados.

Universidad de Medellín – DarkWall Lab 2026. Fines educativos y de demostración.
