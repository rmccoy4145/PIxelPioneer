import os
import re

from flask import Flask, flash, redirect, render_template, request, session, send_file, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from auth_decorators import login_required
from image_service import upload_new_image, apply_image_process, get_image_paths, get_image_serve_path, delete_image
from user_service import register_user, login_user, get_user


# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    user_info = None

    if not session:
        return redirect("/login")

    user_id = session["user_id"]
    user_info = get_user(user_id)

    return render_template("index.html", user_info=user_info)

@app.route('/uploadImage', methods=['GET','POST'])
@login_required
def upload_image():
    if request.method == "GET":
        return render_template("upload_image.html")

    if request.method == "POST":
        user_id = session["user_id"]

        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'message': 'No file part in the request'}), 400
        file = request.files['file']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if not file or file.filename == '':
            return jsonify({'message': 'No selected file'}), 400

        try:
            upload_new_image(file, user_id)
        except RuntimeError as e:
            return jsonify({'message': f"Error occurred: {e}"}), 400

        return redirect("/images")

@app.route('/image/<filename>')
@login_required
def serve_image(filename):
    user_id = session["user_id"]

    if not filename.startswith(str(user_id)):
        return jsonify({'message': "Permission Denined"}), 400

    image_path = get_image_serve_path(filename)
    mime_type = f"image/{filename.rsplit('.', 1)[1].lower()}"
    return send_file(image_path, mimetype=mime_type)

@app.route('/processImage', methods=['POST'])
@login_required
def process_image():
    if request.method == "POST":
        user_id = session["user_id"]
        filter_type = request.form["process_type"]
        image_name = request.form["image_name"]

        image = None

        try:
            image = apply_image_process(image_name, user_id, filter_type)
        except:
            return jsonify({'message': 'error applying filter'}), 400

        # Return the image, set the correct MIME type
        return send_file(image, mimetype='image/png')

@app.route('/removeImage', methods=['POST'])
@login_required
def remove_image():
    if request.method == "POST":
        user_id = session["user_id"]
        image_name = request.form["image_name"]

        try:
            delete_image(image_name, user_id)
        except:
            return jsonify({'message': 'error removing image'}), 400

        return jsonify({'message': 'iamge removed'}), 200

@app.route('/images', methods=['GET'])
@login_required
def images():
    if request.method == "GET":
        user_id = session["user_id"]

        image_paths = get_image_paths(user_id)
        return render_template("images.html", image_paths=image_paths)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()
    if request.method == "GET":
        return render_template("login.html")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return jsonify({'message': 'must provide username & password'}), 403

        auth_user = login_user(username, password)

        if auth_user is None:
            return jsonify({'message': 'invalid username and/or password'}), 403

        # Remember which user has logged in
        session["user_id"] = auth_user["id"]

        return jsonify({'message': 'success'}), 200


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            return jsonify({'message': "Username & Password cannot be blank"}), 400

        try:
            register_user(username, password)
        except RunTimeError as e:
            return jsonify({'message': f"Error occurred: {e}"}), 400

    return redirect("/")
