# Documentación histórica

Referencia de versiones anteriores. Para instalar o actualizar la versión actual, usa [INSTALLATION.md](INSTALLATION.md).

# HikCentral × DJI FlightHub 2 On-Premises Integration

Middleware para integrar eventos de **HikCentral** con workflows de **DJI FlightHub 2 On-Premises (AIO)**.

El sistema recibe eventos HTTP generados por HikCentral, identifica la cámara que originó el evento, obtiene sus coordenadas configuradas localmente y solicita la ejecución de un workflow en FlightHub 2.

El objetivo principal del proyecto es desacoplar HikCentral de la lógica específica de DJI FlightHub 2, permitiendo administrar cámaras, coordenadas y configuración FH2 desde una interfaz web.

## Versión actual: workflows por cámara e instalación Linux

Registra varios workflows en **Configuración** y selecciona uno en cada **Cámara**. Las cámaras existentes siguen usando el workflow predeterminado.

Consulta la [guía de instalación, acceso directo y distribución por GitHub o USB](docs/INSTALLATION.md) para esta versión. Incluye instalación offline, paquetes sin datos privados y actualización del servicio. Esta guía reemplaza las instrucciones históricas de instalación que aparecen más abajo.

---

# 1. Arquitectura

```text
HikCentral
    |
    | HTTP POST
    | {"camera_id":"cam01"}
    v
+----------------------------------+
| HikCentral / FH2 Middleware      |
|                                  |
| Flask + Gunicorn                 |
|                                  |
| /hik-alert                       |
| /dashboard                       |
| /cameras                         |
| /settings                        |
+----------------------------------+
    |
    | DJI OpenAPI
    | X-User-Token
    | x-project-uuid
    v
DJI FlightHub 2 On-Premises
    |
    v
Workflow FH2
    |
    v
Acción configurada en FlightHub 2
```

HikCentral únicamente necesita enviar un identificador de cámara:

```json
{
  "camera_id": "cam01"
}
```

El middleware se encarga de agregar:

- Project UUID
- Workflow UUID
- Creator ID
- X-User-Token
- coordenadas de la cámara
- nivel del evento
- descripción
- Host Header requerido por FlightHub 2

---

# 2. Flujo general

El flujo completo es:

```text
HikCentral detecta un evento
        |
        v
HTTP POST /hik-alert
        |
        v
Middleware recibe camera_id
        |
        v
Busca cámara en cameras.json
        |
        v
Obtiene nombre + latitud + longitud
        |
        v
Construye payload DJI
        |
        v
POST FlightHub 2 OpenAPI
        |
        v
FH2 ejecuta workflow
        |
        v
Evento almacenado en historial
        |
        v
Dashboard se actualiza
```

---

# 3. Funciones principales

El proyecto incluye:

- Receptor HTTP para HikCentral.
- Integración con DJI FlightHub 2 On-Premises OpenAPI.
- Administración web de cámaras.
- Coordenadas diferentes para cada cámara.
- Configuración web de FlightHub 2.
- Dashboard operativo.
- Historial local de eventos.
- Contadores diarios de eventos.
- Estado del middleware.
- Estado de conectividad con FH2.
- Gunicorn como servidor WSGI.
- Servicio `systemd`.
- Inicio automático después de reiniciar Linux.
- Instalador automático.
- Herramienta de diagnóstico.
- Configuración preparada para cambiar de red o AIO.

---

# 4. Endpoints

## Dashboard

```text
http://IP_AIO:5000/dashboard
```

Muestra información como:

- eventos del día
- workflows correctos
- errores
- último evento recibido
- estado del middleware
- cámaras configuradas
- último evento por cámara
- historial reciente

El dashboard consulta periódicamente:

```text
/api/status
```

para actualizar la información sin recargar manualmente la página.

---

## Administración de cámaras

```text
http://IP_AIO:5000/cameras
```

Permite:

- agregar cámaras
- editar cámaras
- eliminar cámaras
- definir coordenadas
- consultar el `camera_id`
- consultar el JSON que debe configurarse en HikCentral

Ejemplo:

```json
{
  "camera_id": "cam01"
}
```

El endpoint mostrado para HikCentral se genera automáticamente usando la dirección con la que se accede al AIO.

Por ejemplo, si se abre:

```text
http://192.168.10.25:5000/cameras
```

la interfaz mostrará:

```text
http://192.168.10.25:5000/hik-alert
```

Esto facilita mover el sistema entre distintas redes.

---

## Settings

```text
http://IP_AIO:5000/settings
```

Permite configurar:

- FH2 URL
- X-User-Token
- Project UUID
- Workflow UUID
- Creator ID
- Host Header
- latitud por defecto
- longitud por defecto
- nivel
- descripción

La configuración se almacena en:

```text
.env
```

Este archivo nunca debe publicarse en GitHub.

---

## Receptor HikCentral

```text
POST /hik-alert
```

Ejemplo:

```json
{
  "camera_id": "cam01"
}
```

El `camera_id` debe existir previamente en:

```text
/cameras
```

---

# 5. Estructura del proyecto

```text
.
├── app.py
├── config.py
├── setup.py
├── manager.py
├── cameras.py
│
├── install.sh
├── diagnose.sh
├── requirements.txt
│
├── .env.example
├── .gitignore
│
├── routes/
│   ├── onprem_routes.py
│   ├── dashboard_routes.py
│   ├── camera_admin_routes.py
│   └── settings_routes.py
│
├── services/
│   ├── fh2_service.py
│   ├── camera_service.py
│   ├── event_service.py
│   └── settings_service.py
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── cameras.html
│   └── settings.html
│
└── logs/
    └── events.json
```

---

# 6. Responsabilidad de cada módulo

## app.py

Punto principal de la aplicación Flask.

Registra los diferentes Blueprints:

```text
onprem_routes
dashboard_routes
camera_admin_routes
settings_routes
```

---

## routes/onprem_routes.py

Contiene el endpoint:

```text
/hik-alert
```

Responsabilidades:

1. recibir JSON desde HikCentral
2. leer `camera_id`
3. buscar cámara
4. obtener coordenadas
5. llamar al servicio FH2
6. registrar el resultado

---

## routes/dashboard_routes.py

Gestiona:

```text
/dashboard
/api/status
```

Calcula:

- eventos diarios
- correctos
- errores
- último evento
- último evento por cámara
- estado del middleware

---

## routes/camera_admin_routes.py

Gestiona:

```text
/cameras
/cameras/add
/cameras/edit/<camera_id>
/cameras/delete/<camera_id>
```

Además genera dinámicamente el endpoint de HikCentral a partir de la dirección actual del servidor.

---

## routes/settings_routes.py

Gestiona:

```text
/settings
/settings/save
```

Permite editar configuración FH2 sin modificar manualmente archivos Python.

---

## services/fh2_service.py

Construye y envía el request hacia DJI FlightHub 2.

Incluye headers como:

```text
Content-Type
X-User-Token
x-project-uuid
Host
```

---

## services/camera_service.py

Administra:

```text
cameras.json
```

Permite:

- cargar cámaras
- guardar cámaras
- agregar
- editar
- eliminar
- validar coordenadas

---

## services/event_service.py

Administra:

```text
logs/events.json
```

Guarda información como:

```text
fecha
hora
camera_id
camera_name
latitude
longitude
fh2_status
fh2_response
```

---

## services/settings_service.py

Administra:

```text
.env
```

También permite validar configuración y comprobar conectividad TCP hacia FH2.

---

# 7. Requisitos

El sistema fue desarrollado y probado sobre Linux/Ubuntu en un DJI FlightHub 2 AIO.

Requiere:

```text
Python 3
python3-venv
pip
systemd
acceso de red entre HikCentral y AIO
acceso del middleware al OpenAPI FH2
```

Dependencias Python principales:

```text
Flask
requests
python-dotenv
gunicorn
```

---

# 8. requirements.txt

El proyecto utiliza:

```text
Flask==3.1.3
requests==2.34.2
python-dotenv==1.2.3
gunicorn
```

Para instalar:

```bash
pip install -r requirements.txt
```

---

# 9. Instalación rápida

Clonar el repositorio:

```bash
git clone https://github.com/josequezada-web/integracionfh2onpremhikcentralmenucamaras.git
```

Entrar:

```bash
cd integracionfh2onpremhikcentralmenucamaras
```

Dar permisos al instalador:

```bash
chmod +x install.sh
```

Ejecutar:

```bash
sudo ./install.sh
```

---

# 10. Qué hace install.sh

El instalador realiza automáticamente:

```text
1. Detecta el usuario Linux
2. Detecta el directorio del proyecto
3. Verifica Python
4. Verifica python3-venv
5. Crea el entorno virtual
6. Instala requirements.txt
7. Prepara .env
8. Prepara cameras.json
9. Prepara logs/events.json
10. Crea servicio systemd
11. Habilita inicio automático
12. Arranca Gunicorn
13. Muestra las URLs de acceso
```

Una ventaja importante es que no depende de una ruta fija como:

```text
/home/fhaio/Proyectos/...
```

El script detecta automáticamente la ubicación actual.

---

# 11. Configuración inicial

Después de instalar:

```text
1. Abrir /settings
2. Configurar FlightHub 2
3. Guardar configuración
4. Abrir /cameras
5. Crear cámaras
6. Configurar HikCentral
7. Ejecutar un evento de prueba
8. Confirmar workflow en FH2
```

---

# 12. Configuración FlightHub 2

Desde:

```text
/settings
```

deben configurarse los valores correspondientes al AIO y al proyecto.

Ejemplo conceptual:

```env
FH2_URL=http://IP_AIO:30812/openapi/v0.1/workflow
FH2_USER_TOKEN=<TOKEN>
FH2_PROJECT_UUID=<PROJECT_UUID>
FH2_WORKFLOW_UUID=<WORKFLOW_UUID>
FH2_CREATOR_ID=<CREATOR_ID>
FH2_HOST_HEADER=192.168.1.1:30812
```

Nunca publicar los valores reales.

---

# 13. X-User-Token

La integración utiliza:

```text
X-User-Token
```

proveniente de la configuración correspondiente de FlightHub 2 / FlightHub Sync.

No se utiliza:

```text
Authorization: Bearer ...
```

para esta integración específica.

El token debe permanecer en:

```text
.env
```

y nunca enviarse al repositorio.

---

# 14. Configuración HikCentral

Todas las cámaras utilizan el mismo endpoint:

```text
http://IP_AIO:5000/hik-alert
```

Lo único que cambia es:

```text
camera_id
```

Ejemplo cámara 1:

```json
{
  "camera_id": "cam01"
}
```

Ejemplo cámara 2:

```json
{
  "camera_id": "cam02"
}
```

El middleware obtiene automáticamente las coordenadas correspondientes.

---

# 15. Ejemplo de cámaras

Ejemplo conceptual:

```json
{
  "cam01": {
    "name": "Camera Demo 01",
    "latitude": 19.432600,
    "longitude": -99.133200
  },
  "cam02": {
    "name": "Camera Demo 02",
    "latitude": 19.433000,
    "longitude": -99.134000
  }
}
```

Las coordenadas anteriores son únicamente de ejemplo.

No publicar coordenadas reales de instalaciones o clientes.

---

# 16. Gunicorn

La aplicación no utiliza el servidor Flask de desarrollo para operación normal.

Se ejecuta con:

```text
Gunicorn
```

administrado por:

```text
systemd
```

Esto permite:

- ejecución continua
- inicio automático
- reinicio del proceso ante fallos
- logs centralizados

---

# 17. systemd

Nombre del servicio:

```text
hikmiddleware.service
```

Estado:

```bash
sudo systemctl status hikmiddleware
```

Reiniciar:

```bash
sudo systemctl restart hikmiddleware
```

Detener:

```bash
sudo systemctl stop hikmiddleware
```

Iniciar:

```bash
sudo systemctl start hikmiddleware
```

Habilitar:

```bash
sudo systemctl enable hikmiddleware
```

Logs en tiempo real:

```bash
sudo journalctl -u hikmiddleware -f
```

Últimos 50 eventos:

```bash
sudo journalctl -u hikmiddleware -n 50
```

---

# 18. Reinicio del AIO

Después de una instalación nueva es recomendable probar:

```bash
sudo reboot
```

Después del reinicio comprobar:

```text
/dashboard
/cameras
/settings
```

y:

```bash
sudo systemctl status hikmiddleware
```

El servicio debe aparecer:

```text
active (running)
```

---

# 19. Diagnóstico automático

El proyecto incluye:

```text
diagnose.sh
```

Dar permisos:

```bash
chmod +x diagnose.sh
```

Ejecutar:

```bash
./diagnose.sh
```

Comprueba automáticamente:

```text
Sistema
Hostname
IP del AIO
Python
venv
Dependencias Python
.env
cameras.json
requirements.txt
Configuración FH2
Cámaras
systemd
Puerto TCP 5000
HTTP local
Conectividad TCP hacia FH2
```

---

# 20. Seguridad de diagnose.sh

`diagnose.sh` no envía un POST al endpoint de workflows.

Por lo tanto:

```text
NO ejecuta workflows
NO despacha drones
NO genera una misión
```

Únicamente realiza comprobaciones locales y pruebas TCP/HTTP seguras.

---

# 21. Migración a otro AIO

Al mover el proyecto a otro AIO pueden cambiar:

```text
IP LAN del AIO
usuario Linux
grupo Linux
directorio del proyecto
X-User-Token
Project UUID
Workflow UUID
Creator ID
FH2 URL
cámaras
coordenadas
IP HikCentral
```

La mayoría de estos cambios no requieren modificar Python.

---

# 22. Qué configurar nuevamente en otro AIO

Normalmente será necesario revisar:

```text
FH2_URL
FH2_USER_TOKEN
FH2_PROJECT_UUID
FH2_WORKFLOW_UUID
FH2_CREATOR_ID
FH2_HOST_HEADER
cameras
```

Esto puede realizarse desde:

```text
/settings
/cameras
```

---

# 23. Cambio de red

Ejemplo:

El AIO originalmente utiliza:

```text
192.168.68.107
```

y después cambia a:

```text
10.20.30.45
```

El endpoint de HikCentral deberá cambiar a:

```text
http://10.20.30.45:5000/hik-alert
```

La pantalla:

```text
/cameras
```

detecta automáticamente la dirección con la que se accede al servidor y muestra el endpoint correspondiente.

---

# 24. FH2_URL al cambiar de red

También debe revisarse:

```text
FH2_URL
```

Por ejemplo:

Antes:

```env
FH2_URL=http://192.168.68.107:30812/openapi/v0.1/workflow
```

Después:

```env
FH2_URL=http://10.20.30.45:30812/openapi/v0.1/workflow
```

Esto se puede modificar desde:

```text
/settings
```

---

# 25. IMPORTANTE: red interna del AIO

No modificar la red interna de FlightHub 2 únicamente para hacerla coincidir con la LAN externa.

La red interna y la red LAN/Station tienen funciones diferentes.

Una configuración interna del AIO puede utilizar:

```text
192.168.1.x
Gateway 192.168.1.1
```

mientras la interfaz LAN puede utilizar:

```text
192.168.68.x
10.x.x.x
172.16.x.x
```

Que cambie la LAN externa no significa que deba cambiarse la red interna de FH2.

Durante las pruebas de este proyecto, modificar la configuración interna para hacerla coincidir con la LAN provocó pérdida de funcionamiento de servicios.

---

# 26. FH2_URL vs FH2_HOST_HEADER

Estas variables tienen funciones diferentes.

Ejemplo:

```env
FH2_URL=http://192.168.68.107:30812/openapi/v0.1/workflow
FH2_HOST_HEADER=192.168.1.1:30812
```

## FH2_URL

Es la dirección mediante la cual el middleware intenta alcanzar el servicio FH2.

## FH2_HOST_HEADER

Es el valor enviado dentro del header:

```text
Host
```

que puede ser requerido por la arquitectura interna de FH2.

Por este motivo ambas configuraciones se mantienen separadas.

Al cambiar de red podría ser necesario cambiar:

```text
FH2_URL
```

sin necesariamente cambiar:

```text
FH2_HOST_HEADER
```

---

# 27. Troubleshooting

Esta sección contiene los problemas más comunes.

---

## Dashboard no abre

Primero revisar:

```bash
sudo systemctl status hikmiddleware
```

Después:

```bash
./diagnose.sh
```

Comprobar puerto:

```bash
ss -ltn | grep 5000
```

Esperado:

```text
0.0.0.0:5000
```

---

## Puerto 5000 no está escuchando

Revisar:

```bash
sudo systemctl status hikmiddleware
```

y:

```bash
sudo journalctl -u hikmiddleware -n 50
```

Posibles causas:

```text
Gunicorn no instalado
venv incorrecto
ruta incorrecta
error Python
puerto ocupado
servicio detenido
```

---

## HikCentral no puede alcanzar el middleware

Desde la máquina donde está HikCentral intentar acceder a:

```text
http://IP_AIO:5000/
```

Si no responde revisar:

```text
IP del AIO
routing
VLAN
firewall
ACL
aislamiento de red
puerto TCP 5000
```

Antes de revisar tokens o workflows debe existir conectividad entre HikCentral y el middleware.

---

## Middleware recibe el evento pero FH2 no responde

Revisar:

```text
FH2_URL
puerto 30812
Host Header
conectividad
estado del AIO
```

Ejecutar:

```bash
./diagnose.sh
```

---

## Cámara desconocida

Si HikCentral envía:

```json
{
  "camera_id": "cam05"
}
```

debe existir exactamente:

```text
cam05
```

en:

```text
/cameras
```

Por ejemplo:

```text
cam05
```

y:

```text
cam5
```

son IDs diferentes.

---

## camera_id faltante

El body debe contener:

```json
{
  "camera_id": "cam01"
}
```

No basta con enviar un JSON vacío.

---

## Coordenadas incorrectas

Revisar:

```text
/cameras
```

Rangos válidos:

```text
Latitude:  -90 a 90
Longitude: -180 a 180
```

Verificar siempre la ubicación antes de ejecutar operaciones reales.

---

## Token inválido

Revisar:

```text
X-User-Token
```

desde la configuración correspondiente de FlightHub 2.

Comprobar que:

```text
no esté vacío
no haya expirado
corresponda al AIO adecuado
```

---

## Project UUID incorrecto

Revisar:

```text
FH2_PROJECT_UUID
```

El proyecto debe coincidir con el proyecto que contiene el workflow.

---

## Workflow UUID incorrecto

Revisar:

```text
FH2_WORKFLOW_UUID
```

El workflow debe existir dentro del proyecto configurado.

Un Project UUID y Workflow UUID que no correspondan pueden provocar errores de FH2.

---

## Creator ID incorrecto

Revisar:

```text
FH2_CREATOR_ID
```

Debe corresponder al contexto requerido por la instalación FH2.

---

## Host Header incorrecto

Si la comunicación TCP funciona pero FH2 rechaza la petición, revisar:

```text
FH2_HOST_HEADER
```

En la instalación utilizada durante el desarrollo se requirió:

```text
192.168.1.1:30812
```

Este valor puede depender de la arquitectura del AIO.

---

## Servicio no inicia

Ejecutar:

```bash
sudo systemctl status hikmiddleware
```

Después:

```bash
sudo journalctl -u hikmiddleware -n 100
```

También:

```bash
./diagnose.sh
```

---

## Cambié Python y dejó de funcionar

Revisar el entorno virtual:

```bash
venv/bin/python --version
```

y:

```bash
venv/bin/pip list
```

Si es necesario:

```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Después:

```bash
sudo systemctl restart hikmiddleware
```

---

## Falta python3-venv

En Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3-venv -y
```

Después volver a crear el entorno virtual.

---

# 28. Orden recomendado de diagnóstico

No diagnosticar los componentes al azar.

Seguir este orden:

```text
1. ¿El AIO tiene IP?
        |
        v
2. ¿HikCentral puede acceder a AIO:5000?
        |
        v
3. ¿Gunicorn/systemd están activos?
        |
        v
4. ¿POST /hik-alert llega al middleware?
        |
        v
5. ¿camera_id existe?
        |
        v
6. ¿FH2_URL es accesible?
        |
        v
7. ¿Token es correcto?
        |
        v
8. ¿Project UUID es correcto?
        |
        v
9. ¿Workflow UUID es correcto?
        |
        v
10. ¿FH2 responde 200?
        |
        v
11. ¿Workflow se ejecuta?
```

---

# 29. Interpretación de HTTP 200

Una respuesta HTTP correcta de FH2 indica que el servidor aceptó la solicitud de workflow.

El dashboard puede mostrar:

```text
WORKFLOW DISPATCHED
```

Esto significa que la solicitud fue aceptada.

No debe interpretarse automáticamente como:

```text
el dron llegó al destino
```

ya que eso corresponde a una etapa operativa posterior.

---

# 30. Archivos sensibles

No deben publicarse:

```text
.env
cameras.json real
logs/
logs/events.json
venv/
tokens
credenciales
coordenadas de clientes
```

El `.gitignore` debe proteger estos archivos.

---

# 31. Comprobar antes de hacer Git push

Antes de publicar cambios:

```bash
git status
```

Comprobar:

```bash
git ls-files .env
```

La salida debería estar vacía.

También se puede revisar:

```bash
git status --ignored
```

---

# 32. Git y SSH

Para evitar autenticación mediante contraseña HTTPS se recomienda utilizar SSH.

Probar:

```bash
ssh -T git@github.com
```

Una autenticación correcta muestra un mensaje similar a:

```text
Hi usuario! You've successfully authenticated...
```

Ejemplo de remote SSH:

```text
git@github.com:josequezada-web/integracionfh2onpremhikcentralmenucamaras.git
```

---

# 33. Actualizar el repositorio

Después de modificar archivos:

```bash
git status
```

Agregar:

```bash
git add .
```

Commit:

```bash
git commit -m "Descripción del cambio"
```

Push:

```bash
git push docs main
```

Si este repositorio se configura posteriormente como `origin`, utilizar:

```bash
git push origin main
```

---

# 34. Seguridad

El proyecto actualmente está pensado principalmente para:

```text
laboratorio
demo
pruebas
red privada/controlada
```

Antes de utilizarlo como producto en producción se recomienda implementar:

- autenticación en `/settings`
- autenticación en `/cameras`
- protección CSRF
- autenticación del endpoint `/hik-alert`
- HTTPS/TLS
- firewall
- ACL
- auditoría
- rotación de tokens
- control de permisos Linux
- backups
- base de datos para eventos
- gestión segura de secretos

Nunca exponer directamente:

```text
/settings
/cameras
/hik-alert
```

a Internet sin controles adicionales.

---

# 35. Consideración sobre Gunicorn y archivos JSON

Actualmente el proyecto utiliza archivos locales:

```text
cameras.json
logs/events.json
.env
```

para persistencia.

Esto es suficiente para una demo o instalación pequeña.

Sin embargo, si se incrementan:

```text
cantidad de eventos
usuarios
workers
instancias
```

pueden existir problemas de concurrencia.

Para una versión más robusta sería recomendable migrar a:

```text
SQLite
PostgreSQL
otra base de datos
```

especialmente para:

```text
eventos
cámaras
configuración
auditoría
```

---

# 36. Consideración sobre múltiples workers

Gunicorn puede ejecutar varios workers.

Sin embargo, cada worker es un proceso independiente.

Si la aplicación modifica configuración en memoria después de guardar `/settings`, ese cambio puede existir únicamente en el worker que atendió la petición.

Además, múltiples procesos escribiendo archivos JSON pueden provocar condiciones de carrera.

Para una instalación pequeña existen dos opciones:

```text
Opción A:
usar un único worker Gunicorn

Opción B:
migrar persistencia/configuración a una arquitectura preparada para concurrencia
```

Para una futura versión de producción se recomienda resolver este punto explícitamente.

---

# 37. Backups

Antes de cambios importantes se recomienda respaldar:

```text
.env
cameras.json
logs/events.json
```

Ejemplo:

```bash
cp .env .env.backup
cp cameras.json cameras.json.backup
cp logs/events.json logs/events.json.backup
```

Nunca subir los backups al repositorio.

---

# 38. Qué hacer al llegar a una nueva instalación

Checklist recomendado:

```text
[ ] Conectar AIO a la red
[ ] Identificar IP LAN
[ ] Confirmar acceso a FlightHub 2
[ ] Clonar repositorio
[ ] Ejecutar install.sh
[ ] Abrir /settings
[ ] Configurar FH2_URL
[ ] Configurar X-User-Token
[ ] Configurar Project UUID
[ ] Configurar Workflow UUID
[ ] Configurar Creator ID
[ ] Revisar Host Header
[ ] Ejecutar diagnose.sh
[ ] Crear cámaras
[ ] Configurar HikCentral
[ ] Probar camera_id
[ ] Confirmar respuesta FH2
[ ] Confirmar workflow
[ ] Reiniciar AIO
[ ] Confirmar inicio automático
```

---

# 39. Qué hacer después de cambiar de red

Checklist:

```text
[ ] Identificar nueva IP del AIO
[ ] Confirmar /dashboard
[ ] Confirmar /cameras
[ ] Confirmar /settings
[ ] Actualizar endpoint HikCentral
[ ] Revisar FH2_URL
[ ] NO modificar automáticamente DHCP interno
[ ] Ejecutar diagnose.sh
[ ] Probar evento
```

---

# 40. Estado actual del proyecto

El flujo validado es:

```text
HikCentral
        |
        v
HTTP POST
        |
        v
Flask / Gunicorn Middleware
        |
        v
DJI FlightHub 2 On-Premises OpenAPI
        |
        v
Workflow
```

También se ha validado:

```text
múltiples cámaras
coordenadas dinámicas
dashboard
historial de eventos
configuración web
cambio de configuración
Gunicorn
systemd
inicio automático
diagnóstico
instalador
endpoint dinámico según IP
```

---

# 41. Mejoras futuras

Posibles evoluciones:

```text
Autenticación
Roles de usuario
CSRF
API key para HikCentral
HTTPS
SQLite/PostgreSQL
Mapa de cámaras
Snapshots
Logs estructurados
Exportación CSV
Auditoría
Docker
Reverse proxy Nginx
Health checks
Alertas
Backups automáticos
Installer mejorado
Actualizador automático
```

---

# 42. Disclaimer

Este proyecto es una integración técnica independiente desarrollada para pruebas, demostración e investigación.

El uso con drones, sistemas de seguridad o automatizaciones físicas debe cumplir:

- procedimientos operativos
- políticas de seguridad
- normativas locales
- restricciones de vuelo
- documentación oficial del fabricante

DJI, FlightHub 2, HikCentral y demás marcas pertenecen a sus respectivos propietarios.