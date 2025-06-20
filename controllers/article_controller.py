from flask import Blueprint, jsonify, request
from services.article_service import ArticleService

article_controller = Blueprint('article_controller', __name__)
article_service = ArticleService()


@article_controller.route('/api/articles', methods=['POST'])
def get_articles():
    """Fetch and return articles for a specific date as JSON"""
    try:
        # Retrieve the date and language from the JSON body
        data = request.get_json()

        # Ensure that the 'date' field is present in the request body
        date = data.get('date', None)
        language = data.get('language', 'marathi')  # Default to 'marathi'

        if not date:
            return jsonify({"error": "Date parameter is required"}), 400

        # Call the service to get articles for the given date and language
        articles = article_service.get_articles_by_date(date, language)
        return jsonify({"articles": articles}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@article_controller.route('/api/articles/all', methods=['GET'])
def get_all_articles():
    """Fetch and return all articles as JSON based on language"""
    try:
        # Retrieve language from query parameters, default to 'marathi'
        language = request.args.get('language', 'marathi')

        # Call the service to get all articles for the selected language
        articles = article_service.get_all_articles(language)
        return jsonify({"articles": articles}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# To get a specific article by unique_id_url
@article_controller.route('/api/articles/<unique_id_url>', methods=['GET'])
def get_article_by_unique_id_url(unique_id_url):
    """Fetch and return a specific article by unique_id_url as JSON"""
    try:
        # Retrieve language from query parameters, default to 'marathi'
        language = request.args.get('language', 'marathi')

        # Call the service to get the article by unique_id_url and language
        article = article_service.get_article_by_unique_id_url(unique_id_url, language)
        if not article:
            return jsonify({"error": "Article not found"}), 404
        return jsonify({"article": article}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# To get news articles by category keyword in the URL
@article_controller.route('/api/articles/category/<category>', methods=['GET'])
def get_articles_by_category(category):
    """Fetch and return articles filtered by category keyword in URL"""
    try:
        # Retrieve language from query parameters, default to 'marathi'
        language = request.args.get('language', 'marathi')

        # Call the service to get articles by category and language
        articles = article_service.get_articles_by_category(category, language)
        return jsonify({"articles": articles}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@article_controller.route('/api/languages', methods=['GET'])
def get_supported_languages():
    """Return the list of supported languages"""
    from lang_config import LANGUAGE_TABLES
    return jsonify({"languages": list(LANGUAGE_TABLES.keys())}), 200
