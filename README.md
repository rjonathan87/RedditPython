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

Para Windows:
```
install.bat
```

O manualmente:
```bash
pip install -r requirements.txt
python -m spacy download es_core_news_sm
```


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

- Si MoviePy no funciona, el programa intentará usar OpenCV como alternativa
- Verifica que FFmpeg esté instalado y en el PATH del sistema
- Para problemas con las APIs, revisa las claves en los archivos correspondientes

## Créditos

Desarrollado por rjonathan87. Este proyecto utiliza varias APIs y bibliotecas, incluidas Edge TTS, OpenAI, DeepSeek y PRAW para Reddit.