#!/usr/bin/env python3
"""
Script para crear una imagen con esteganografía LSB
Oculta el mensaje: /internal/student-status?debug=true
FLAG{images_should_not_talk}

Ejecutar desde la raíz del proyecto: python scripts/create_stego_image.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

def text_to_binary(text):
    """Convierte texto a binario"""
    return ''.join(format(ord(char), '08b') for char in text)

def encode_lsb(image_path, secret_message, output_path):
    """Codifica un mensaje en una imagen usando LSB"""
    img = Image.open(image_path)
    encoded = img.copy()
    width, height = img.size

    # Agregar delimitador al mensaje
    secret_message += "###END###"
    binary_message = text_to_binary(secret_message)

    data_index = 0
    data_len = len(binary_message)

    for y in range(height):
        for x in range(width):
            if data_index < data_len:
                pixel = list(img.getpixel((x, y)))

                # Modificar el LSB del canal rojo
                pixel[0] = (pixel[0] & ~1) | int(binary_message[data_index])

                encoded.putpixel((x, y), tuple(pixel))
                data_index += 1
            else:
                break
        if data_index >= data_len:
            break

    encoded.save(output_path)
    print(f"[OK] Imagen con esteganografia creada: {output_path}")
    print(f"[OK] Mensaje oculto: {secret_message.replace('###END###', '')}")

def create_profile_card():
    """Crea una imagen de carnet universitario"""
    # Crear imagen base
    width, height = 400, 300
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # Fondo del header
    draw.rectangle([0, 0, width, 60], fill='#8b0000')

    # Texto del header
    try:
        # Intentar cargar una fuente, si falla usar la default
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Título
    draw.text((20, 20), "UNIVERSIDAD DE MELLÍN", fill='white', font=font_large)

    # Información del estudiante
    draw.rectangle([0, 60, width, height], fill='#f0f0f0')

    y_pos = 80
    draw.text((20, y_pos), "CARNET ESTUDIANTIL", fill='#333', font=font_large)

    y_pos += 40
    draw.text((20, y_pos), "Nombre: Carlos Mendoza", fill='#333', font=font_small)

    y_pos += 25
    draw.text((20, y_pos), "Documento: 1031086399", fill='#333', font=font_small)

    y_pos += 25
    draw.text((20, y_pos), "Programa: Ingeniería de Sistemas", fill='#333', font=font_small)

    y_pos += 25
    draw.text((20, y_pos), "Vigencia: 2026", fill='#333', font=font_small)

    # Foto placeholder
    draw.rectangle([280, 100, 370, 220], fill='#ddd', outline='#666', width=2)
    draw.text((295, 150), "FOTO", fill='#666', font=font_small)

    # Guardar imagen base (rutas relativas al cwd = raíz del proyecto)
    base_path = 'static/uploads/profile_card_base.png'
    os.makedirs('static/uploads', exist_ok=True)
    img.save(base_path)
    print(f"[OK] Imagen base creada: {base_path}")

    return base_path

def main():
    print("=" * 60)
    print("Generador de Imagen con Esteganografía - DarkWall Lab")
    print("=" * 60)

    # Crear imagen base
    base_image = create_profile_card()

    # Mensaje secreto que guiará al siguiente paso
    secret_message = "/internal/student-status?debug=true | FLAG{images_should_not_talk}"

    # Codificar mensaje
    output_path = 'static/uploads/profile_card.png'
    encode_lsb(base_image, secret_message, output_path)

    print("\n" + "=" * 60)
    print("INFORMACIÓN PARA EL LABORATORIO")
    print("=" * 60)
    print("\nPara extraer el mensaje oculto, usa:")
    print("  - CyberChef: https://gchq.github.io/CyberChef/")
    print("  - AperiSolve: https://www.aperisolve.com/")
    print("  - StegOnline: https://stegonline.georgeom.net/")
    print("  - O el script: python scripts/decode_stego.py")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
