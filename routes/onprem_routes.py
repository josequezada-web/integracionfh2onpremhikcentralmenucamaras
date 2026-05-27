from flask import Blueprint, request, jsonify
import datetime

from config import Config
from services.fh2_service import enviar_workflow_fh2


onprem_bp = Blueprint("onprem", __name__)


@onprem_bp.route("/")
def home():
    return "FH2 On-Prem Middleware Running"


@onprem_bp.route("/hik-alert", methods=["POST"])
def hik_alert():
    data = request.json or {}

    print("\n========== EVENTO RECIBIDO ==========")
    print(data)

    response = enviar_workflow_fh2(
        nombre_evento="Alerta HikCentral",
        descripcion=Config.DEFAULT_DESCRIPTION,
        latitud=Config.DEFAULT_LATITUDE,
        longitud=Config.DEFAULT_LONGITUDE,
        nivel=Config.DEFAULT_LEVEL
    )

    print("\n========== RESPUESTA FH2 ==========")
    print(response.status_code)
    print(response.text)

    return jsonify({
        "fh2_status": response.status_code,
        "fh2_response": response.text,
        "time": datetime.datetime.now().strftime("%H:%M:%S")
    })