from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for
)

from services.settings_service import (
    cargar_configuracion,
    guardar_configuracion,
    validar_configuracion,
    comprobar_gateway,
    ocultar_valor
)


settings_bp = Blueprint(
    "settings",
    __name__
)


@settings_bp.route(
    "/settings",
    methods=["GET"]
)
def settings():
    configuracion = cargar_configuracion()

    message = request.args.get(
        "message"
    )

    message_type = request.args.get(
        "type",
        "success"
    )

    return render_template(
        "settings.html",
        config=configuracion,
        gateway_reachable=comprobar_gateway(),
        token_masked=ocultar_valor(
            configuracion.get(
                "FH2_USER_TOKEN",
                ""
            )
        ),
        message=message,
        message_type=message_type
    )


@settings_bp.route(
    "/settings/save",
    methods=["POST"]
)
def save_settings():
    actual = cargar_configuracion()

    token_nuevo = request.form.get(
        "fh2_user_token",
        ""
    ).strip()

    # Si el usuario deja Token vacío,
    # conservamos el existente.
    token = (
        token_nuevo
        if token_nuevo
        else actual.get(
            "FH2_USER_TOKEN",
            ""
        )
    )

    datos = {
        "FH2_URL": request.form.get(
            "fh2_url",
            ""
        ).strip(),

        "FH2_USER_TOKEN": token,

        "FH2_PROJECT_UUID": request.form.get(
            "fh2_project_uuid",
            ""
        ).strip(),

        "FH2_WORKFLOW_UUID": request.form.get(
            "fh2_workflow_uuid",
            ""
        ).strip(),

        "FH2_CREATOR_ID": request.form.get(
            "fh2_creator_id",
            ""
        ).strip(),

        "FH2_HOST_HEADER": request.form.get(
            "fh2_host_header",
            ""
        ).strip(),

        "DEFAULT_LATITUDE": actual.get(
            "DEFAULT_LATITUDE",
            "0"
        ),

        "DEFAULT_LONGITUDE": actual.get(
            "DEFAULT_LONGITUDE",
            "0"
        ),

        "DEFAULT_LEVEL": actual.get(
            "DEFAULT_LEVEL",
            "5"
        ),

        "DEFAULT_DESCRIPTION": actual.get(
            "DEFAULT_DESCRIPTION",
            "Movimiento detectado por HikCentral"
        )
    }

    errores = validar_configuracion(
        datos
    )

    if errores:
        return redirect(
            url_for(
                "settings.settings",
                message=" ".join(errores),
                type="error"
            )
        )

    guardar_configuracion(
        datos
    )

    return redirect(
        url_for(
            "settings.settings",
            message=(
                "Configuración actualizada correctamente. "
                "Los nuevos valores ya están activos."
            ),
            type="success"
        )
    )
