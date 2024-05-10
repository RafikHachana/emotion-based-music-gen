from flask import Flask, request, jsonify, send_file
import os
from dotenv import load_dotenv
from flask_cors import CORS
import uuid
import threading
from emotion2music import generate_sample

load_dotenv()

app = Flask(__name__)

generating = False

CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/submit", methods=['POST'])
def submit():
    global generating
    if generating:
        return jsonify(
            {
                "error": "Already generating a sample"
            }
        ), 400
    data = request.get_json()
    # description = data['description']

    try:
        danceability = data['danceability']
        energy = data['energy']
        valence = data['valence']
        tempo = data['tempo']
        acousticness = data['acousticness']
        instrumentalness = data['instrumentalness']
        key = data['key']
        mode = data['mode']
        time_signature = data['time_signature']
    except KeyError:
        return jsonify(
            {
                "error": "Invalid data"
            }
        ), 400

    uid = str(uuid.uuid4())

    threading.Thread(target=generate_sample,
                     args=(
                        danceability,
                        energy,
                        valence,
                        tempo,
                        acousticness,
                        instrumentalness,
                        key,
                        mode,
                        time_signature,
                        uid
                     )).start()
    generating = True

    return jsonify(
        {
            "task_id": uid
        }
    )

@app.route("/status", methods=['GET'])
def status():
    global generating
    uid = request.args.get('task_id')
    if os.path.exists(f"./{uid}.wav"):
        generating = False
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
