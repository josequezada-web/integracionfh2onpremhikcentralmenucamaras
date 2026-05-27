import requests

from config import Config


def enviar_workflow_fh2(nombre_evento, descripcion, latitud, longitud, nivel=5):
    payload = {
        "workflow_uuid": Config.FH2_WORKFLOW_UUID,
        "trigger_type": 0,
        "name": nombre_evento,
        "params": {
            "creator": Config.FH2_CREATOR_ID,
            "latitude": float(latitud),
            "longitude": float(longitud),
            "level": int(nivel),
            "desc": descripcion
        }
    }

    headers = {
        "Content-Type": "application/json",
        "X-User-Token": Config.FH2_USER_TOKEN,
        "x-project-uuid": Config.FH2_PROJECT_UUID
    }

    if Config.FH2_HOST_HEADER:
        headers["Host"] = Config.FH2_HOST_HEADER

    response = requests.post(
        Config.FH2_URL,
        json=payload,
        headers=headers,
        timeout=10
    )

    return response