from flask import Blueprint, jsonify, request
from services.article_service import ArticleService

article_controller = Blueprint('article_controller', __name__)
article_service = ArticleService()


@article_controller.route('/api/articles', methods=['POST'])
def get_articles():
    """Fetch and return articles for a specific date as JSON"""
    try:
        # Retrieve the date from the JSON body
        data = request.get_json()

        # Ensure that the 'date' field is present in the request body
        date = data.get('date', None)

        if not date:
            return jsonify({"error": "Date parameter is required"}), 400

        # Call the service to get articles for the given date
        articles = article_service.get_articles_by_date(date)
        return jsonify({"articles": articles}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@article_controller.route('/api/articles/all', methods=['GET'])
def get_all_articles():
    """Fetch and return all articles as JSON"""
    try:
        articles = article_service.get_all_articles()
        return jsonify({"articles": articles}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# to get specific article by unique_id
@article_controller.route('/api/articles/<unique_id>', methods=['GET'])
def get_article_by_unique_id(unique_id):
    """Fetch and return a specific article by unique_id as JSON"""
    try:
        article = article_service.get_article_by_unique_id(unique_id)
        if not article:
            return jsonify({"error": "Article not found"}), 404
        return jsonify({"article": article}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# to get news articles by category keyword in URL
@article_controller.route('/api/articles/category/<category>', methods=['GET'])
def get_articles_by_category(category):
    """Fetch and return articles filtered by category keyword in URL"""
    try:
        articles = article_service.get_articles_by_category(category)
        return jsonify({"articles": articles}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
