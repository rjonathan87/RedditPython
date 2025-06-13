import os
import sys
import json
import urllib.request
import re
import subprocess
from datetime import datetime
import tempfile
import requests
from colorama import Fore, Style

def verificar_ffmpeg():
    """Verifica si FFmpeg está instalado en el sistema"""
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        print(f"{Fore.RED}❌ FFmpeg no está instalado. Por favor, instala FFmpeg primero.")
        print(f"{Fore.YELLOW}📝 Guía de instalación: https://ffmpeg.org/download.html{Style.RESET_ALL}")
        return False

def identificar_tipo_video():
    """Muestra las opciones para seleccionar el tipo de video a descargar"""
    print(f"{Fore.YELLOW}🎥 SELECCIONA EL TIPO DE VIDEO A DESCARGAR{Style.RESET_ALL}")
    print(f"{Fore.CYAN}-" * 70)
    print(f"{Fore.CYAN}1. 🌆 Paisaje urbano nocturno")
    print(f"{Fore.CYAN}2. 🌳 Naturaleza")
    print(f"{Fore.CYAN}3. 🌌 Espacio y galaxias")
    print(f"{Fore.CYAN}4. 🌊 Océano")
    print(f"{Fore.CYAN}5. 🔥 Fuego y llamas")
    print(f"{Fore.CYAN}6. 🌧️ Lluvia")
    print(f"{Fore.CYAN}7. 🌫️ Niebla y misterio")
    print(f"{Fore.CYAN}8. ⚡ Tormenta")
    print(f"{Fore.CYAN}9. 🏚️ Casa abandonada")
    print(f"{Fore.CYAN}10. 🏙️ Ciudad")
    print(f"{Fore.CYAN}-" * 70)
    
    while True:
        try:
            opcion = int(input(f"{Fore.YELLOW}Selecciona una opción (1-10): {Style.RESET_ALL}"))
            if 1 <= opcion <= 10:
                tipos_video = {
                    1: "city night urban",
                    2: "nature forest",
                    3: "space galaxy stars",
                    4: "ocean waves sea",
                    5: "fire flames",
                    6: "rain drops",
                    7: "fog mist mysterious",
                    8: "storm lightning thunder",
                    9: "abandoned house spooky",
                    10: "city buildings"
                }
                return tipos_video[opcion]
            else:
                print(f"{Fore.RED}❌ Opción no válida. Intenta de nuevo.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}❌ Por favor, ingresa un número válido.{Style.RESET_ALL}")

def descargar_video(tipo_video, duracion_minima=60, modo_multiples=False, duracion_requerida=None):
    """Descarga uno o varios videos de stock gratuito según el tipo seleccionado
    
    Args:
        tipo_video: Tipo de video a buscar
        duracion_minima: Duración mínima del video en segundos
        modo_multiples: Si es True, descarga múltiples videos hasta alcanzar la duración requerida
        duracion_requerida: Duración total requerida en segundos (para modo_multiples=True)
    
    Returns:
        Una lista de rutas de videos descargados o una única ruta si modo_multiples es False
    """
    print(f"{Fore.YELLOW}🔍 Buscando videos de '{tipo_video}'...{Style.RESET_ALL}")
    
    # Usar Pexels API para buscar videos
    from dotenv import load_dotenv
    load_dotenv()
    
    PEXELS_KEY = os.getenv('PEXELS_API_KEY') or os.getenv('PEXEL_API_KEY')
    if not PEXELS_KEY:
        raise EnvironmentError("Variable PEXELS_API_KEY no definida en .env")    # Intentamos usar la biblioteca de Pexels
    videos = None
    api = None
    try:
        # Usar pexelsapi que parece estar disponible
        from pexelsapi.pexels import Pexels
        api = Pexels(PEXELS_KEY)
        videos = api.search_videos(query=tipo_video, orientation="portrait", page=1, per_page=15 if modo_multiples else 5)
    except Exception as e:
        print(f"{Fore.RED}❌ Error al buscar videos con pexelsapi: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}ℹ️ Asegúrate de tener la biblioteca 'pexelsapi' instalada correctamente.{Style.RESET_ALL}")
        return None
    
    if not videos or not videos.get('videos'):
        print(f"{Fore.RED}❌ No se encontraron videos para '{tipo_video}'.{Style.RESET_ALL}")
        return None
    
    if not videos or not videos.get('videos'):
        print(f"{Fore.RED}❌ No se encontraron videos para '{tipo_video}'.{Style.RESET_ALL}")
        return None
    
    if not modo_multiples:
        # Modo de un solo video
        # Descargar el primer video disponible
        for video in videos['videos']:
            video_files = video.get('video_files', [])
            if not video_files:
                continue
            
                    # Encontrar el archivo con mejor resolución
            best = max(video_files, key=lambda f: f.get('width', 0))
            temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            
            print(f"{Fore.YELLOW}⬇️ Descargando video...{Style.RESET_ALL}")
            try:
                with requests.get(best.get('link'), stream=True) as r, open(temp_path, 'wb') as f:
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
                return temp_path
            except Exception as e:
                print(f"{Fore.RED}❌ Error al descargar el video: {str(e)}{Style.RESET_ALL}")
        
        return None
    else:
        # Modo de múltiples videos
        duracion_total = 0
        videos_descargados = []
        videos_list = videos.get('videos', [])
        # Si hay pocos videos, busquemos más en páginas adicionales
        if len(videos_list) < 10 and api and duracion_requerida:
            page = 2
            max_pages = 3            
            while len(videos_list) < 15 and page <= max_pages:
                try:
                    additional_videos = api.search_videos(query=tipo_video, orientation="portrait", page=page, per_page=15)
                    
                    if additional_videos and additional_videos.get('videos'):
                        videos_list.extend(additional_videos['videos'])
                    page += 1
                except Exception as e:
                    print(f"{Fore.YELLOW}⚠️ No se pudieron obtener más videos: {str(e)}{Style.RESET_ALL}")
                    break
        
        print(f"{Fore.CYAN}ℹ️ Se encontraron {len(videos_list)} videos para descargar.{Style.RESET_ALL}")
        
        for idx, video in enumerate(videos_list):
            if duracion_requerida and duracion_total >= duracion_requerida:
                break
                
            video_files = video.get('video_files', [])
            if not video_files:
                continue
            
            # Encontrar el archivo con mejor resolución
            best = max(video_files, key=lambda f: f.get('width', 0))
            temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            
            print(f"{Fore.YELLOW}⬇️ Descargando video {idx+1} de {len(videos_list)}...{Style.RESET_ALL}")
            try:
                with requests.get(best.get('link'), stream=True) as r, open(temp_path, 'wb') as f:
                    total_length = int(r.headers.get('content-length', 0))
                    downloaded = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            done = int(50 * downloaded / total_length)
                            sys.stdout.write(f"\r[{'#' * done}{'.' * (50-done)}] {downloaded/total_length*100:.1f}%")
                            sys.stdout.flush()
                
                # Verificar duración del video descargado
                dur_video = float(subprocess.check_output([
                    "ffprobe", "-v", "error", "-show_entries",
                    "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
                    temp_path
                ]).strip())
                
                print(f"\n{Fore.GREEN}✅ Video descargado correctamente. Duración: {dur_video:.2f}s{Style.RESET_ALL}")
                videos_descargados.append(temp_path)
                duracion_total += dur_video
                
                if duracion_requerida:
                    print(f"{Fore.CYAN}ℹ️ Duración acumulada: {duracion_total:.2f}s / {duracion_requerida:.2f}s ({(duracion_total/duracion_requerida)*100:.1f}%){Style.RESET_ALL}")
                
            except Exception as e:
                print(f"{Fore.RED}❌ Error al descargar el video {idx+1}: {str(e)}{Style.RESET_ALL}")
        
        if not videos_descargados:
            print(f"{Fore.RED}❌ No se pudo descargar ningún video.{Style.RESET_ALL}")
            return None
            
        print(f"{Fore.GREEN}✅ Se descargaron {len(videos_descargados)} videos con una duración total de {duracion_total:.2f}s{Style.RESET_ALL}")
        return videos_descargados

def convertir_a_vertical(ruta_video_input):
    """Convierte un video horizontal a formato vertical para TikTok (9:16)
    
    Args:
        ruta_video_input: Ruta del video a convertir
    
    Returns:
        Ruta del video convertido a formato vertical
    """
    try:
        # Crear un nombre para el archivo temporal de salida
        video_vertical = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        
        print(f"{Fore.CYAN}ℹ️ Convirtiendo video a formato vertical para TikTok...{Style.RESET_ALL}")
        
        # Obtener información del video original
        info_cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "json", ruta_video_input
        ]
        
        info_result = subprocess.run(info_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        video_info = json.loads(info_result.stdout)
        
        # Extraer dimensiones
        width = int(video_info['streams'][0]['width'])
        height = int(video_info['streams'][0]['height'])
        
        # Calcular dimensiones para formato vertical 9:16
        # Si el video ya es vertical, lo dejamos como está
        if height > width:
            print(f"{Fore.CYAN}ℹ️ El video ya está en formato vertical. Manteniendo dimensiones originales.{Style.RESET_ALL}")
            return ruta_video_input
        
        # Para videos horizontales, recortamos del centro y redimensionamos
        new_height = height
        new_width = int(height * 9 / 16)  # Relación de aspecto 9:16
        
        # Calcular el punto de inicio para el recorte centrado
        x_center = width / 2
        crop_x = max(0, int(x_center - new_width / 2))
          # Comando FFmpeg para recortar y redimensionar
        subprocess.run([
            "ffmpeg", "-y", "-i", ruta_video_input,
            "-vf", f"crop={new_width}:{new_height}:{crop_x}:0,scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k", video_vertical
        ], check=True)
        
        print(f"{Fore.GREEN}✅ Video convertido a formato vertical (9:16) para TikTok{Style.RESET_ALL}")
        return video_vertical
    
    except Exception as e:
        print(f"{Fore.RED}❌ Error al convertir video a formato vertical: {str(e)}{Style.RESET_ALL}")
        # Si falla, devolvemos el video original
        return ruta_video_input

def integrar_audio_video(historia_id, ruta_videos_temp, modo_multiples=False):
    """Integra el audio de la narración con el video descargado
    
    Args:
        historia_id: ID de la historia
        ruta_videos_temp: Ruta del video o lista de rutas de videos
        modo_multiples: Si es True, concatena múltiples videos
    
    Returns:
        Ruta del video final generado o False si hay error
    """
    if not verificar_ffmpeg():
        return False
    
    try:
        ruta_historia = f"historias/{historia_id}"
        
        # Asegurarse de que la carpeta de historia existe
        if not os.path.exists(ruta_historia):
            print(f"{Fore.RED}❌ La carpeta de historia no existe: {ruta_historia}{Style.RESET_ALL}")
            return False
        # Verificar permisos de escritura
        try:
            test_file = os.path.join(ruta_historia, "test_write.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print(f"{Fore.GREEN}✅ Permisos de escritura verificados en: {ruta_historia}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error de permisos en la carpeta: {str(e)}{Style.RESET_ALL}")
            return False
            
        ruta_audio = os.path.join(ruta_historia, "narracion.mp3")
        # Asegurarnos de usar la ruta absoluta para el archivo de salida
        ruta_video_final = os.path.abspath(os.path.join(ruta_historia, "video_integrado.mp4"))
        
        # Asegurarnos de que la carpeta de destino existe
        os.makedirs(os.path.dirname(ruta_video_final), exist_ok=True)
        
        if not os.path.exists(ruta_audio):
            print(f"{Fore.RED}❌ No se encontró el archivo de audio narracion.mp3{Style.RESET_ALL}")
            return False
            
        print(f"{Fore.YELLOW}🔄 Integrando audio con video...{Style.RESET_ALL}")
        
        # 1) Determinar duración del audio
        dur_audio = float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            ruta_audio
        ]).strip())
        
        if not modo_multiples or (isinstance(ruta_videos_temp, str)):
            # Modo de un solo video en loop
            ruta_video_temp = ruta_videos_temp
            print(f"{Fore.CYAN}ℹ️ Usando un solo video en bucle para cubrir la duración del audio ({dur_audio:.2f}s){Style.RESET_ALL}")
            # 2) Loopear video hasta cubrir audio si es necesario
            loop_mp4 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            subprocess.run([
                "ffmpeg", "-y", "-stream_loop", "-1", "-i", ruta_video_temp,
                "-t", str(dur_audio), "-c", "copy", loop_mp4
            ], check=True)
            # Convertir a formato vertical para TikTok
            loop_mp4_vertical = convertir_a_vertical(loop_mp4)

            # 3) Silenciar video y poner narración
            # Nota: No usamos -c:v copy aquí para evitar problemas de compatibilidad después de la conversión
            try:
                print(f"{Fore.YELLOW}🔄 Aplicando audio al video vertical...{Style.RESET_ALL}")
                print(f"{Fore.CYAN}ℹ️ Comando: ffmpeg -y -i {loop_mp4_vertical} -i {ruta_audio} -c:v libx264 -preset medium -c:a aac -map 0:v:0 -map 1:a:0 -shortest {ruta_video_final}{Style.RESET_ALL}")
                
                # Primero intentar con el método normal
                process = subprocess.run([
                    "ffmpeg", "-y", "-i", loop_mp4_vertical, "-i", ruta_audio,
                    "-c:v", "libx264", "-preset", "medium", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0",
                    "-shortest", ruta_video_final
                ], capture_output=True, text=True)
                
                if process.returncode != 0:
                    print(f"{Fore.RED}❌ Error al ejecutar ffmpeg: {process.stderr}{Style.RESET_ALL}")
                    # Intentar método alternativo
                    print(f"{Fore.YELLOW}⚠️ Intentando método alternativo...{Style.RESET_ALL}")
                    
                    # Usar un archivo temporal en la misma carpeta
                    temp_output = os.path.join(os.path.dirname(ruta_video_final), "temp_output.mp4")
                    
                    proceso_alt = subprocess.run([
                        "ffmpeg", "-y", "-i", loop_mp4_vertical, "-i", ruta_audio,
                        "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", 
                        "-map", "0:v:0", "-map", "1:a:0",
                        "-shortest", temp_output
                    ], capture_output=True, text=True)
                    
                    if proceso_alt.returncode == 0 and os.path.exists(temp_output):
                        try:
                            # Copiar del archivo temporal al destino final
                            import shutil
                            shutil.copy2(temp_output, ruta_video_final)
                            os.remove(temp_output)
                            print(f"{Fore.GREEN}✅ Método alternativo exitoso{Style.RESET_ALL}")
                        except Exception as e:
                            print(f"{Fore.RED}❌ Error al copiar archivo temporal: {str(e)}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}❌ Método alternativo también falló: {proceso_alt.stderr}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}✅ FFmpeg completó correctamente{Style.RESET_ALL}")
                
            except Exception as e:
                print(f"{Fore.RED}❌ Error al aplicar audio: {str(e)}{Style.RESET_ALL}")
                import traceback
                print(f"{Fore.RED}Detalles del error: {traceback.format_exc()}{Style.RESET_ALL}")
                return False
        else:
            # Modo de múltiples videos concatenados
            print(f"{Fore.CYAN}ℹ️ Concatenando {len(ruta_videos_temp)} videos para cubrir la duración del audio ({dur_audio:.2f}s){Style.RESET_ALL}")
            
            # Crear un archivo de lista para FFmpeg
            concat_list = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w')
            for video_path in ruta_videos_temp:
                concat_list.write(f"file '{video_path}'\n")
            concat_list.close()
            
            # Concatenar los videos
            concat_mp4 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list.name,
                "-c", "copy", concat_mp4
            ], check=True)
            
            # Verificar duración del video concatenado
            dur_video_concat = float(subprocess.check_output([
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
                concat_mp4
            ]).strip())
            
            print(f"{Fore.CYAN}ℹ️ Duración del video concatenado: {dur_video_concat:.2f}s{Style.RESET_ALL}")
            
            # Si el video concatenado es más corto que el audio, hacer loop
            if dur_video_concat < dur_audio:
                print(f"{Fore.YELLOW}⚠️ El video concatenado es más corto que el audio. Aplicando loop para completar...{Style.RESET_ALL}")
                loop_mp4 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
                subprocess.run([
                    "ffmpeg", "-y", "-stream_loop", "-1", "-i", concat_mp4,
                    "-t", str(dur_audio), "-c", "copy", loop_mp4
                ], check=True)
                video_final_temp = loop_mp4
            else:
                # Si es más largo, recortar al tamaño del audio
                if dur_video_concat > dur_audio:
                    print(f"{Fore.YELLOW}⚠️ El video concatenado es más largo que el audio. Recortando...{Style.RESET_ALL}")
                    trimmed_mp4 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
                    subprocess.run([
                        "ffmpeg", "-y", "-i", concat_mp4, "-t", str(dur_audio),
                        "-c", "copy", trimmed_mp4
                    ], check=True)                    
                    video_final_temp = trimmed_mp4
                else:
                    video_final_temp = concat_mp4
                # Primero convertimos a formato vertical
                video_final_temp_vertical = convertir_a_vertical(video_final_temp)
                
                try:
                    print(f"{Fore.YELLOW}🔄 Aplicando audio al video vertical...{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}ℹ️ Comando: ffmpeg -y -i {video_final_temp_vertical} -i {ruta_audio} -c:v libx264 -preset medium -c:a aac -map 0:v:0 -map 1:a:0 -shortest {ruta_video_final}{Style.RESET_ALL}")
                    
                    # Primero intentar con el método normal
                    process = subprocess.run([
                        "ffmpeg", "-y", "-i", video_final_temp_vertical, "-i", ruta_audio,
                        "-c:v", "libx264", "-preset", "medium", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0",
                        "-shortest", ruta_video_final
                    ], capture_output=True, text=True)
                    
                    if process.returncode != 0:
                        print(f"{Fore.RED}❌ Error al ejecutar ffmpeg: {process.stderr}{Style.RESET_ALL}")
                        # Intentar método alternativo
                        print(f"{Fore.YELLOW}⚠️ Intentando método alternativo...{Style.RESET_ALL}")
                        
                        # Usar un archivo temporal en la misma carpeta
                        temp_output = os.path.join(os.path.dirname(ruta_video_final), "temp_output.mp4")
                        
                        proceso_alt = subprocess.run([
                            "ffmpeg", "-y", "-i", video_final_temp_vertical, "-i", ruta_audio,
                            "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac", 
                            "-map", "0:v:0", "-map", "1:a:0",
                            "-shortest", temp_output
                        ], capture_output=True, text=True)
                        
                        if proceso_alt.returncode == 0 and os.path.exists(temp_output):
                            try:
                                # Copiar del archivo temporal al destino final
                                import shutil
                                shutil.copy2(temp_output, ruta_video_final)
                                os.remove(temp_output)
                                print(f"{Fore.GREEN}✅ Método alternativo exitoso{Style.RESET_ALL}")
                            except Exception as e:
                                print(f"{Fore.RED}❌ Error al copiar archivo temporal: {str(e)}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.RED}❌ Método alternativo también falló: {proceso_alt.stderr}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN}✅ FFmpeg completó correctamente{Style.RESET_ALL}")
                    
                except Exception as e:
                    print(f"{Fore.RED}❌ Error al aplicar audio: {str(e)}{Style.RESET_ALL}")
                    import traceback
                    print(f"{Fore.RED}Detalles del error: {traceback.format_exc()}{Style.RESET_ALL}")
                    return False
              # Eliminar archivo temporal de lista
            os.unlink(concat_list.name)
          
        # Verificar explícitamente que el archivo se ha creado
        print(f"{Fore.YELLOW}🔍 Verificando si el archivo de video fue creado...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}ℹ️ Buscando archivo en: {ruta_video_final}{Style.RESET_ALL}")
        
        # Dar tiempo al sistema de archivos para actualizar
        import time
        time.sleep(2)
        
        if os.path.exists(ruta_video_final):
            tamano_mb = os.path.getsize(ruta_video_final) / (1024*1024)
            print(f"{Fore.GREEN}✅ Video con audio integrado generado: {ruta_video_final}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}ℹ️ Tamaño del archivo: {tamano_mb:.2f} MB{Style.RESET_ALL}")
            return ruta_video_final
        else:
            print(f"{Fore.RED}❌ ERROR: El archivo de video no se creó en la ruta: {ruta_video_final}{Style.RESET_ALL}")
            
            # Verificar si existe algún archivo de video en la carpeta
            archivos_video = [f for f in os.listdir(os.path.dirname(ruta_video_final)) if f.endswith('.mp4')]
            if archivos_video:
                print(f"{Fore.YELLOW}⚠️ Se encontraron otros archivos de video en la carpeta: {', '.join(archivos_video)}{Style.RESET_ALL}")
            
            # Intentar crear una copia del video vertical (sin audio) como alternativa
            try:
                if 'video_final_temp_vertical' in locals() and os.path.exists(video_final_temp_vertical):
                    ruta_alternativa = os.path.join(os.path.dirname(ruta_video_final), "video_alternativo.mp4")
                    import shutil
                    shutil.copy2(video_final_temp_vertical, ruta_alternativa)
                    print(f"{Fore.YELLOW}⚠️ Se ha creado una copia del video vertical en: {ruta_alternativa}{Style.RESET_ALL}")
                    return ruta_alternativa
            except Exception as e:
                print(f"{Fore.RED}❌ Error al intentar guardar una copia alternativa: {str(e)}{Style.RESET_ALL}")
            
            # Como último recurso, intentar usar corrector_video.py
            try:
                print(f"{Fore.YELLOW}⚠️ Intentando usar corrector_video.py como último recurso...{Style.RESET_ALL}")
                subprocess.run([sys.executable, "corrector_video.py", historia_id], check=True)
                
                # Verificar si se creó el video con el corrector
                ruta_alternativa = os.path.join(ruta_historia, "video_tiktok.mp4")
                if os.path.exists(ruta_alternativa):
                    print(f"{Fore.GREEN}✅ Se ha generado un video alternativo con el corrector: {ruta_alternativa}{Style.RESET_ALL}")
                    # Intentar copiar a la ruta esperada
                    try:
                        shutil.copy2(ruta_alternativa, ruta_video_final)
                        print(f"{Fore.GREEN}✅ Video copiado a la ruta estándar.{Style.RESET_ALL}")
                        return ruta_video_final
                    except:
                        return ruta_alternativa
                        
            except Exception as e:
                print(f"{Fore.RED}❌ Error al intentar usar el corrector: {str(e)}{Style.RESET_ALL}")
            
            return False
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error al integrar audio y video: {str(e)}{Style.RESET_ALL}")
        # Intentar recopilar más información sobre el error
        import traceback
        print(f"{Fore.RED}Detalles del error: {traceback.format_exc()}{Style.RESET_ALL}")
        return False

def reproducir_video(ruta_video):
    """Reproduce el video generado"""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(ruta_video)
        else:  # Linux/Mac
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, ruta_video])
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Error al reproducir el video: {str(e)}{Style.RESET_ALL}")
        return False

def integrar_video(historia_id):
    """Flujo completo para integrar video con audio"""
    if not historia_id:
        print(f"{Fore.RED}❌ No hay ninguna historia activa. Primero obtén una historia.{Style.RESET_ALL}")
        input("Presiona Enter para continuar...")
        return False
        
    # Paso 1: Identificar tipo de video
    tipo_video = identificar_tipo_video()
    
    # Paso 2: Preguntar el modo de video
    print(f"{Fore.YELLOW}\n🎬 SELECCIONA EL MODO DE VIDEO{Style.RESET_ALL}")
    print(f"{Fore.CYAN}-" * 70)
    print(f"{Fore.CYAN}1. 🔄 Un solo video en bucle (un video que se repite para cubrir el audio)")
    print(f"{Fore.CYAN}2. 📚 Múltiples videos concatenados (varios videos unidos para cubrir el audio)")
    print(f"{Fore.CYAN}-" * 70)
    
    modo_multiples = False
    while True:
        try:
            opcion_modo = int(input(f"{Fore.YELLOW}Selecciona una opción (1-2): {Style.RESET_ALL}"))
            if 1 <= opcion_modo <= 2:
                modo_multiples = (opcion_modo == 2)
                break
            else:
                print(f"{Fore.RED}❌ Opción no válida. Intenta de nuevo.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}❌ Por favor, ingresa un número válido.{Style.RESET_ALL}")
    
    # Paso 3: Obtener la duración del audio para el modo de múltiples videos
    duracion_audio = None
    if modo_multiples:
        ruta_historia = f"historias/{historia_id}"
        ruta_audio = os.path.join(ruta_historia, "narracion.mp3")
        
        if os.path.exists(ruta_audio):
            try:
                duracion_audio = float(subprocess.check_output([
                    "ffprobe", "-v", "error", "-show_entries",
                    "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
                    ruta_audio
                ]).strip())
                print(f"{Fore.CYAN}ℹ️ Duración del audio: {duracion_audio:.2f} segundos{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️ No se pudo determinar la duración del audio: {str(e)}{Style.RESET_ALL}")
    
    # Paso 4: Descargar video(s)
    if modo_multiples:
        print(f"{Fore.YELLOW}🎥 Descargando múltiples videos para cubrir la duración del audio...{Style.RESET_ALL}")
        rutas_videos = descargar_video(tipo_video, modo_multiples=True, duracion_requerida=duracion_audio)
    else:
        print(f"{Fore.YELLOW}🎥 Descargando un solo video que se repetirá...{Style.RESET_ALL}")
        rutas_videos = descargar_video(tipo_video)
    
    if not rutas_videos:
        print(f"{Fore.RED}❌ No se pudo descargar ningún video.{Style.RESET_ALL}")
        input("Presiona Enter para continuar...")
        return False
        
    # Paso 5: Integrar audio con video(s)
    ruta_video_final = integrar_audio_video(historia_id, rutas_videos, modo_multiples)
    if not ruta_video_final:
        print(f"{Fore.RED}❌ No se pudo integrar el audio con el video.{Style.RESET_ALL}")
        input("Presiona Enter para continuar...")
        return False
        
    # Paso 6: Preguntar si desea reproducir el video
    reproducir = input(f"{Fore.YELLOW}¿Deseas reproducir el video ahora? (s/n): {Style.RESET_ALL}").lower()
    if reproducir == "s":
        reproducir_video(ruta_video_final)
        
    print(f"{Fore.GREEN}✅ Proceso de integración de video completado con éxito.{Style.RESET_ALL}")
    input(f"{Fore.YELLOW}Presiona Enter para continuar...{Style.RESET_ALL}")
    return True
