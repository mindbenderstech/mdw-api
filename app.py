import logging
import os

from flask import Flask, send_from_directory, Response, request
from flask_cors import CORS
from controllers.article_controller import article_controller
from controllers.actuator_controller import actuator_controller
from controllers.auth_controller import auth_controller, init_jwt

from controllers.sitemap_controller import sitemap_controller


# Configure logging globally for the entire application
logging.basicConfig(
    level=logging.INFO,  # Change to logging.DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Logs to the console
    ]
)

# Get the logger for the main app
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# (Optionally tighten CORS to your admin UI origin)
# CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": os.getenv("ADMIN_UI_ORIGIN", "http://localhost:3000")}})
CORS(app)

# ✅ INIT JWT **before** registering blueprints
init_jwt(app)

IMAGE_DIR = r'F:\Media World\mdw-scraper\images'

@app.route('/images/<path:filename>')
def serve_image(filename):
    normalized_filename = filename.replace("\\", "/")
    full_image_path = os.path.join(IMAGE_DIR, normalized_filename)
    logger.info(f"Serving image from path: {full_image_path}")
    return send_from_directory(IMAGE_DIR, normalized_filename)

# Register Blueprints
app.register_blueprint(article_controller)
app.register_blueprint(actuator_controller)
app.register_blueprint(auth_controller)
app.register_blueprint(sitemap_controller)

# Log that the app has started
logger.info("App is starting...")

if __name__ == '__main__':
    # Log when the app runs
    logger.info("Running the Flask application...")
    # previous code app.run(debug=True)

    app.run(host='0.0.0.0', debug=True)
