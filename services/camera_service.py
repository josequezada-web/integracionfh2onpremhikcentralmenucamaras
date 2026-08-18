import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CAMERAS_FILE = os.path.join(BASE_DIR, "cameras.json")


def cargar_camaras():
    if not os.path.exists(CAMERAS_FILE):
        return {}

    try:
        with open(CAMERAS_FILE, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    except (json.JSONDecodeError, OSError):
        return {}


def guardar_camaras(camaras):
    with open(CAMERAS_FILE, "w", encoding="utf-8") as archivo:
        json.dump(
            camaras,
            archivo,
            indent=4,
            ensure_ascii=False
        )


def obtener_camara(camera_id):
    camaras = cargar_camaras()

    return camaras.get(camera_id)


def validar_coordenadas(latitude, longitude):
    try:
        latitude = float(latitude)
        longitude = float(longitude)

    except (TypeError, ValueError):
        return False, None, None

    if not -90 <= latitude <= 90:
        return False, None, None

    if not -180 <= longitude <= 180:
        return False, None, None

    return True, latitude, longitude


def agregar_camara(camera_id, name, latitude, longitude):
    camera_id = camera_id.strip()
    name = name.strip()

    if not camera_id:
        return False, "El ID de cámara es obligatorio."

    if not name:
        return False, "El nombre de cámara es obligatorio."

    valido, latitude, longitude = validar_coordenadas(
        latitude,
        longitude
    )

    if not valido:
        return False, "Las coordenadas no son válidas."

    camaras = cargar_camaras()

    if camera_id in camaras:
        return False, f"La cámara '{camera_id}' ya existe."

    camaras[camera_id] = {
        "name": name,
        "latitude": latitude,
        "longitude": longitude
    }

    guardar_camaras(camaras)

    return True, "Cámara agregada correctamente."


def editar_camara(camera_id, name, latitude, longitude):
    camaras = cargar_camaras()

    if camera_id not in camaras:
        return False, "La cámara no existe."

    name = name.strip()

    if not name:
        return False, "El nombre no puede estar vacío."

    valido, latitude, longitude = validar_coordenadas(
        latitude,
        longitude
    )

    if not valido:
        return False, "Las coordenadas no son válidas."

    camaras[camera_id] = {
        "name": name,
        "latitude": latitude,
        "longitude": longitude
    }

    guardar_camaras(camaras)

    return True, "Cámara actualizada correctamente."


def eliminar_camara(camera_id):
    camaras = cargar_camaras()

    if camera_id not in camaras:
        return False, "La cámara no existe."

    del camaras[camera_id]

    guardar_camaras(camaras)

    return True, "Cámara eliminada correctamente."