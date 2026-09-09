import json
import os
import datetime
from services.storage_service import atomic_json, locked

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
EVENTS_FILE = os.path.join(LOGS_DIR, 'events.json')


def asegurar_archivo():
    os.makedirs(LOGS_DIR, exist_ok=True)
    try:
        with open(EVENTS_FILE, 'x', encoding='utf-8') as output:
            output.write('[]')
    except FileExistsError:
        pass


def cargar_eventos():
    try:
        with open(EVENTS_FILE, encoding='utf-8') as source:
            return json.load(source)
    except (OSError, json.JSONDecodeError):
        return []


@locked
def guardar_evento(camera_id, camera_name, latitude, longitude, fh2_status,
                   fh2_response='', workflow_uuid=None):
    os.makedirs(LOGS_DIR, exist_ok=True)
    eventos = cargar_eventos()
    evento = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'camera_id': camera_id,
        'camera_name': camera_name,
        'latitude': latitude,
        'longitude': longitude,
        'fh2_status': fh2_status,
        'fh2_response': fh2_response[:500],
        'workflow_uuid': workflow_uuid,
    }
    eventos.append(evento)
    atomic_json(EVENTS_FILE, eventos[-500:])
    return evento


def obtener_ultimo_evento():
    eventos = cargar_eventos()
    return eventos[-1] if eventos else None


def contar_eventos():
    return len(cargar_eventos())
