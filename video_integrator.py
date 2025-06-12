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
        from pexels.api import API
        pexels_module = "pexels-api"
    
    from dotenv import load_dotenv
    
    load_dotenv()
    
    PEXELS_KEY = os.getenv('PEXELS_API_KEY') or os.getenv('PEXEL_API_KEY')
    if not PEXELS_KEY:
        raise EnvironmentError("Variable PEXELS_API_KEY no definida en .env")
    
    if pexels_module == "pexelsapi":
        api = Pexels(PEXELS_KEY)
        videos = api.search_videos(query=tipo_video, page=1, per_page=5)
    else:
        api = API(PEXELS_KEY)
        videos = api.search_videos(query=tipo_video, page=1, per_page=5)
        # Adaptar el formato de respuesta si es necesario
        if "videos" not in videos and "media" in videos:
            videos["videos"] = videos["media"]
    
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
        
        # 2) Loopear video hasta cubrir audio si es necesario
        loop_mp4 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        subprocess.run([
            "ffmpeg", "-y", "-stream_loop", "-1", "-i", ruta_video_temp,
            "-t", str(dur_audio), "-c", "copy", loop_mp4
        ], check=True)
        
        # 3) Silenciar video y poner narración
        subprocess.run([
            "ffmpeg", "-y", "-i", loop_mp4, "-i", ruta_audio,
            "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0",
            "-shortest", ruta_video_final
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

def integrar_video(historia_id):
    """Flujo completo para integrar video con audio"""
    if not historia_id:
        print(f"{Fore.RED}❌ No hay ninguna historia activa. Primero obtén una historia.{Style.RESET_ALL}")
        input("Presiona Enter para continuar...")
        return False
        
    # Paso 1: Identificar tipo de video
    tipo_video = identificar_tipo_video()
    
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
