import os
import sys
import json
import subprocess
from colorama import Fore, Style
import shutil

# Importar funciones de otros módulos
from video_integrator_new import verificar_ffmpeg, identificar_tipo_video, descargar_video

def obtener_duracion_audio(ruta_audio):
    """
    Obtiene la duración de un archivo de audio en segundos
    """
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', 
           '-show_format', ruta_audio]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except Exception as e:
        print(f"❌ Error al obtener duración del audio: {e}")
        return None

def integrar_audio_video(ruta_video, ruta_audio, ruta_salida):
    """
    Integra un archivo de audio con un video
    """
    comando = [
        'ffmpeg', '-y',
        '-i', ruta_video,
        '-i', ruta_audio,
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-shortest',
        ruta_salida
    ]
    
    try:
        subprocess.run(comando, check=True)
        return True
    except Exception as e:
        print(f"❌ Error al integrar audio y video: {e}")
        return False

def integrar_videos_segmentados(historia_id):
    """
    Integra videos para cada segmento de audio
    """
    if not verificar_ffmpeg():
        return False
    
    ruta_historia = f"historias/{historia_id}"
    carpeta_segmentos_audio = f"{ruta_historia}/segmentos_audio"
    
    # Verificar si existen los segmentos de audio
    if not os.path.exists(carpeta_segmentos_audio):
        print(f"{Fore.RED}❌ No se encontraron segmentos de audio para esta historia.")
        print(f"❗ Asegúrate de haber generado los segmentos primero.{Style.RESET_ALL}")
        return False
    
    # Crear carpeta para los videos segmentados
    carpeta_videos_segmentados = f"{ruta_historia}/videos_segmentados"
    os.makedirs(carpeta_videos_segmentados, exist_ok=True)
    
    # Leer metadata de los segmentos de audio
    try:
        with open(f"{ruta_historia}/metadata_audio.json", "r", encoding="utf-8") as f:
            metadata_audio = json.load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}❌ No se encontró el archivo de metadata de audio.{Style.RESET_ALL}")
        return False
    
    segmentos_audio = metadata_audio.get("segmentos_audio", [])
    if not segmentos_audio:
        print(f"{Fore.RED}❌ No hay información sobre los segmentos de audio.{Style.RESET_ALL}")
        return False
    
    # Preguntar por el tipo de video a utilizar
    tipo_video = identificar_tipo_video()
    
    # Metadata para los videos generados
    videos_generados = []
    
    # Procesar cada segmento de audio
    for i, nombre_segmento in enumerate(segmentos_audio):
        print(f"{Fore.YELLOW}🔄 Procesando segmento {i+1} de {len(segmentos_audio)}{Style.RESET_ALL}")
        
        ruta_audio = os.path.join(carpeta_segmentos_audio, nombre_segmento)
        
        # Obtener duración del audio
        duracion_audio = obtener_duracion_audio(ruta_audio)
        if not duracion_audio:
            print(f"{Fore.RED}❌ No se pudo obtener la duración del audio: {ruta_audio}{Style.RESET_ALL}")
            continue
        
        # Descargar un video para este segmento
        print(f"{Fore.CYAN}📥 Descargando video para el segmento {i+1}...{Style.RESET_ALL}")
        ruta_video_descargado = descargar_video(tipo_video, duracion_minima=duracion_audio + 10)
        
        if not ruta_video_descargado:
            print(f"{Fore.RED}❌ No se pudo descargar video para el segmento {i+1}.{Style.RESET_ALL}")
            continue
        
        # Nombre del archivo de salida
        nombre_video_salida = f"video_parte_{i+1}.mp4"
        ruta_video_salida = os.path.join(carpeta_videos_segmentados, nombre_video_salida)
        
        # Integrar audio y video
        print(f"{Fore.CYAN}🔄 Integrando audio y video para el segmento {i+1}...{Style.RESET_ALL}")
        if integrar_audio_video(ruta_video_descargado, ruta_audio, ruta_video_salida):
            print(f"{Fore.GREEN}✅ Video para segmento {i+1} generado correctamente: {ruta_video_salida}{Style.RESET_ALL}")
            videos_generados.append(nombre_video_salida)
        else:
            print(f"{Fore.RED}❌ Error al generar video para segmento {i+1}.{Style.RESET_ALL}")
        
        # Eliminar el video descargado para ahorrar espacio
        if os.path.exists(ruta_video_descargado):
            os.remove(ruta_video_descargado)
    
    # Guardar metadata de los videos generados
    if videos_generados:
        metadata_videos = {
            "titulo": metadata_audio.get("titulo", "Sin título"),
            "videos_segmentados": videos_generados,
            "tipo_video": tipo_video
        }
        
        with open(f"{ruta_historia}/metadata_videos.json", "w", encoding="utf-8") as f:
            json.dump(metadata_videos, f, ensure_ascii=False, indent=4)
        
        print(f"{Fore.GREEN}✅ Se generaron {len(videos_generados)} videos segmentados.{Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.RED}❌ No se pudo generar ningún video segmentado.{Style.RESET_ALL}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        historia_id = sys.argv[1]
        integrar_videos_segmentados(historia_id)
    else:
        print("Uso: python video_integrator_segmentos.py <historia_id>")
