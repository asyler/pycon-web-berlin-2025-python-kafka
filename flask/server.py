import json
import socket
from collections import defaultdict
from io import BytesIO
from threading import Thread, Event

import qrcode
from flask_socketio import SocketIO
from flask import Flask, request, jsonify, render_template, send_file

from kafka.consumer import read_messages_once, read_messages_live, read_messages_new
from kafka.producer import send_message

app = Flask(__name__)
socketio = SocketIO(app)

KAFKA_TOPIC = 'page-clicks'


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('10.255.255.255', 1))
    return s.getsockname()[0]

@app.route('/qr')
def qr():
    # Get the local IP and generate the full URL for the page
    local_ip = get_local_ip()
    page_url = f"http://{local_ip}:5001/"

    # Generate a QR code for the URL
    qr = qrcode.QRCode(version=1, box_size=100, border=5)
    qr.add_data(page_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Return the QR code as an image response
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype='image/png', as_attachment=False, download_name='qrcode.png')

@app.route('/log-click', methods=['POST'])
def log_click():
    image_id = request.get_data(as_text=True)
    send_message(KAFKA_TOPIC, image_id, partition=int(image_id)-1)
    return "OK", 200

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats')
def stats():
    stats_dict = defaultdict(int)
    for image_id in read_messages_once(KAFKA_TOPIC):
        stats_dict[image_id] += 1
    return jsonify(stats_dict), 200

@app.route('/stats_partitioned')
def stats_partitioned():
    stats_dict = {}
    for i in range(1, 5):
        try:
            fr = open(f'flask/static/stats_{i}.json', 'r')
            stats_dict[i] = fr.read()
            fr.close()
        except FileNotFoundError:
            pass
    return jsonify(stats_dict), 200

@app.route('/live')
def live():
    return render_template('live.html')

@app.route('/process')
def process():
    stats_dict = defaultdict(int)
    try:
        fr = open('flask/static/stats.json', 'r')
        stats_dict.update(json.loads(fr.read()))
        fr.close()
    except FileNotFoundError:
        pass
    for image_id in read_messages_new(KAFKA_TOPIC):
        stats_dict[image_id] += 1
    fw = open('flask/static/stats.json', 'w')
    fw.write(json.dumps(stats_dict))
    fw.close()
    return "OK", 200

@app.route('/process/<image_id>')
def process_by_id(image_id):
    try:
        fr = open(f'flask/static/stats_{image_id}.json', 'r')
        stats = int(fr.read())
        fr.close()
    except FileNotFoundError:
        stats = 0
    for _ in read_messages_new(KAFKA_TOPIC, partition=int(image_id)-1):
        stats += 1
    fw = open(f'flask/static/stats_{image_id}.json', 'w')
    fw.write(str(stats))
    fw.close()
    return "OK", 200

stop_events = {}
threads = {}

def kafka_consumer_thread(stop_event, sid):
    for image_id in read_messages_live(KAFKA_TOPIC, stop_event, sid):
        socketio.emit('response', {'data': image_id})

@socketio.on('connect')
def handle_connect():
    stop_events[request.sid] = stop_event = Event()
    threads[request.sid] = thread = Thread(
        target=kafka_consumer_thread, args=(stop_event, request.sid)
    )
    thread.start()

@socketio.on("disconnect")
def handle_disconnect():
    stop_events[request.sid].set()
    threads[request.sid].join()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)
