import os

def leer_historia(historia_id):
    """
    Lee y muestra el contenido de una historia desde su archivo.
    """
    ruta = f"historias/{historia_id}/historia.txt"
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("❌ No se encontró la historia.")
