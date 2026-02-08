#!/usr/bin/env python3
"""
Script para decodificar el mensaje oculto en la imagen
Ejecutar desde la raíz del proyecto: python scripts/decode_stego.py
"""

from PIL import Image

def binary_to_text(binary_str):
    """Convierte binario a texto"""
    text = ''
    for i in range(0, len(binary_str), 8):
        byte = binary_str[i:i+8]
        if len(byte) == 8:
            text += chr(int(byte, 2))
    return text

def decode_lsb(image_path):
    """Decodifica el mensaje oculto en una imagen"""
    img = Image.open(image_path)
    width, height = img.size

    binary_message = ''

    for y in range(height):
        for x in range(width):
            pixel = img.getpixel((x, y))
            # Extraer LSB del canal rojo
            binary_message += str(pixel[0] & 1)

    # Convertir a texto
    message = binary_to_text(binary_message)

    # Buscar el delimitador
    end_marker = "###END###"
    if end_marker in message:
        message = message[:message.index(end_marker)]

    return message

def main():
    print("=" * 60)
    print("Decodificador de Esteganografía LSB")
    print("=" * 60)

    image_path = 'static/uploads/profile_card.png'

    try:
        message = decode_lsb(image_path)
        print(f"\n[OK] Mensaje oculto encontrado:\n")
        print(f"  {message}\n")
        print("=" * 60)
    except FileNotFoundError:
        print(f"\n[ERROR] No se encontro la imagen en {image_path}")
        print("  Ejecuta primero desde la raiz: python scripts/create_stego_image.py\n")
    except Exception as e:
        print(f"\n[ERROR] Error al decodificar: {e}\n")

if __name__ == '__main__':
    main()
