from flask import (
    Flask, render_template, request, redirect, url_for, abort, flash
)
import os
import requests
from dotenv import load_dotenv
import psycopg2
import page_analyzer.utils as utils
from page_analyzer.classes import Repository

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
repo = Repository(conn)
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route("/")
def index():
    return render_template("index.html", url='')


@app.get("/urls")
def get_urls():
    urls = repo.get_all_urls()
    return render_template("urls.html", urls=urls)


@app.route("/urls/<int:url_id>")
def website(url_id):
    url = repo.find_url_by_id(url_id)
    if url is None:
        abort(404)
    checks = repo.get_all_checks(url_id)
    return render_template("website.html", website=url, checks=checks)


@app.post("/urls")
def add_url():
    name = request.form.get('url')
    if not utils.is_valid_url(name):
        flash("Некорректный URL", "danger")
        return render_template("index.html", url=name), 422
    name = utils.clean_url(name)
    url = repo.find_url_by_name(name)
    if url:
        flash("Страница уже существует", "info")
    else:
        url = repo.save_url(name)
        flash("Страница успешно добавлена", "success")
    return redirect(url_for("website", url_id=url.id))


@app.post('/urls/<int:url_id>/checks')
def make_check(url_id):
    url = repo.find_url_by_id(url_id)
    try:
        r = requests.get(url.name)
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
            }
        )
        check = repo.save_check(url_id, status_code, h1, title, description)
        flash("Страница успешно проверена", "success")
        url.last_check = check.created_at
        url.last_status_code = check.status_code
        repo.update_url(url)

    return redirect(url_for('website', url_id=url.id))
