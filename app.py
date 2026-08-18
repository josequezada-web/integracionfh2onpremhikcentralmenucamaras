from flask import Flask

from routes.onprem_routes import onprem_bp
from routes.dashboard_routes import dashboard_bp
from routes.camera_admin_routes import camera_admin_bp
from routes.settings_routes import settings_bp


app = Flask(__name__)


# ==============================
# BLUEPRINTS
# ==============================

app.register_blueprint(onprem_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(camera_admin_bp)
app.register_blueprint(settings_bp)


# ==============================
# RUN DESARROLLO
# ==============================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )