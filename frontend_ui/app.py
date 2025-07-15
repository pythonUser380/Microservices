from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, static_folder="static", template_folder="templates")

# Docker Compose service name
AUTH_SERVICE_URL = "http://authservice:5000"


# ---------- HTML ROUTES ----------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


# ---------- API PROXIES ----------
@app.route("/auth/login", methods=["POST"])
def proxy_login():
    try:
        resp = requests.post(f"{AUTH_SERVICE_URL}/login", json=request.get_json())
        return (resp.content, resp.status_code, resp.headers.items())
    except requests.exceptions.RequestException:
        return jsonify({"error": "Auth service unreachable"}), 503

@app.route("/auth/signup", methods=["POST"])
def proxy_signup():
    try:
        resp = requests.post(f"{AUTH_SERVICE_URL}/signup", json=request.get_json())
        return (resp.content, resp.status_code, resp.headers.items())
    except requests.exceptions.RequestException:
        return jsonify({"error": "Auth service unreachable"}), 503

@app.route("/auth/profile", methods=["GET"])
def proxy_profile():
    auth_header = request.headers.get("Authorization")
    try:
        resp = requests.get(
            f"{AUTH_SERVICE_URL}/profile",
            headers={"Authorization": auth_header} if auth_header else {}
        )
        return (resp.content, resp.status_code, resp.headers.items())
    except requests.exceptions.RequestException:
        return jsonify({"error": "Auth service unreachable"}), 503

@app.route("/auth/logout", methods=["POST"])
def proxy_logout():
    auth_header = request.headers.get("Authorization")
    try:
        resp = requests.post(
            f"{AUTH_SERVICE_URL}/logout",
            headers={"Authorization": auth_header} if auth_header else {}
        )
        return (resp.content, resp.status_code, resp.headers.items())
    except requests.exceptions.RequestException:
        return jsonify({"error": "Auth service unreachable"}), 503
