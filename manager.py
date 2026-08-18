import subprocess
import sys
import socket
import json
import os

from services.event_service import obtener_ultimo_evento, contar_eventos


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMERAS_FILE = os.path.join(BASE_DIR, "cameras.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")


def ejecutar_script(script):
    try:
        subprocess.run([sys.executable, script])
    except KeyboardInterrupt:
        print("\nOperacion cancelada.")


def iniciar_middleware():
    print("\nIniciando middleware Flask...\n")

    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\nMiddleware detenido.")


def puerto_activo(host="127.0.0.1", port=5000):
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def cargar_camaras():
    if not os.path.exists(CAMERAS_FILE):
        return {}

    try:
        with open(CAMERAS_FILE, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return {}


def cargar_env():
    datos = {}

    if not os.path.exists(ENV_FILE):
        return datos

    with open(ENV_FILE, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()

            if not linea or linea.startswith("#") or "=" not in linea:
                continue

            clave, valor = linea.split("=", 1)
            datos[clave] = valor

    return datos


def ocultar_uuid(valor):
    if not valor:
        return "NO CONFIGURADO"

    if len(valor) <= 12:
        return valor

    return f"{valor[:6]}...{valor[-6:]}"


def mostrar_estado():
    print("\n" + "=" * 55)
    print(" ESTADO DEL SISTEMA")
    print("=" * 55)

    env = cargar_env()
    camaras = cargar_camaras()
    ultimo_evento = obtener_ultimo_evento()

    middleware_online = puerto_activo()

    print("\nMIDDLEWARE")
    print("-" * 55)

    if middleware_online:
        print("Estado:              ONLINE")
        print("Puerto 5000:         ESCUCHANDO")
    else:
        print("Estado:              OFFLINE")
        print("Puerto 5000:         NO DISPONIBLE")

    print("\nFLIGHTHUB 2")
    print("-" * 55)

    print(
        "Token:               "
        + ("CONFIGURADO" if env.get("FH2_USER_TOKEN") else "NO CONFIGURADO")
    )

    print(
        f"Project UUID:        "
        f"{ocultar_uuid(env.get('FH2_PROJECT_UUID'))}"
    )

    print(
        f"Workflow UUID:       "
        f"{ocultar_uuid(env.get('FH2_WORKFLOW_UUID'))}"
    )

    print(
        f"Creator ID:          "
        f"{ocultar_uuid(env.get('FH2_CREATOR_ID'))}"
    )

    print("\nCAMARAS")
    print("-" * 55)

    print(f"Configuradas:         {len(camaras)}")

    print("\nEVENTOS")
    print("-" * 55)

    print(f"Eventos registrados:  {contar_eventos()}")

    if ultimo_evento:

        print("\nUltimo evento:")
        print(f"Fecha/Hora:           {ultimo_evento['timestamp']}")
        print(f"Camera ID:            {ultimo_evento['camera_id']}")
        print(f"Nombre:               {ultimo_evento['camera_name']}")
        print(f"Latitud:              {ultimo_evento['latitude']}")
        print(f"Longitud:             {ultimo_evento['longitude']}")
        print(f"Respuesta FH2:        {ultimo_evento['fh2_status']}")

        if ultimo_evento["fh2_status"] == 200:
            print("Resultado:            OK")
        else:
            print("Resultado:            ERROR")

    else:
        print("\nNo hay eventos registrados.")

    print("\nEndpoint HikCentral:")
    print("http://192.168.68.107:5000/hik-alert")

    print("\n" + "=" * 55)


def main():

    while True:

        print("\n" + "=" * 55)
        print(" FH2 × HIKCENTRAL INTEGRATION MANAGER")
        print("=" * 55)

        print("\n1. Configurar FlightHub 2")
        print("2. Configurar camaras")
        print("3. Ver configuracion HikCentral")
        print("4. Iniciar middleware")
        print("5. Ver estado")
        print("6. Salir")

        opcion = input("\nSeleccione una opcion: ").strip()

        if opcion == "1":
            ejecutar_script("setup.py")

        elif opcion == "2":
            ejecutar_script("cameras.py")

        elif opcion == "3":
            ejecutar_script("cameras.py")

        elif opcion == "4":
            iniciar_middleware()

        elif opcion == "5":
            mostrar_estado()

        elif opcion == "6":
            print("\nCerrando Integration Manager.")
            break

        else:
            print("\nOpcion invalida.")


if __name__ == "__main__":
    main()