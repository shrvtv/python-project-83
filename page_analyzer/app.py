from flask import Flask

app = Flask("page_analyzer")


@app.route("/")
def hello_world():
    return "Hello, World!"
