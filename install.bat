@echo off
echo ===== Instalando dependencias para Generador de Podcasts Reddit =====
echo.

echo Instalando requisitos desde requirements.txt...
pip install -r requirements.txt

echo.
echo Instalando modelo de español para spaCy...
python -m spacy download es_core_news_sm

echo.
echo Verificando archivo .env...
if not exist .env (
    if exist .env.example (
        echo Copiando .env.example a .env...
        copy .env.example .env
        echo Archivo .env creado a partir de .env.example. Por favor, edítalo con tus claves API antes de ejecutar el programa.
    ) else (
        echo No se encontró archivo .env ni .env.example - Creando plantilla...
        echo # Reddit API credentials > .env
        echo REDDIT_CLIENT_ID=tu_client_id_aqui >> .env
        echo REDDIT_CLIENT_SECRET=tu_client_secret_aqui >> .env
        echo REDDIT_USER_AGENT=PodcastScraper/1.0 >> .env
        echo REDDIT_USERNAME=tu_usuario_reddit >> .env
        echo REDDIT_PASSWORD=tu_contraseña_reddit >> .env
        echo. >> .env
        echo # OpenRouter API >> .env
        echo OPENROUTER_API_KEY=tu_openrouter_key_aqui >> .env
        echo OPENROUTER_URL=https://openrouter.ai/api/v1/chat/completions >> .env
        echo. >> .env
        echo # DeepSeek API >> .env
        echo DEEPSEEK_API_KEY=tu_deepseek_key_aqui >> .env
        echo DEEPSEEK_URL=https://api.deepseek.com >> .env
        echo. >> .env
        echo # Pexel API >> .env
        echo PEXEL_API_KEY=tu_pexel_api_key_aqui >> .env
        echo. >> .env
        echo # OpenAI (DALL-E) API >> .env
        echo OPENAI_API_KEY=tu_openai_api_key_aqui >> .env
        echo. >> .env
        echo # Stability AI (Stable Diffusion) API >> .env
        echo STABILITY_API_KEY=tu_stability_api_key_aqui >> .env
        echo.
        echo Archivo .env creado. Por favor, edítalo con tus claves API antes de ejecutar el programa.
    )
) else (
    echo Archivo .env encontrado.
)

echo.
echo ===== Instalación completada =====
echo Ahora puedes ejecutar el programa con: python main.py
echo.
pause
