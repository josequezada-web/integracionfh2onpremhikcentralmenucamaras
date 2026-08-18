import json
import os
import datetime


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
EVENTS_FILE = os.path.join(LOGS_DIR, "events.json")


def asegurar_archivo():
    os.makedirs(LOGS_DIR, exist_ok=True)

    if not os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "w", encoding="utf-8") as archivo:
            json.dump([], archivo)


def cargar_eventos():
    asegurar_archivo()

    try:
        with open(EVENTS_FILE, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return []


def guardar_evento(
    camera_id,
    camera_name,
    latitude,
    longitude,
    fh2_status,
    fh2_response=""
):
    eventos = cargar_eventos()

    evento = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "camera_id": camera_id,
        "camera_name": camera_name,
        "latitude": latitude,
        "longitude": longitude,
        "fh2_status": fh2_status,
        "fh2_response": fh2_response[:500]
    }

    eventos.append(evento)

    # Conservamos solamente los últimos 500 eventos.
    eventos = eventos[-500:]

    with open(EVENTS_FILE, "w", encoding="utf-8") as archivo:
        json.dump(
            eventos,
            archivo,
            indent=4,
            ensure_ascii=False
        )

    return evento


def obtener_ultimo_evento():
    eventos = cargar_eventos()

    if not eventos:
        return None

    return eventos[-1]


def contar_eventos():
    return len(cargar_eventos())
