import requests

from services.settings_service import configuracion_actual


def enviar_workflow_fh2(nombre_evento, descripcion, latitud, longitud, nivel=5, workflow_uuid=None, configuracion=None):
    config = configuracion if configuracion is not None else configuracion_actual()
    selected_workflow = workflow_uuid or config.get("FH2_WORKFLOW_UUID")
    if not selected_workflow:
        raise ValueError("No hay un workflow configurado.")
    payload = {
        "workflow_uuid": selected_workflow,
        "trigger_type": 0,
        "name": nombre_evento,
        "params": {
            "creator": config.get("FH2_CREATOR_ID"),
            "latitude": float(latitud),
            "longitude": float(longitud),
            "level": int(nivel),
            "desc": descripcion
        }
    }

    headers = {
        "Content-Type": "application/json",
        "X-User-Token": config.get("FH2_USER_TOKEN"),
        "x-project-uuid": config.get("FH2_PROJECT_UUID")
    }

    if config.get("FH2_HOST_HEADER"):
        headers["Host"] = config.get("FH2_HOST_HEADER")

    response = requests.post(
        config.get("FH2_URL"),
        json=payload,
        headers=headers,
        timeout=10
    )

    return response