import os
import socket
from urllib.parse import urlparse

from config import Config


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")


CONFIG_KEYS = [
    "FH2_URL",
    "FH2_USER_TOKEN",
    "FH2_PROJECT_UUID",
    "FH2_WORKFLOW_UUID",
    "FH2_CREATOR_ID",
    "FH2_HOST_HEADER",
    "DEFAULT_LATITUDE",
    "DEFAULT_LONGITUDE",
    "DEFAULT_LEVEL",
    "DEFAULT_DESCRIPTION"
]


def cargar_configuracion():
    datos = {}

    if not os.path.exists(ENV_FILE):
        return datos

    try:
        with open(ENV_FILE, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()

                if (
                    not linea
                    or linea.startswith("#")
                    or "=" not in linea
                ):
                    continue

                clave, valor = linea.split("=", 1)
                datos[clave] = valor

    except OSError:
        return {}

    return datos


def guardar_configuracion(datos):
    actual = cargar_configuracion()

    actual.update(datos)

    with open(ENV_FILE, "w", encoding="utf-8") as archivo:
        for clave in CONFIG_KEYS:
            valor = actual.get(clave, "")
            archivo.write(f"{clave}={valor}\n")

    aplicar_configuracion_runtime(actual)

    return actual


def aplicar_configuracion_runtime(datos):
    """
    Actualiza Config dentro del proceso Flask actual.

    Esto permite cambiar Project UUID, Workflow UUID,
    token, etc. sin reiniciar el middleware.
    """

    Config.FH2_URL = datos.get(
        "FH2_URL",
        Config.FH2_URL
    )

    Config.FH2_USER_TOKEN = datos.get(
        "FH2_USER_TOKEN",
        Config.FH2_USER_TOKEN
    )

    Config.FH2_PROJECT_UUID = datos.get(
        "FH2_PROJECT_UUID",
        Config.FH2_PROJECT_UUID
    )

    Config.FH2_WORKFLOW_UUID = datos.get(
        "FH2_WORKFLOW_UUID",
        Config.FH2_WORKFLOW_UUID
    )

    Config.FH2_CREATOR_ID = datos.get(
        "FH2_CREATOR_ID",
        Config.FH2_CREATOR_ID
    )

    Config.FH2_HOST_HEADER = datos.get(
        "FH2_HOST_HEADER",
        Config.FH2_HOST_HEADER
    )

    try:
        Config.DEFAULT_LATITUDE = float(
            datos.get(
                "DEFAULT_LATITUDE",
                Config.DEFAULT_LATITUDE
            )
        )
    except (TypeError, ValueError):
        pass

    try:
        Config.DEFAULT_LONGITUDE = float(
            datos.get(
                "DEFAULT_LONGITUDE",
                Config.DEFAULT_LONGITUDE
            )
        )
    except (TypeError, ValueError):
        pass

    try:
        Config.DEFAULT_LEVEL = int(
            datos.get(
                "DEFAULT_LEVEL",
                Config.DEFAULT_LEVEL
            )
        )
    except (TypeError, ValueError):
        pass

    Config.DEFAULT_DESCRIPTION = datos.get(
        "DEFAULT_DESCRIPTION",
        Config.DEFAULT_DESCRIPTION
    )


def validar_configuracion(datos):
    errores = []

    fh2_url = datos.get(
        "FH2_URL",
        ""
    ).strip()

    project_uuid = datos.get(
        "FH2_PROJECT_UUID",
        ""
    ).strip()

    workflow_uuid = datos.get(
        "FH2_WORKFLOW_UUID",
        ""
    ).strip()

    creator_id = datos.get(
        "FH2_CREATOR_ID",
        ""
    ).strip()

    token = datos.get(
        "FH2_USER_TOKEN",
        ""
    ).strip()

    if not fh2_url:
        errores.append(
            "FH2 URL es obligatorio."
        )

    elif not (
        fh2_url.startswith("http://")
        or fh2_url.startswith("https://")
    ):
        errores.append(
            "FH2 URL debe comenzar con http:// o https://."
        )

    if not token:
        errores.append(
            "X-User-Token no puede estar vacío."
        )

    if not project_uuid:
        errores.append(
            "Project UUID es obligatorio."
        )

    if not workflow_uuid:
        errores.append(
            "Workflow UUID es obligatorio."
        )

    if not creator_id:
        errores.append(
            "Creator ID es obligatorio."
        )

    return errores


def comprobar_gateway():
    configuracion = cargar_configuracion()

    fh2_url = configuracion.get(
        "FH2_URL",
        ""
    )

    if not fh2_url:
        return False

    try:
        parsed = urlparse(fh2_url)

        host = parsed.hostname

        if not host:
            return False

        if parsed.port:
            port = parsed.port
        elif parsed.scheme == "https":
            port = 443
        else:
            port = 80

        with socket.create_connection(
            (host, port),
            timeout=2
        ):
            return True

    except (OSError, ValueError):
        return False


def ocultar_valor(valor):
    if not valor:
        return "NO CONFIGURADO"

    if len(valor) <= 12:
        return "••••••••"

    return (
        valor[:6]
        + "••••••••"
        + valor[-6:]
    )
