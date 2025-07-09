import logging
import os

from flask import Flask, send_from_directory, Response, request
from flask_cors import CORS
from controllers.article_controller import article_controller
from controllers.actuator_controller import actuator_controller
import xml.etree.ElementTree as Et
from datetime import datetime, timezone
from lang_config import LANGUAGE_TABLES
from models.article_model import ArticleModel


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

IMAGE_DIR = r'F:\Media World\mdw-scraper\images'

@app.route('/images/<path:filename>')
def serve_image(filename):
    normalized_filename = filename.replace("\\", "/")
    full_image_path = os.path.join(IMAGE_DIR, normalized_filename)
    logger.info(f"Serving image from path: {full_image_path}")
    return send_from_directory(IMAGE_DIR, normalized_filename)

@app.route('/robots.txt')
def robots_txt():
    return Response("""User-agent: *
Disallow:

Sitemap: https://headliness.com/sitemap.xml
""", mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap_index():
    host_url = request.host_url.rstrip('/')
    sitemapindex = Et.Element("sitemapindex", xmlns="https://www.sitemaps.org/schemas/sitemap/0.9")
    article_model = ArticleModel()

    for lang in LANGUAGE_TABLES.keys():
        articles = article_model.get_all_articles(lang)

        latest_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')  # fallback
        if articles:
            latest_created_at = max(
                (a.get("created_at") for a in articles if a.get("created_at")),
                default=None
            )
            if latest_created_at:
                latest_created_at: datetime
                latest_timestamp = latest_created_at.strftime('%Y-%m-%dT%H:%M:%S')

        sitemap = Et.SubElement(sitemapindex, "sitemap")
        Et.SubElement(sitemap, "loc").text = f"{host_url}/sitemap-{lang}.xml"
        Et.SubElement(sitemap, "lastmod").text = latest_timestamp

    xml_data = Et.tostring(sitemapindex, encoding='utf-8', method='xml')
    return Response(xml_data, mimetype='application/xml')

@app.route('/sitemap-<lang>.xml')
def language_sitemap(lang):
    if lang not in LANGUAGE_TABLES:
        return Response("Language not supported", status=404)

    host_url = request.host_url.rstrip('/')
    article_model = ArticleModel()

    articles = sorted(
        article_model.get_all_articles(lang),
        key=lambda a: a.get("article_date_and_time") or datetime.min,
        reverse=True
    )

    urlset = Et.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for article in articles:
        if not article.get("unique_id_url"):
            continue

        loc = f"{host_url}/news/{lang}/{article['unique_id_url']}"
        lastmod = article["article_date_and_time"].isoformat() if article.get("article_date_and_time") else None

        url_tag = Et.SubElement(urlset, "url")
        Et.SubElement(url_tag, "loc").text = loc
        if lastmod:
            Et.SubElement(url_tag, "lastmod").text = lastmod
        Et.SubElement(url_tag, "changefreq").text = "daily"
        Et.SubElement(url_tag, "priority").text = "0.8"

    xml_data = Et.tostring(urlset, encoding='utf-8', method='xml')
    return Response(xml_data, mimetype='application/xml')


# Register Blueprints
app.register_blueprint(article_controller)
app.register_blueprint(actuator_controller)

# Log that the app has started
logger.info("App is starting...")

if __name__ == '__main__':
    # Log when the app runs
    logger.info("Running the Flask application...")
    # previous code app.run(debug=True)

    app.run(host='0.0.0.0', debug=True)
