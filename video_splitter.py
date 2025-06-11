import os
import subprocess
import sys
import json


def verificar_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        print("❌ FFmpeg no está instalado. Por favor, instala FFmpeg primero.")
        print("📝 Guía de instalación: https://ffmpeg.org/download.html")
        return False

def obtener_duracion_video(ruta_video):
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', 
           '-show_format', ruta_video]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except Exception as e:
        print(f"❌ Error al obtener duración del video: {e}")
        return None

def mostrar_progreso(porcentaje, mensaje="Progreso"):
    barra = "#" * int(porcentaje // 2) + "-" * (50 - int(porcentaje // 2))
    print(f"\r{mensaje}: [{barra}] {porcentaje:.2f}%", end="")

def obtener_ultima_historia():
    """
    Identifica la última historia generada basándose en la fecha de modificación
    de las carpetas en el directorio historias/
    """
    try:
        if not os.path.exists("historias"):
            print("❌ No hay historias generadas.")
            return None

        historias = []
        for historia_id in os.listdir("historias"):
            ruta = os.path.join("historias", historia_id)
            if os.path.isdir(ruta):
                timestamp = os.path.getmtime(ruta)
                historias.append((historia_id, timestamp))

        if not historias:
            print("❌ No se encontraron historias.")
            return None

        ultima_historia = sorted(historias, key=lambda x: x[1], reverse=True)[0][0]
        return ultima_historia

    except Exception as e:
        print(f"❌ Error al buscar la última historia: {e}")
        return None

def ajustar_duraciones(duracion_total, num_segmentos, min_duracion=60):
    """
    Ajusta las duraciones de los segmentos para que ninguno sea menor a min_duracion segundos
    """
    duracion_por_segmento = duracion_total / num_segmentos
    if duracion_por_segmento < min_duracion:
        # Si los segmentos son muy cortos, reducir el número de segmentos
        num_segmentos = int(duracion_total / min_duracion)
        duracion_por_segmento = duracion_total / num_segmentos
    
    # Verificar si el último segmento sería menor a 1 minuto
    ultimo_segmento = duracion_total - (duracion_por_segmento * (num_segmentos - 1))
    if ultimo_segmento < min_duracion and num_segmentos > 1:
        # Distribuir el tiempo del último segmento entre los demás
        tiempo_extra = ultimo_segmento / (num_segmentos - 1)
        duracion_por_segmento += tiempo_extra
        num_segmentos -= 1
    
    return duracion_por_segmento, num_segmentos

def dividir_video(historia_id):
    if not verificar_ffmpeg():
        return False

    try:
        ruta_historia = f"historias/{historia_id}"
        
        # Encontrar el archivo de video (con o sin subtítulos)
        archivos_video = [f for f in os.listdir(ruta_historia) if f.endswith('.mp4')]
        if not archivos_video:
            print("❌ No se encontró ningún archivo de video")
            return False
            
        archivo_video = next((f for f in archivos_video if '_subtitulos.mp4' in f), archivos_video[0])
        ruta_video = os.path.join(ruta_historia, archivo_video)
        
        duracion_total = obtener_duracion_video(ruta_video)
        if not duracion_total:
            return False

        duracion_deseada = 120  # 2 minutos en segundos
        num_segmentos = max(1, int(duracion_total / duracion_deseada))
        duracion_por_segmento, num_segmentos = ajustar_duraciones(duracion_total, num_segmentos)
        
        dir_segmentos = os.path.join(ruta_historia, "segmentos")
        os.makedirs(dir_segmentos, exist_ok=True)
        
        for i in range(num_segmentos):
            inicio = i * duracion_por_segmento
            fin = inicio + duracion_por_segmento if i < num_segmentos - 1 else duracion_total
            
            nombre_segmento = f"segmento_{i + 1}.mp4"
            ruta_segmento = os.path.join(dir_segmentos, nombre_segmento)
            
            cmd = [
                'ffmpeg', '-y', '-i', ruta_video,
                '-ss', str(inicio),
                '-t', str(fin - inicio),
                '-c', 'copy',
                ruta_segmento
            ]
            
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            porcentaje = ((i + 1) / num_segmentos) * 100
            mostrar_progreso(porcentaje, "Dividiendo video")
        
        print(f"\n✅ Video dividido en {num_segmentos} segmentos")
        return True
        
    except Exception as e:
        print(f"❌ Error al dividir el video: {str(e)}")
        return False
