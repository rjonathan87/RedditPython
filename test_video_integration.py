#!/usr/bin/env python
# test_video_integration.py - Script para probar la integración de video

import os
import sys
from colorama import init, Fore, Style

# Inicializar colorama
init()

def main():
    """Función principal"""
    print(f"{Fore.CYAN}=" * 70)
    print(f"{Fore.YELLOW}🎬 PRUEBA DE INTEGRACIÓN DE VIDEO{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=" * 70)
    
    if len(sys.argv) < 2:
        print(f"{Fore.YELLOW}ℹ️ Uso: python test_video_integration.py <ID_HISTORIA>{Style.RESET_ALL}")
        return 1
    
    historia_id = sys.argv[1]
    print(f"{Fore.CYAN}ℹ️ Procesando historia: {historia_id}{Style.RESET_ALL}")
    
    # Importar y ejecutar la integración de video
    from video_integrator_new import integrar_video
    resultado = integrar_video(historia_id)
    
    if resultado:
        print(f"{Fore.GREEN}✅ Prueba completada con éxito{Style.RESET_ALL}")
        return 0
    else:
        print(f"{Fore.RED}❌ Prueba fallida{Style.RESET_ALL}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
