"""
Diagnóstico de instalación de MoviePy

Este script verifica si MoviePy está instalado correctamente e intenta solucionar
problemas comunes.
"""

import sys
import subprocess
import os

def instalar_paquete(paquete):
    print(f"Instalando {paquete}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])

def verificar_imports():
    imports_requeridos = [
        ("numpy", "numpy"),
        ("imageio", "imageio"),
        ("decorator", "decorator"),
        ("proglog", "proglog"),
        ("requests", "requests"),
        ("tqdm", "tqdm"),
        ("PIL", "Pillow"),
        ("moviepy", "moviepy"),
        ("imageio_ffmpeg", "imageio-ffmpeg")
    ]
    
    faltantes = []
    
    for modulo, paquete in imports_requeridos:
        try:
            __import__(modulo)
            print(f"✅ {modulo} está instalado correctamente")
        except ImportError:
            print(f"❌ {modulo} no está instalado")
            faltantes.append(paquete)
    
    return faltantes

def verificar_moviepy():
    try:
        import moviepy.editor
        print(f"✅ moviepy.editor importado correctamente desde: {moviepy.editor.__file__}")
        return True
    except ImportError as e:
        print(f"❌ Error al importar moviepy.editor: {str(e)}")
        return False

def main():
    print("Diagnóstico de MoviePy")
    print("-" * 50)
    
    # Verificar paquetes necesarios
    print("\n1. Verificando paquetes necesarios...")
    faltantes = verificar_imports()
    
    if faltantes:
        print("\nInstalando paquetes faltantes...")
        for paquete in faltantes:
            instalar_paquete(paquete)
        
        print("\nVerificando nuevamente los imports...")
        faltantes = verificar_imports()
        if faltantes:
            print("\n⚠️ Todavía hay paquetes que no se pudieron instalar.")
        else:
            print("\n✅ Todos los paquetes están instalados correctamente.")
    else:
        print("\n✅ Todos los paquetes necesarios están instalados.")
    
    # Verificar moviepy.editor
    print("\n2. Verificando moviepy.editor...")
    moviepy_ok = verificar_moviepy()
    
    if not moviepy_ok:
        print("\nIntentando solucionar el problema de moviepy.editor...")
        
        # Reinstalar moviepy
        print("Reinstalando moviepy...")
        instalar_paquete("--upgrade moviepy")
        
        # Verificar imageio-ffmpeg
        print("Instalando imageio-ffmpeg...")
        instalar_paquete("imageio-ffmpeg")
        
        # Verificar nuevamente
        moviepy_ok = verificar_moviepy()
        
        if not moviepy_ok:
            print("\n⚠️ No se pudo resolver el problema con moviepy.editor.")
            print("Sugerencia: prueba a usar una alternativa como 'vidpy' o 'PySceneDetect'.")
        else:
            print("\n✅ El problema con moviepy.editor ha sido resuelto.")
    
    # Resultado final
    if moviepy_ok:
        print("\nDiagnóstico finalizado: ✅ MoviePy está instalado correctamente.")
    else:
        print("\nDiagnóstico finalizado: ❌ Hay problemas con la instalación de MoviePy.")
        print("Alternativas recomendadas:")
        print("1. PySceneDetect - Para detección de escenas y división de videos")
        print("2. vidpy - Una alternativa más simple a MoviePy")
        print("3. opencv-python - Para procesamiento de video básico")
        print("\nPara instalar alternativas:")
        print("pip install opencv-python pyscenedetect vidpy")

if __name__ == "__main__":
    main()
