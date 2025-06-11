import os
import sys
import time
import argparse
from pathlib import Path
import json
import colorama
from colorama import Fore, Back, Style

# Inicializar colorama para Windows
colorama.init()

# Variables globales para estado del proceso
historia_actual = {
    "id": None,
    "titulo": None,
    "texto": None,
    "paso_actual": 0,
    "pasos_completados": []
}

def mostrar_titulo():
    """Muestra el título del programa con formato"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.CYAN}=" * 70)
    print(f"{Fore.YELLOW}🎙️  GENERADOR DE PODCASTS REDDIT - MODO INTERACTIVO  🎙️")
    print(f"{Fore.CYAN}=" * 70)
    print(Style.RESET_ALL)
    
    # Mostrar información de la historia actual si existe
    if historia_actual["id"]:
        print(f"{Fore.GREEN}Historia actual: {Fore.WHITE}{historia_actual['titulo']}")
        print(f"{Fore.GREEN}ID: {Fore.WHITE}{historia_actual['id']}")
        print(f"{Fore.GREEN}Estado: {Fore.WHITE}Paso {historia_actual['paso_actual']} de 5")
        print(f"{Fore.GREEN}Pasos completados: {Fore.WHITE}{', '.join(historia_actual['pasos_completados'])}")
        print(f"{Fore.CYAN}-" * 70)
        print(Style.RESET_ALL)

def verificar_requisitos():
    """Verifica que todos los requisitos estén instalados"""
    requisitos = {
        'praw': 'Para acceder a la API de Reddit',
        'requests': 'Para realizar peticiones HTTP',
        'deep_translator': 'Para traducir textos',
        'spacy': 'Para análisis de lenguaje natural',
        'edge_tts': 'Para generar audio con Edge TTS',
        'moviepy': 'Para edición de video',
        'colorama': 'Para colorear la salida en terminal',
        'openai': 'Para acceder a servicios de IA',
        'PIL': 'Para procesamiento de imágenes (Pillow)'
    }
    
    modulos_faltantes = []
    
    for modulo, descripcion in requisitos.items():
        try:
            if modulo == 'PIL':
                __import__('PIL.Image')
            else:
                __import__(modulo)
        except ImportError:
            modulos_faltantes.append((modulo, descripcion))
    
    if modulos_faltantes:
        print(f"{Fore.RED}❌ Faltan los siguientes módulos:{Style.RESET_ALL}")
        for modulo, desc in modulos_faltantes:
            print(f"{Fore.YELLOW}  - {modulo}: {desc}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Para instalar todos los requisitos, ejecuta:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  pip install -r requirements.txt{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}O para instalar módulos específicos:{Style.RESET_ALL}")
        comandos = []
        for modulo, _ in modulos_faltantes:
            # Convertir nombre del módulo para pip si es necesario
            nombre_pip = modulo
            if modulo == 'PIL':
                nombre_pip = 'Pillow'
            comandos.append(nombre_pip)
        
        print(f"{Fore.GREEN}  pip install {' '.join(comandos)}{Style.RESET_ALL}")
        return False
    
    # Verificar si FFmpeg está instalado
    try:
        from video_splitter import verificar_ffmpeg
        if not verificar_ffmpeg():
            return False
    except Exception as e:
        print(f"{Fore.RED}❌ Error al verificar FFmpeg: {str(e)}{Style.RESET_ALL}")
        return False
    
    return True

def cargar_ultima_historia():
    """Carga la última historia procesada si existe"""
    try:
        from video_splitter import obtener_ultima_historia
        historia_id = obtener_ultima_historia()
        
        if historia_id:
            ruta_historia = f"historias/{historia_id}"
            # Verificar si existe el archivo metadata.json
            if os.path.exists(f"{ruta_historia}/metadata.json"):
                with open(f"{ruta_historia}/metadata.json", "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                
                historia_actual["id"] = historia_id
                historia_actual["titulo"] = metadata.get("titulo", "Sin título")
                
                # Determinar los pasos completados
                pasos_completados = []
                if os.path.exists(f"{ruta_historia}/historia.txt"):
                    pasos_completados.append("Obtener historia")
                    historia_actual["paso_actual"] = 1
                
                if os.path.exists(f"{ruta_historia}/narracion.mp3"):
                    pasos_completados.append("Generar audio")
                    historia_actual["paso_actual"] = 2
                
                if os.path.exists(f"{ruta_historia}/imagenes/imagen_1.png"):
                    pasos_completados.append("Generar imagen")
                    historia_actual["paso_actual"] = 3
                
                if os.path.exists(f"{ruta_historia}/video.mp4"):
                    pasos_completados.append("Crear video")
                    historia_actual["paso_actual"] = 4
                
                if os.path.exists(f"{ruta_historia}/segmentos"):
                    pasos_completados.append("Dividir video")
                    historia_actual["paso_actual"] = 5
                
                historia_actual["pasos_completados"] = pasos_completados
                return True
    except Exception as e:
        print(f"{Fore.RED}⚠️ No se pudo cargar la última historia: {str(e)}")
    
    return False

def obtener_historia():
    """Obtiene una nueva historia de Reddit"""
    try:
        mostrar_titulo()
        print(f"{Fore.YELLOW}🔍 PASO 1: OBTENER HISTORIA DE REDDIT{Style.RESET_ALL}")
        print(f"{Fore.CYAN}-" * 70)
        print("Buscando historias interesantes en r/nosleep...")
        
        # Importar después de verificar los requisitos
        from story_fetcher import obtener_historia as fetch_story
        
        historia_id, titulo, texto = fetch_story()
        if not historia_id:
            input(f"{Fore.RED}❌ No se pudo obtener ninguna historia. Presiona Enter para continuar...{Style.RESET_ALL}")
            return False
        
        # Actualizar el estado global
        historia_actual["id"] = historia_id
        historia_actual["titulo"] = titulo
        historia_actual["texto"] = texto
        historia_actual["paso_actual"] = 1
        historia_actual["pasos_completados"] = ["Obtener historia"]
        
        print(f"{Fore.GREEN}✅ Historia obtenida con éxito: {titulo}")
        print(f"{Fore.GREEN}✅ ID de la historia: {historia_id}")
        input(f"{Fore.YELLOW}Presiona Enter para continuar...{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Error al obtener historia: {str(e)}{Style.RESET_ALL}")
        input("Presiona Enter para continuar...")
        return False

def generar_audio():
    """Genera el audio para la historia actual"""
    try:
        if not historia_actual["id"]:
            print(f"{Fore.RED}❌ No hay ninguna historia activa. Primero obtén una historia.{Style.RESET_ALL}")
            input("Presiona Enter para continuar...")
            return False
        
        mostrar_titulo()
        print(f"{Fore.YELLOW}🔊 PASO 2: GENERAR AUDIO{Style.RESET_ALL}")
        print(f"{Fore.CYAN}-" * 70)
        print(f"Generando audio para la historia: {historia_actual['titulo']}")
        
        # Importar y ejecutar la generación de audio
        from audio_generator import texto_a_audio
        texto_a_audio(historia_actual["id"])
        
        # Actualizar estado
        historia_actual["paso_actual"] = 2
        if "Generar audio" not in historia_actual["pasos_completados"]:
            historia_actual["pasos_completados"].append("Generar audio")
        
        print(f"{Fore.GREEN}✅ Audio generado con éxito")
        input(f"{Fore.YELLOW}Presiona Enter para continuar...{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Error al generar audio: {str(e)}{Style.RESET_ALL}")
        input("Presiona Enter para continuar...")
        return False

def generar_imagen():
    """Genera la imagen para la historia actual"""
    try:
        if not historia_actual["id"]:
            print(f"{Fore.RED}❌ No hay ninguna historia activa. Primero obtén una historia.{Style.RESET_ALL}")
            input("Presiona Enter para continuar...")
            return False
        
        mostrar_titulo()
        print(f"{Fore.YELLOW}🖼️ PASO 3: GENERAR IMAGEN{Style.RESET_ALL}")
        print(f"{Fore.CYAN}-" * 70)
        print(f"Generando imagen para la historia: {historia_actual['titulo']}")
        
        # Importar y ejecutar la generación de imagen
        from image_generator import generar_imagenes
        resultado = generar_imagenes(historia_actual["id"], historia_actual["titulo"])
        
        if resultado:
            # Actualizar estado
            historia_actual["paso_actual"] = 3
            if "Generar imagen" not in historia_actual["pasos_completados"]:
                historia_actual["pasos_completados"].append("Generar imagen")
            
            print(f"{Fore.GREEN}✅ Imagen generada con éxito")
        else:
            print(f"{Fore.RED}❌ No se pudo generar la imagen")
        
        input(f"{Fore.YELLOW}Presiona Enter para continuar...{Style.RESET_ALL}")
        return resultado
    except Exception as e:
        print(f"{Fore.RED}❌ Error al generar imagen: {str(e)}{Style.RESET_ALL}")
        input("Presiona Enter para continuar...")
        return False

def crear_video():
    """Crea el video con la imagen y el audio"""
    try:
        if not historia_actual["id"]:
            print(f"{Fore.RED}❌ No hay ninguna historia activa. Primero obtén una historia.{Style.RESET_ALL}")
            input("Presiona Enter para continuar...")
            return False
        
        mostrar_titulo()
        print(f"{Fore.YELLOW}🎬 PASO 4: CREAR VIDEO{Style.RESET_ALL}")
        print(f"{Fore.CYAN}-" * 70)
        print(f"Creando video para la historia: {historia_actual['titulo']}")
        
        ruta_historia = f"historias/{historia_actual['id']}"
        ruta_audio = f"{ruta_historia}/narracion.mp3"
        ruta_imagen = f"{ruta_historia}/imagenes/imagen_1.png"
        ruta_video = f"{ruta_historia}/video.mp4"
        
        if not os.path.exists(ruta_audio):
            print(f"{Fore.RED}❌ No se encontró el archivo de audio. Primero genera el audio.{Style.RESET_ALL}")
            input("Presiona Enter para continuar...")
            return False
            
        if not os.path.exists(ruta_imagen):
            print(f"{Fore.YELLOW}⚠️ No se encontró la imagen. Usando una imagen genérica...{Style.RESET_ALL}")
            # Usar una imagen por defecto
            os.makedirs(os.path.dirname(ruta_imagen), exist_ok=True)
            if not os.path.exists("recursos"):
                os.makedirs("recursos", exist_ok=True)
            
            # Crear imagen por defecto si no existe
            if not os.path.exists("recursos/imagen_default.png"):
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (1080, 1920), color=(0, 0, 0))
                d = ImageDraw.Draw(img)
                d.text((540, 960), "Historia", fill=(255, 255, 255), anchor="mm")
                img.save("recursos/imagen_default.png")
                
            import shutil
            shutil.copy("recursos/imagen_default.png", ruta_imagen)
        
        # Importar moviepy para crear el video
        from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
        
        print("🔄 Generando video...")
        audio = AudioFileClip(ruta_audio)
        imagen = ImageClip(ruta_imagen).set_duration(audio.duration)
        
        # Ajustar la imagen para que ocupe toda la pantalla
        imagen = imagen.resize(height=1920)
        imagen = imagen.resize(width=1080)
        
        video = CompositeVideoClip([imagen])
        video = video.set_audio(audio)
        
        # Guardar el video
        video.write_videofile(ruta_video, codec="libx264", fps=24)
        print(f"{Fore.GREEN}✅ Video generado en {ruta_video}")
        
        # Generar subtítulos
        print("💬 Añadiendo subtítulos al video...")
        ruta_video_subtitulos = f"{ruta_historia}/video_subtitulos.mp4"
        import scriptVideo
        scriptVideo.main(ruta_video, ruta_video_subtitulos)
        
        # Actualizar estado
        historia_actual["paso_actual"] = 4
        if "Crear video" not in historia_actual["pasos_completados"]:
            historia_actual["pasos_completados"].append("Crear video")
        
        print(f"{Fore.GREEN}✅ Video con subtítulos creado con éxito")
        input(f"{Fore.YELLOW}Presiona Enter para continuar...{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Error al crear video: {str(e)}{Style.RESET_ALL}")
        input("Presiona Enter para continuar...")
        return False

def dividir_video():
    """Divide el video en segmentos para redes sociales"""
    try:
        if not historia_actual["id"]:
            print(f"{Fore.RED}❌ No hay ninguna historia activa. Primero obtén una historia.{Style.RESET_ALL}")
            input("Presiona Enter para continuar...")
            return False
        
        mostrar_titulo()
        print(f"{Fore.YELLOW}✂️ PASO 5: DIVIDIR VIDEO{Style.RESET_ALL}")
        print(f"{Fore.CYAN}-" * 70)
        print(f"Dividiendo video para la historia: {historia_actual['titulo']}")
        
        # Importar y ejecutar la división del video
        from video_splitter import dividir_video as split_video
        resultado = split_video(historia_actual["id"])
        
        if resultado:
            # Actualizar estado
            historia_actual["paso_actual"] = 5
            if "Dividir video" not in historia_actual["pasos_completados"]:
                historia_actual["pasos_completados"].append("Dividir video")
            
            print(f"{Fore.GREEN}✅ Video dividido con éxito")
        else:
            print(f"{Fore.RED}❌ No se pudo dividir el video")
        
        input(f"{Fore.YELLOW}Presiona Enter para continuar...{Style.RESET_ALL}")
        return resultado
    except Exception as e:
        print(f"{Fore.RED}❌ Error al dividir video: {str(e)}{Style.RESET_ALL}")
        input("Presiona Enter para continuar...")
        return False

def ejecutar_todos_pasos():
    """Ejecuta todos los pasos automáticamente"""
    mostrar_titulo()
    print(f"{Fore.YELLOW}🚀 EJECUCIÓN AUTOMÁTICA DE TODOS LOS PASOS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}-" * 70)
    
    # Paso 1: Obtener historia
    if not obtener_historia():
        return
    
    # Paso 2: Generar audio
    if not generar_audio():
        return
    
    # Paso 3: Generar imagen
    if not generar_imagen():
        return
    
    # Paso 5: Dividir video
    if not dividir_video():
        return
    
    # Todo completado
    mostrar_titulo()
    print(f"{Fore.GREEN}🎉 ¡TODOS LOS PASOS COMPLETADOS CON ÉXITO!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}-" * 70)
    print(f"Historia: {historia_actual['titulo']}")
    print(f"ID: {historia_actual['id']}")
    print(f"Ruta: historias/{historia_actual['id']}")
    print(f"{Fore.CYAN}-" * 70)
    input(f"{Fore.YELLOW}Presiona Enter para volver al menú principal...{Style.RESET_ALL}")

def ver_historia_actual():
    """Muestra el contenido de la historia actual"""
    try:
        if not historia_actual["id"]:
            print(f"{Fore.RED}❌ No hay ninguna historia activa. Primero obtén una historia.{Style.RESET_ALL}")
            input("Presiona Enter para continuar...")
            return
        
        mostrar_titulo()
        print(f"{Fore.YELLOW}📖 CONTENIDO DE LA HISTORIA ACTUAL{Style.RESET_ALL}")
        print(f"{Fore.CYAN}-" * 70)
        
        # Importar y ejecutar la lectura de la historia
        from story_reader import leer_historia
        leer_historia(historia_actual["id"])
        
        print(f"{Fore.CYAN}-" * 70)
        input(f"{Fore.YELLOW}Presiona Enter para volver al menú principal...{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error al mostrar la historia: {str(e)}{Style.RESET_ALL}")
        input("Presiona Enter para continuar...")

def abrir_carpeta_historia():
    """Abre la carpeta de la historia actual en el explorador"""
    try:
        if not historia_actual["id"]:
            print(f"{Fore.RED}❌ No hay ninguna historia activa. Primero obtén una historia.{Style.RESET_ALL}")
            input("Presiona Enter para continuar...")
            return
        
        ruta = f"historias/{historia_actual['id']}"
        if not os.path.exists(ruta):
            print(f"{Fore.RED}❌ La carpeta de la historia no existe.{Style.RESET_ALL}")
            input("Presiona Enter para continuar...")
            return
        
        # Abrir carpeta en el explorador
        ruta_absoluta = os.path.abspath(ruta)
        os.startfile(ruta_absoluta) if os.name == 'nt' else os.system(f'xdg-open "{ruta_absoluta}"')
        
        print(f"{Fore.GREEN}✅ Carpeta abierta: {ruta_absoluta}")
        input(f"{Fore.YELLOW}Presiona Enter para volver al menú principal...{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error al abrir la carpeta: {str(e)}{Style.RESET_ALL}")
        input("Presiona Enter para continuar...")

def mostrar_menu_principal():
    """Muestra el menú principal de opciones"""
    while True:
        mostrar_titulo()
        print(f"{Fore.YELLOW}📋 MENÚ PRINCIPAL{Style.RESET_ALL}")
        print(f"{Fore.CYAN}-" * 70)
        
        # Opciones de flujo paso a paso
        print(f"{Fore.WHITE}-- PROCESO PASO A PASO --")
        print(f"{Fore.CYAN}1. 🔍 Obtener nueva historia de Reddit")
        print(f"{Fore.CYAN}2. 🔊 Generar audio")
        print(f"{Fore.CYAN}3. 🖼️ Generar imagen")
        print(f"{Fore.CYAN}4. 🎬 Crear video con subtítulos")
        print(f"{Fore.CYAN}5. ✂️ Dividir video en segmentos")
        
        # Opción de flujo automático
        print(f"{Fore.WHITE}\n-- PROCESO AUTOMÁTICO --")
        print(f"{Fore.CYAN}6. 🚀 Ejecutar todos los pasos automáticamente")
        
        # Opciones adicionales
        print(f"{Fore.WHITE}\n-- OPCIONES ADICIONALES --")
        print(f"{Fore.CYAN}7. 📖 Ver contenido de la historia actual")
        print(f"{Fore.CYAN}8. 📂 Abrir carpeta de la historia actual")
        
        # Salir
        print(f"{Fore.WHITE}\n-- SISTEMA --")
        print(f"{Fore.CYAN}9. ❌ Salir")
        
        print(f"{Fore.CYAN}-" * 70)
        opcion = input(f"{Fore.YELLOW}Selecciona una opción (1-9): {Style.RESET_ALL}")
        
        try:
            opcion = int(opcion)
            if opcion == 1:
                obtener_historia()
            elif opcion == 2:
                generar_audio()
            elif opcion == 3:
                generar_imagen()
            
            elif opcion == 4:
                ejecutar_todos_pasos()
            elif opcion == 5:
                ver_historia_actual()
            elif opcion == 6:
                abrir_carpeta_historia()
            elif opcion == 7:
                print(f"{Fore.GREEN}¡Gracias por usar el Generador de Podcasts Reddit!{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}❌ Opción no válida. Intenta de nuevo.{Style.RESET_ALL}")
                time.sleep(1)
        except ValueError:
            print(f"{Fore.RED}❌ Por favor, ingresa un número válido.{Style.RESET_ALL}")
            time.sleep(1)

def main():
    """Función principal"""
    # Crear estructura de directorios si no existe
    os.makedirs("historias", exist_ok=True)
    os.makedirs("recursos", exist_ok=True)
    
    # Verificar requisitos
    if not verificar_requisitos():
        print(f"{Fore.RED}❌ Por favor, instala los requisitos necesarios")
        print(f"{Fore.YELLOW}📝 Ejecuta: pip install -r requirements.txt{Style.RESET_ALL}")
        input("Presiona Enter para salir...")
        return
    
    # Cargar la última historia si existe
    cargar_ultima_historia()
    
    # Mostrar el menú principal
    mostrar_menu_principal()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"{Fore.YELLOW}\n\n⚠️ Proceso interrumpido por el usuario{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}\n❌ Error inesperado: {str(e)}{Style.RESET_ALL}")
