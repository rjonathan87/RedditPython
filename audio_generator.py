import os
import spacy
import re
from edge_tts import Communicate
import asyncio
import json

nlp = spacy.load("es_core_news_sm")

def detectar_genero(texto):
    """
    Detecta el género del narrador basado en el texto utilizando spaCy.
    """
    doc = nlp(texto)
    pronombres_masculinos = ["él", "su", "suyo", "suyos", "hombre", "señor", "chico"]
    pronombres_femeninos = ["ella", "su", "suya", "suyas", "mujer", "señora", "chica"]

    contador_masculino = sum(1 for token in doc if token.text.lower() in pronombres_masculinos)
    contador_femenino = sum(1 for token in doc if token.text.lower() in pronombres_femeninos)

    return "femenino" if contador_femenino > contador_masculino else "masculino"

def limpiar_texto_para_audio(texto):
    """
    Limpia el texto de marcadores y símbolos no deseados para el audio
    """
    # Eliminar marcadores de formato
    texto = texto.replace("[Texto mejorado aquí]", "")
    texto = texto.replace("[Título mejorado]", "")
    texto = texto.replace("[", "")
    texto = texto.replace("]", "")
    texto = texto.replace("*", "")
    texto = texto.replace("#", "")
    texto = texto.replace(">", "")
    texto = texto.replace("-", "")
    texto = texto.replace("Texto mejorado:", "")
    texto = texto.replace("Título mejorado:", "")
    
    # Eliminar líneas de metadata específicas
    lineas = texto.splitlines()
    lineas_filtradas = []
    for linea in lineas:
        # Ignorar líneas con metadatos o formatos específicos
        if ("Género detectado" in linea or 
            "Recursos literarios" in linea or 
            "Terror psicológico" in linea or
            "misterio sobrenatural" in linea or
            "Presagios" in linea or
            "narrador poco fiable" in linea or
            "atmósfera claustrofóbica" in linea or
            "---" == linea.strip()):
            continue
        lineas_filtradas.append(linea)
    
    return "\n".join(lineas_filtradas).strip()

def dividir_texto_en_segmentos(texto, max_duracion_segundos=300):
    """
    Divide el texto en segmentos más pequeños para generar audios de aproximadamente 5 minutos.
    Intenta hacer el corte en puntos naturales como finales de párrafo o frases.
    
    Args:
        texto: El texto a dividir
        max_duracion_segundos: Duración máxima deseada para cada segmento en segundos (por defecto 5 minutos)
    
    Returns:
        Lista de segmentos de texto
    """
    # Aproximadamente 150 palabras por minuto (ritmo de lectura promedio)
    # Para 5 minutos, serían unas 750 palabras
    palabras_por_segmento = max_duracion_segundos / 60 * 150
    
    # Dividir el texto en párrafos
    parrafos = texto.split('\n\n')
    
    segmentos = []
    segmento_actual = []
    palabras_en_segmento = 0
    
    for parrafo in parrafos:
        palabras_parrafo = len(parrafo.split())
        
        # Si añadir este párrafo excede el límite y ya tenemos contenido
        if palabras_en_segmento + palabras_parrafo > palabras_por_segmento and segmento_actual:
            segmentos.append('\n\n'.join(segmento_actual))
            segmento_actual = [parrafo]
            palabras_en_segmento = palabras_parrafo
        else:
            segmento_actual.append(parrafo)
            palabras_en_segmento += palabras_parrafo
    
    # Añadir el último segmento si quedó algo
    if segmento_actual:
        segmentos.append('\n\n'.join(segmento_actual))
    
    # Si algún segmento único es muy largo, dividirlo por oraciones
    segmentos_finales = []
    for segmento in segmentos:
        if len(segmento.split()) > palabras_por_segmento * 1.2:  # Si excede por más del 20%
            oraciones = re.split(r'(?<=[.!?])\s+', segmento)
            segmento_oracion = []
            palabras_en_segmento = 0
            
            for oracion in oraciones:
                palabras_oracion = len(oracion.split())
                
                if palabras_en_segmento + palabras_oracion > palabras_por_segmento and segmento_oracion:
                    segmentos_finales.append(' '.join(segmento_oracion))
                    segmento_oracion = [oracion]
                    palabras_en_segmento = palabras_oracion
                else:
                    segmento_oracion.append(oracion)
                    palabras_en_segmento += palabras_oracion
            
            if segmento_oracion:
                segmentos_finales.append(' '.join(segmento_oracion))
        else:
            segmentos_finales.append(segmento)
    
    return segmentos_finales

async def generar_audio_segmento(texto, ruta_salida, voz, indice=0):
    """
    Genera un archivo de audio para un segmento de texto específico
    
    Args:
        texto: Texto a convertir en audio
        ruta_salida: Ruta base donde guardar el archivo
        voz: Voz a utilizar para el TTS
        indice: Índice del segmento para nombrar el archivo
    
    Returns:
        Ruta del archivo de audio generado
    """
    nombre_archivo = f"narracion_parte_{indice+1}.mp3"
    ruta_archivo = os.path.join(ruta_salida, nombre_archivo)
    
    communicate = Communicate(texto, 
                            voice=voz,
                            rate="-10%",
                            volume="+10%",
                            pitch="-10Hz")
    
    print(f"🔄 Generando audio parte {indice+1}...")
    await communicate.save(ruta_archivo)
    print(f"✅ Audio parte {indice+1} guardado en {ruta_archivo}")
    
    return nombre_archivo

async def texto_a_audio_edge(historia_id):
    ruta = f"historias/{historia_id}"
    archivo_texto = f"{ruta}/historia.txt"

    if not os.path.exists(archivo_texto):
        print("❌ No se encontró el archivo de texto.")
        return

    with open(archivo_texto, "r", encoding="utf-8") as f:
        texto = f.read()

    lineas = texto.splitlines()
    titulo = lineas[0] if lineas else "Sin título"
    texto_mejorado = "\n".join(lineas[1:])  # Omitir la primera línea (título)
    texto_limpio = limpiar_texto_para_audio(texto_mejorado)

    genero = detectar_genero(texto_limpio)
    voz = "es-ES-ElviraNeural" if genero == "femenino" else "es-ES-AlvaroNeural"

    # Dividir el texto en segmentos de aproximadamente 5 minutos
    segmentos = dividir_texto_en_segmentos(texto_limpio)
    
    # Crear carpeta para los segmentos de audio si no existe
    carpeta_segmentos = f"{ruta}/segmentos_audio"
    os.makedirs(carpeta_segmentos, exist_ok=True)
    
    # Generar un archivo de audio para cada segmento
    archivos_audio = []
    
    for i, segmento in enumerate(segmentos):
        nombre_archivo = await generar_audio_segmento(segmento, carpeta_segmentos, voz, i)
        archivos_audio.append(nombre_archivo)
    
    # Guardar metadata sobre los segmentos
    metadata = {
        "titulo": titulo,
        "segmentos_audio": archivos_audio,
        "genero_narrador": genero,
        "voz_utilizada": voz
    }
    
    with open(f"{ruta}/metadata_audio.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
    
    # También generar un único archivo de audio completo para compatibilidad
    communicate = Communicate(texto_limpio, 
                            voice=voz,
                            rate="-10%",
                            volume="+10%",
                            pitch="-10Hz")

    archivo_audio_completo = f"{ruta}/narracion.mp3"
    print("🔄 Generando audio completo...")
    await communicate.save(archivo_audio_completo)
    print(f"✅ Audio completo guardado en {archivo_audio_completo}")

def texto_a_audio(historia_id):
    asyncio.run(texto_a_audio_edge(historia_id))
