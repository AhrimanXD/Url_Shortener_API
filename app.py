from flask import Flask, request, jsonify, redirect
import os
import random
import string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///urls.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Get BASE_URL from env or fallback to localhost
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False)

def generate_short_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    long_url = data.get("url")
    if not long_url:
        return jsonify({"error": "URL is required"}), 400

    short_code = generate_short_code()
    new_url = URL(original_url=long_url, short_code=short_code)
    db.session.add(new_url)
    db.session.commit()

    short_url = f"{BASE_URL.rstrip('/')}/{short_code}"
    return jsonify({"short_url": short_url}), 201

@app.route('/<short_code>')
def redirect_to_original(short_code):
    url_entry = URL.query.filter_by(short_code=short_code).first()
    if url_entry:
        return redirect(url_entry.original_url)
    return jsonify({"error": "URL not found"}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
