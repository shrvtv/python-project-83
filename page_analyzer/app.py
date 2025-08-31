from flask import Flask, render_template, request, redirect, url_for, abort, flash
from validators.url import url as is_valid_url
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

with psycopg2.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                name VARCHAR(255),
                created_at DATE NOT NULL DEFAULT CURRENT_DATE
            );
        """)

@app.route("/")
def index():
    return render_template("index.html")

@app.get("/urls")
def urls():
    return render_template("urls.html")

@app.route("/urls/<int:website_id>")
def website(website_id):
    if website_id:
        abort(404)

@app.post("/urls")
def add_url():
    url = request.form.get('url')
    if is_valid_url(url) and len(url) <= 255:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO urls (name)
                    VALUES (%s)
                    RETURNING id;
                """, (url,))
                website_id = cur.fetchone()[0]
        return redirect(url_for("website", website_id=website_id))
    else:
        flash("Некорректный URL")
        return render_template(url_for("index"))
