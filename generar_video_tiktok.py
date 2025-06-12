#!/usr/bin/env python
# generar_video_tiktok.py - Script principal para generar videos en formato TikTok

import os
import sys
import argparse
from colorama import Fore, Style, init

# Importar el módulo de generación de videos para TikTok
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tiktok_video_generator import integrar_video

# Inicializar colorama
init()

def main():
    parser = argparse.ArgumentParser(description='Genera un video en formato vertical para TikTok a partir de una historia')
    parser.add_argument('historia_id', help='ID de la historia para generar el video')
    args = parser.parse_args()
    
    print(f"{Fore.YELLOW}🎬 GENERADOR DE VIDEOS PARA TIKTOK{Style.RESET_ALL}")
    print(f"{Fore.CYAN}-" * 70)
    print(f"{Fore.CYAN}Este script convertirá la historia en un video de formato vertical (9:16)")
    print(f"{Fore.CYAN}optimizado para TikTok y otras plataformas de video móvil.{Style.RESET_ALL}")
    print(f"{Fore.CYAN}-" * 70)
    
    # Verificar que la carpeta de la historia existe
    ruta_historia = f"historias/{args.historia_id}"
    if not os.path.exists(ruta_historia):
        print(f"{Fore.RED}❌ La carpeta de historia no existe: {ruta_historia}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Verificar que la narración existe
    ruta_audio = os.path.join(ruta_historia, "narracion.mp3")
    if not os.path.exists(ruta_audio):
        print(f"{Fore.RED}❌ No se encontró el archivo de audio: {ruta_audio}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Ejecutar el proceso de integración de video
    resultado = integrar_video(args.historia_id)
    
    if resultado:
        ruta_video_final = os.path.join(ruta_historia, "video_integrado.mp4")
        if os.path.exists(ruta_video_final):
            print(f"{Fore.GREEN}✅ Video generado correctamente: {ruta_video_final}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✅ El video está listo para subirse a TikTok u otras plataformas.{Style.RESET_ALL}")
            return 0
    
    print(f"{Fore.RED}❌ No se pudo generar el video correctamente{Style.RESET_ALL}")
    return 1

if __name__ == "__main__":
    sys.exit(main())
