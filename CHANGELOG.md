# Cambios

## 1.0.0 — 2026-09-09

- Dashboard React y diseño compartido en cámaras y configuración, con logotipos locales.
- Catálogo de workflows con nombre y UUID, y asignación individual por cámara.
- Compatibilidad con cámaras existentes mediante el workflow predeterminado.
- Registro del workflow ejecutado en los eventos y protección de workflows asignados frente a eliminación.
- Escrituras atómicas y lectura de configuración por solicitud para Gunicorn con varios procesos.
- Instalador Linux con systemd, usuario de servicio, dependencias fijadas y acceso directo.
- Frontend compilado incluido: instalar desde GitHub no requiere Node.js.
- Empaquetado limpio con opción offline, sin credenciales ni datos reales.
- Pruebas aisladas de workflows, distribución y compatibilidad.
