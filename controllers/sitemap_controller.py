import xml.etree.ElementTree as Et
from flask import Blueprint, Response
from datetime import datetime, timezone
from models.article_model import ArticleModel
from datetime import timedelta
from lang_config import LANGUAGE_TABLES

sitemap_controller = Blueprint('sitemap_controller', __name__)

# @app.route('/robots.txt')
# def robots_txt():
#     return Response("""User-agent: *
# Disallow:
#
# Sitemap: https://theheadlineworld.com/sitemap.xml
# """, mimetype='text/plain')

@sitemap_controller.route('/sitemap.xml')
def sitemap_index():
    host_url = "https://api.theheadlineworld.com"  # Correct domain for the sitemap
    sitemapindex = Et.Element("sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    article_model = ArticleModel()

    for lang in LANGUAGE_TABLES.keys():
        articles = article_model.get_all_articles(lang)

        latest_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d')  # fallback
        if articles:
            latest_created_at = max(
                (a.get("created_at") for a in articles if a.get("created_at")),
                default=None
            )
            if latest_created_at:
                latest_created_at: datetime
                latest_timestamp = latest_created_at.strftime('%Y-%m-%d')

        sitemap = Et.SubElement(sitemapindex, "sitemap")
        Et.SubElement(sitemap, "loc").text = f"{host_url}/sitemap-{lang}.xml"
        Et.SubElement(sitemap, "lastmod").text = latest_timestamp

    xml_data = Et.tostring(sitemapindex, encoding='utf-8', method='xml')
    return Response(xml_data, mimetype='application/xml')

@sitemap_controller.route('/sitemap-<lang>.xml')
def language_sitemap(lang):
    if lang not in LANGUAGE_TABLES:
        return Response("Language not supported", status=404)

    host_url = "https://www.theheadlineworld.com"
    article_model = ArticleModel()

    # Get current time
    now = datetime.now(timezone.utc)

    # Set your timeframe for recent articles (e.g., last 24 hours)
    time_threshold = now - timedelta(hours=12)

    # Filter articles that are within the last 24 hours
    recent_articles = sorted(
        [article for article in article_model.get_all_articles(lang)
         if article.get("article_date_and_time") and article["article_date_and_time"] > time_threshold],
        key=lambda a: a.get("article_date_and_time") or datetime.min,
        reverse=True
    )

    urlset = Et.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for article in recent_articles:
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