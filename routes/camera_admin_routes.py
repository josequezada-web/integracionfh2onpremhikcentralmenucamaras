from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

from services.camera_service import (
    cargar_camaras,
    agregar_camara,
    editar_camara,
    eliminar_camara
)


camera_admin_bp = Blueprint(
    "camera_admin",
    __name__
)


def obtener_endpoint_middleware():
    """
    Genera automáticamente el endpoint del middleware
    usando la misma dirección con la que el usuario
    accedió a la interfaz web.

    Ejemplos:

    http://192.168.68.107:5000/cameras
        ->
    http://192.168.68.107:5000/hik-alert


    http://192.168.10.25:5000/cameras
        ->
    http://192.168.10.25:5000/hik-alert
    """

    base_url = request.host_url.rstrip("/")

    return f"{base_url}/hik-alert"


@camera_admin_bp.route("/cameras")
def cameras():
    camaras = cargar_camaras()

    message = request.args.get(
        "message"
    )

    message_type = request.args.get(
        "type",
        "success"
    )

    middleware_endpoint = (
        obtener_endpoint_middleware()
    )

    return render_template(
        "cameras.html",
        camaras=camaras,
        middleware_endpoint=middleware_endpoint,
        message=message,
        message_type=message_type
    )


@camera_admin_bp.route(
    "/cameras/add",
    methods=["POST"]
)
def add_camera():

    camera_id = request.form.get(
        "camera_id",
        ""
    )

    name = request.form.get(
        "name",
        ""
    )

    latitude = request.form.get(
        "latitude",
        ""
    )

    longitude = request.form.get(
        "longitude",
        ""
    )

    success, message = agregar_camara(
        camera_id,
        name,
        latitude,
        longitude
    )

    return redirect(
        url_for(
            "camera_admin.cameras",
            message=message,
            type=(
                "success"
                if success
                else "error"
            )
        )
    )


@camera_admin_bp.route(
    "/cameras/edit/<camera_id>",
    methods=["POST"]
)
def edit_camera(camera_id):

    name = request.form.get(
        "name",
        ""
    )

    latitude = request.form.get(
        "latitude",
        ""
    )

    longitude = request.form.get(
        "longitude",
        ""
    )

    success, message = editar_camara(
        camera_id,
        name,
        latitude,
        longitude
    )

    return redirect(
        url_for(
            "camera_admin.cameras",
            message=message,
            type=(
                "success"
                if success
                else "error"
            )
        )
    )


@camera_admin_bp.route(
    "/cameras/delete/<camera_id>",
    methods=["POST"]
)
def delete_camera(camera_id):

    success, message = eliminar_camara(
        camera_id
    )

    return redirect(
        url_for(
            "camera_admin.cameras",
            message=message,
            type=(
                "success"
                if success
                else "error"
            )
        )
    )