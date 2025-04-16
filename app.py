import logging
from flask import Flask
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

# Register Blueprints
app.register_blueprint(article_controller)
app.register_blueprint(actuator_controller)

# Log that the app has started
logger.info("App is starting...")

if __name__ == '__main__':
    # Log when the app runs
    logger.info("Running the Flask application...")
    app.run(debug=True)
