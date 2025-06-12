#!/usr/bin/env python
# corrector_video.py - Script para corregir la generación de videos de TikTok

import os
import sys
import json
import subprocess
import tempfile
import shutil
import time
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
    """Obtiene información sobre el video"""
    try:
        info_cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height,codec_name",
            "-of", "json", ruta_video
        ]
        
        info_result = subprocess.run(info_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        video_info = json.loads(info_result.stdout)
        return video_info
    except Exception as e:
        print(f"{Fore.RED}❌ Error al obtener información del video: {str(e)}{Style.RESET_ALL}")
        return None

def crear_video_tiktok(ruta_video, ruta_audio, ruta_salida):
    """Crea un video en formato TikTok (vertical) con audio"""
    try:
        # Crear archivo temporal para el video vertical
        video_vertical = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        
        # Obtener información del video
        info_video = obtener_info_video(ruta_video)
        if not info_video:
            print(f"{Fore.RED}❌ No se pudo obtener información del video.{Style.RESET_ALL}")
            return False
        
        # Extraer dimensiones
        width = int(info_video['streams'][0]['width'])
        height = int(info_video['streams'][0]['height'])
        
        print(f"{Fore.CYAN}ℹ️ Dimensiones del video original: {width}x{height}{Style.RESET_ALL}")
        
        # Convertir a formato vertical (9:16)
        if height > width:  # Ya es vertical
            print(f"{Fore.CYAN}ℹ️ El video ya está en formato vertical.{Style.RESET_ALL}")
            video_vertical = ruta_video
        else:
            print(f"{Fore.YELLOW}🔄 Convirtiendo video a formato vertical (9:16)...{Style.RESET_ALL}")
            
            # Para videos horizontales, recortamos del centro y redimensionamos
            new_height = height
            new_width = int(height * 9 / 16)  # Relación de aspecto 9:16
            
            # Calcular el punto de inicio para el recorte centrado
            x_center = width / 2
            crop_x = max(0, int(x_center - new_width / 2))
            
            # Comando FFmpeg para recortar y redimensionar
            process = subprocess.run([
                "ffmpeg", "-y", "-i", ruta_video,
                "-vf", f"crop={new_width}:{new_height}:{crop_x}:0,scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
                "-c:v", "libx264", "-preset", "medium", "-crf", "23", 
                "-c:a", "copy", video_vertical
            ], check=True, capture_output=True, text=True)
            
            # Verificar dimensiones del video generado
            info_vertical = obtener_info_video(video_vertical)
            if info_vertical:
                width_final = int(info_vertical['streams'][0]['width'])
                height_final = int(info_vertical['streams'][0]['height'])
                print(f"{Fore.CYAN}ℹ️ Dimensiones del video vertical: {width_final}x{height_final}{Style.RESET_ALL}")
        
        # Combinar video vertical con audio
        print(f"{Fore.YELLOW}🔄 Combinando video vertical con audio...{Style.RESET_ALL}")
        
        # Usamos la ruta absoluta para evitar problemas
        ruta_salida_abs = os.path.abspath(ruta_salida)
        
        # Crear directorio de salida si no existe
        os.makedirs(os.path.dirname(ruta_salida_abs), exist_ok=True)
        
        # Mostrar el comando completo para diagnóstico
        print(f"{Fore.CYAN}ℹ️ Comando: ffmpeg -y -i {video_vertical} -i {ruta_audio} -c:v libx264 -preset medium -c:a aac -map 0:v:0 -map 1:a:0 -shortest {ruta_salida_abs}{Style.RESET_ALL}")
        
        # Ejecutar comando con salida capturada
        proceso = subprocess.run([
            "ffmpeg", "-y", "-i", video_vertical, "-i", ruta_audio,
            "-c:v", "libx264", "-preset", "medium", "-c:a", "aac", 
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest", ruta_salida_abs
        ], capture_output=True, text=True)
        
        # Verificar si el proceso fue exitoso
        if proceso.returncode != 0:
            print(f"{Fore.RED}❌ Error al combinar video y audio:{Style.RESET_ALL}")
            print(f"{Fore.RED}{proceso.stderr}{Style.RESET_ALL}")
            
            # Intentar método alternativo con archivo intermediario
            print(f"{Fore.YELLOW}⚠️ Intentando método alternativo...{Style.RESET_ALL}")
            
            # Usar un archivo temporal en la misma carpeta
            temp_output = os.path.join(os.path.dirname(ruta_salida_abs), "temp_output.mp4")
            
            proceso_alt = subprocess.run([
                "ffmpeg", "-y", "-i", video_vertical, "-i", ruta_audio,
                "-c:v", "libx264", "-preset", "medium", "-c:a", "aac", 
                "-map", "0:v:0", "-map", "1:a:0",
                "-shortest", temp_output
            ], capture_output=True, text=True)
            
            if proceso_alt.returncode == 0 and os.path.exists(temp_output):
                try:
                    # Copiar del archivo temporal al destino final
                    shutil.copy2(temp_output, ruta_salida_abs)
                    os.remove(temp_output)
                    print(f"{Fore.GREEN}✅ Método alternativo exitoso{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}❌ Error al copiar archivo temporal: {str(e)}{Style.RESET_ALL}")
                    return False
            else:
                print(f"{Fore.RED}❌ Método alternativo también falló{Style.RESET_ALL}")
                return False
        
        # Dar tiempo al sistema de archivos para actualizar
        time.sleep(1)
        
        # Verificar que el archivo se creó correctamente
        if os.path.exists(ruta_salida_abs):
            tamano_mb = os.path.getsize(ruta_salida_abs) / (1024*1024)
            print(f"{Fore.GREEN}✅ Video generado exitosamente: {ruta_salida_abs}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}ℹ️ Tamaño del archivo: {tamano_mb:.2f} MB{Style.RESET_ALL}")
            return ruta_salida_abs
        else:
            print(f"{Fore.RED}❌ El archivo final no se creó: {ruta_salida_abs}{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        import traceback
        print(f"{Fore.RED}❌ Error al crear video TikTok: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.RED}{traceback.format_exc()}{Style.RESET_ALL}")
        return False

def main():
    """Función principal"""
    print(f"{Fore.CYAN}=" * 70)
    print(f"{Fore.YELLOW}🎬 CORRECTOR DE VIDEOS PARA TIKTOK{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=" * 70)
    
    if len(sys.argv) < 2:
        print(f"{Fore.YELLOW}ℹ️ Uso: python corrector_video.py <ID_HISTORIA>{Style.RESET_ALL}")
        return 1
    
    historia_id = sys.argv[1]
    print(f"{Fore.CYAN}ℹ️ Procesando historia: {historia_id}{Style.RESET_ALL}")
    
    # Verificar ffmpeg
    if not verificar_ffmpeg():
        return 1
    
    # Definir rutas
    ruta_historia = f"historias/{historia_id}"
    ruta_audio = os.path.join(ruta_historia, "narracion.mp3")
    ruta_salida = os.path.join(ruta_historia, "video_tiktok.mp4")
    
    # Verificar archivos necesarios
    if not os.path.exists(ruta_historia):
        print(f"{Fore.RED}❌ No se encontró la carpeta de la historia: {ruta_historia}{Style.RESET_ALL}")
        return 1
    
    if not os.path.exists(ruta_audio):
        print(f"{Fore.RED}❌ No se encontró el archivo de audio: {ruta_audio}{Style.RESET_ALL}")
        return 1
    
    # Buscar o descargar un video
    from tiktok_video_generator import descargar_video, identificar_tipo_video
    
    print(f"{Fore.YELLOW}🎥 Necesitamos un video para combinar con el audio{Style.RESET_ALL}")
    tipo_video = identificar_tipo_video()
    
    print(f"{Fore.YELLOW}⬇️ Descargando video...{Style.RESET_ALL}")
    ruta_video = descargar_video(tipo_video)
    
    if not ruta_video:
        print(f"{Fore.RED}❌ No se pudo descargar el video.{Style.RESET_ALL}")
        return 1
    
    # Ajustar la duración del video al audio
    dur_audio = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        ruta_audio
    ]).strip())
    
    print(f"{Fore.CYAN}ℹ️ Duración del audio: {dur_audio:.2f} segundos{Style.RESET_ALL}")
    
    # Hacer loop del video para cubrir el audio
    loop_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
    subprocess.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", ruta_video,
        "-t", str(dur_audio), "-c", "copy", loop_video
    ], check=True)
    
    # Crear el video final
    resultado = crear_video_tiktok(loop_video, ruta_audio, ruta_salida)
    
    if resultado:
        print(f"{Fore.GREEN}✅ Video para TikTok generado exitosamente{Style.RESET_ALL}")
        
        # Preguntar si desea reproducir el video
        reproducir = input(f"{Fore.YELLOW}¿Deseas reproducir el video ahora? (s/n): {Style.RESET_ALL}").lower()
        if reproducir == "s":
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(resultado)
                else:  # Linux/Mac
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.call([opener, resultado])
            except Exception as e:
                print(f"{Fore.RED}❌ Error al reproducir el video: {str(e)}{Style.RESET_ALL}")
        
        return 0
    else:
        print(f"{Fore.RED}❌ No se pudo generar el video para TikTok{Style.RESET_ALL}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
