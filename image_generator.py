import requests
import os
from PIL import Image
import json
import spacy
from collections import Counter
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Intentar importar OpenAI de la nueva manera
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    USING_NEW_API = True
except ImportError:
    # Fallback a la versión antigua
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    USING_NEW_API = False

def mostrar_progreso(porcentaje, mensaje="Progreso"):
    barra = "#" * int(porcentaje // 2) + "-" * (50 - int(porcentaje // 2))
    print(f"\r{mensaje}: [{barra}] {porcentaje:.2f}%", end="")

def generar_imagen_dalle(prompt):
    """
    Genera una imagen usando DALL-E con mejor manejo de errores
    """
    try:
        if USING_NEW_API:
            response = client.images.generate(
                model="dall-e-2",
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            return response.data[0].url
        else:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024"
            )
            return response['data'][0]['url']
    except Exception as e:
        error_str = str(e)
        if 'billing_hard_limit_reached' in error_str:
            print("❌ Error: Se ha alcanzado el límite de facturación de DALL-E.")
            print("📝 Por favor, verifica tu saldo y límites en: https://platform.openai.com/account/billing")
        elif 'insufficient_quota' in error_str:
            print("❌ Error: Cuota insuficiente en tu cuenta de DALL-E.")
            print("💰 Considera actualizar tu plan o esperar al próximo ciclo de facturación.")
        else:
            print(f"❌ Error inesperado al generar imagen con DALL-E: {error_str}")
        return None

def generar_imagen_stable_diffusion(prompt):
    """
    Genera una imagen usando Stable Diffusion web API
    """
    try:
        url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {os.getenv('STABILITY_API_KEY')}"
        }
        
        payload = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "steps": 30,
            "width": 1024,
            "height": 1024,
        }
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            # Guardar la primera imagen generada
            image_data = response.json()["artifacts"][0]["base64"]
            return f"data:image/png;base64,{image_data}"
    except Exception as e:
        print(f"❌ Error al usar Stable Diffusion: {str(e)}")
    return None

def generar_imagen_con_fallback(prompt):
    """
    Intenta generar una imagen usando diferentes servicios
    """
    # Intentar con DALL-E primero
    imagen_url = generar_imagen_dalle(prompt)
    if (imagen_url):
        return imagen_url, "dalle"
        
    # Si DALL-E falla, intentar con Stable Diffusion
    imagen_url = generar_imagen_stable_diffusion(prompt)
    if (imagen_url):
        return imagen_url, "stable-diffusion"
        
    return None, None

def guardar_imagen_base64(base64_str, ruta):
    """
    Guarda una imagen desde una cadena base64
    """
    try:
        import base64
        imagen_data = base64.b64decode(base64_str.split(',')[1])
        with open(ruta, 'wb') as f:
            f.write(imagen_data)
        return True
    except Exception as e:
        print(f"❌ Error al guardar imagen base64: {str(e)}")
        return False

def obtener_ultima_historia():
    """
    Obtiene el ID de la última historia creada
    Retorna: (str) ID de la historia o None si no hay historias
    """
    historias_path = Path("historias")
    if not historias_path.exists():
        print("❌ No existe el directorio de historias.")
        return None
            
    historias = [d for d in historias_path.iterdir() if d.is_dir()]
    if not historias:
        print("❌ No hay historias disponibles.")
        return None
            
    return sorted(historias, key=lambda x: x.stat().st_mtime, reverse=True)[0].name

def generar_imagenes(historia_id=None, titulo=None):
    """
    Genera imágenes basadas en el contenido de la historia.
    Si no se proporciona historia_id, se usa la última historia creada.
    """
    try:
        if historia_id is None:
            historia_id = obtener_ultima_historia()
            if historia_id is None:
                return False
            print(f"ℹ️ Usando la última historia creada: {historia_id}")

        # Cargar el contenido de la historia
        ruta_historia = Path(f"historias/{historia_id}/historia.json")
        if not ruta_historia.exists():
            print(f"❌ No se encontró el archivo historia.json en {historia_id}")
            return False

        with open(ruta_historia, "r", encoding="utf-8") as f:
            datos = json.load(f)
            contenido = datos.get("contenido", "")
            # Si no se proporcionó título, usar el del JSON
            if titulo is None:
                titulo = datos.get("titulo", "Historia sin título")

        # Procesar el texto para extraer palabras clave
        nlp = spacy.load("es_core_news_sm")
        doc = nlp(contenido)
        
        # Extraer sustantivos y adjetivos relevantes
        palabras_clave = []
        for token in doc:
            if token.pos_ in ["NOUN", "ADJ"] and not token.is_stop:
                palabras_clave.append(token.text.lower())
        
        # Obtener las palabras más frecuentes
        palabras_frecuentes = Counter(palabras_clave).most_common(3)
        prompt_palabras = " ".join([palabra for palabra, _ in palabras_frecuentes])
        
        print(f"🔍 Palabras clave extraídas: {prompt_palabras}")
        
        # Generar prompt para DALL-E
        prompt_final = f"{titulo}. {prompt_palabras}. estilo artístico digital"
        
        # Generar imagen con fallback
        imagen_url, proveedor = generar_imagen_con_fallback(prompt_final)
        if imagen_url:
            # Crear directorio para imágenes si no existe
            Path(f"historias/{historia_id}/imagenes").mkdir(parents=True, exist_ok=True)
            
            if proveedor == "stable-diffusion":
                # Guardar imagen base64
                if guardar_imagen_base64(imagen_url, f"historias/{historia_id}/imagenes/imagen_1.png"):
                    print("✅ Imagen generada con Stable Diffusion y guardada exitosamente")
                    return True
            else:
                # Descargar y guardar la imagen de URL
                response = requests.get(imagen_url)
                if response.status_code == 200:
                    with open(f"historias/{historia_id}/imagenes/imagen_1.png", "wb") as f:
                        f.write(response.content)
                    print(f"✅ Imagen generada con {proveedor} y guardada exitosamente")
                    return True
        
        print("❌ No se pudo generar la imagen con ningún proveedor")
        return False
        
    except Exception as e:
        print(f"❌ Error al generar imágenes: {str(e)}")
        return False
