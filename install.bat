@echo off
echo Actualizando pip, setuptools y wheel...
pip install -U pip setuptools wheel

echo Instalando dependencias principales...
pip install -r requirements.txt

echo Instalando dependencias específicas para moviepy...
pip install imageio-ffmpeg decorator proglog tqdm requests

echo Instalando spaCy y dependencias...
pip install spacy==3.1.6
python -m spacy download es_core_news_sm

echo Verificando la instalación de moviepy...
python -c "import sys; import moviepy.editor as mp; print('Moviepy instalado correctamente en:', mp.__file__)" || echo "Error al importar moviepy.editor, pero continuaremos con la instalación."

echo Instalación completada
pause
