import os
import spacy
from edge_tts import Communicate
import asyncio

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

async def texto_a_audio_edge(historia_id):
    ruta = f"historias/{historia_id}"
    archivo_texto = f"{ruta}/historia.txt"

    if not os.path.exists(archivo_texto):
        print("❌ No se encontró el archivo de texto.")
        return

    with open(archivo_texto, "r", encoding="utf-8") as f:
        texto = f.read()

    lineas = texto.splitlines()
    texto_mejorado = "\n".join(lineas[1:])  # Omitir la primera línea (título)
    texto_limpio = limpiar_texto_para_audio(texto_mejorado)

    genero = detectar_genero(texto_limpio)
    voz = "es-ES-ElviraNeural" if genero == "femenino" else "es-ES-AlvaroNeural"

    communicate = Communicate(texto_limpio, 
                            voice=voz,
                            rate="-10%",
                            volume="+10%",
                            pitch="-10Hz")

    archivo_audio = f"{ruta}/narracion.mp3"
    print("🔄 Generando audio...")
    await communicate.save(archivo_audio)
    print(f"✅ Audio guardado en {archivo_audio}")

def texto_a_audio(historia_id):
    asyncio.run(texto_a_audio_edge(historia_id))
