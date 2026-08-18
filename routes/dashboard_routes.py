from flask import Blueprint, render_template, jsonify
import json
import os
import socket
import datetime

from services.event_service import cargar_eventos


dashboard_bp = Blueprint("dashboard", __name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CAMERAS_FILE = os.path.join(BASE_DIR, "cameras.json")


def middleware_online():
    try:
        with socket.create_connection(("127.0.0.1", 5000), timeout=1):
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


def obtener_eventos_hoy(eventos):
    hoy = datetime.datetime.now().strftime("%Y-%m-%d")

    return [
        evento
        for evento in eventos
        if evento.get("timestamp", "").startswith(hoy)
    ]


def obtener_ultimo_evento_por_camara(camaras, eventos):
    resultado = {}

    for camera_id, datos in camaras.items():
        resultado[camera_id] = {
            "name": datos["name"],
            "latitude": datos["latitude"],
            "longitude": datos["longitude"],
            "last_event": None
        }

    for evento in eventos:
        camera_id = evento.get("camera_id")

        if camera_id in resultado:
            resultado[camera_id]["last_event"] = evento

    return resultado


def obtener_estado():
    eventos = cargar_eventos()
    camaras = cargar_camaras()

    eventos_hoy = obtener_eventos_hoy(eventos)

    eventos_exitosos_hoy = [
        evento
        for evento in eventos_hoy
        if evento.get("fh2_status") == 200
    ]

    eventos_error_hoy = [
        evento
        for evento in eventos_hoy
        if evento.get("fh2_status") != 200
    ]

    ultimo_evento = eventos[-1] if eventos else None

    ultimos_eventos = list(reversed(eventos[-10:]))

    camaras_estado = obtener_ultimo_evento_por_camara(
        camaras,
        eventos
    )

    return {
        "middleware_status": middleware_online(),

        "camera_count": len(camaras),

        "events_today": len(eventos_hoy),
        "success_today": len(eventos_exitosos_hoy),
        "errors_today": len(eventos_error_hoy),

        "total_events": len(eventos),

        "ultimo_evento": ultimo_evento,

        "eventos": ultimos_eventos,

        "camaras": camaras_estado,

        "current_date": datetime.datetime.now().strftime(
            "%Y-%m-%d"
        )
    }


@dashboard_bp.route("/dashboard")
def dashboard():
    estado = obtener_estado()

    return render_template(
        "dashboard.html",
        **estado
    )


@dashboard_bp.route("/api/status")
def api_status():
    return jsonify(obtener_estado())