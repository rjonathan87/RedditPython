# Instalación de paquetes alternativos a MoviePy
Write-Host "Instalando paquetes necesarios para procesamiento de video..." -ForegroundColor Cyan

# Actualizar pip y herramientas básicas
Write-Host "Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel

# Desinstalar versiones problemáticas
Write-Host "Limpiando instalaciones existentes..." -ForegroundColor Yellow
python -m pip uninstall -y moviepy imageio-ffmpeg

# Instalar dependencias principales
Write-Host "Instalando dependencias básicas..." -ForegroundColor Yellow
python -m pip install numpy Pillow decorator proglog tqdm requests

# Instalar alternativas
Write-Host "Instalando OpenCV como alternativa a MoviePy..." -ForegroundColor Yellow
python -m pip install opencv-python

# Instalar FFmpeg si es necesario
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "FFmpeg no está instalado o no está en el PATH." -ForegroundColor Yellow
    Write-Host "Por favor, descarga e instala FFmpeg desde https://ffmpeg.org/download.html" -ForegroundColor Yellow
    Write-Host "O usa 'winget install ffmpeg' si tienes winget instalado." -ForegroundColor Yellow
}

# Intentar instalar MoviePy de nuevo (por si acaso)
Write-Host "Intentando instalar MoviePy..." -ForegroundColor Yellow
python -m pip install moviepy imageio-ffmpeg

# Verificar instalaciones
Write-Host "Verificando instalaciones..." -ForegroundColor Cyan
$packages = @("numpy", "opencv-python", "moviepy")

foreach ($package in $packages) {
    $result = python -c "import importlib.util; print('$package:', importlib.util.find_spec('$package') is not None)"
    Write-Host $result
}

# Verificar específicamente moviepy.editor
$moviepyResult = python -c "import sys; print('Verificando moviepy.editor:'); try: import moviepy.editor; print('OK - ' + moviepy.editor.__file__); except Exception as e: print('ERROR - ' + str(e))" 2>&1
Write-Host $moviepyResult -ForegroundColor Yellow

Write-Host "`nInstalación completada" -ForegroundColor Green
Write-Host "Si moviepy.editor sigue sin funcionar, use la alternativa de OpenCV" -ForegroundColor Green
Write-Host "El script ya está configurado para usar OpenCV automáticamente si MoviePy falla" -ForegroundColor Green

# Pausa para ver los resultados
Write-Host "`nPresiona cualquier tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
