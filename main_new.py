import os
import sys
import time
import argparse
from pathlib import Path
import json
import colorama
from colorama import Fore, Back, Style
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

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
        'dotenv': 'Para cargar variables de entorno',
        'colorama': 'Para colorear la salida en terminal',
        'openai': 'Para acceder a servicios de IA',
        'PIL': 'Para procesamiento de imágenes (Pillow)'
    }
    
    modulos_faltantes = []
    
    for modulo, descripcion in requisitos.items():
        try:
            if modulo == 'PIL':
                __import__('PIL.Image')
            elif modulo == 'dotenv':
                __import__('dotenv')
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
            elif modulo == 'dotenv':
                nombre_pip = 'python-dotenv'
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

def integrar_video():
    """Integra un video con el audio de la historia actual"""
    try:        
        if not historia_actual["id"]:
            print(f"{Fore.RED}❌ No hay ninguna historia activa. Primero obtén una historia.{Style.RESET_ALL}")
            input("Presiona Enter para continuar...")
            return False
        
        mostrar_titulo()
        print(f"{Fore.YELLOW}🎥 PASO 3: INTEGRAR VIDEO{Style.RESET_ALL}")
        print(f"{Fore.CYAN}-" * 70)
        print(f"Integrando video para la historia: {historia_actual['titulo']}")
        
        # Importar y ejecutar la integración de video
        from video_integrator import integrar_video as integrar
        integrar(historia_actual["id"])
        
        # Actualizar estado
        historia_actual["paso_actual"] = 3
        if "Integrar video" not in historia_actual["pasos_completados"]:
            historia_actual["pasos_completados"].append("Integrar video")
        
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Error al integrar video: {str(e)}{Style.RESET_ALL}")
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
    
    # Paso 3: Integrar video
    if not integrar_video():
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

def procesar_multiples_historias(cantidad=5):
    """Procesa múltiples historias de Reddit automáticamente
    
    Args:
        cantidad: Número de historias a procesar (por defecto 5)
    """
    mostrar_titulo()
    print(f"{Fore.YELLOW}🚀 PROCESAMIENTO AUTOMÁTICO DE {cantidad} HISTORIAS{Style.RESET_ALL}")
    print(f"{Fore.CYAN}-" * 70)
    print(f"Este proceso descargará {cantidad} historias de Reddit y generará")
    print(f"automáticamente el audio y video para cada una de ellas.")
    print(f"{Fore.CYAN}-" * 70)
    
    # Importar después de verificar los requisitos
    from story_fetcher import obtener_multiples_historias
    from audio_generator import texto_a_audio
    from video_integrator import integrar_video
    
    # Obtener múltiples historias
    print(f"{Fore.YELLOW}🔍 Obteniendo {cantidad} historias de Reddit...{Style.RESET_ALL}")
    historias = obtener_multiples_historias(cantidad)
    
    if not historias:
        print(f"{Fore.RED}❌ No se pudieron obtener historias de Reddit.{Style.RESET_ALL}")
        input("Presiona Enter para continuar...")
        return
    
    print(f"{Fore.GREEN}✅ Se obtuvieron {len(historias)} historias de Reddit{Style.RESET_ALL}")
    
    # Procesar cada historia
    for i, (historia_id, titulo, texto) in enumerate(historias, 1):
        print(f"\n{Fore.CYAN}=" * 70)
        print(f"{Fore.YELLOW}Historia {i}/{len(historias)}: {titulo}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}=" * 70)
        
        # Actualizar el estado global
        historia_actual["id"] = historia_id
        historia_actual["titulo"] = titulo
        historia_actual["texto"] = texto
        
        try:
            # Paso 1: Ya tenemos la historia
            print(f"{Fore.GREEN}✅ Historia obtenida con éxito: {titulo}")
            print(f"{Fore.GREEN}✅ ID de la historia: {historia_id}")
            
            # Paso 2: Generar audio
            print(f"\n{Fore.YELLOW}🔊 Generando audio para: {titulo}{Style.RESET_ALL}")
            texto_a_audio(historia_id)
            print(f"{Fore.GREEN}✅ Audio generado con éxito{Style.RESET_ALL}")
              # Paso 3: Integrar video
            print(f"\n{Fore.YELLOW}🎥 Integrando video para: {titulo}{Style.RESET_ALL}")
            integrar_video(historia_id, True)  # Usar selección aleatoria de video
            print(f"{Fore.GREEN}✅ Video integrado con éxito{Style.RESET_ALL}")
            
            print(f"\n{Fore.GREEN}✅ Procesamiento completo para la historia: {titulo}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}✅ Archivos guardados en: historias/{historia_id}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error al procesar la historia: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}⚠️ Continuando con la siguiente historia...{Style.RESET_ALL}")
            continue
    
    # Resumen final
    print(f"\n{Fore.GREEN}🎉 ¡PROCESAMIENTO DE MÚLTIPLES HISTORIAS COMPLETADO!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}-" * 70)
    print(f"{Fore.YELLOW}Se procesaron {len(historias)} historias de Reddit{Style.RESET_ALL}")
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
        print(f"{Fore.CYAN}3. 🎥 Integrar video")
        
        
        # Opción de flujo automático
        print(f"{Fore.WHITE}\n-- PROCESO AUTOMÁTICO --")
        print(f"{Fore.CYAN}4. 🚀 Ejecutar todos los pasos automáticamente")
        print(f"{Fore.CYAN}5. 📚 Procesar 5 historias automáticamente")
        
        # Opciones adicionales
        print(f"{Fore.WHITE}\n-- OPCIONES ADICIONALES --")
        print(f"{Fore.CYAN}6. 📖 Ver contenido de la historia actual")
        print(f"{Fore.CYAN}7. 📂 Abrir carpeta de la historia actual")
        # Salir
        print(f"{Fore.WHITE}\n-- SISTEMA --")
        print(f"{Fore.CYAN}8. ❌ Salir")

        print(f"{Fore.CYAN}-" * 70)
        opcion = input(f"{Fore.YELLOW}Selecciona una opción (1-8): {Style.RESET_ALL}")

        try:
            opcion = int(opcion)
            if opcion == 1:
                obtener_historia()
            elif opcion == 2:
                generar_audio()
            elif opcion == 3:
                integrar_video()
            elif opcion == 4:
                ejecutar_todos_pasos()
            elif opcion == 5:
                procesar_multiples_historias(5)
            elif opcion == 6:
                ver_historia_actual()
            elif opcion == 7:
                abrir_carpeta_historia()
            elif opcion == 8:
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