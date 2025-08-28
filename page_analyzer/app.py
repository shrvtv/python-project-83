from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask("page_analyzer")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route("/")
def hello_world():
    return "Hello, World!"
