#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
shortcut_url="${1:-http://127.0.0.1:5000/dashboard}"
case "$shortcut_url" in
    http://*|https://*) ;;
    *) echo 'Indica una URL http:// o https://'; exit 1 ;;
esac
# The Exec line accepts a URL as one literal argument, never shell syntax.
if [[ ! "$shortcut_url" =~ ^https?://[a-zA-Z0-9._:/-]+$ ]]; then
    echo 'Usa una URL simple sin espacios, parámetros ni caracteres especiales.'; exit 1
fi
shortcut_data="${XDG_DATA_HOME:-$HOME/.local/share}"
mkdir -p "$shortcut_data/applications" "$shortcut_data/icons"
cp "$project_dir/static/brand/fh2xhikcentral.png" "$shortcut_data/icons/centro-operaciones.png"
cat > "$shortcut_data/applications/centro-operaciones.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Version=1.0
Name=Centro de Operaciones
Comment=HikCentral y DJI FlightHub 2
Exec=xdg-open $shortcut_url
Icon=$shortcut_data/icons/centro-operaciones.png
Terminal=false
Categories=Network;
StartupNotify=false
DESKTOP
chmod 644 "$shortcut_data/applications/centro-operaciones.desktop"
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$shortcut_data/applications" || true
fi
printf 'Acceso directo instalado en el menú de aplicaciones: %s\n' "$shortcut_url"
