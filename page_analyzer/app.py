from flask import Flask, render_template, request, redirect, url_for, abort, flash
from validators.url import url as is_valid_url
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import NamedTupleCursor

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def init_db():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    created_at DATE NOT NULL DEFAULT CURRENT_DATE
                );
            """)
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS url_checks (
                    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                    url_id BIGINT REFERENCES urls(id) ON DELETE CASCADE NOT NULL,
                    status_code SMALLINT,
                    h1 VARCHAR(255),
                    title VARCHAR(255),
                    description TEXT,
                    created_at DATE NOT NULL DEFAULT CURRENT_DATE
                );
            """)


@app.route("/")
def index():
    init_db()
    return render_template("index.html")


@app.get("/urls")
def urls():
    init_db()
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("SELECT id, name FROM urls ORDER BY id DESC;")
            rows = cur.fetchall()
    return render_template("urls.html", rows=rows)


@app.route("/urls/<int:url_id>")
def website(url_id):
    init_db()
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute(
                "SELECT id, name, created_at FROM urls WHERE id = %s;",
                (url_id,)
            )
            website = cur.fetchone()
    if website:
        return render_template("website.html", website=website)
    abort(404)


@app.post("/urls")
def add_url():
    init_db()
    url = request.form.get('url')
    if not (is_valid_url(url) and len(url) <= 255):
        flash("Некорректный URL")
        return render_template(url_for("index"))

    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM urls WHERE name = %s;", (url,))
            url_exists = cur.fetchone() is not None

        if not url_exists:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO urls (name) VALUES (%s);", (url,))

        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("SELECT id FROM urls WHERE name = %s;", (url,))
            website_id = cur.fetchone().id
    return redirect(url_for("website", website_id=website_id))
        
