#!/usr/bin/env bash

set -e

# ============================================================
# FH2 × HikCentral Integration Installer
# ============================================================

SERVICE_NAME="hikmiddleware"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -n "$SUDO_USER" ]; then
    APP_USER="$SUDO_USER"
else
    APP_USER="$(whoami)"
fi

APP_GROUP="$(id -gn "$APP_USER")"

VENV_DIR="$PROJECT_DIR/venv"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"
ENV_FILE="$PROJECT_DIR/.env"
ENV_EXAMPLE="$PROJECT_DIR/.env.example"

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"


echo
echo "============================================================"
echo " FH2 × HikCentral Integration Installer"
echo "============================================================"
echo
echo "Usuario:       $APP_USER"
echo "Grupo:         $APP_GROUP"
echo "Proyecto:      $PROJECT_DIR"
echo "Servicio:      $SERVICE_NAME"
echo


# ============================================================
# ROOT CHECK
# ============================================================

if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Este instalador debe ejecutarse con sudo."
    echo
    echo "Ejemplo:"
    echo "sudo ./install.sh"
    exit 1
fi


# ============================================================
# PYTHON CHECK
# ============================================================

echo "[1/8] Verificando Python..."

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 no está instalado."
    echo "Instalando..."
    apt update
    apt install -y python3
fi

PYTHON_VERSION="$(python3 --version)"

echo "OK: $PYTHON_VERSION"


# ============================================================
# VENV SUPPORT
# ============================================================

echo
echo "[2/8] Verificando soporte para entornos virtuales..."

if ! python3 -m venv --help >/dev/null 2>&1; then

    echo "python3-venv no está disponible."
    echo "Instalando..."

    apt update
    apt install -y python3-venv

fi

echo "OK: python3-venv disponible."


# ============================================================
# REQUIREMENTS
# ============================================================

echo
echo "[3/8] Verificando requirements.txt..."

if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "ERROR: No existe:"
    echo "$REQUIREMENTS_FILE"
    exit 1
fi

echo "OK: requirements.txt encontrado."


# ============================================================
# VIRTUAL ENVIRONMENT
# ============================================================

echo
echo "[4/8] Preparando entorno virtual..."

if [ ! -d "$VENV_DIR" ]; then

    sudo -u "$APP_USER" python3 -m venv "$VENV_DIR"

    echo "Entorno virtual creado."

else

    echo "El entorno virtual ya existe."

fi


echo
echo "Instalando dependencias..."

sudo -u "$APP_USER" \
    "$VENV_DIR/bin/pip" install --upgrade pip

sudo -u "$APP_USER" \
    "$VENV_DIR/bin/pip" install -r "$REQUIREMENTS_FILE"

echo "OK: dependencias instaladas."


# ============================================================
# ENV FILE
# ============================================================

echo
echo "[5/8] Verificando configuración .env..."

if [ ! -f "$ENV_FILE" ]; then

    if [ -f "$ENV_EXAMPLE" ]; then

        cp "$ENV_EXAMPLE" "$ENV_FILE"

        chown "$APP_USER:$APP_GROUP" "$ENV_FILE"

        chmod 600 "$ENV_FILE"

        echo ".env creado desde .env.example."

    else

        touch "$ENV_FILE"

        chown "$APP_USER:$APP_GROUP" "$ENV_FILE"

        chmod 600 "$ENV_FILE"

        echo ".env vacío creado."

    fi

    echo
    echo "IMPORTANTE:"
    echo "La configuración FH2 aún debe completarse desde /settings."

else

    echo "El archivo .env ya existe."
    chmod 600 "$ENV_FILE"

fi


# ============================================================
# LOG DIRECTORY
# ============================================================

echo
echo "[6/8] Preparando archivos de aplicación..."

mkdir -p "$PROJECT_DIR/logs"

chown -R "$APP_USER:$APP_GROUP" "$PROJECT_DIR/logs"

if [ ! -f "$PROJECT_DIR/logs/events.json" ]; then

    echo "[]" > "$PROJECT_DIR/logs/events.json"

    chown "$APP_USER:$APP_GROUP" \
        "$PROJECT_DIR/logs/events.json"

fi


if [ ! -f "$PROJECT_DIR/cameras.json" ]; then

    echo "{}" > "$PROJECT_DIR/cameras.json"

    chown "$APP_USER:$APP_GROUP" \
        "$PROJECT_DIR/cameras.json"

fi

echo "OK: archivos de datos preparados."


# ============================================================
# SYSTEMD SERVICE
# ============================================================

echo
echo "[7/8] Creando servicio systemd..."

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=HikCentral to FH2 Middleware
After=network-online.target
Wants=network-online.target

[Service]
User=$APP_USER
Group=$APP_GROUP

WorkingDirectory=$PROJECT_DIR

EnvironmentFile=$ENV_FILE

ExecStart=$VENV_DIR/bin/gunicorn \\
    --workers 2 \\
    --bind 0.0.0.0:5000 \\
    --timeout 30 \\
    app:app

Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

chmod 644 "$SERVICE_FILE"

systemctl daemon-reload

systemctl enable "$SERVICE_NAME"

echo "OK: servicio creado."


# ============================================================
# START SERVICE
# ============================================================

echo
echo "[8/8] Iniciando middleware..."

systemctl restart "$SERVICE_NAME"

sleep 2


if systemctl is-active \
    --quiet "$SERVICE_NAME"; then

    echo
    echo "============================================================"
    echo " INSTALACION COMPLETADA"
    echo "============================================================"
    echo
    echo "Servicio:"
    echo "  $SERVICE_NAME"
    echo
    echo "Estado:"
    echo "  ACTIVE"
    echo

else

    echo
    echo "============================================================"
    echo " ERROR INICIANDO EL SERVICIO"
    echo "============================================================"
    echo
    echo "Ejecuta:"
    echo
    echo "sudo systemctl status $SERVICE_NAME"
    echo
    echo "sudo journalctl -u $SERVICE_NAME -n 50"
    echo

    exit 1

fi


# ============================================================
# NETWORK INFORMATION
# ============================================================

AIO_IP="$(hostname -I 2>/dev/null | awk '{print $1}')"

if [ -n "$AIO_IP" ]; then

    echo "Abre desde un equipo de la misma red:"
    echo
    echo "  http://$AIO_IP:5000/dashboard"
    echo
    echo "Configuración FH2:"
    echo
    echo "  http://$AIO_IP:5000/settings"
    echo
    echo "Configuración de cámaras:"
    echo
    echo "  http://$AIO_IP:5000/cameras"
    echo

else

    echo "No fue posible determinar automáticamente la IP."
    echo
    echo "Consulta la IP del AIO con:"
    echo
    echo "hostname -I"
    echo

fi


echo "Comandos útiles:"
echo
echo "  sudo systemctl status $SERVICE_NAME"
echo "  sudo systemctl restart $SERVICE_NAME"
echo "  sudo journalctl -u $SERVICE_NAME -f"
echo

echo "Siguiente paso:"
echo
echo "1. Abrir /settings"
echo "2. Configurar FlightHub 2"
echo "3. Crear cámaras"
echo "4. Configurar HikCentral"
echo "5. Ejecutar un evento de prueba"
echo
