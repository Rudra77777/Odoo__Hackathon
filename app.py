from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(_name_)
CORS(app)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

# ------------------------
# ✅ SIGN-UP ROUTE
# ------------------------
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    first_name = data.get('firstName', '').strip()
    last_name = data.get('lastName', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not first_name or not last_name or not email or not password:
        return jsonify(success=False, message="All fields are required"), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify(success=False, message="Invalid email address"), 400

    if len(password) < 8:
        return jsonify(success=False, message="Password must be at least 8 characters"), 400

    if User.query.filter_by(email=email).first():
        return jsonify(success=False, message="Email already registered"), 400

    hashed_password = generate_password_hash(password)

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=hashed_password
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify(success=True, message="Account created successfully"), 201
    except Exception:
        db.session.rollback()
        return jsonify(success=False, message="Server error. Please try again."), 500

# ------------------------
# ✅ SIGN-IN ROUTE
# ------------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify(success=False, message="Email and password are required"), 400

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return jsonify(success=True, message="Login successful", user={
            "id": user.id,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email
        }), 200
    else:
        return jsonify(success=False, message="Invalid email or password"), 401

# ------------------------
# ✅ VIEW USERS
# ------------------------
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_data = []
    for user in users:
        users_data.append({
            "id": user.id,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email
        })
    return jsonify(success=True, users=users_data)

# ------------------------
# ✅ DELETE USER
# ------------------------
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify(success=False, message="User not found"), 404
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify(success=True, message="User deleted successfully"), 200
    except Exception:
        db.session.rollback()
        return jsonify(success=False, message="Server error. Please try again."), 500

# ------------------------
# ✅ RUN APP
# ------------------------
if _name_ == '_main_':
    app.run(debug=True)