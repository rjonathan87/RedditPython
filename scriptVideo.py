import os
import sys
from importlib import util

def verificar_dependencias():
    dependencias = ['whisper', 'moviepy']
    faltantes = []
    
    for modulo in dependencias:
        if util.find_spec(modulo) is None:
            faltantes.append(modulo)
    
    if faltantes:
        print("❌ Error: Faltan las siguientes dependencias:")
        print("\n".join(f"- {dep}" for dep in faltantes))
        print("\n📝 Ejecuta:")
        print(f"pip install {' '.join(faltantes)}")
        return False
    return True

# Variable global para controlar el modo de funcionamiento
USAR_OPENCV = False

# Verificar dependencias antes de importar
if not verificar_dependencias():
    print("⚠️ Intentando utilizar OpenCV como alternativa...")
    try:
        import cv2
        USAR_OPENCV = True
        print("✅ OpenCV está disponible. Se utilizará como alternativa a MoviePy.")
    except ImportError:
        print("❌ OpenCV no está disponible. Intente instalar las dependencias:")
        print("pip install moviepy opencv-python")
        sys.exit(1)

try:
    import whisper
    if not USAR_OPENCV:
        try:
            import moviepy.editor as mp
            print("✅ MoviePy importado correctamente.")
        except ImportError as e:
            print(f"❌ Error al importar MoviePy: {str(e)}")
            try:
                import cv2
                USAR_OPENCV = True
                print("✅ Se utilizará OpenCV como alternativa a MoviePy.")
            except ImportError:
                print("❌ OpenCV no está disponible. Se utilizará el video sin subtítulos.")
                sys.exit(1)
except ImportError as e:
    print(f"❌ Error inesperado al importar: {str(e)}")
    print("⚠️ Se utilizará el video sin subtítulos")
    sys.exit(1)

def obtener_texto_narracion(video_path):
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

def crear_subtitulos(video_path, segments, output_path):
    # Si estamos usando OpenCV, llamar a la implementación alternativa
    if USAR_OPENCV:
        # Importar la implementación de OpenCV
        try:
            from opencv_video import crear_subtitulos_opencv
            return crear_subtitulos_opencv(video_path, segments, output_path)
        except ImportError:
            print("❌ No se pudo importar la implementación de OpenCV")
            return False
    
    # Implementación original con MoviePy
    try:
        # Configurar la ruta de ImageMagick
        import moviepy.config as mp_config
        mp_config.change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})
        
        if not segments:
            print("⚠️ No hay segmentos de subtítulos disponibles")
            return False
            
        print("📼 Cargando video...")
        video = mp.VideoFileClip(video_path)
        
        # Obtener dimensiones del video para ajustar subtítulos
        video_width, video_height = video.size
        
        # Función para crear un clip de texto con estilo TikTok
        def crear_clip_texto_tiktok(texto, duracion, tiempo_inicio):
            # Dividir el texto en líneas si es muy largo
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
            
            texto_formateado = "\n".join(lineas)
            
            # Crear clip de texto con estilo TikTok
            txt_clip = mp.TextClip(
                texto_formateado, 
                fontsize=70,  # Tamaño más grande para móviles
                color='white',  # Texto blanco
                font='Arial-Bold',  # Fuente más moderna
                bg_color='rgba(0,0,0,0.8)',  # Fondo negro más opaco
                method='caption',  # Usar método caption para mejor formato
                align='center',  # Centrar texto
                size=(video_width * 0.9, None),  # Ancho del 90% del video, altura automática
                stroke_color='black',  # Borde negro
                stroke_width=1.5  # Grosor del borde
            )
            
            # Añadir padding al clip de texto
            txt_clip = txt_clip.margin(top=10, bottom=10, left=20, right=20, opacity=0)
            
            # Posicionar en el centro horizontal y a 2/3 de la altura (más visible)
            txt_clip = txt_clip.set_position(('center', 0.65), relative=True)
            
            # Añadir efectos de entrada y salida suaves
            txt_clip = txt_clip.set_duration(duracion).set_start(tiempo_inicio)
            txt_clip = txt_clip.crossfadein(0.3).crossfadeout(0.3)
            
            return txt_clip
        
        print("💬 Generando subtítulos estilo TikTok...")
        subtitles = []
        for segment in segments:
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text']
            
            txt_clip = crear_clip_texto_tiktok(text, end_time - start_time, start_time)
            subtitles.append(txt_clip)
        
        print("🎬 Combinando video con subtítulos...")
        final_video = mp.CompositeVideoClip([video] + subtitles)
        
        print("💾 Guardando video final...")
        final_video.write_videofile(output_path, codec='libx264')
        return True
        
    except Exception as e:
        print(f"❌ Error al crear subtítulos: {str(e)}")
        return False
    finally:
        try:
            video.close()
        except:
            pass

def main(video_path, output_path):
    try:
        print("📖 Obteniendo texto de la narración...")
        segments = obtener_texto_narracion(video_path)
        
        if segments is None:
            print("⚠️ No se pudo transcribir el audio")
            return False
            
        if not crear_subtitulos(video_path, segments, output_path):
            print("⚠️ Se utilizará el video sin subtítulos")
            # Copiar el video original como respaldo
            import shutil
            shutil.copy2(video_path, output_path)
            
        print("✅ Proceso completado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en el proceso principal: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            print("Uso: python scriptVideo.py <video_path> <output_path>")
        else:
            print("Ejecutando scriptVideo.py...")
            video_path = sys.argv[1]
            output_path = sys.argv[2]
            main(video_path, output_path)
    except Exception as e:
        print(f"Error en scriptVideo.py: {e}")
        sys.exit(1)
