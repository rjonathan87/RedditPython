#!/usr/bin/env python
# test_vertical_video.py - Utilidad para probar la conversión a formato vertical

import os
import sys
import tempfile
import subprocess
import json
import argparse
from colorama import Fore, Style, init

# Inicializar colorama
init()

def verificar_ffmpeg():
    """Verifica si FFmpeg está instalado en el sistema"""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        print(f"{Fore.RED}❌ FFmpeg no está instalado. Por favor, instala FFmpeg primero.")
        print(f"{Fore.YELLOW}📝 Guía de instalación: https://ffmpeg.org/download.html{Style.RESET_ALL}")
        return False

def obtener_info_video(ruta_video):
    """Obtiene información detallada del video usando ffprobe"""
    info_cmd = [
        "ffprobe", "-v", "error", 
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,codec_name,display_aspect_ratio,r_frame_rate",
        "-show_entries", "format=duration,bit_rate",
        "-of", "json", ruta_video
    ]
    
    try:
        info_result = subprocess.run(info_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        video_info = json.loads(info_result.stdout)
        return video_info
    except Exception as e:
        print(f"{Fore.RED}❌ Error al obtener información del video: {str(e)}{Style.RESET_ALL}")
        return None

def mostrar_info_video(info_video):
    """Muestra información formateada del video"""
    if not info_video:
        return
    
    try:
        # Información del stream de video
        stream = info_video.get('streams', [{}])[0]
        formato = info_video.get('format', {})
        
        width = stream.get('width', 'N/A')
        height = stream.get('height', 'N/A')
        codec = stream.get('codec_name', 'N/A')
        aspect_ratio = stream.get('display_aspect_ratio', 'N/A')
        
        # Frame rate (viene como fracción, lo convertimos a float)
        fps_str = stream.get('r_frame_rate', 'N/A')
        if fps_str != 'N/A' and '/' in fps_str:
            num, denom = map(int, fps_str.split('/'))
            fps = num / denom if denom != 0 else 0
        else:
            fps = fps_str
        
        # Duración y bitrate
        duracion = float(formato.get('duration', 0))
        bitrate = int(formato.get('bit_rate', 0)) / 1000  # Convertir a Kbps
        
        print(f"{Fore.CYAN}▶️ Información del video:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📐 Dimensiones: {width}x{height} (Relación: {aspect_ratio})")
        print(f"{Fore.CYAN}⏱️ Duración: {duracion:.2f} segundos")
        print(f"{Fore.CYAN}🎞️ FPS: {fps if isinstance(fps, str) else fps:.2f}")
        print(f"{Fore.CYAN}📊 Bitrate: {bitrate:.2f} Kbps")
        print(f"{Fore.CYAN}🔌 Códec: {codec}{Style.RESET_ALL}")
        
        # Determinar si es vertical u horizontal
        if height > width:
            print(f"{Fore.GREEN}✅ El video está en formato VERTICAL{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ El video está en formato HORIZONTAL{Style.RESET_ALL}")
            
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Error al mostrar información del video: {str(e)}{Style.RESET_ALL}")
        return False

def convertir_a_vertical(ruta_video_input):
    """Convierte un video horizontal a formato vertical para TikTok (9:16)"""
    try:
        # Obtener información del video original
        print(f"{Fore.YELLOW}🔍 Analizando video original...{Style.RESET_ALL}")
        info_video = obtener_info_video(ruta_video_input)
        if not info_video or not mostrar_info_video(info_video):
            return None
        
        # Extraer dimensiones
        stream = info_video.get('streams', [{}])[0]
        width = int(stream.get('width', 0))
        height = int(stream.get('height', 0))
          # Si el video ya es vertical, lo dejamos como está
        if height > width:
            print(f"{Fore.CYAN}ℹ️ El video ya está en formato vertical. No se requiere conversión.{Style.RESET_ALL}")
            return ruta_video_input
        
        # Crear un nombre para el archivo temporal de salida
        video_vertical = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        
        print(f"{Fore.YELLOW}🔄 Convirtiendo video a formato vertical para TikTok...{Style.RESET_ALL}")
        
        # Para videos horizontales, recortamos del centro y redimensionamos
        new_height = height
        new_width = int(height * 9 / 16)  # Relación de aspecto 9:16
        
        # Calcular el punto de inicio para el recorte centrado
        x_center = width / 2
        crop_x = max(0, int(x_center - new_width / 2))
        
        print(f"{Fore.CYAN}ℹ️ Recortando a: {new_width}x{new_height}, desde X={crop_x}{Style.RESET_ALL}")
          # Comando FFmpeg para recortar y redimensionar
        cmd = [
            "ffmpeg", "-y", "-i", ruta_video_input,
            "-vf", f"crop={new_width}:{new_height}:{crop_x}:0,scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-c:a", "aac", "-b:a", "128k", video_vertical
        ]
        
        print(f"{Fore.YELLOW}🔧 Ejecutando comando:{Style.RESET_ALL}")
        print(" ".join(cmd))
        
        subprocess.run(cmd, check=True)
        
        print(f"{Fore.GREEN}✅ Video convertido correctamente{Style.RESET_ALL}")
        
        # Verificar el video resultante
        print(f"{Fore.YELLOW}🔍 Analizando video convertido...{Style.RESET_ALL}")
        info_convertido = obtener_info_video(video_vertical)
        if info_convertido:
            mostrar_info_video(info_convertido)
            
        return video_vertical
    
    except Exception as e:
        print(f"{Fore.RED}❌ Error al convertir video a formato vertical: {str(e)}{Style.RESET_ALL}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Convierte un video horizontal a formato vertical para TikTok (9:16)')
    parser.add_argument('input', help='Ruta del video a convertir')
    parser.add_argument('-o', '--output', help='Ruta del video de salida (opcional)')
    args = parser.parse_args()
    
    if not verificar_ffmpeg():
        sys.exit(1)
    
    # Verificar que el archivo de entrada existe
    if not os.path.exists(args.input):
        print(f"{Fore.RED}❌ El archivo de entrada no existe: {args.input}{Style.RESET_ALL}")
        sys.exit(1)
        
    # Convertir el video
    video_vertical = convertir_a_vertical(args.input)
    if not video_vertical:
        print(f"{Fore.RED}❌ No se pudo convertir el video{Style.RESET_ALL}")
        sys.exit(1)
    
    # Si se especificó una salida, copiar el archivo temporal allí
    if args.output:
        output_path = args.output
        try:
            import shutil
            shutil.copy2(video_vertical, output_path)
            print(f"{Fore.GREEN}✅ Video guardado en: {output_path}{Style.RESET_ALL}")
            
            # Eliminar el archivo temporal
            os.unlink(video_vertical)
        except Exception as e:
            print(f"{Fore.RED}❌ Error al guardar el video: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}ℹ️ El video convertido está disponible en: {video_vertical}{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}✅ Video convertido disponible en: {video_vertical}{Style.RESET_ALL}")
    
    # Preguntar si desea reproducir el video
    reproducir = input(f"{Fore.YELLOW}¿Deseas reproducir el video ahora? (s/n): {Style.RESET_ALL}").lower()
    if reproducir == "s":
        try:
            video_a_reproducir = output_path if args.output else video_vertical
            if os.name == 'nt':  # Windows
                os.startfile(video_a_reproducir)
            else:  # Linux/Mac
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, video_a_reproducir])
        except Exception as e:
            print(f"{Fore.RED}❌ Error al reproducir el video: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
