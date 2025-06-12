# scriptVideo.py  – v2 sin MoviePy
import os
import tempfile
import subprocess
import requests
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

# ---------- constructor principal --------------------------------------- #
def crear_video(historia_id: str) -> str:
    """Crea video.mp4 en la carpeta historias/<id> usando clips de Pexels."""
    ruta = f'historias/{historia_id}'
    texto_path   = os.path.join(ruta, 'historia.txt')
    audio_path   = os.path.join(ruta, 'narracion.mp3')    
    salida_final = os.path.join(ruta, 'video.mp4')
    
    if not (os.path.exists(texto_path) and os.path.exists(audio_path)):
        raise FileNotFoundError("Faltan historia.txt o narracion.mp3")
        
    with open(texto_path, encoding='utf-8') as f:
        texto = f.read()

    api = Pexels(PEXELS_KEY)
    clips = []
    for kw in _keywords(texto, 6):
        videos = api.search_videos(query=kw, page=1, per_page=3)
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
         audio_path]).strip())

    # 3) loopear video hasta cubrir audio
    loop_mp4 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
    subprocess.run(
        ["ffmpeg", "-y", "-stream_loop", "-1", "-i", concat_mp4,
         "-t", str(dur_audio), "-c", "copy", loop_mp4],
        check=True
    )

    # 4) silenciar y poner narración
    subprocess.run(
        ["ffmpeg", "-y", "-i", loop_mp4, "-i", audio_path,
         "-c:v", "copy", "-c:a", "aac", "-shortest", salida_final],
        check=True
    )
    print(f"✅ Video generado: {salida_final}")
    return salida_final