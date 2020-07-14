from flask import Flask, jsonify

app: Flask = Flask(__name__)


@app.route('/ping')
def pong() -> str:
    return jsonify("pong")
