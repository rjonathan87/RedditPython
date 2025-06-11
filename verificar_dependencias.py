# Verificador e instalador de dependencias para el Generador de Podcasts Reddit
import subprocess
import sys
import importlib
import os
from colorama import Fore, Style, init

# Inicializar colorama
init()

print(f"{Fore.CYAN}=" * 70)
print(f"{Fore.YELLOW}🔧  VERIFICADOR DE DEPENDENCIAS - GENERADOR DE PODCASTS REDDIT  🔧")
print(f"{Fore.CYAN}=" * 70 + Style.RESET_ALL)
print("")

def verificar_instalar_modulo(nombre, nombre_pip=None, mensaje=None):
    if nombre_pip is None:
        nombre_pip = nombre
    
    if mensaje is None:
        mensaje = f"Módulo {nombre}"
    
    print(f"{Fore.CYAN}Verificando {mensaje}...{Style.RESET_ALL}", end=" ")
    
    try:
        importlib.import_module(nombre)
        print(f"{Fore.GREEN}✅ Instalado{Style.RESET_ALL}")
        return True
    except ImportError:
        print(f"{Fore.YELLOW}⚠️ No encontrado. Instalando...{Style.RESET_ALL}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", nombre_pip])
            print(f"{Fore.GREEN}✅ {mensaje} instalado correctamente{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error al instalar {mensaje}: {str(e)}{Style.RESET_ALL}")
            return False

def verificar_spacy():
    print(f"{Fore.CYAN}Verificando spaCy y modelos...{Style.RESET_ALL}")
    
    try:
        import spacy
        print(f"{Fore.GREEN}✅ spaCy instalado{Style.RESET_ALL}")
        
        # Verificar modelo español
        try:
            spacy.load("es_core_news_sm")
            print(f"{Fore.GREEN}✅ Modelo español (es_core_news_sm) instalado{Style.RESET_ALL}")
        except OSError:
            print(f"{Fore.YELLOW}⚠️ Modelo español no encontrado. Instalando...{Style.RESET_ALL}")
            try:
                subprocess.check_call([sys.executable, "-m", "spacy", "download", "es_core_news_sm"])
                print(f"{Fore.GREEN}✅ Modelo español instalado correctamente{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}❌ Error al instalar modelo español: {str(e)}{Style.RESET_ALL}")
                return False
        return True
    except ImportError:
        print(f"{Fore.YELLOW}⚠️ spaCy no encontrado. Instalando...{Style.RESET_ALL}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "spacy"])
            print(f"{Fore.GREEN}✅ spaCy instalado correctamente{Style.RESET_ALL}")
            
            # Instalar modelo español
            print(f"{Fore.YELLOW}⚠️ Instalando modelo español...{Style.RESET_ALL}")
            try:
                subprocess.check_call([sys.executable, "-m", "spacy", "download", "es_core_news_sm"])
                print(f"{Fore.GREEN}✅ Modelo español instalado correctamente{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}❌ Error al instalar modelo español: {str(e)}{Style.RESET_ALL}")
                return False
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error al instalar spaCy: {str(e)}{Style.RESET_ALL}")
            return False

def verificar_nltk():
    print(f"{Fore.CYAN}Verificando NLTK y recursos...{Style.RESET_ALL}")
    
    try:
        import nltk
        print(f"{Fore.GREEN}✅ NLTK instalado{Style.RESET_ALL}")
        
        # Verificar recursos
        try:
            nltk.data.find('tokenizers/punkt')
            print(f"{Fore.GREEN}✅ Recurso 'punkt' instalado{Style.RESET_ALL}")
        except LookupError:
            print(f"{Fore.YELLOW}⚠️ Recurso 'punkt' no encontrado. Descargando...{Style.RESET_ALL}")
            nltk.download('punkt')
            print(f"{Fore.GREEN}✅ Recurso 'punkt' descargado correctamente{Style.RESET_ALL}")
            
        try:
            nltk.data.find('corpora/stopwords')
            print(f"{Fore.GREEN}✅ Recurso 'stopwords' instalado{Style.RESET_ALL}")
        except LookupError:
            print(f"{Fore.YELLOW}⚠️ Recurso 'stopwords' no encontrado. Descargando...{Style.RESET_ALL}")
            nltk.download('stopwords')
            print(f"{Fore.GREEN}✅ Recurso 'stopwords' descargado correctamente{Style.RESET_ALL}")
        
        return True
    except ImportError:
        print(f"{Fore.YELLOW}⚠️ NLTK no encontrado. Instalando...{Style.RESET_ALL}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk"])
            print(f"{Fore.GREEN}✅ NLTK instalado correctamente{Style.RESET_ALL}")
            
            # Importar de nuevo y descargar recursos
            import nltk
            print(f"{Fore.YELLOW}⚠️ Descargando recursos NLTK...{Style.RESET_ALL}")
            nltk.download('punkt')
            nltk.download('stopwords')
            print(f"{Fore.GREEN}✅ Recursos NLTK descargados correctamente{Style.RESET_ALL}")
            
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Error al instalar NLTK: {str(e)}{Style.RESET_ALL}")
            return False

def verificar_ffmpeg():
    print(f"{Fore.CYAN}Verificando FFmpeg...{Style.RESET_ALL}", end=" ")
    try:
        # Verificar si FFmpeg está instalado
        resultado = subprocess.run(["ffmpeg", "-version"], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
        if resultado.returncode == 0:
            print(f"{Fore.GREEN}✅ FFmpeg instalado{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}❌ Error al verificar FFmpeg{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}⚠️ Por favor, instala FFmpeg manualmente desde: https://ffmpeg.org/download.html{Style.RESET_ALL}")
            return False
    except FileNotFoundError:
        print(f"{Fore.RED}❌ FFmpeg no encontrado{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠️ Por favor, instala FFmpeg manualmente desde: https://ffmpeg.org/download.html{Style.RESET_ALL}")
        return False

def main():
    # Comprobar que estamos en el directorio correcto
    if not os.path.exists("main.py"):
        print(f"{Fore.RED}❌ Este script debe ejecutarse desde el directorio principal del proyecto{Style.RESET_ALL}")
        return False
    
    # Verificar/instalar dependencias básicas
    modules = [
        ("requests", None, "Requests (para API)"),
        ("PIL", "Pillow", "Pillow (para imágenes)"),
        ("colorama", None, "Colorama (para texto en color)"),
        ("tqdm", None, "TQDM (para barras de progreso)"),
        ("httpx", None, "HTTPX (para peticiones HTTP)"),
        ("deep_translator", None, "Deep Translator (para traducciones)"),
        ("praw", None, "PRAW (para Reddit API)"),
        ("cv2", "opencv-python", "OpenCV (para procesamiento de video)"),
        ("imageio_ffmpeg", "imageio-ffmpeg", "ImageIO-FFmpeg (para manejo de video)"),
        ("openai", None, "OpenAI SDK (para IA)"),
        ("edge_tts", None, "Edge TTS (para síntesis de voz)"),
        ("whisper", None, "Whisper (para transcripción)"),
        ("pexels_api", "pexels-api-py==0.0.5", "Pexels API (para videos)")
    ]
    
    # Verificar e instalar cada módulo
    todo_ok = True
    for module in modules:
        if not verificar_instalar_modulo(*module):
            todo_ok = False
    
    # Verificar spaCy y sus modelos
    if not verificar_spacy():
        todo_ok = False
    
    # Verificar NLTK y sus recursos
    if not verificar_nltk():
        todo_ok = False
    
    # Verificar FFmpeg
    if not verificar_ffmpeg():
        todo_ok = False
    
    # Resultado final
    print("")
    if todo_ok:
        print(f"{Fore.GREEN}=" * 70)
        print(f"{Fore.GREEN}✅ ¡Todas las dependencias están instaladas correctamente!")
        print(f"{Fore.GREEN}=" * 70 + Style.RESET_ALL)
        print(f"\n{Fore.CYAN}Puedes ejecutar el programa con:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}python main.py{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}=" * 70)
        print(f"{Fore.RED}❌ Algunas dependencias no pudieron ser instaladas.")
        print(f"{Fore.RED}=" * 70 + Style.RESET_ALL)
        print(f"\n{Fore.YELLOW}Por favor, intenta instalarlas manualmente con:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}pip install -r requirements.txt{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Y luego ejecuta:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}python -m spacy download es_core_news_sm{Style.RESET_ALL}")
    
    return todo_ok

if __name__ == "__main__":
    main()
