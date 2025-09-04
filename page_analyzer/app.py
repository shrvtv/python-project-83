from flask import (
    Flask, render_template, request, redirect, url_for, abort, flash
)
from validators.url import url as is_valid_url
import os
import requests
from dotenv import load_dotenv
import psycopg2
import page_analyzer.utils as utils
from psycopg2.extras import NamedTupleCursor

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route("/")
def index():
    return render_template("index.html", url='')


@app.get("/urls")
def urls():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id, name, last_check, last_status_code
                FROM urls
                ORDER BY id DESC
            """)
            rows = cur.fetchall()
    return render_template("urls.html", rows=rows)


@app.route("/urls/<int:url_id>")
def website(url_id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute(
                "SELECT id, name, created_at FROM urls WHERE id = %s;",
                (url_id,)
            )
            row = cur.fetchone()
        if row is None:
            abort(404)
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("""
                SELECT id, url_id, status_code, h1,
                       title, description, created_at
                FROM url_checks WHERE url_id = %s
                ORDER BY id DESC;
                """,
                (url_id,)
            )
            checks = cur.fetchall()
    return render_template("website.html", website=row, checks=checks)


@app.post("/urls")
def add_url():
    url = request.form.get('url')
    if not (is_valid_url(url) and len(url) <= 255):
        flash("Некорректный URL", "danger")
        return render_template("index.html", url=url), 422

    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM urls WHERE name = %s;", (url,))
            row = cur.fetchone()
        if row:
            url_id = row[0]
            flash("Страница уже существует", "info")
        else:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO urls (name)
                    VALUES (%s)
                    RETURNING id;
                    """,
                    (url,)
                )
                url_id = cur.fetchone()[0]
            flash("Страница успешно добавлена", "success")

    return redirect(url_for("website", url_id=url_id))


@app.post('/urls/<int:url_id>/checks')
def check(url_id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as cur:
            cur.execute("SELECT name FROM urls WHERE id = %s;", (url_id,))
            url = cur.fetchone().name
        
        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.RequestException:
            flash("Произошла ошибка при проверке", "danger")
        else:
            status_code = r.status_code
            raw_html = r.text
            h1 = utils.extract_tag_value(raw_html, 'h1')
            title = utils.extract_tag_value(raw_html, 'title')
            description = utils.extract_tag_attribute_value(
                raw_html=raw_html,
                tag='meta',
                attribute='content',
                required_attributes={
                    'name': 'description'
                })

            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO url_checks
                    (url_id, status_code, h1, title, description)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING created_at;
                    """,
                    (url_id, status_code, h1, title, description)
                )
                last_check = cur.fetchone()[0]
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE urls
                    SET last_check = %s, last_status_code = %s
                    WHERE id = %s;
                    """,
                    (last_check, status_code, url_id)
                )
    return redirect(url_for('website', url_id=url_id))
