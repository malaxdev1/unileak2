# Scripts

Utilidades del laboratorio. Ejecutar siempre desde la **raíz del proyecto**:

```bash
# Generar imagen con esteganografía (carnet y mensaje oculto)
python scripts/create_stego_image.py

# Decodificar mensaje oculto en profile_card.png
python scripts/decode_stego.py
```

Las rutas a `static/uploads/` y `data/` son relativas al directorio de trabajo (raíz del repo).
