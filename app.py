# -*- coding: utf-8 -*-
"""
Flask Web Server for FinBot -- Finance Chatbot
-----------------------------------------------
HOW TO RUN:
  1. pip install flask
  2. python app.py
  3. Open http://localhost:5000 in your browser

Fix for VS Code Unicode error:
  - Open the file in VS Code
  - Bottom-right corner: click on the encoding (e.g. "UTF-8")
  - Select "Save with Encoding" -> "UTF-8"
  OR just run: python -X utf8 app.py
"""

import sys
import os

# Fix for Windows charmap/unicode errors
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from flask import Flask, request, jsonify, render_template
from chatbot_engine import get_response

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    result = get_response(user_message)
    return jsonify(result)


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "bot": "FinBot v1.0"})


if __name__ == "__main__":
    print("\nFinBot Web Server starting...")
    print("Open http://localhost:5000 in your browser\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
