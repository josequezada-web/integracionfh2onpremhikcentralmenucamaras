#!/usr/bin/env bash

set -u

SERVICE_NAME="hikmiddleware"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$PROJECT_DIR/.env"
CAMERAS_FILE="$PROJECT_DIR/cameras.json"
VENV_DIR="$PROJECT_DIR/venv"

GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
RESET="\033[0m"

ok() {
    echo -e "${GREEN}✓${RESET} $1"
}

warn() {
    echo -e "${YELLOW}!${RESET} $1"
}

error() {
    echo -e "${RED}✗${RESET} $1"
}


echo
echo "============================================================"
echo " FH2 × HikCentral Diagnostic Tool"
echo "============================================================"
echo


# ============================================================
# 1. SYSTEM / NETWORK
# ============================================================

echo "[1] SISTEMA Y RED"
echo "------------------------------------------------------------"

if command -v hostname >/dev/null 2>&1; then
    HOSTNAME_VALUE="$(hostname)"
    ok "Hostname: $HOSTNAME_VALUE"
fi

AIO_IPS="$(hostname -I 2>/dev/null || true)"

if [ -n "$AIO_IPS" ]; then
    ok "IP(s) detectadas: $AIO_IPS"
else
    warn "No fue posible detectar IP del AIO."
fi

echo


# ============================================================
# 2. PYTHON
# ============================================================

echo "[2] PYTHON"
echo "------------------------------------------------------------"

if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION="$(python3 --version 2>&1)"
    ok "$PYTHON_VERSION"
else
    error "Python 3 no está instalado."
fi

if [ -x "$VENV_DIR/bin/python" ]; then
    VENV_VERSION="$("$VENV_DIR/bin/python" --version 2>&1)"
    ok "Entorno virtual disponible: $VENV_VERSION"
else
    error "No existe el entorno virtual en:"
    echo "  $VENV_DIR"
fi

echo


# ============================================================
# 3. DEPENDENCIES
# ============================================================

echo "[3] DEPENDENCIAS"
echo "------------------------------------------------------------"

if [ -x "$VENV_DIR/bin/python" ]; then

    for MODULE in flask requests dotenv gunicorn; do

        if "$VENV_DIR/bin/python" -c "import $MODULE" >/dev/null 2>&1; then
            ok "Módulo disponible: $MODULE"
        else
            error "Módulo faltante: $MODULE"
        fi

    done

fi

echo


# ============================================================
# 4. FILES
# ============================================================

echo "[4] ARCHIVOS"
echo "------------------------------------------------------------"

if [ -f "$ENV_FILE" ]; then
    ok ".env encontrado"
else
    error ".env no existe"
fi

if [ -f "$CAMERAS_FILE" ]; then
    ok "cameras.json encontrado"
else
    error "cameras.json no existe"
fi

if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    ok "requirements.txt encontrado"
else
    warn "requirements.txt no existe"
fi

echo


# ============================================================
# 5. FH2 CONFIGURATION
# ============================================================

echo "[5] CONFIGURACION FH2"
echo "------------------------------------------------------------"

FH2_URL=""
FH2_PROJECT_UUID=""
FH2_WORKFLOW_UUID=""
FH2_CREATOR_ID=""
FH2_HOST_HEADER=""
FH2_USER_TOKEN=""

if [ -f "$ENV_FILE" ]; then

    while IFS='=' read -r KEY VALUE; do

        case "$KEY" in
            FH2_URL)
                FH2_URL="$VALUE"
                ;;
            FH2_PROJECT_UUID)
                FH2_PROJECT_UUID="$VALUE"
                ;;
            FH2_WORKFLOW_UUID)
                FH2_WORKFLOW_UUID="$VALUE"
                ;;
            FH2_CREATOR_ID)
                FH2_CREATOR_ID="$VALUE"
                ;;
            FH2_HOST_HEADER)
                FH2_HOST_HEADER="$VALUE"
                ;;
            FH2_USER_TOKEN)
                FH2_USER_TOKEN="$VALUE"
                ;;
        esac

    done < "$ENV_FILE"

fi


if [ -n "$FH2_URL" ]; then
    ok "FH2_URL configurado: $FH2_URL"
else
    error "FH2_URL vacío"
fi

if [ -n "$FH2_PROJECT_UUID" ]; then
    ok "Project UUID configurado"
else
    error "Project UUID vacío"
fi

if [ -n "$FH2_WORKFLOW_UUID" ]; then
    ok "Workflow UUID configurado"
else
    error "Workflow UUID vacío"
fi

if [ -n "$FH2_CREATOR_ID" ]; then
    ok "Creator ID configurado"
else
    error "Creator ID vacío"
fi

if [ -n "$FH2_HOST_HEADER" ]; then
    ok "Host Header configurado: $FH2_HOST_HEADER"
else
    warn "Host Header vacío"
fi

if [ -n "$FH2_USER_TOKEN" ]; then
    ok "X-User-Token configurado"
else
    error "X-User-Token vacío"
fi

echo


# ============================================================
# 6. CAMERAS
# ============================================================

echo "[6] CAMARAS"
echo "------------------------------------------------------------"

if [ -f "$CAMERAS_FILE" ] && command -v python3 >/dev/null 2>&1; then

    CAMERA_COUNT="$(
        python3 - "$CAMERAS_FILE" <<'PY'
import json
import sys

path = sys.argv[1]

try:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        print(len(data))
    else:
        print("ERROR")

except Exception:
    print("ERROR")
PY
    )"

    if [ "$CAMERA_COUNT" = "ERROR" ]; then
        error "cameras.json no contiene JSON válido"
    else
        ok "Cámaras configuradas: $CAMERA_COUNT"
    fi

fi

echo


# ============================================================
# 7. SYSTEMD SERVICE
# ============================================================

echo "[7] SERVICIO"
echo "------------------------------------------------------------"

if systemctl list-unit-files \
    | grep -q "^${SERVICE_NAME}.service"; then

    ok "Servicio systemd instalado"

    if systemctl is-enabled \
        --quiet "$SERVICE_NAME" 2>/dev/null; then
        ok "Servicio habilitado para inicio automático"
    else
        warn "Servicio NO habilitado para inicio automático"
    fi

    if systemctl is-active \
        --quiet "$SERVICE_NAME" 2>/dev/null; then
        ok "Servicio activo"
    else
        error "Servicio detenido"
    fi

else

    error "Servicio $SERVICE_NAME no está instalado"

fi

echo


# ============================================================
# 8. PORT 5000
# ============================================================

echo "[8] MIDDLEWARE HTTP"
echo "------------------------------------------------------------"

if command -v ss >/dev/null 2>&1; then

    if ss -ltn 2>/dev/null \
        | grep -q ':5000 '; then

        ok "Puerto TCP 5000 está escuchando"

    else

        error "Puerto TCP 5000 NO está escuchando"

    fi

else

    warn "Comando ss no disponible"

fi


if command -v curl >/dev/null 2>&1; then

    HTTP_CODE="$(
        curl \
            --silent \
            --output /dev/null \
            --write-out "%{http_code}" \
            --max-time 3 \
            http://127.0.0.1:5000/ \
            2>/dev/null \
        || true
    )"

    if [ "$HTTP_CODE" = "200" ]; then
        ok "Middleware responde HTTP 200 localmente"
    else
        error "Middleware local respondió: ${HTTP_CODE:-sin respuesta}"
    fi

else

    warn "curl no está instalado; no se pudo probar HTTP"

fi

echo


# ============================================================
# 9. FH2 GATEWAY
# ============================================================

echo "[9] FH2 GATEWAY"
echo "------------------------------------------------------------"

if [ -n "$FH2_URL" ] && command -v python3 >/dev/null 2>&1; then

    GATEWAY_RESULT="$(
        python3 - "$FH2_URL" <<'PY'
import socket
import sys
from urllib.parse import urlparse

url = sys.argv[1]

try:
    parsed = urlparse(url)
    host = parsed.hostname

    if not host:
        print("INVALID")
        raise SystemExit

    if parsed.port:
        port = parsed.port
    elif parsed.scheme == "https":
        port = 443
    else:
        port = 80

    with socket.create_connection((host, port), timeout=2):
        print(f"OK|{host}|{port}")

except Exception:
    print("FAIL")
PY
    )"

    case "$GATEWAY_RESULT" in

        OK\|*)
            GATEWAY_HOST="$(echo "$GATEWAY_RESULT" | cut -d'|' -f2)"
            GATEWAY_PORT="$(echo "$GATEWAY_RESULT" | cut -d'|' -f3)"

            ok "FH2 accesible por TCP: $GATEWAY_HOST:$GATEWAY_PORT"
            ;;

        INVALID)
            error "FH2_URL inválido"
            ;;

        *)
            error "No fue posible conectar al gateway definido en FH2_URL"
            ;;

    esac

else

    warn "No se pudo comprobar gateway FH2"

fi

echo


# ============================================================
# RESULT
# ============================================================

echo "============================================================"
echo " DIAGNOSTICO FINALIZADO"
echo "============================================================"
echo
echo "Este script NO ejecuta workflows."
echo "No envía ningún POST al endpoint de FlightHub 2."
echo
echo "Si hay problemas, revisa también:"
echo
echo "  sudo systemctl status $SERVICE_NAME"
echo "  sudo journalctl -u $SERVICE_NAME -n 50"
echo
