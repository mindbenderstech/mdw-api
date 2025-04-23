import logging
from flask import Flask, send_from_directory
import os
from flask_cors import CORS

from controllers.article_controller import article_controller
from controllers.actuator_controller import actuator_controller

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

CORS(app)

# Serve images from the 'images' folder
IMAGE_DIR = r'F:\Media World\mdw-scraper\images'  # Ensure this path is correct for your image storage

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve an image from the images' directory."""
    normalized_filename = filename.replace("\\", "/")
    full_image_path = os.path.join(IMAGE_DIR, normalized_filename)
    logger.info(f"Serving image from path: {full_image_path}")
    return send_from_directory(IMAGE_DIR, normalized_filename)


# Register Blueprints
app.register_blueprint(article_controller)
app.register_blueprint(actuator_controller)

# Log that the app has started
logger.info("App is starting...")

if __name__ == '__main__':
    # Log when the app runs
    logger.info("Running the Flask application...")
    app.run(debug=True)
