@echo off
echo Instalando paquetes para DeepSeek...
pip install openai>=1.0.0
pip install requests>=2.25.0
pip install spacy>=3.0.0
pip install deep-translator>=1.9.0
pip install -r requirements.txt

echo Descargando modelo de lenguaje para español...
python -m spacy download es_core_news_sm

echo Instalación completada.
pause
