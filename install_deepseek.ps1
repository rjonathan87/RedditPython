Write-Host "Instalando paquetes para DeepSeek..." -ForegroundColor Cyan
pip install "openai>=1.0.0"
pip install "requests>=2.25.0"
pip install "spacy>=3.0.0"
pip install "deep-translator>=1.9.0"
pip install -r requirements.txt

Write-Host "Descargando modelo de lenguaje para español..." -ForegroundColor Cyan
python -m spacy download es_core_news_sm

Write-Host "Instalación completada." -ForegroundColor Green
Read-Host "Presiona Enter para salir"
