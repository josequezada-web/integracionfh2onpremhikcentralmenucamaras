# Dashboard React

El dashboard se sirve desde Flask en `/dashboard` y consulta `/api/status` cada cinco segundos. No modifica el backend ni envía comandos a FlightHub.

Los archivos compilados de `static/dist/` se incluyen en el repositorio: el servidor no necesita Node.js ni acceso a un CDN.

Para modificar la interfaz, con Node.js 18 o superior:

```sh
npm ci
npm run build
```

Fuentes: `frontend/dashboard.jsx` y `frontend/dashboard.css`. Después de editar, incluir también los archivos regenerados de `static/dist/`.

Los tres módulos comparten la navegación y estructura de `templates/base.html`, así como la hoja de estilos del dashboard. `static/admin.css` y `static/admin.js` complementan los formularios de cámaras y configuración, que conservan sus rutas POST existentes.


La compilación genera `templates/_assets.html` con versiones basadas en el contenido de los cuatro archivos CSS/JavaScript. Incluye este archivo al desplegar: permite que una recarga normal solicite los recursos actualizados sin reutilizar copias antiguas del navegador.

Después de desplegar cambios de plantillas, recarga el servicio Gunicorn para que todos sus procesos vuelvan a cargarlas. La instalación habitual permite usar `sudo systemctl reload` si el servicio define `ExecReload`; en caso contrario, usa `sudo systemctl restart` con el nombre del servicio instalado. Node.js solo es necesario para compilar, no para ejecutar el middleware.

Los logotipos originales se mantienen en `icons/`. La compilación copia las variantes transparentes seleccionadas (`fh2xhikcentral.png`, `logohikcentral2.png`, `logofh22.png`) a `static/brand/` y genera sus versiones de caché. Las cabeceras de los tres módulos se definen en `templates/base.html`; sus tamaños y distribución adaptable, en `static/admin.css`.
