import praw
import requests
import os
import uuid
import json
from deep_translator import GoogleTranslator
import spacy
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Reddit API
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD"),
)

# Configuración de OpenRouter
openrouter_key = os.getenv("OPENROUTER_API_KEY")
openrouter_url = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")

# Configuración de DeepSeek
deepseek_key = os.getenv("DEEPSEEK_API_KEY")
deepseek_url = os.getenv("DEEPSEEK_URL", "https://api.deepseek.com")

# Configuración de APIs
client_deepseek = OpenAI(api_key=deepseek_key, base_url=deepseek_url)

# apikey pexel
pexel_key = os.getenv("PEXEL_API_KEY")

# Cargar el modelo de spaCy con manejo de errores
try:
    nlp = spacy.load("es_core_news_sm")
    print("✅ Modelo de spaCy cargado correctamente")
except OSError:
    print("⚠️ No se encontró el modelo de spaCy 'es_core_news_sm'. Intentando descargarlo...")
    try:
        import subprocess
        subprocess.run(["python", "-m", "spacy", "download", "es_core_news_sm"], check=True)
        nlp = spacy.load("es_core_news_sm")
        print("✅ Modelo de spaCy descargado e instalado correctamente")
    except Exception as e:
        print(f"❌ Error al descargar el modelo: {str(e)}")
        print("⚠️ Usando un modelo genérico como alternativa...")
        nlp = spacy.blank("es")  # Usar un modelo genérico si no se puede descargar

# Mantener un registro de historias consultadas
historias_consultadas = set()


def crear_carpeta_historia():
    historia_id = str(uuid.uuid4())
    ruta = f"historias/{historia_id}"
    os.makedirs(ruta, exist_ok=True)
    return historia_id, ruta


def detectar_idioma(texto):
    try:
        if not texto or texto.isspace():
            print("⚠️ El texto para detectar el idioma está vacío.")
            return "en"
        # Intentamos traducir al español. Si funciona sin error, es otro idioma
        if GoogleTranslator(source="auto", target="es").translate(texto[:100]):
            return "en"
        return "es"
    except Exception as e:
        print(f"Error detectando idioma: {e}")
        return "en"


def traducir_a_espanol(texto):
    try:
        if not texto or texto.isspace():
            print("⚠️ El texto para traducir está vacío.")
            return texto

        # Dividir el texto en chunks si es muy largo
        max_length = 4900
        if len(texto) > max_length:
            chunks = [
                texto[i : i + max_length] for i in range(0, len(texto), max_length)
            ]
            translated_chunks = []
            for chunk in chunks:
                translated_chunk = GoogleTranslator(
                    source="auto", target="es"
                ).translate(chunk)
                translated_chunks.append(translated_chunk)
            return " ".join(translated_chunks)
        else:
            return GoogleTranslator(source="auto", target="es").translate(texto)
    except Exception as e:
        print(f"Error traduciendo texto: {e}")
        return texto


def mejorar_historia(titulo, texto):
    prompt = f"""
    "Eres un experto en análisis literario, narrativa envolvente y storytelling viral. 
⮞ Tu doble función será:
   1) **Analizar** la historia para determinar:
    • Género literario predominante (p. ej. misterio, terror psicológico, realismo mágico, drama gótico, etc.).  
    • Recursos literarios clave que ya estén presentes o que mejor convengan (metáfora, presagio, giro de tuerca, voz epistolar, narrador poco fiable, etc.).
   2) **Reescribir** la historia reforzando precisamente ese género y esos recursos para enganchar al público.

🎯 **Público objetivo**
    • Edad: 18-45 (oyentes habituales de podcasts narrativos).  
    • Gustos: misterio, terror psicológico, drama, sucesos paranormales.  
    • Formato ideal: relato inmersivo con descripciones sensoriales.

🔧 **Proceso detallado**
    0. _Identificación_: Enumera en una línea el género detectado y dos-tres recursos literarios que potenciarás.  
    1. _Título mejorado_: Intrigante, emocional, sin spoilers.  
    2. _Inmersión sensorial_: Añade sonidos, olores y atmósferas que intensifiquen la tensión.  
    3. _Giros narrativos_: Incorpora revelaciones inesperadas alineadas con el género identificado.  
    4. _Final abierto_: Cierra con una incógnita que invite al debate y a futuras entregas.  
    5. _Preserva la esencia_: No alteres hechos clave del argumento; solo optimiza estructura, lenguaje y engagement.  
    6. _Limpieza de formato_: Elimina asteriscos, emojis o marcadores que interfieran con la lectura automatizada.  
    7. _Salida limpia_: No incluyas frases como “Comienza el relato:”; entrega directamente el texto.  

📥 **Entrada**  
    • Título original: {titulo}  
    • Texto original: {texto}

📤 **Entrega**:
- En la primera línea, solo el título mejorado (sin marcadores como [Título] o **)
- A partir de la segunda línea, solo el texto mejorado de la historia (sin marcadores ni formato adicional)

No incluyas en la salida final ninguna línea que contenga:
- Menciones al género detectado
- Recursos literarios
- Líneas separadoras (---)
- Análisis o comentarios sobre la historia
- Marcas de formato como **, [], etc.

Solo quiero ver:
1. Título en la primera línea
2. Historia en las siguientes líneas
"
    """
    try:
        # Usar DeepSeek como opción principal
        try:
            print("✨ Mejorando la historia con DeepSeek...")
            response = client_deepseek.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": prompt},
                ],
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error con DeepSeek: {e}, intentando con OpenRouter...")

        # Si DeepSeek falla, usar OpenRouter como respaldo
        try:
            print("✨ Intentando con OpenRouter como respaldo...")
            headers = {
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
            }
            response = requests.post(openrouter_url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error con OpenRouter: {e}")
            return None

    except Exception as e:
        print(f"Error mejorando la historia: {e}")
        return None


def obtener_historia():
    historia_id, ruta = crear_carpeta_historia()
    try:
        subreddit = reddit.subreddit("nosleep")
        for post in subreddit.hot(limit=20):
            if post.id in historias_consultadas:
                continue

            if post.selftext:
                titulo = post.title
                historia = post.selftext

                if not historia or historia.isspace():
                    print(
                        "❌ El texto de la historia está vacío. Saltando al siguiente post..."
                    )
                    continue

                idioma = detectar_idioma(historia)
                if idioma != "es":
                    print(f"🔍 Idioma detectado: {idioma}. Traduciendo al español...")
                    titulo = traducir_a_espanol(titulo)
                    historia = traducir_a_espanol(historia)
                    print("✨ Mejorando la historia con DeepSeek...")                      
                    historia_mejorada = mejorar_historia(titulo, historia)
                if historia_mejorada:
                    # Procesar la respuesta para eliminar los marcadores entre corchetes
                    lineas = historia_mejorada.splitlines()
                    
                    # Filtrar líneas que contengan metadatos o formatos
                    lineas_filtradas = []
                    for linea in lineas:
                        # Ignorar líneas con metadatos o formatos específicos
                        if ("**Género" in linea or 
                            "Recursos literarios" in linea or 
                            "Terror psicológico" in linea or
                            "misterio sobrenatural" in linea or
                            "Presagios" in linea or
                            "narrador poco fiable" in linea or
                            "atmósfera claustrofóbica" in linea or
                            "---" == linea.strip() or
                            "[Género" in linea or
                            "**Título" in linea):
                            continue
                        
                        # Limpiar la línea de marcadores
                        linea_limpia = linea.replace("[", "").replace("]", "").replace("*", "").strip()
                        if linea_limpia:  # Solo añadir líneas no vacías
                            lineas_filtradas.append(linea_limpia)
                    # La primera línea debe ser el título, el resto es el contenido
                    if lineas_filtradas:
                        titulo_mejorado = lineas_filtradas[0].replace("Título mejorado:", "").strip()
                        texto_mejorado = "\n".join(lineas_filtradas[1:]).replace("Texto mejorado:", "").strip()
                    else:
                        titulo_mejorado = titulo  # Usar el título original si no encontramos uno mejorado
                        texto_mejorado = historia  # Usar la historia original si no encontramos una mejorada
                        
                    with open(f"{ruta}/historia.txt", "w", encoding="utf-8") as f:
                        # Guardamos solo el título y el texto mejorado, sin ningún formato
                        f.write(f"{titulo_mejorado}\n{texto_mejorado}")

                    with open(f"{ruta}/metadata.json", "w", encoding="utf-8") as f:
                        json.dump(
                            {
                                "id": historia_id,
                                "titulo": titulo_mejorado,
                                "ruta": ruta,
                            },
                            f,
                        )

                    with open(f"{ruta}/historia.json", "w", encoding="utf-8") as f:
                        json.dump(
                            {
                                "título": titulo_mejorado,
                                "historia": texto_mejorado,
                                "descripción": f"📖 {titulo_mejorado}\n\n¡Una historia de terror que te pondrá los pelos de punta! 😱",
                                "hashtags": "#terrorparanodormir #miedoyterror #historiasterror #terror #miedo #paranormal #relatos",
                            },
                            f,
                            ensure_ascii=False,
                            indent=4,
                        )

                    historias_consultadas.add(post.id)
                    print(f"✅ Historia mejorada guardada en {ruta}")
                    return historia_id, titulo_mejorado, texto_mejorado
    except Exception as e:
        print(f"Error obteniendo historia: {e}")
        return None, None, None
        
def obtener_multiples_historias(cantidad=5):
    """Obtiene múltiples historias de Reddit
    
    Args:
        cantidad: Número de historias a obtener
        
    Returns:
        Lista de tuplas (historia_id, titulo, texto)
    """
    historias = []
    try:
        subreddit = reddit.subreddit("nosleep")
        posts = list(subreddit.hot(limit=40))  # Obtenemos más posts para tener margen
        
        # Contamos los posts procesados para evitar bucles infinitos
        posts_procesados = 0
        
        for post in posts:
            if len(historias) >= cantidad:
                break
                
            # Si ya hemos procesado demasiados posts, salimos
            posts_procesados += 1
            if posts_procesados > 40:
                print("⚠️ Se ha alcanzado el límite de posts procesados")
                break
                
            # Si ya hemos consultado esta historia, la saltamos
            if post.id in historias_consultadas:
                continue

            if post.selftext:
                titulo = post.title
                historia = post.selftext

                if not historia or historia.isspace():
                    print("❌ El texto de la historia está vacío. Saltando al siguiente post...")
                    continue

                print(f"🔄 Procesando historia: {titulo}")
                
                # Crear carpeta para la historia
                historia_id, ruta = crear_carpeta_historia()
                
                # Detectar idioma y traducir si es necesario
                idioma = detectar_idioma(historia)
                if idioma != "es":
                    print(f"🔍 Idioma detectado: {idioma}. Traduciendo al español...")
                    titulo = traducir_a_espanol(titulo)
                    historia = traducir_a_espanol(historia)
                    print("✨ Mejorando la historia con DeepSeek...")                      
                    historia_mejorada = mejorar_historia(titulo, historia)
                
                    if historia_mejorada:
                        # Procesar la respuesta para eliminar los marcadores entre corchetes
                        lineas = historia_mejorada.splitlines()
                        
                        # Filtrar líneas que contengan metadatos o formatos
                        lineas_filtradas = []
                        for linea in lineas:
                            # Ignorar líneas con metadatos o formatos específicos
                            if ("**Género" in linea or 
                                "Recursos literarios" in linea or 
                                "Terror psicológico" in linea or
                                "misterio sobrenatural" in linea or
                                "Presagios" in linea or
                                "narrador poco fiable" in linea or
                                "atmósfera claustrofóbica" in linea or
                                "---" == linea.strip() or
                                "[Género" in linea or
                                "**Título" in linea):
                                continue
                            
                            # Limpiar la línea de marcadores
                            linea_limpia = linea.replace("[", "").replace("]", "").replace("*", "").strip()
                            if linea_limpia:  # Solo añadir líneas no vacías
                                lineas_filtradas.append(linea_limpia)
                        
                        # La primera línea debe ser el título, el resto es el contenido
                        if lineas_filtradas:
                            titulo_mejorado = lineas_filtradas[0].replace("Título mejorado:", "").strip()
                            texto_mejorado = "\n".join(lineas_filtradas[1:]).replace("Texto mejorado:", "").strip()
                        else:
                            titulo_mejorado = titulo  # Usar el título original si no encontramos uno mejorado
                            texto_mejorado = historia  # Usar la historia original si no encontramos una mejorada
                            
                        # Guardar los archivos
                        with open(f"{ruta}/historia.txt", "w", encoding="utf-8") as f:
                            # Guardamos solo el título y el texto mejorado, sin ningún formato
                            f.write(f"{titulo_mejorado}\n{texto_mejorado}")

                        with open(f"{ruta}/metadata.json", "w", encoding="utf-8") as f:
                            json.dump(
                                {
                                    "id": historia_id,
                                    "titulo": titulo_mejorado,
                                    "ruta": ruta,
                                },
                                f,
                            )

                        with open(f"{ruta}/historia.json", "w", encoding="utf-8") as f:
                            json.dump(
                                {
                                    "título": titulo_mejorado,
                                    "historia": texto_mejorado,
                                    "descripción": f"📖 {titulo_mejorado}\n\n¡Una historia de terror que te pondrá los pelos de punta! 😱",
                                    "hashtags": "#terrorparanodormir #miedoyterror #historiasterror #terror #miedo #paranormal #relatos",
                                },
                                f,
                                ensure_ascii=False,
                                indent=4,
                            )

                        historias_consultadas.add(post.id)
                        print(f"✅ Historia mejorada guardada en {ruta}")
                        
                        # Añadir la historia a la lista de historias procesadas
                        historias.append((historia_id, titulo_mejorado, texto_mejorado))
        
        print(f"✅ Se obtuvieron {len(historias)} historias de un total de {cantidad} solicitadas")
        return historias
    except Exception as e:
        print(f"Error obteniendo múltiples historias: {e}")
        return historias  # Devolvemos las historias que pudimos obtener

