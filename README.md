Este proyecto permite generar de forma automática podcasts de audio y video a partir de historias obtenidas de Reddit, específicamente del subreddit r/nosleep. El sistema completo se encarga de:

1. Obtener historias de Reddit
2. Mejorar las historias mediante IA
3. Generar narraciones de audio
4. Crear imágenes relacionadas
5. Combinar todo en un video con subtítulos
6. Dividir el video en segmentos para compartir en redes sociales

## Requisitos previos

- Python 3.8 o superior
- FFmpeg instalado en el sistema (para procesamiento de video)
- Conexión a internet
- Una cuenta de Reddit (para la API)
- Claves de API para servicios de IA (opcionales)

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/rjonathan87/RedditPython
cd RedditPython
```

### 2. Instalar dependencias

manualmente:
```bash
pip install -r requirements.txt
python -m spacy download es_core_news_sm
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
# Reddit API credentials
REDDIT_CLIENT_ID=tu_client_id_aqui
REDDIT_CLIENT_SECRET=tu_client_secret_aqui
REDDIT_USER_AGENT=PodcastScraper/1.0
REDDIT_USERNAME=tu_usuario_reddit
REDDIT_PASSWORD=tu_contraseña_reddit

# OpenRouter API
OPENROUTER_API_KEY=tu_openrouter_key_aqui
OPENROUTER_URL=https://openrouter.ai/api/v1/chat/completions

# DeepSeek API
DEEPSEEK_API_KEY=tu_deepseek_key_aqui
DEEPSEEK_URL=https://api.deepseek.com

# Pexel API
PEXEL_API_KEY=tu_pexel_api_key_aqui

# OpenAI (DALL-E) API
OPENAI_API_KEY=tu_openai_api_key_aqui

# Stability AI (Stable Diffusion) API
STABILITY_API_KEY=tu_stability_api_key_aqui
```

Puedes copiar el archivo `.env.example` incluido en el proyecto y renombrarlo a `.env`:

```bash
copy .env.example .env
```

Luego, edita el archivo `.env` con tus propias claves de API.


## Estructura del proyecto

- main.py: Aplicación principal con menú interactivo
- story_fetcher.py: Obtiene historias de Reddit
- audio_generator.py: Genera archivos de audio a partir del texto
- image_generator.py: Crea imágenes para acompañar las historias
- scriptVideo.py: Crea videos con subtítulos
- video_splitter.py: Divide videos en segmentos más pequeños

## Uso

1. Ejecuta el programa principal:
```bash
python main.py
```

2. Sigue el menú interactivo para:
   - Obtener una nueva historia
   - Generar audio
   - Crear imágenes
   - Compilar el video
   - Dividir el video en segmentos

## Solución de problemas

- Verifica que FFmpeg esté instalado y en el PATH del sistema
- Asegúrate de que el archivo `.env` esté correctamente configurado con todas las claves API necesarias
- Si tienes problemas con una API específica, verifica que la clave correspondiente en el archivo `.env` sea válida
- Si necesitas actualizar alguna clave API, solo necesitas cambiarla en el archivo `.env`, no en el código fuente

## Créditos

Desarrollado por rjonathan87. Este proyecto utiliza varias APIs y bibliotecas, incluidas Edge TTS, OpenAI, DeepSeek y PRAW para Reddit.