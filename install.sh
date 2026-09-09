#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="/opt/fh2-hikcentral"
SERVICE_NAME="hikmiddleware"
APP_USER="hikmiddleware"
OFFLINE=false
CHECK_ONLY=false
usage() {
    cat <<HELP
Centro de Operaciones · instalador Linux con systemd
sudo bash install.sh [--target /ruta/permanente] [--offline]
bash install.sh --check [--offline]

--offline  Instala Python desde wheelhouse/ sin acceder a Internet.
           Requiere Python 3.10+ con venv/ensurepip ya instalado.
--check    Verifica requisitos y archivos, sin modificar el sistema.
--target   Directorio de instalación permanente (predeterminado: /opt/fh2-hikcentral).
HELP
}
while (($#)); do
    case "$1" in
        --target) [[ $# -ge 2 ]] || { usage; exit 1; }; TARGET_DIR="$2"; shift 2 ;;
        --offline) OFFLINE=true; shift ;;
        --check) CHECK_ONLY=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) usage; exit 1 ;;
    esac
done
# Keep generated systemd directives literal and unambiguous.
[[ "$TARGET_DIR" =~ ^/[a-zA-Z0-9_/-]+$ && "$TARGET_DIR" != / && "$TARGET_DIR" != *'/../'* && "$TARGET_DIR" != */.. ]] || {
    echo 'Usa una ruta absoluta permanente, sin espacios ni componentes ..'; exit 1;
}
for file in app.py requirements.lock .env.example templates/_assets.html static/dist/dashboard.js static/dist/dashboard.css static/brand/fh2xhikcentral.png; do
    [[ -f "$SOURCE_DIR/$file" ]] || { echo "Falta $file. Genera el frontend antes de instalar."; exit 1; }
done
if $OFFLINE; then
    compgen -G "$SOURCE_DIR/wheelhouse/*.whl" >/dev/null || { echo 'Falta wheelhouse/. Prepara el paquete offline en otro equipo.'; exit 1; }
fi
if $CHECK_ONLY; then
    command -v python3 >/dev/null
    python3 -c 'import sys, venv, ensurepip; assert sys.version_info >= (3, 10), "Se requiere Python 3.10+"'
    command -v systemctl >/dev/null
    echo "Preflight correcto. Destino: $TARGET_DIR. Offline: $OFFLINE. No se modificó el sistema."
    exit 0
fi
[[ "$EUID" -eq 0 ]] || { echo 'Ejecuta con sudo bash install.sh'; exit 1; }
[[ -d /run/systemd/system ]] || { echo 'Este instalador requiere Linux iniciado con systemd.'; exit 1; }
if ! python3 -c 'import sys, venv, ensurepip; assert sys.version_info >= (3, 10)' >/dev/null 2>&1; then
    if $OFFLINE; then
        echo 'Instala previamente Python 3.10+ y python3-venv para usar el modo offline.'; exit 1
    fi
    command -v apt-get >/dev/null || { echo 'Instala Python 3.10+ y venv con el gestor de tu distribución.'; exit 1; }
    apt-get update
    apt-get install -y python3 python3-venv
fi
python3 -c 'import sys, venv, ensurepip; assert sys.version_info >= (3, 10)'
if ! id "$APP_USER" >/dev/null 2>&1; then
    useradd --system --user-group --home-dir "$TARGET_DIR" --shell /usr/sbin/nologin "$APP_USER"
fi
APP_GROUP="$(id -gn "$APP_USER")"
if [[ -d "$TARGET_DIR" && -n "$(find "$TARGET_DIR" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
    [[ -f "$TARGET_DIR/app.py" && -f "$TARGET_DIR/templates/base.html" ]] || {
        echo 'El destino contiene archivos de otra aplicación. Elige un directorio vacío.'; exit 1;
    }
fi
mkdir -p "$TARGET_DIR"
python3 "$SOURCE_DIR/scripts/deploy_files.py" "$SOURCE_DIR" "$TARGET_DIR"
chown -R "$APP_USER:$APP_GROUP" "$TARGET_DIR"
if [[ ! -x "$TARGET_DIR/venv/bin/python" ]]; then
    runuser -u "$APP_USER" -- python3 -m venv "$TARGET_DIR/venv"
fi
if $OFFLINE; then
    # The service account may not be able to traverse a user's home or USB mount.
    if [[ "$SOURCE_DIR" != "$TARGET_DIR" ]]; then
        mkdir -p "$TARGET_DIR/wheelhouse"
        cp "$SOURCE_DIR"/wheelhouse/*.whl "$TARGET_DIR/wheelhouse/"
        chown -R "$APP_USER:$APP_GROUP" "$TARGET_DIR/wheelhouse"
    fi
    runuser -u "$APP_USER" -- "$TARGET_DIR/venv/bin/python" -m pip install --no-index --find-links="$TARGET_DIR/wheelhouse" -r "$TARGET_DIR/requirements.lock"
else
    runuser -u "$APP_USER" -- "$TARGET_DIR/venv/bin/python" -m pip install -r "$TARGET_DIR/requirements.lock"
fi
if [[ ! -f "$TARGET_DIR/.env" ]]; then
    cp "$TARGET_DIR/.env.example" "$TARGET_DIR/.env"
fi
mkdir -p "$TARGET_DIR/logs"
for file in cameras.json workflows.json; do
    if [[ ! -f "$TARGET_DIR/$file" ]]; then printf '{}\n' > "$TARGET_DIR/$file"; fi
done
if [[ ! -f "$TARGET_DIR/logs/events.json" ]]; then printf '[]\n' > "$TARGET_DIR/logs/events.json"; fi
chown -R "$APP_USER:$APP_GROUP" "$TARGET_DIR"
chmod 600 "$TARGET_DIR/.env" "$TARGET_DIR/cameras.json" "$TARGET_DIR/workflows.json"
cat > "/etc/systemd/system/$SERVICE_NAME.service" <<UNIT
[Unit]
Description=Centro de Operaciones - HikCentral and DJI FlightHub 2
After=network-online.target
Wants=network-online.target

[Service]
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$TARGET_DIR
ExecStart=$TARGET_DIR/venv/bin/gunicorn --workers 2 --bind 0.0.0.0:5000 --timeout 30 app:app
ExecReload=/bin/kill -HUP \$MAINPID
Restart=on-failure
RestartSec=5
UMask=0077

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"
# HTTP readiness is more informative than merely checking the master PID.
"$TARGET_DIR/venv/bin/python" - <<'PY'
import time
import urllib.request
for attempt in range(20):
    try:
        with urllib.request.urlopen('http://127.0.0.1:5000/dashboard', timeout=2) as response:
            assert response.status == 200
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit('El dashboard no respondió. Revisa: journalctl -u hikmiddleware -n 50')
PY
if [[ -n "${SUDO_USER:-}" && "$SUDO_USER" != root ]]; then
    runuser -l "$SUDO_USER" -s /bin/sh -c "bash '$TARGET_DIR/scripts/install-shortcut.sh'" || echo 'Puedes crear el acceso directo manualmente desde tu sesión de escritorio.'
fi
printf '\nInstalación completada. Abre http://IP_DEL_SERVIDOR:5000/dashboard\n'
printf 'Configura FlightHub 2 en /settings y las cámaras en /cameras.\n'
printf 'Servicio: sudo systemctl status %s\n' "$SERVICE_NAME"
printf 'Archivos y datos: %s\n' "$TARGET_DIR"
