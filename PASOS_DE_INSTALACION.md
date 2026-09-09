# Pasos de instalación

Esta guía instala **Centro de Operaciones · HikCentral × DJI FlightHub 2**, versión **v1.0.1**, en otro servidor Linux.

## 1. Preparar el servidor

Utiliza Ubuntu 24.04 LTS o Debian 12 con systemd, un usuario con permisos `sudo` y conexión a Internet para descargar el repositorio y las dependencias. El puerto 5000 debe estar disponible.

El instalador requiere Python 3.10 o posterior y prepara Python y venv mediante apt si faltan. **No necesitas instalar Node.js ni compilar React**: el frontend y los logotipos ya vienen incluidos.

Abre una terminal y ejecuta:

```bash
sudo apt-get update
sudo apt-get install -y git
```

## 2. Descargar el repositorio

```bash
git clone https://github.com/josequezada-web/integracionfh2onpremhikcentralmenucamaras.git
cd integracionfh2onpremhikcentralmenucamaras
```

Para instalar exactamente la versión publicada:

```bash
git checkout v1.0.1
```

Si prefieres la versión más reciente de `main`, omite ese último comando.

## 3. Ejecutar el instalador

```bash
sudo bash install.sh
```

El instalador:

- Copia la aplicación a `/opt/fh2-hikcentral`.
- Crea el usuario de servicio `hikmiddleware` y el entorno Python.
- Instala las dependencias fijadas en `requirements.lock`.
- Prepara la configuración y los archivos de datos vacíos.
- Registra e inicia el servicio `hikmiddleware`, con arranque automático.
- Crea el acceso directo **Centro de Operaciones** para el usuario que ejecutó sudo, si dispone de escritorio.

Cuando termine, no necesitas dejar la terminal abierta.

## 4. Abrir la aplicación

Consulta las direcciones IP del servidor:

```bash
hostname -I
```

Desde un navegador del servidor o de otro equipo de la misma red, abre:

```text
http://IP_DEL_SERVIDOR:5000/dashboard
```

Sustituye `IP_DEL_SERVIDOR` por la dirección del servidor accesible desde tu equipo. En el propio servidor también puedes abrir:

```text
http://127.0.0.1:5000/dashboard
```

## 5. Configurar FlightHub 2

Entra a **Configuración**, desde el menú lateral, y completa:

- URL de FlightHub 2 On-Premises.
- X-User-Token.
- Project UUID.
- Workflow UUID predeterminado.
- Creator ID.
- Host Header, si tu integración lo requiere.

Pulsa **Guardar configuración**. El indicador del gateway comprueba conectividad, no ejecuta un workflow.

### FlightHub 2 instalado en el mismo servidor Linux

En **FH2 URL**, usa:

```text
http://127.0.0.1:30812/openapi/v0.1/workflow
```

La conexión se realiza dentro del servidor, por lo que no depende de la IP de su tarjeta de red. Las instalaciones nuevas incluyen esta URL en `.env.example`. Si FlightHub 2 está en otro equipo, usa la IP o el nombre de ese equipo; `127.0.0.1` siempre se refiere al entorno donde corre el middleware.

Esta URL es diferente del endpoint que configuras en HikCentral:

```text
http://IP_DEL_SERVIDOR_LINUX:5000/hik-alert
```

HikCentral debe utilizar una dirección del servidor Linux accesible desde su propia red, no `127.0.0.1`.

**FH2 Host Header** es independiente de la URL y puede depender del enrutamiento interno del AIO. Conserva el valor requerido por tu instalación; no lo sustituyas automáticamente al cambiar de red.

Si actualizas una instalación existente, el instalador conserva `.env`. Revisa y guarda **FH2 URL** desde Configuración para aplicar esta corrección; actualizar GitHub no cambia tus valores privados.


## 6. Registrar workflows y cámaras

Para utilizar respuestas diferentes por cámara:

1. En **Configuración → Workflows disponibles**, pulsa **Agregar workflow**.
2. Escribe un nombre y el UUID de un workflow que ya exista en el mismo proyecto de FlightHub 2.
3. En **Cámaras**, agrega el identificador, nombre y coordenadas de cada cámara.
4. En **Workflow de respuesta**, selecciona el correspondiente o deja **Usar workflow predeterminado**.
5. Guarda los cambios.

Registrar un workflow en esta interfaz no lo crea en DJI ni lo ejecuta.

## 7. Conectar HikCentral

Configura HikCentral para enviar un HTTP POST a:

```text
http://IP_DEL_SERVIDOR:5000/hik-alert
```

Utiliza `Content-Type: application/json` y un cuerpo con el identificador de la cámara registrada:

```json
{"camera_id":"cam01"}
```

Al recibir esa alerta, el middleware solicita la ejecución del workflow asignado. Revisa el resultado en **Vista general → Eventos recientes**.

## 8. Comprobar el servicio

```bash
sudo systemctl status hikmiddleware
```

Debe aparecer activo. Para consultar los registros:

```bash
sudo journalctl -u hikmiddleware -n 50
```

Para reiniciarlo:

```bash
sudo systemctl restart hikmiddleware
```

Si un evento llega al dashboard y muestra **502: No se pudo conectar con FlightHub 2**, revisa la URL configurada en FlightHub: podría conservar una IP de una red anterior. Esto no confirma un error del UUID. «Gateway accesible» solo confirma conectividad TCP; la aceptación del token, el Host y el workflow requiere una comprobación posterior de la API o un evento operativo controlado.

Si funciona en `127.0.0.1` pero no desde otro equipo, revisa la IP, la conectividad entre equipos y las reglas de acceso al puerto TCP 5000 del servidor.

## Actualizar posteriormente

Desde la carpeta donde clonaste el repositorio:

```bash
git switch main
git pull --ff-only
sudo bash install.sh
```

Antes de actualizar, respalda `.env`, `cameras.json`, `workflows.json` y `logs/` desde `/opt/fh2-hikcentral`. Reinstalar sobre el mismo destino conserva estos datos.

## Trasladar una configuración existente o instalar desde USB

Clonar GitHub copia el programa, **no las credenciales ni las cámaras del servidor anterior**. Una instalación nueva comienza vacía.

Para migrar tus datos o instalar desde un paquete USB sin Internet, consulta la [guía completa de instalación y traslado](docs/INSTALLATION.md). El modo offline necesita dependencias preparadas para la versión de Python y arquitectura del servidor de destino.
