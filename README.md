# HikCentral × DJI FlightHub 2 On-Premises Integration

Middleware para integrar eventos de **HikCentral** con workflows de **DJI FlightHub 2 On-Premises (AIO)**.

El sistema recibe eventos HTTP generados por HikCentral, identifica la cámara que originó el evento, obtiene sus coordenadas configuradas localmente y solicita la ejecución de un workflow en FlightHub 2.

---

## Arquitectura

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
