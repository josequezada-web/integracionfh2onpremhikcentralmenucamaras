from flask import Blueprint, request, jsonify
import datetime

from config import Config
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

    camera_id = data.get("camera_id")

    if not camera_id:
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

    response = enviar_workflow_fh2(
        nombre_evento=f"Intrusion - {nombre}",
        descripcion=f"Intrusion detectada en {nombre}",
        latitud=latitud,
        longitud=longitud,
        nivel=Config.DEFAULT_LEVEL
    )

    print("\n========== RESPUESTA FH2 ==========")
    print(response.status_code)
    print(response.text)

    evento = guardar_evento(
        camera_id=camera_id,
        camera_name=nombre,
        latitude=latitud,
        longitude=longitud,
        fh2_status=response.status_code,
        fh2_response=response.text
    )

    print("\n========== EVENTO REGISTRADO ==========")
    print(evento)

    return jsonify({
        "status": "ok",
        "camera_id": camera_id,
        "camera_name": nombre,
        "latitude": latitud,
        "longitude": longitud,
        "fh2_status": response.status_code,
        "fh2_response": response.text,
        "time": datetime.datetime.now().strftime("%H:%M:%S")
    })