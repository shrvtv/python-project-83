from flask import Flask, render_template, url_for
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/urls")
def urls():
    return render_template("urls.html")
