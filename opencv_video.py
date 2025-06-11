"""
Video Subtitle Generator - OpenCV Version

Este script procesa videos y agrega subtítulos usando OpenCV en lugar de MoviePy.
Se utiliza como alternativa cuando hay problemas con la importación de moviepy.editor.
"""

import os
import sys
import cv2
import numpy as np
import subprocess
from importlib import util

def verificar_dependencias():
    dependencias = ['cv2', 'numpy', 'whisper']
    faltantes = []
    
    for modulo in dependencias:
        if util.find_spec(modulo) is None:
            faltantes.append(modulo)
    
    if faltantes:
        print("❌ Error: Faltan las siguientes dependencias:")
        print("\n".join(f"- {dep}" for dep in faltantes))
        print("\n📝 Ejecuta:")
        
        # Mapeo de módulos a paquetes pip
        paquetes = {
            'cv2': 'opencv-python',
            'numpy': 'numpy',
            'whisper': 'whisper'
        }
        
        paquetes_instalar = [paquetes.get(dep, dep) for dep in faltantes]
        print(f"pip install {' '.join(paquetes_instalar)}")
        return False
    return True

# Verificar dependencias antes de importar
if not verificar_dependencias():
    sys.exit(1)

try:
    import whisper
except ImportError as e:
    print(f"❌ Error inesperado al importar: {str(e)}")
    print("⚠️ Se utilizará el video sin subtítulos")
    sys.exit(1)

def obtener_texto_narracion(video_path):
    """
    Obtiene el texto de narración a partir del archivo de texto asociado.
    Divide el texto en segmentos para los subtítulos.
    """
    try:
        # Obtener la ruta del archivo de texto
        dir_path = os.path.dirname(video_path)
        txt_path = os.path.join(dir_path, "historia.txt")
        
        # Leer el archivo de texto
        with open(txt_path, 'r', encoding='utf-8') as f:
            texto = f.read()
        
        # Dividir el texto en segmentos más naturales (por puntos, comas, etc.)
        import re
        # Dividir por puntos, puntos y comas, dos puntos, signos de interrogación y exclamación
        frases = re.split(r'([.!?;:])', texto)
        
        # Reconstruir las frases con sus signos de puntuación
        frases_completas = []
        for i in range(0, len(frases)-1, 2):
            if i+1 < len(frases):
                frases_completas.append(frases[i] + frases[i+1])
            else:
                frases_completas.append(frases[i])
        
        # Si quedó alguna frase suelta al final
        if len(frases) % 2 != 0:
            frases_completas.append(frases[-1])
        
        # Filtrar frases vacías
        frases_completas = [f.strip() for f in frases_completas if f.strip()]
        
        # Para frases muy largas, dividirlas en segmentos más pequeños
        segmentos_finales = []
        for frase in frases_completas:
            palabras = frase.split()
            # Si la frase tiene más de 15 palabras, dividirla
            if len(palabras) > 15:
                for i in range(0, len(palabras), 15):
                    segmento = ' '.join(palabras[i:i+15])
                    segmentos_finales.append(segmento)
            else:
                segmentos_finales.append(frase)
        
        # Asignar tiempos aproximados (ajustar según la longitud del segmento)
        segmentos = []
        tiempo_actual = 0
        for segmento in segmentos_finales:
            # Calcular duración basada en la cantidad de palabras (aprox. 0.3 segundos por palabra)
            palabras = len(segmento.split())
            duracion = max(2, min(palabras * 0.3, 5))  # Entre 2 y 5 segundos
            
            segmentos.append({
                'start': tiempo_actual,
                'end': tiempo_actual + duracion,
                'text': segmento
            })
            tiempo_actual += duracion
            
        return segmentos
    except Exception as e:
        print(f"❌ Error al obtener la narración: {str(e)}")
        return None

def crear_subtitulos_opencv(video_path, segments, output_path):
    """
    Crea subtítulos en el video usando OpenCV en lugar de MoviePy.
    """
    try:
        if not segments:
            print("⚠️ No hay segmentos de subtítulos disponibles")
            return False
            
        print("📼 Cargando video...")
        # Abrir el video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Error al abrir el video")
            return False
            
        # Obtener propiedades del video
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Configurar el escritor de video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Códec
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Procesar cada frame
        frame_number = 0
        print(f"🎞️ Procesando {total_frames} frames...")
        
        # Mostrar una barra de progreso simple
        progress_interval = total_frames // 20  # Actualizar cada 5%
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Calcular el tiempo actual en segundos
            tiempo_actual = frame_number / fps
            
            # Buscar subtítulos para este tiempo
            subtitulos_actuales = [
                s for s in segments 
                if s['start'] <= tiempo_actual <= s['end']
            ]
            
            # Agregar subtítulos al frame
            if subtitulos_actuales:
                for subtitulo in subtitulos_actuales:
                    # Preparar el texto (dividir en líneas si es muy largo)
                    texto = subtitulo['text']
                    palabras = texto.split()
                    lineas = []
                    linea_actual = ""
                    
                    for palabra in palabras:
                        if len(linea_actual + " " + palabra) <= 30:  # Máximo ~30 caracteres por línea
                            linea_actual += " " + palabra if linea_actual else palabra
                        else:
                            lineas.append(linea_actual)
                            linea_actual = palabra
                    
                    if linea_actual:
                        lineas.append(linea_actual)
                    
                    # Agregar cada línea al frame
                    y_pos = int(height * 0.65)  # Posición vertical (65% desde arriba)
                    
                    # Dibujar fondo semi-transparente para mejorar legibilidad
                    for i, linea in enumerate(lineas):
                        # Obtener tamaño del texto
                        text_size = cv2.getTextSize(linea, cv2.FONT_HERSHEY_DUPLEX, 1.0, 2)[0]
                        text_x = (width - text_size[0]) // 2  # Centrar texto
                        text_y = y_pos + i * 40  # Espacio entre líneas
                        
                        # Dibujar rectángulo de fondo
                        overlay = frame.copy()
                        cv2.rectangle(
                            overlay,
                            (text_x - 10, text_y - 30),  # Punto superior izquierdo
                            (text_x + text_size[0] + 10, text_y + 10),  # Punto inferior derecho
                            (0, 0, 0),  # Color negro
                            -1  # Rellenar
                        )
                        
                        # Aplicar transparencia
                        alpha = 0.7  # Transparencia (0-1)
                        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
                        
                        # Dibujar texto con borde para mejor visibilidad
                        # Borde (sombra)
                        cv2.putText(
                            frame, linea, (text_x - 1, text_y - 1),
                            cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 0), 2
                        )
                        # Texto principal
                        cv2.putText(
                            frame, linea, (text_x, text_y),
                            cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2
                        )
            
            # Escribir el frame modificado
            out.write(frame)
            
            # Actualizar contador
            frame_number += 1
            
            # Mostrar progreso
            if frame_number % progress_interval == 0 or frame_number == 1:
                progress = (frame_number / total_frames) * 100
                print(f"⏳ Progreso: {progress:.1f}% ({frame_number}/{total_frames})")
        
        # Liberar recursos
        cap.release()
        out.release()
        
        print(f"✅ Video con subtítulos guardado en: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear subtítulos con OpenCV: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def analizar_video_con_whisper(video_path):
    """
    Analiza el audio del video con Whisper para obtener la transcripción.
    """
    try:
        print("🔊 Extrayendo audio del video...")
        audio_path = video_path.replace('.mp4', '.wav')
        
        # Usar ffmpeg para extraer el audio
        cmd = [
            'ffmpeg', '-i', video_path, 
            '-q:a', '0', '-map', 'a', audio_path, 
            '-y'  # Sobrescribir si existe
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("🧠 Analizando audio con Whisper...")
        model = whisper.load_model("small")  # Cargar modelo pequeño para rapidez
        result = model.transcribe(audio_path)
        
        # Convertir el resultado en el formato esperado por nuestra función
        segments = []
        for segment in result["segments"]:
            segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text']
            })
        
        # Limpiar el archivo de audio temporal
        os.remove(audio_path)
        
        return segments
    except Exception as e:
        print(f"❌ Error al analizar el video con Whisper: {str(e)}")
        return None

def procesar_video(video_path, output_dir=None, usar_narracion=True):
    """
    Procesa un video agregando subtítulos.
    """
    try:
        # Verificar que el archivo exista
        if not os.path.exists(video_path):
            print(f"❌ El archivo {video_path} no existe")
            return False
        
        # Determinar directorio de salida
        if output_dir is None:
            output_dir = os.path.dirname(video_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Definir ruta de salida
        base_name = os.path.basename(video_path)
        output_path = os.path.join(output_dir, f"subtitulado_{base_name}")
        
        # Obtener los segmentos de texto
        print("📝 Obteniendo segmentos de texto...")
        segments = None
        
        if usar_narracion:
            # Intentar usar el texto de narración
            segments = obtener_texto_narracion(video_path)
        
        if segments is None:
            print("🔄 Usando Whisper para generar subtítulos...")
            segments = analizar_video_con_whisper(video_path)
            
        if segments is None:
            print("❌ No se pudieron obtener subtítulos")
            return False
        
        # Crear video con subtítulos
        print("🎬 Creando video con subtítulos...")
        resultado = crear_subtitulos_opencv(video_path, segments, output_path)
        
        if resultado:
            print(f"✅ Video procesado exitosamente: {output_path}")
            return output_path
        else:
            print("❌ Error al procesar el video")
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Función principal para usar desde línea de comandos
def main():
    if len(sys.argv) < 2:
        print("❌ Error: Debe proporcionar la ruta al video")
        print("📝 Uso: python opencv_video.py [ruta_al_video]")
        return
        
    video_path = sys.argv[1]
    procesar_video(video_path)

if __name__ == "__main__":
    main()
