# Centro de Operaciones: instalación y traslado

La aplicación incluye el dashboard React compilado, los logotipos y el backend Flask. El servidor de destino no necesita Node.js. Esta versión agrega workflows por cámara: en **Configuración → Workflows disponibles → Agregar workflow**, registra nombre y UUID; en **Cámaras → Editar cámara → Workflow de respuesta**, elige el destino. El workflow debe existir en el mismo Project UUID configurado en FlightHub 2. Registrar un UUID aquí no crea el workflow en DJI ni lo ejecuta.

Las cámaras antiguas y la opción **Usar workflow predeterminado** conservan el comportamiento anterior. No se permite eliminar del catálogo un workflow asignado. El detalle de los eventos nuevos muestra el UUID utilizado; los eventos anteriores muestran «No registrado».

## Instalar desde GitHub o desde un paquete

Requisitos: Linux con systemd, Python 3.10 o posterior y soporte `venv`/`ensurepip`. La instalación automática de paquetes del sistema está preparada para Debian/Ubuntu; en otras distribuciones, instala esos requisitos con su gestor antes de ejecutar el script. El puerto 5000 debe estar disponible. La aplicación está destinada a una red interna de confianza; conserva el modelo de acceso existente, sin autenticación de usuarios.

Desde GitHub:

```sh
git clone https://github.com/josequezada-web/integracionfh2onpremhikcentralmenucamaras.git
cd integracionfh2onpremhikcentralmenucamaras
sudo bash install.sh
```

Desde el archivo `.tar.gz`, copiado por USB o subido al servidor:

```sh
sha256sum -c centro-operaciones-linux.tar.gz.sha256
tar -xzf centro-operaciones-linux.tar.gz
cd centro-operaciones
sudo bash install.sh
```

El instalador copia los archivos a `/opt/fh2-hikcentral`, crea el usuario de servicio `hikmiddleware`, prepara el entorno virtual y registra el servicio systemd `hikmiddleware`. Las dependencias de Python se instalan con versiones fijadas en `requirements.lock`. Abre `http://IP_DEL_SERVIDOR:5000/dashboard`, completa la conexión en `/settings` y registra las cámaras. No se envían comandos a FlightHub durante la instalación.

No ejecutes el servidor directamente desde la USB: después de instalar puedes retirarla. Con `--target /ruta/permanente` puedes elegir otro directorio. Repetir la instalación sobre el mismo destino conserva `.env`, `cameras.json`, `workflows.json` y `logs/`. Haz copia de esos archivos antes de actualizar. El nombre del servicio y el puerto son fijos: este instalador gestiona una instancia por servidor.

## URL local de FlightHub 2

Cuando ambos servicios están instalados directamente en el mismo servidor Linux, la URL recomendada es `http://127.0.0.1:30812/openapi/v0.1/workflow`. Es el valor incluido en `.env.example` desde v1.0.1. Evita conservar en ese campo una IP de una LAN anterior. Si FlightHub está en otro equipo, usa su IP o nombre; si el middleware está aislado en un contenedor, su loopback no es el del host.

No cambies el endpoint de HikCentral a loopback: HikCentral debe seguir enviando a `http://IP_DEL_SERVIDOR_LINUX:5000/hik-alert`. El Host Header de FlightHub puede ser distinto de ambas direcciones y debe conservar el valor requerido por el AIO.

El instalador no sobrescribe `.env` existente. Para aplicar el cambio a una instalación anterior, guarda la URL correcta en `/settings`; no es necesario reiniciar. «Gateway accesible» comprueba TCP y no garantiza que el workflow se haya ejecutado.

## Acceso directo con logotipo

Si la instalación se ejecuta con `sudo` desde un usuario con escritorio, crea **Centro de Operaciones** en su menú de aplicaciones. Abre el navegador predeterminado con el dashboard. En un servidor sin entorno gráfico, usa el navegador de otro equipo.

Para instalar el acceso directo manualmente en una sesión Linux, incluso apuntando a otro servidor:

```sh
bash scripts/install-shortcut.sh http://192.168.1.50:5000/dashboard
```

No requiere sudo. No inicia el backend: el servicio instalado lo mantiene en ejecución. La entrada usa el [formato de accesos directos de freedesktop.org](https://specifications.freedesktop.org/desktop-entry/latest/recognized-keys.html).

## USB sin Internet

El paquete offline generado en este proyecto incluye wheels para **Linux x86_64 con Python 3.12 y glibc 2.17+**. El destino debe tener previamente Python 3.12, `venv` y `ensurepip`; el paquete no incluye paquetes del sistema ni sirve para Alpine/musl o ARM. Para otro Python o arquitectura, prepara el wheelhouse desde un equipo compatible con ese destino.

```sh
sha256sum -c centro-operaciones-linux-offline-py312-x86_64.tar.gz.sha256
tar -xzf centro-operaciones-linux-offline-py312-x86_64.tar.gz
cd centro-operaciones
bash install.sh --check --offline
sudo bash install.sh --offline
```

El modo offline instala exclusivamente desde `wheelhouse/`, con `--no-index`, según la [documentación de pip para paquetes locales](https://pip.pypa.io/en/stable/user_guide/#installing-from-local-packages). No intenta descargar dependencias ni ejecutar apt. Sigue necesitando conectividad de red interna con HikCentral y FlightHub para operar.

## Generar un paquete para compartir

En el equipo de desarrollo:

```sh
npm ci
npm run build
python3 scripts/package_release.py
```

Para preparar el paquete USB con dependencias, usa Python compatible con el destino:

```sh
python3 -m pip download --only-binary=:all: --dest wheelhouse -r requirements.lock
python3 scripts/package_release.py --wheelhouse wheelhouse --output release/centro-operaciones-linux-offline-py312-x86_64.tar.gz
```

Los archivos salen en `release/`, junto con su SHA256. El empaquetador usa una lista explícita de archivos: excluye credenciales, cámaras, catálogo real de workflows, historial, `.git`, dependencias Node y entornos virtuales. No es una copia de seguridad de la configuración de un cliente.

Para distribuir por GitHub, incluye fuentes, `static/dist/`, `static/brand/` y `templates/_assets.html`. Los paquetes y `wheelhouse/` no se añaden al historial; pueden adjuntarse a una publicación de GitHub. La versión 1.0.1 está identificada por la etiqueta `v1.0.1`.

## Operación y comprobaciones

```sh
sudo systemctl status hikmiddleware
sudo systemctl reload hikmiddleware
sudo journalctl -u hikmiddleware -n 50
python3 -m unittest discover -s tests -v
```

El instalador nuevo define una recarga gradual con `ExecReload`. En instalaciones antiguas sin esa directiva, usa `sudo systemctl restart hikmiddleware` después de actualizar. Las asignaciones y los cambios guardados en la interfaz se leen desde disco en cada solicitud, por lo que no requieren reinicio y funcionan con ambos procesos Gunicorn.


## Trasladar los datos de una instalación existente

Clonar el repositorio instala el programa, pero no copia la configuración privada del servidor anterior. Si deseas conservarla, respalda `.env`, `cameras.json`, `workflows.json` (si existe) y la carpeta `logs/` desde el directorio que usa ese servidor. No los subas a GitHub.

Instala primero en el destino. Detén `hikmiddleware` antes de restaurar esos archivos en `/opt/fh2-hikcentral`, asígnalos al usuario/grupo `hikmiddleware` y deja los JSON y `.env` con permisos `600`. Después inicia el servicio. Si elegiste otro `--target`, utiliza esa ruta. Revisa las IP y la conectividad con el AIO; el endpoint configurado en HikCentral debe apuntar al servidor nuevo.

Una instalación antigua puede tener su servicio apuntando a una carpeta del usuario. El instalador actual utiliza `/opt/fh2-hikcentral`: respalda y traslada los archivos privados antes de sustituir ese servicio. No asumas que cambiar de ruta mueve los datos automáticamente.
