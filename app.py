# URL Shortener API using Flask and SQLite
from flask import Flask, request, jsonify, redirect
import random
import string
import os
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable=False)
    short_url = db.Column(db.String(10), nullable=False, unique=True)


def generate_short_url():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    long_url = data.get('url')
    if not long_url:
        return jsonify({'error': 'Please provide a url'}), 400
    
    short_code = generate_short_url()
    new_url = Url(original_url=long_url, short_url=short_code)
    db.session.add(new_url)
    db.session.commit()
    
    return jsonify({'short_url': f'http://localhost:5000/{short_code}'}), 201

@app.route('/<short_code>')
def redirect_to_original(short_code):
    url_entry = Url.query.filter_by(short_url=short_code).first()
    if url_entry:
        return redirect(url_entry.original_url)
    return jsonify({'error': 'Invalid short URL'}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
