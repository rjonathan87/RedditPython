@echo off
echo ===================================================
echo  Solución para problemas con MoviePy
echo ===================================================

echo.
echo Paso 1: Actualizando pip...
pip install --upgrade pip

echo.
echo Paso 2: Desinstalando versiones actuales de MoviePy...
pip uninstall -y moviepy imageio-ffmpeg

echo.
echo Paso 3: Limpiando caché de pip...
pip cache purge

echo.
echo Paso 4: Instalando dependencias básicas...
pip install numpy Pillow decorator proglog tqdm requests

echo.
echo Paso 5: Instalando imageio y ffmpeg...
pip install imageio imageio-ffmpeg

echo.
echo Paso 6: Instalando MoviePy...
pip install moviepy

echo.
echo Paso 7: Verificando la instalación...
python -c "import moviepy.editor as mp; print('MoviePy instalado correctamente en:', mp.__file__)" || echo Error al importar moviepy.editor

echo.
echo Paso 8: Instalando alternativas por si acaso...
pip install opencv-python pyscenedetect

echo.
echo ===================================================
echo  Instalación completada
echo ===================================================
echo.
echo Si continúas teniendo problemas con moviepy.editor,
echo considera modificar tu código para usar OpenCV o PySceneDetect.
echo.
pause
