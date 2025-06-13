import os
import sys
import json
import urllib.request
def descargar_video(tipo_video, duracion_minima=60):
    """Descarga un video de stock gratuito según el tipo seleccionado"""
    print(f"{Fore.YELLOW}🔍 Buscando videos de '{tipo_video}'...{Style.RESET_ALL}")
    
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

def identificar_tipo_video(aleatorio=False):
    """Muestra las opciones para seleccionar el tipo de video a descargar
    
    Args:
        aleatorio: Si es True, selecciona un tipo de video al azar
                  Si es False, muestra el menú para que el usuario elija
    """
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
    
    if aleatorio:
        import random
        opcion = random.randint(1, 10)
        print(f"{Fore.YELLOW}🎲 Seleccionando tipo de video aleatorio: {Fore.CYAN}{opcion}. {list(tipos_video.values())[opcion-1]}{Style.RESET_ALL}")
        return tipos_video[opcion]
    
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
                return tipos_video[opcion]
            else:
                print(f"{Fore.RED}❌ Opción no válida. Intenta de nuevo.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}❌ Por favor, ingresa un número válido.{Style.RESET_ALL}")

def descargar_video(tipo_video, duracion_minima=60):
    """Descarga un video de stock gratuito según el tipo seleccionado"""    
    print(f"{Fore.YELLOW}🔍 Buscando videos de '{tipo_video}'...{Style.RESET_ALL}")
      # Usar Pexels API para buscar videos
    # Primero intentamos con pexelsapi
    try:
        from pexelsapi.pexels import Pexels
        pexels_module = "pexelsapi"
    except ImportError:
        # Si falla, intentamos con pexels-api
        print(f"{Fore.YELLOW}⚠️ No se encontró pexelsapi. Intentando con pexels-api...{Style.RESET_ALL}")
    
    from dotenv import load_dotenv
    
    load_dotenv()
    
    PEXELS_KEY = os.getenv('PEXELS_API_KEY') or os.getenv('PEXEL_API_KEY')
    if not PEXELS_KEY:
        raise EnvironmentError("Variable PEXELS_API_KEY no definida en .env")
        
    # Buscar videos en orientación vertical para TikTok
    orientacion = "portrait"
    
    if pexels_module == "pexelsapi":
        api = Pexels(PEXELS_KEY)
        videos = api.search_videos(query=tipo_video, orientation=orientacion, page=1, per_page=5)
    else:
        print(f"{Fore.YELLOW}⚠️ Usando pexels-api como alternativa...{Style.RESET_ALL}")
        # api = API(PEXELS_KEY)
        # videos = api.search_videos(query=tipo_video, orientation=orientacion, page=1, per_page=5)
        # # Adaptar el formato de respuesta si es necesario
        # if "videos" not in videos and "media" in videos:
        #     videos["videos"] = videos["media"]
    
    if not videos or not videos.get('videos'):
        print(f"{Fore.RED}❌ No se encontraron videos para '{tipo_video}'.{Style.RESET_ALL}")
        return None
        
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

def integrar_audio_video(historia_id, ruta_video_temp):
    """Integra el audio de la narración con el video descargado"""
    if not verificar_ffmpeg():
        return False
        
    try:
        ruta_historia = f"historias/{historia_id}"
        ruta_audio = os.path.join(ruta_historia, "narracion.mp3")
        ruta_video_final = os.path.join(ruta_historia, "video_integrado.mp4")
        
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
        
        print(f"{Fore.CYAN}ℹ️ Duración del audio: {dur_audio:.2f} segundos{Style.RESET_ALL}")
        
        # Añadir un margen de seguridad para evitar que el video se corte antes que el audio
        dur_audio_con_margen = dur_audio + 5.0  # Aumentamos el margen a 5 segundos
          # 2) Loopear video hasta cubrir audio si es necesario
        loop_mp4 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        print(f"{Fore.CYAN}ℹ️ Creando video en bucle con duración {dur_audio_con_margen:.2f} segundos...{Style.RESET_ALL}")
        subprocess.run([
            "ffmpeg", "-y", "-stream_loop", "-1", "-i", ruta_video_temp,
            "-t", str(dur_audio_con_margen), 
            # No usamos -c copy para evitar problemas de compatibilidad
            "-c:v", "libx264", "-preset", "ultrafast",
            loop_mp4
        ], check=True)
        
        # Verificar duración del video en bucle
        dur_loop = float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            loop_mp4
        ]).strip())
        print(f"{Fore.CYAN}ℹ️ Duración del video en bucle: {dur_loop:.2f} segundos{Style.RESET_ALL}")# Convertir a formato vertical para TikTok
        loop_mp4_vertical = convertir_a_vertical(loop_mp4)
          # 3) Silenciar video y poner narración completa
        # Verificamos duraciones antes de procesar
        dur_video = float(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            loop_mp4_vertical
        ]).strip())
        
        print(f"{Fore.CYAN}ℹ️ Duración del video procesado: {dur_video:.2f} segundos{Style.RESET_ALL}")
        print(f"{Fore.CYAN}ℹ️ Duración del audio original: {dur_audio:.2f} segundos{Style.RESET_ALL}")
        
        # Usamos un enfoque diferente: NO usamos -shortest ni -c:v copy para que no se corten streams
        subprocess.run([
            "ffmpeg", "-y", 
            "-i", loop_mp4_vertical, 
            "-i", ruta_audio,
            "-map", "0:v:0", 
            "-map", "1:a:0", 
            "-c:a", "aac",
            "-c:v", "libx264", 
            "-preset", "medium",
            # Aseguramos que dure exactamente lo mismo que el audio original
            "-t", str(dur_audio),
            ruta_video_final
        ], check=True)
        
        print(f"{Fore.GREEN}✅ Video con audio integrado generado: {ruta_video_final}{Style.RESET_ALL}")
        return ruta_video_final
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error al integrar audio y video: {str(e)}{Style.RESET_ALL}")
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

def integrar_video(historia_id, aleatorio=True):
    """Flujo completo para integrar video con audio
    
    Args:
        historia_id: ID de la historia a procesar
        aleatorio: Si es True, selecciona un tipo de video al azar
    """
    if not historia_id:
        print(f"{Fore.RED}❌ No hay ninguna historia activa. Primero obtén una historia.{Style.RESET_ALL}")
        input("Presiona Enter para continuar...")
        return False
        
    # Paso 1: Identificar tipo de video
    tipo_video = identificar_tipo_video(aleatorio)
    
    # Paso 2: Descargar video
    ruta_video_temp = descargar_video(tipo_video)
    if not ruta_video_temp:
        print(f"{Fore.RED}❌ No se pudo descargar el video.{Style.RESET_ALL}")
        input("Presiona Enter para continuar...")
        return False
        
    # Paso 3: Integrar audio con video
    ruta_video_final = integrar_audio_video(historia_id, ruta_video_temp)
    if not ruta_video_final:
        print(f"{Fore.RED}❌ No se pudo integrar el audio con el video.{Style.RESET_ALL}")
        input("Presiona Enter para continuar...")
        return False
        
    # Paso 4: Preguntar si desea reproducir el video
    reproducir = input(f"{Fore.YELLOW}¿Deseas reproducir el video ahora? (s/n): {Style.RESET_ALL}").lower()
    if reproducir == "s":
        reproducir_video(ruta_video_final)
        
    print(f"{Fore.GREEN}✅ Proceso de integración de video completado con éxito.{Style.RESET_ALL}")
    input(f"{Fore.YELLOW}Presiona Enter para continuar...{Style.RESET_ALL}")
    return True
