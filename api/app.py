from flask import Flask, request, jsonify, send_file
import os
from dotenv import load_dotenv
from flask_cors import CORS
from figaro import generate_sample_from_description
import uuid
import threading
import config

load_dotenv()

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/submit", methods=['POST'])
def submit():
    data = request.get_json()
    description = data['description']

    uid = str(uuid.uuid4())

    threading.Thread(target=generate_sample_from_description,
                     args=(description, uid)).start()

    return jsonify(
        {
            "task_id": uid
        }
    )

@app.route("/status", methods=['GET'])
def status():
    uid = request.args.get('task_id')
    if os.path.exists(f"./{uid}.wav"):
        return jsonify({
        "status": "ready"
        })
    return jsonify({
        "status": "in_progress"
    })

@app.route("/result", methods=['GET'])
def result():
    uid = request.args.get('task_id')
    return send_file(f"{uid}.wav")

if __name__ == '__main__':
    app.run(debug=True)
