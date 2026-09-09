from flask import Blueprint, request, jsonify
import datetime

import requests
from services.settings_service import configuracion_actual
from services.workflow_service import cargar_workflows
from services.fh2_service import enviar_workflow_fh2
from services.camera_service import obtener_camara
from services.event_service import guardar_evento


onprem_bp = Blueprint("onprem", __name__)


@onprem_bp.route("/")
def home():
    return "FH2 On-Prem Middleware Running"


@onprem_bp.route("/hik-alert", methods=["POST"])
def hik_alert():
    data = request.get_json(silent=True) or {}

    print("\n========== EVENTO RECIBIDO ==========")
    print(data)

    if not isinstance(data, dict):
        return jsonify(status="error", message="Se esperaba un objeto JSON."), 400

    camera_id = data.get("camera_id")

    if not isinstance(camera_id, str) or not camera_id:
        return jsonify({
            "status": "error",
            "message": "camera_id no fue recibido"
        }), 400

    camera = obtener_camara(camera_id)

    if not camera:
        return jsonify({
            "status": "error",
            "message": f"Camara '{camera_id}' no encontrada"
        }), 404

    nombre = camera["name"]
    latitud = camera["latitude"]
    longitud = camera["longitude"]

    print("\n========== CAMARA IDENTIFICADA ==========")
    print(f"ID: {camera_id}")
    print(f"Nombre: {nombre}")
    print(f"Latitud: {latitud}")
    print(f"Longitud: {longitud}")

    config = configuracion_actual()
    workflow_uuid = camera.get("workflow_uuid") or config.get("FH2_WORKFLOW_UUID")
    if camera.get("workflow_uuid") and workflow_uuid not in cargar_workflows():
        return jsonify(status="error", message="El workflow asignado ya no está registrado."), 409
    if not workflow_uuid:
        return jsonify(status="error", message="Configura un workflow antes de recibir eventos."), 409

    try:
        response = enviar_workflow_fh2(
            nombre_evento=f"Intrusion - {nombre}",
            descripcion=f"Intrusion detectada en {nombre}",
            latitud=latitud,
            longitud=longitud,
            nivel=int(config.get("DEFAULT_LEVEL") or 5),
            workflow_uuid=workflow_uuid,
            configuracion=config
        )
    except requests.RequestException:
        guardar_evento(camera_id, nombre, latitud, longitud, 502,
                       "No se pudo conectar con FlightHub 2", workflow_uuid=workflow_uuid)
        return jsonify(status="error", message="No se pudo conectar con FlightHub 2.",
                       workflow_uuid=workflow_uuid), 502

    print("\n========== RESPUESTA FH2 ==========")
    print(response.status_code)
    print(response.text)

    evento = guardar_evento(
        camera_id=camera_id,
        camera_name=nombre,
        latitude=latitud,
        longitude=longitud,
        fh2_status=response.status_code,
        fh2_response=response.text,
        workflow_uuid=workflow_uuid
    )

    print("\n========== EVENTO REGISTRADO ==========")
    print(evento)

    return jsonify({
        "status": "ok",
        "camera_id": camera_id,
        "camera_name": nombre,
        "latitude": latitud,
        "longitude": longitud,
        "workflow_uuid": workflow_uuid,
        "fh2_status": response.status_code,
        "fh2_response": response.text,
        "time": datetime.datetime.now().strftime("%H:%M:%S")
    })