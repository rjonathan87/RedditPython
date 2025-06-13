# scriptVideo.py  – v2 sin MoviePy
import os
import tempfile
import subprocess
import requests
import json
import nltk
from pexelsapi.pexels import Pexels
from dotenv import load_dotenv

load_dotenv()                                    # .env con PEXELS_API_KEY
nltk.download('punkt', quiet=True)               # 1ª vez descarga corpora
nltk.download('stopwords', quiet=True)


PEXELS_KEY = os.getenv('PEXELS_API_KEY') or os.getenv('PEXEL_API_KEY')
if not PEXELS_KEY:
    raise EnvironmentError("Variable PEXELS_API_KEY no definida en .env")

# ---------- utilidades -------------------------------------------------- #
def _keywords(text: str, n: int = 5) -> list[str]:
    tokens = [t.lower() for t in nltk.word_tokenize(text) if t.isalpha()]
    stop = set(nltk.corpus.stopwords.words('spanish'))
    fdist = nltk.FreqDist([t for t in tokens if t not in stop])
    return [w for w, _ in fdist.most_common(n)] or ['misterio', 'sótano']

def _download(video_obj) -> str:
    # La estructura de los videos ha cambiado en la nueva API
    video_files = video_obj.get('video_files', [])
    if not video_files:
        raise ValueError("No se encontraron archivos de video")
    
    # Encontrar el archivo con mayor resolución
    best = max(video_files, key=lambda f: f.get('width', 0))
    path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
    with requests.get(best.get('link'), stream=True) as r, open(path, 'wb') as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    return path

def _convertir_a_vertical(ruta_video_input):
    """Convierte un video horizontal a formato vertical para TikTok (9:16)"""
    try:
        # Crear un nombre para el archivo temporal de salida
        video_vertical = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        
        print(f"ℹ️ Convirtiendo video a formato vertical para TikTok...")
        
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
        
        print(f"ℹ️ Dimensiones originales del video: {width}x{height}")
        
        # Calcular dimensiones para formato vertical 9:16
        # Si el video ya es vertical, lo dejamos como está
        if height > width:
            print(f"ℹ️ El video ya está en formato vertical. Manteniendo dimensiones originales.")
            return ruta_video_input
        
        # Para videos horizontales, recortamos del centro y redimensionamos
        new_height = height
        new_width = int(height * 9 / 16)  # Relación de aspecto 9:16
        
        # Calcular el punto de inicio para el recorte centrado
        x_center = width / 2
        crop_x = max(0, int(x_center - new_width / 2))
        
        print(f"ℹ️ Recortando a: {new_width}x{new_height}, desde X={crop_x}")
          # Comando FFmpeg para recortar y redimensionar
        subprocess.run([
            "ffmpeg", "-y", "-i", ruta_video_input,
            "-vf", f"crop={new_width}:{new_height}:{crop_x}:0,scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k", video_vertical
        ], check=True)
        print(f"✅ Video convertido a formato vertical (9:16) para TikTok")
        
        # Verificar dimensiones del video generado
        info_cmd = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "json", video_vertical
        ]
        
        info_result = subprocess.run(info_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        video_info = json.loads(info_result.stdout)
        
        # Extraer dimensiones
        width_final = int(video_info['streams'][0]['width'])
        height_final = int(video_info['streams'][0]['height'])
        
        print(f"ℹ️ Dimensiones finales del video: {width_final}x{height_final}")
        
        return video_vertical
    
    except Exception as e:
        print(f"❌ Error al convertir video a formato vertical: {str(e)}")
        # Si falla, devolvemos el video original
        return ruta_video_input

# ---------- constructor principal --------------------------------------- #
def crear_video(historia_id: str) -> str:
    """Crea video.mp4 en la carpeta historias/<id> usando clips de Pexels."""
    ruta = f'historias/{historia_id}'
    texto_path   = os.path.join(ruta, 'historia.txt')
    audio_path   = os.path.join(ruta, 'narracion.mp3')    
    salida_final = os.path.join(ruta, 'video.mp4')
    
    if not (os.path.exists(texto_path) and os.path.exists(audio_path)):
        raise FileNotFoundError("Faltan historia.txt o narracion.mp3")
    
    # Verificar permisos de escritura
    try:
        test_file = os.path.join(ruta, "test_write.tmp")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print(f"✅ Permisos de escritura verificados en: {ruta}")
    except Exception as e:
        print(f"❌ Error de permisos en la carpeta: {str(e)}")
        return None
        
    with open(texto_path, encoding='utf-8') as f:
        texto = f.read()    api = Pexels(PEXELS_KEY)
    clips = []
    for kw in _keywords(texto, 6):
        videos = api.search_videos(query=kw, orientation="portrait", page=1, per_page=3)
        if videos and videos.get('videos'):
            for video in videos['videos']:
                clips.append(_download(video))
                break  # Solo tomamos el primer video de cada búsqueda
        if len(clips) >= 3:
            break
    if not clips:
        raise RuntimeError("No se encontraron vídeos en Pexels")

    # 1) concatenar clips
    concat_txt = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt')
    for c in clips:
        concat_txt.write(f"file '{c}'\n")
    concat_txt.close()
    concat_mp4 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt.name,
         "-c", "copy", concat_mp4],
        check=True
    )

    # 2) averiguar duración del audio
    dur_audio = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
         audio_path]).strip())    # 3) loopear video hasta cubrir audio
    loop_mp4 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
    subprocess.run(
        ["ffmpeg", "-y", "-stream_loop", "-1", "-i", concat_mp4,
         "-t", str(dur_audio), "-c", "copy", loop_mp4],
        check=True
    )
    
    # Convertir a formato vertical para TikTok
    loop_mp4_vertical = _convertir_a_vertical(loop_mp4)    # 4) silenciar y poner narración    # Usamos libx264 en lugar de copy para evitar problemas de compatibilidad
    subprocess.run(
        ["ffmpeg", "-y", "-i", loop_mp4_vertical, "-i", audio_path,
         "-c:v", "libx264", "-preset", "medium", "-c:a", "aac", "-shortest", salida_final],
        check=True
    )
    
    # Verificar explícitamente que el archivo se ha creado
    if os.path.exists(salida_final):
        print(f"✅ Video generado: {salida_final}")
        print(f"ℹ️ Tamaño del archivo: {os.path.getsize(salida_final) / (1024*1024):.2f} MB")
        return salida_final
    else:
        print(f"❌ ERROR: El archivo de video no se creó en la ruta: {salida_final}")
        return None