#!/usr/bin/env python
# fix_video_integration.py - Script para corregir problemas de integración de audio y video

import os
import sys
import subprocess
import tempfile
import shutil
from colorama import init, Fore, Style

# Inicializar colorama
init()

def corregir_integracion_video(historia_id):
    """Corrige la integración de audio y video para una historia específica"""
    try:
        print(f"{Fore.CYAN}=" * 70)
        print(f"{Fore.YELLOW}🔧 CORRECTOR DE INTEGRACIÓN DE AUDIO Y VIDEO{Style.RESET_ALL}")
        print(f"{Fore.CYAN}=" * 70)
        
        # Obtener la ruta absoluta del script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construir rutas absolutas
        ruta_historia = os.path.join(script_dir, "historias", historia_id)
        ruta_audio = os.path.join(ruta_historia, "narracion.mp3")
        ruta_video_final = os.path.join(ruta_historia, "video_integrado.mp4")
        
        print(f"{Fore.CYAN}ℹ️ Ruta de la historia: {ruta_historia}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}ℹ️ Ruta del audio: {ruta_audio}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}ℹ️ Ruta del video final: {ruta_video_final}{Style.RESET_ALL}")
        
        # Verificar que existan las carpetas y archivos necesarios
        if not os.path.exists(ruta_historia):
            print(f"{Fore.RED}❌ No existe la carpeta de la historia: {ruta_historia}{Style.RESET_ALL}")
            try:
                os.makedirs(ruta_historia, exist_ok=True)
                print(f"{Fore.GREEN}✅ Se ha creado la carpeta: {ruta_historia}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}❌ Error al crear la carpeta: {str(e)}{Style.RESET_ALL}")
                return False
        
        if not os.path.exists(ruta_audio):
            print(f"{Fore.RED}❌ No se encontró el archivo de audio: {ruta_audio}{Style.RESET_ALL}")
            return False
        
        # Buscar un video de stock predeterminado si no se especifica uno
        video_stock = os.path.join(script_dir, "recursos", "stock_video.mp4")
        
        if not os.path.exists(video_stock):
            print(f"{Fore.YELLOW}⚠️ No se encontró un video stock. Descargando uno...{Style.RESET_ALL}")
            # Usar un video de prueba (puede cambiarse por uno más adecuado)
            temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            
            # Crear directorio de recursos si no existe
            recursos_dir = os.path.join(script_dir, "recursos")
            os.makedirs(recursos_dir, exist_ok=True)
            
            # Descargar un video de stock genérico
            try:
                import requests
                # URL de un video de stock gratuito (ejemplo, puede cambiarse)
                stock_url = "https://joy1.videvo.net/videvo_files/video/free/2019-09/large_watermarked/190828_27_SuperTrees_HD_17_preview.mp4"
                
                print(f"{Fore.YELLOW}⬇️ Descargando video de stock...{Style.RESET_ALL}")
                with requests.get(stock_url, stream=True) as r, open(temp_video, 'wb') as f:
                    total_length = int(r.headers.get('content-length', 0))
                    downloaded = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            done = int(50 * downloaded / total_length)
                            sys.stdout.write(f"\r[{'#' * done}{'.' * (50-done)}] {downloaded/total_length*100:.1f}%")
                            sys.stdout.flush()
                            
                print(f"\n{Fore.GREEN}✅ Video descargado correctamente.{Style.RESET_ALL}")
                
                # Guardar en la carpeta de recursos
                shutil.copy2(temp_video, video_stock)
                os.remove(temp_video)
                
            except Exception as e:
                print(f"{Fore.RED}❌ Error al descargar video: {str(e)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}⚠️ Creando un video de color negro como alternativa...{Style.RESET_ALL}")
                
                # Crear un video negro de 10 segundos como alternativa
                try:
                    subprocess.run([
                        "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=1280x720:r=30", 
                        "-t", "10", video_stock
                    ], check=True)
                except Exception as e:
                    print(f"{Fore.RED}❌ Error al crear video alternativo: {str(e)}{Style.RESET_ALL}")
                    return False
        
        # Obtener duración del audio
        dur_audio = float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            ruta_audio
        ]).strip())
        
        print(f"{Fore.CYAN}ℹ️ Duración del audio: {dur_audio:.2f}s{Style.RESET_ALL}")
        
        # Crear video en bucle para cubrir la duración del audio
        loop_mp4 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        subprocess.run([
            "ffmpeg", "-y", "-stream_loop", "-1", "-i", video_stock,
            "-t", str(dur_audio), "-c", "copy", loop_mp4
        ], check=True)
        
        # Convertir a formato vertical si el video no lo es
        # Obtener información del video
        info_cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "json", loop_mp4
        ]
        
        info_result = subprocess.run(info_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        import json
        video_info = json.loads(info_result.stdout)
        
        # Extraer dimensiones
        width = int(video_info['streams'][0]['width'])
        height = int(video_info['streams'][0]['height'])
        
        video_vertical = loop_mp4
        
        # Si el video no es vertical, convertirlo
        if height <= width:
            print(f"{Fore.CYAN}ℹ️ Convirtiendo video a formato vertical...{Style.RESET_ALL}")
            video_vertical = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            
            # Calcular dimensiones para formato vertical 9:16
            new_height = height
            new_width = int(height * 9 / 16)  # Relación de aspecto 9:16
            
            # Calcular el punto de inicio para el recorte centrado
            x_center = width / 2
            crop_x = max(0, int(x_center - new_width / 2))
            
            # Comando FFmpeg para recortar y redimensionar
            subprocess.run([
                "ffmpeg", "-y", "-i", loop_mp4,
                "-vf", f"crop={new_width}:{new_height}:{crop_x}:0,scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
                "-c:a", "copy", video_vertical
            ], check=True)
        
        # Integrar audio con video
        print(f"{Fore.YELLOW}🔄 Integrando audio con video...{Style.RESET_ALL}")
        
        # Usar un archivo temporal en la misma carpeta que el destino final
        temp_output = os.path.join(os.path.dirname(ruta_video_final), "temp_output.mp4")
        
        try:
            subprocess.run([
                "ffmpeg", "-y", "-i", video_vertical, "-i", ruta_audio,
                "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", 
                "-map", "0:v:0", "-map", "1:a:0",
                "-shortest", temp_output
            ], check=True)
            
            # Verificar que se haya creado el archivo temporal
            if os.path.exists(temp_output):
                # Copiar del archivo temporal al destino final
                shutil.copy2(temp_output, ruta_video_final)
                os.remove(temp_output)
                print(f"{Fore.GREEN}✅ Video con audio integrado generado: {ruta_video_final}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ No se pudo crear el archivo temporal: {temp_output}{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}❌ Error al integrar audio con video: {str(e)}{Style.RESET_ALL}")
            return False
        
        # Verificar que el archivo final existe
        if os.path.exists(ruta_video_final):
            tamano_mb = os.path.getsize(ruta_video_final) / (1024*1024)
            print(f"{Fore.GREEN}✅ Corrección completada con éxito. Tamaño del archivo: {tamano_mb:.2f} MB{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}❌ El archivo final no se creó: {ruta_video_final}{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}❌ Error en la corrección: {str(e)}{Style.RESET_ALL}")
        import traceback
        print(f"{Fore.RED}Detalles del error: {traceback.format_exc()}{Style.RESET_ALL}")
        return False

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print(f"{Fore.YELLOW}ℹ️ Uso: python fix_video_integration.py <ID_HISTORIA>{Style.RESET_ALL}")
        return 1
    
    historia_id = sys.argv[1]
    print(f"{Fore.CYAN}ℹ️ Corrigiendo integración para historia: {historia_id}{Style.RESET_ALL}")
    
    if corregir_integracion_video(historia_id):
        print(f"{Fore.GREEN}✅ Corrección completada con éxito{Style.RESET_ALL}")
        return 0
    else:
        print(f"{Fore.RED}❌ No se pudo completar la corrección{Style.RESET_ALL}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
