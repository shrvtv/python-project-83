from flask import Flask, render_template
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

@app.route("/urls")
def urls():
    return render_template("urls.html")
