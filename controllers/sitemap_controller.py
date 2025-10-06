import xml.etree.ElementTree as Et
from flask import Blueprint, Response
from datetime import datetime, timezone, timedelta
from models.article_model import ArticleModel
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
@sitemap_controller.route('/sitemap.xml')
def sitemap_index():
    sitemap_host = "https://api.theheadlineworld.com"
    site_host = "https://www.theheadlineworld.com"

    sitemapindex = Et.Element("sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    article_model = ArticleModel()

    for lang in LANGUAGE_TABLES.keys():
        articles = article_model.get_all_articles(lang)
        latest_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d')

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
        # ✅ Keep a sitemap file on API, but reference www URLs inside those sitemaps
        Et.SubElement(sitemap, "loc").text = f"{sitemap_host}/sitemap-{lang}.xml"
        Et.SubElement(sitemap, "lastmod").text = latest_timestamp

    # ✅ Add news & archive sitemap pointers
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    for special in ["news", "all"]:
        sitemap = Et.SubElement(sitemapindex, "sitemap")
        Et.SubElement(sitemap, "loc").text = f"{sitemap_host}/sitemap-{special}.xml"
        Et.SubElement(sitemap, "lastmod").text = today

    xml_data = Et.tostring(sitemapindex, encoding='utf-8', method='xml')
    return Response(xml_data, mimetype='application/xml')

@sitemap_controller.route('/sitemap-<lang>.xml')
def language_sitemap(lang):
    if lang not in LANGUAGE_TABLES:
        return Response("Language not supported", status=404)

    host_url = "https://www.theheadlineworld.com"
    article_model = ArticleModel()

    now = datetime.now(timezone.utc)

    # First try: last 2 days
    time_threshold = now - timedelta(days=2)

    recent_articles = sorted(
        [a for a in article_model.get_all_articles(lang)
         if a.get("created_at") and a["created_at"] > time_threshold],
        key=lambda a: a.get("created_at") or datetime.min,
        reverse=True
    )

    # Fallback: last 4 days if no recent
    if not recent_articles:
        time_threshold = now - timedelta(days=4)
        recent_articles = sorted(
            [a for a in article_model.get_all_articles(lang)
             if a.get("created_at") and a["created_at"] > time_threshold],
            key=lambda a: a.get("created_at") or datetime.min,
            reverse=True
        )

    urlset = Et.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for article in recent_articles:
        if not article.get("unique_id_url"):
            continue

        loc = f"{host_url}/news/{lang}/{article['unique_id_url']}"
        lastmod = (
            article["article_date_and_time"].isoformat()
            if article.get("article_date_and_time")
            else None
        )

        url_tag = Et.SubElement(urlset, "url")
        Et.SubElement(url_tag, "loc").text = loc
        if lastmod:
            Et.SubElement(url_tag, "lastmod").text = lastmod
        Et.SubElement(url_tag, "changefreq").text = "daily"
        Et.SubElement(url_tag, "priority").text = "0.8"

    xml_data = Et.tostring(urlset, encoding='utf-8', method='xml')
    return Response(xml_data, mimetype='application/xml')

# ✅ News sitemap (last 48h across all languages)
@sitemap_controller.route('/sitemap-news.xml')
def news_sitemap():
    host_url = "https://www.theheadlineworld.com"
    article_model = ArticleModel()
    now = datetime.now(timezone.utc)
    time_threshold = now - timedelta(days=2)

    articles = []
    for lang in LANGUAGE_TABLES.keys():
        arts = article_model.get_all_articles(lang)
        articles.extend([(lang, a) for a in arts if a.get("created_at") and a["created_at"] > time_threshold])

    if not articles:
        time_threshold = now - timedelta(days=4)
        for lang in LANGUAGE_TABLES.keys():
            arts = article_model.get_all_articles(lang)
            articles.extend([
                (lang, a) for a in arts
                if a.get("created_at") and a["created_at"] > time_threshold
            ])

    articles.sort(key=lambda x: x[1].get("created_at") or datetime.min, reverse=True)

    urlset = Et.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for lang, article in articles:
        if not article.get("unique_id_url"):
            continue
        loc = f"{host_url}/news/{lang}/{article['unique_id_url']}"
        lastmod = (
            article["article_date_and_time"].isoformat()
            if article.get("article_date_and_time")
            else None
        )
        url_tag = Et.SubElement(urlset, "url")
        Et.SubElement(url_tag, "loc").text = loc
        if lastmod:
            Et.SubElement(url_tag, "lastmod").text = lastmod
        Et.SubElement(url_tag, "changefreq").text = "hourly"
        Et.SubElement(url_tag, "priority").text = "1.0"

    xml_data = Et.tostring(urlset, encoding='utf-8', method='xml')
    return Response(xml_data, mimetype='application/xml')


# ✅ All sitemap index (splits by year-month)
@sitemap_controller.route('/sitemap-all.xml')
def all_sitemap_index():
    sitemap_host = "https://api.theheadlineworld.com"
    article_model = ArticleModel()
    articles = []
    for lang in LANGUAGE_TABLES.keys():
        articles.extend(article_model.get_all_articles(lang))

    groups = {}
    for a in articles:
        if not a.get("created_at"):
            continue
        dt = a["created_at"]
        ym = dt.strftime("%Y-%B")
        if ym not in groups or dt > groups[ym]:
            groups[ym] = dt

    sitemapindex = Et.Element("sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for ym, last_dt in sorted(groups.items(), reverse=True):
        sitemap = Et.SubElement(sitemapindex, "sitemap")
        # ✅ Sitemap files stay under API domain
        Et.SubElement(sitemap, "loc").text = f"{sitemap_host}/sitemap-all-{ym}.xml"
        Et.SubElement(sitemap, "lastmod").text = last_dt.strftime('%Y-%m-%d')

    xml_data = Et.tostring(sitemapindex, encoding='utf-8', method='xml')
    return Response(xml_data, mimetype='application/xml')


# ✅ Child sitemaps by year-month
@sitemap_controller.route('/sitemap-all-<year>-<month>.xml')
def all_sitemap_by_month(year, month):
    try:
        month_num = datetime.strptime(month, "%B").month
    except ValueError:
        return Response("Invalid month", status=400)
    host_url = "https://www.theheadlineworld.com"
    article_model = ArticleModel()

    articles = []
    for lang in LANGUAGE_TABLES.keys():
        arts = article_model.get_all_articles(lang)
        for a in arts:
            if not a.get("created_at"):
                continue
            dt = a["created_at"]
            if dt.year == int(year) and dt.month == month_num:
                articles.append((lang, a))

    articles.sort(key=lambda x: x[1].get("created_at") or datetime.min, reverse=True)

    urlset = Et.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for lang, article in articles:
        if not article.get("unique_id_url"):
            continue
        loc = f"{host_url}/news/{lang}/{article['unique_id_url']}"
        lastmod = (
            article["article_date_and_time"].isoformat()
            if article.get("article_date_and_time")
            else None
        )
        url_tag = Et.SubElement(urlset, "url")
        Et.SubElement(url_tag, "loc").text = loc
        if lastmod:
            Et.SubElement(url_tag, "lastmod").text = lastmod
        Et.SubElement(url_tag, "changefreq").text = "weekly"
        Et.SubElement(url_tag, "priority").text = "0.5"

    xml_data = Et.tostring(urlset, encoding='utf-8', method='xml')
    return Response(xml_data, mimetype='application/xml')
