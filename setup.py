import os
import subprocess
import getpass


ENV_FILE = ".env"


def pedir_valor(nombre, valor_actual="", secreto=False):
    if valor_actual:
        texto_actual = "configurado"
    else:
        texto_actual = "vacío"

    print(f"\n{nombre} [{texto_actual}]")

    if secreto:
        valor = getpass.getpass("> ")
    else:
        valor = input("> ").strip()

    if not valor and valor_actual:
        return valor_actual

    return valor


def cargar_env_actual():
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


def guardar_env(datos):
    with open(ENV_FILE, "w", encoding="utf-8") as archivo:
        archivo.write(
            f"FH2_URL={datos['FH2_URL']}\n"
            f"FH2_USER_TOKEN={datos['FH2_USER_TOKEN']}\n"
            f"FH2_PROJECT_UUID={datos['FH2_PROJECT_UUID']}\n"
            f"FH2_WORKFLOW_UUID={datos['FH2_WORKFLOW_UUID']}\n"
            f"FH2_CREATOR_ID={datos['FH2_CREATOR_ID']}\n"
            f"FH2_HOST_HEADER={datos['FH2_HOST_HEADER']}\n"
            "\n"
            f"DEFAULT_LATITUDE={datos['DEFAULT_LATITUDE']}\n"
            f"DEFAULT_LONGITUDE={datos['DEFAULT_LONGITUDE']}\n"
            f"DEFAULT_LEVEL={datos['DEFAULT_LEVEL']}\n"
            f"DEFAULT_DESCRIPTION={datos['DEFAULT_DESCRIPTION']}\n"
        )


def main():
    print("=" * 50)
    print(" FH2 + HikCentral On-Prem Integration")
    print("=" * 50)

    actual = cargar_env_actual()

    datos = {}

    # Datos que normalmente NO cambian
    datos["FH2_URL"] = actual.get(
        "FH2_URL",
        "http://192.168.68.107:30812/openapi/v0.1/workflow"
    )

    datos["FH2_HOST_HEADER"] = actual.get(
        "FH2_HOST_HEADER",
        "192.168.1.1:30812"
    )

    # Datos variables de FH2
    datos["FH2_USER_TOKEN"] = pedir_valor(
        "X-User-Token",
        actual.get("FH2_USER_TOKEN", ""),
        secreto=True
    )

    datos["FH2_PROJECT_UUID"] = pedir_valor(
        "Project UUID",
        actual.get("FH2_PROJECT_UUID", "")
    )

    datos["FH2_WORKFLOW_UUID"] = pedir_valor(
        "Workflow UUID",
        actual.get("FH2_WORKFLOW_UUID", "")
    )

    datos["FH2_CREATOR_ID"] = pedir_valor(
        "Creator ID",
        actual.get("FH2_CREATOR_ID", "")
    )

    # Valores actuales o defaults
    datos["DEFAULT_LATITUDE"] = actual.get("DEFAULT_LATITUDE", "19.498072")
    datos["DEFAULT_LONGITUDE"] = actual.get("DEFAULT_LONGITUDE", "-99.210212")
    datos["DEFAULT_LEVEL"] = actual.get("DEFAULT_LEVEL", "5")
    datos["DEFAULT_DESCRIPTION"] = actual.get(
        "DEFAULT_DESCRIPTION",
        "Movimiento detectado por HikCentral"
    )

    if not datos["FH2_USER_TOKEN"]:
        print("\nERROR: X-User-Token no puede estar vacío.")
        return

    if not datos["FH2_PROJECT_UUID"]:
        print("\nERROR: Project UUID no puede estar vacío.")
        return

    if not datos["FH2_WORKFLOW_UUID"]:
        print("\nERROR: Workflow UUID no puede estar vacío.")
        return

    if not datos["FH2_CREATOR_ID"]:
        print("\nERROR: Creator ID no puede estar vacío.")
        return

    guardar_env(datos)

    print("\nConfiguración guardada correctamente en .env")
    print(f"FH2 URL: {datos['FH2_URL']}")
    print(f"Project UUID: {datos['FH2_PROJECT_UUID']}")
    print(f"Workflow UUID: {datos['FH2_WORKFLOW_UUID']}")
    print(f"Creator ID: {datos['FH2_CREATOR_ID']}")
    print("X-User-Token: ***************")

    iniciar = input("\n¿Deseas iniciar el middleware ahora? [S/n]: ").strip().lower()

    if iniciar in ("", "s", "si", "sí", "y", "yes"):
        print("\nIniciando Flask...\n")
        subprocess.run(["python", "app.py"])
    else:
        print("\nConfiguración terminada.")
        print("Puedes iniciar posteriormente con:")
        print("python app.py")


if __name__ == "__main__":
    main()
