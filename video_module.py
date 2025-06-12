import os
from colorama import Fore, Style

def integrar_video(historia_actual):
    """Integra un video con el audio de la historia actual"""
    try:
        if not historia_actual["id"]:
            print(f"{Fore.RED}❌ No hay ninguna historia activa. Primero obtén una historia.{Style.RESET_ALL}")
            input("Presiona Enter para continuar...")
            return False
        
        # Mostrar información
        print(f"{Fore.YELLOW}🎥 PASO 3: INTEGRAR VIDEO{Style.RESET_ALL}")
        print(f"{Fore.CYAN}-" * 70)
        print(f"Integrando video para la historia: {historia_actual['titulo']}")
        
        # Importar y ejecutar la integración de video
        from video_integrator_new import integrar_video as integrar
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
