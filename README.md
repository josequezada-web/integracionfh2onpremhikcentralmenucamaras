# Centro de Operaciones · HikCentral × DJI FlightHub 2

Consola web para recibir eventos de HikCentral y ejecutar el workflow de DJI FlightHub 2 On-Premises asignado a cada cámara.

**Versión 1.0.1** · Dashboard React · Workflows por cámara · Instalador Linux · Acceso directo con logotipo

## Instalar en otro servidor Linux

📖 [Pasos de instalación: guía paso a paso para un servidor nuevo](PASOS_DE_INSTALACION.md)

Recomendado: Ubuntu 24.04 LTS o Debian 12, con systemd y acceso a Internet para descargar dependencias. El servidor no necesita Node.js: los archivos del frontend están incluidos. El instalador requiere Python 3.10+ y prepara Python/venv mediante apt si faltan.

```bash
sudo apt-get update
sudo apt-get install -y git

git clone https://github.com/josequezada-web/integracionfh2onpremhikcentralmenucamaras.git
cd integracionfh2onpremhikcentralmenucamaras
sudo bash install.sh
```

Abre **http://IP_DEL_SERVIDOR:5000/dashboard** desde un equipo de la misma red.

El instalador copia la aplicación a `/opt/fh2-hikcentral`, crea un entorno Python y el servicio `hikmiddleware`, y lo habilita al arrancar el servidor. No hace falta mantener abierta una terminal ni ejecutar el programa desde la carpeta clonada o una USB.

Para instalar exactamente esta versión, ejecuta `git checkout v1.0.1` antes del instalador.

## Configurar la operación

Si FlightHub 2 On-Premises y el middleware están instalados en este mismo servidor Linux, configura **FH2 URL** como `http://127.0.0.1:30812/openapi/v0.1/workflow`. Así no depende de cambios en la IP de la LAN. El endpoint de HikCentral sigue siendo `http://IP_DEL_SERVIDOR:5000/hik-alert`. Si FlightHub está en otro equipo, utiliza su IP o nombre. Conserva el Host Header requerido por tu AIO.

Al actualizar una instalación existente, `.env` se conserva: ajusta la URL desde **Configuración** si todavía apunta a una dirección anterior.

1. En **Configuración**, guarda la URL, token, Project UUID, workflow predeterminado y Creator ID de tu FlightHub 2.
2. En **Workflows disponibles**, agrega los workflows adicionales con nombre y UUID. Deben existir en el mismo proyecto de FlightHub 2.
3. En **Cámaras**, agrega cada cámara, sus coordenadas y el workflow que debe utilizar. Puedes conservar el predeterminado.
4. En HikCentral, configura el envío HTTP POST a `http://IP_DEL_SERVIDOR:5000/hik-alert` con el identificador de cámara:

```json
{"camera_id":"cam01"}
```

El dashboard muestra actividad, resultados y el UUID utilizado en el detalle de cada evento nuevo. Registrar cámaras o workflows no los ejecuta: una alerta en `/hik-alert` sí solicita su ejecución.

Una instalación nueva comienza vacía. Este repositorio no incluye tokens, cámaras, coordenadas de clientes ni historial. Para trasladar una instalación existente, consulta [la guía de migración](docs/INSTALLATION.md#trasladar-los-datos-de-una-instalación-existente).

## Acceso directo y USB

El instalador agrega **Centro de Operaciones** al menú de aplicaciones del usuario que ejecutó sudo, si dispone de un escritorio. En un servidor sin interfaz gráfica, abre el dashboard desde otro equipo.

Para crear el acceso directo manualmente en un equipo Linux:

```bash
bash scripts/install-shortcut.sh http://IP_DEL_SERVIDOR:5000/dashboard
```

También puedes descargar el código como ZIP/TAR desde GitHub, extraerlo y ejecutar `sudo bash install.sh`. Para instalar sin Internet usa un paquete con `wheelhouse/` y `sudo bash install.sh --offline`; Python y venv deben existir previamente.

[Guía completa: requisitos, paquetes USB, acceso directo y actualización](docs/INSTALLATION.md)

## Actualizar y comprobar el servicio

Desde la carpeta clonada:

```bash
git pull --ff-only
sudo bash install.sh
sudo systemctl status hikmiddleware
```

La reinstalación sobre el mismo destino conserva `.env`, `cameras.json`, `workflows.json` y `logs/`. Haz respaldo antes de actualizar. El servicio y el puerto 5000 son únicos por servidor.

## Desarrollo y pruebas

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements.lock
venv/bin/python -m unittest discover -s tests -v

# Solo si modificas React, CSS o logotipos:
npm ci
npm run build
```

Incluye `static/dist/`, `static/brand/` y `templates/_assets.html` al publicar cambios. El proceso de compilación versiona los recursos para evitar caché antigua. El instalador usa `requirements.lock` con versiones fijadas de las dependencias.

[Notas de la versión](CHANGELOG.md) · [Detalles del frontend](frontend/README.md) · [Referencia histórica de la integración](docs/LEGACY.md)
