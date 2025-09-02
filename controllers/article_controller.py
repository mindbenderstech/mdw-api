import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request
import boto3
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required
from services.article_service import ArticleService

load_dotenv()

article_controller = Blueprint('article_controller', __name__)

# Define default_language here
default_language = os.getenv("DEFAULT_LANGUAGE", "hindi")  # Default to 'hindi' if not set

# Initialize ArticleService with default_language
article_service = ArticleService(default_language)

# --- S3 setup (env-driven) ---
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION,
)

def _build_s3_url(bucket: str, region: str, key: str) -> str:
    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

def _upload_file_to_s3(file_storage) -> str:
    """
    Uploads a Werkzeug FileStorage to S3 and returns the public URL.
    Path style: YYYY-MM-DD/<uuid>.<ext>
    """
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Choose a safe extension; default to .jpg if none
    filename = secure_filename(file_storage.filename or "")
    _, ext = os.path.splitext(filename)
    ext = (ext or ".jpg").lower()

    s3_key = f"{today_str}/{uuid.uuid4().hex}{ext}"

    # Upload
    s3_client.upload_fileobj(
        Fileobj=file_storage,
        Bucket=S3_BUCKET_NAME,
        Key=s3_key,
        ExtraArgs={"ContentType": file_storage.mimetype or "image/jpeg"},
    )

    return _build_s3_url(S3_BUCKET_NAME, AWS_DEFAULT_REGION, s3_key)

@article_controller.route('/api/articles', methods=['POST'])
def get_articles():
    """Fetch and return articles for a specific date as JSON"""
    try:
        # Retrieve the date and language from the JSON body
        data = request.get_json()

        # Ensure that the 'date' field is present in the request body
        date = data.get('date', None)
        language = data.get('language', default_language)  # Use default_language if not provided

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
        # Retrieve language from query parameters, default to 'hindi'
        language = request.args.get('language', default_language)

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
        # Retrieve language from query parameters, default to 'hindi'
        language = request.args.get('language', default_language)

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
        # Retrieve language from query parameters, default to 'hindi'
        language = request.args.get('language', default_language)

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


@article_controller.route('/api/articles/submit', methods=['POST'])
@jwt_required()
def submit_article():
    """
    Supports:
      - multipart/form-data (with an optional 'image' file)
      - application/json (no image, or 'image_path' pre-supplied)
    Stores image to S3 and saves the resulting image URL in DB.
    """
    try:
        # Prefer multipart/form-data first
        if request.files or request.form:
            form = request.form

            title = form.get('title')
            slug = form.get('slug')
            news_source_url = form.get('news_source_url')
            byline_author = form.get('byline_author')
            article_detail = form.get('article_detail')
            article_date = form.get('article_date')
            language = form.get('language', default_language)

            image_file = request.files.get('image')

        else:
            # Fallback: JSON body
            data = request.get_json() or {}
            title = data.get('title')
            slug = data.get('slug')
            news_source_url = data.get('news_source_url')
            byline_author = data.get('byline_author')
            article_detail = data.get('article_detail')
            article_date = data.get('article_date')
            language = data.get('language', default_language)
            image_file = None  # JSON can still pass 'image_path' directly if you want

        # Validate required fields
        missing = [k for k, v in {
            'title': title,
            'slug': slug,
            'news_source_url': news_source_url,
            'byline_author': byline_author,
            'article_detail': article_detail,
            'article_date': article_date,
            'language': language,
        }.items() if not v]
        if missing:
            return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

        # Upload image if provided
        image_path = ""
        if image_file:
            image_path = _upload_file_to_s3(image_file)
            # Example result:
            # https://headliness-website-images.s3.ap-south-1.amazonaws.com/2025-08-14/23cd75a917864b3796e60f4547e832be.jpg

        # Save article
        article = article_service.save_custom_article({
            "title": title,
            "slug": slug,
            "news_source_url": news_source_url,
            "byline_author": byline_author,
            "article_detail": article_detail,
            "article_date": article_date,
            "language": language,
            "image_path": image_path,  # stored in DB
        })

        return jsonify({"message": "Article submitted successfully", "article": article}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
@article_controller.route('/api/articles/latest', methods=['GET'])
def latest_articles():
    try:
        language = request.args.get('language', default_language)
        limit = int(request.args.get('limit', 6))
        offset = int(request.args.get('offset', 0))
        data = article_service.latest(language, limit, offset)
        return jsonify({"articles": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@article_controller.route('/api/articles/category/<category>/latest', methods=['GET'])
def latest_by_category(category):
    try:
        language = request.args.get('language', default_language)
        limit = int(request.args.get('limit', 8))
        data = article_service.category(category, language, limit)
        return jsonify({"articles": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@article_controller.route('/api/articles/trending', methods=['GET'])
def trending_articles():
    try:
        language = request.args.get('language', default_language)
        pick = int(request.args.get('pick', 5))
        data = article_service.trending(language, pick)
        return jsonify({"articles": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
