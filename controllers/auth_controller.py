# controllers/auth_controller.py
import os, hmac
from datetime import timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token

auth_controller = Blueprint('auth_controller', __name__)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

def _eq(a, b):  # constant-time compare
    return hmac.compare_digest(a.encode(), b.encode())

def init_jwt(app):
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET environment variable is required")
    app.config["JWT_SECRET_KEY"] = secret
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)
    JWTManager(app)


@auth_controller.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    user, pwd = data.get('username', ''), data.get('password', '')
    if _eq(user, ADMIN_USERNAME) and _eq(pwd, ADMIN_PASSWORD):
        token = create_access_token(identity=user)
        return jsonify(access_token=token), 200
    return jsonify(error="Invalid credentials"), 401
