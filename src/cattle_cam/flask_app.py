import logging

from flask import Flask, render_template, Response

app = Flask(__name__)
log = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template("video_player.html")

def gen():
    log.info("in gen")
    from .cattle_cam import global_queue
    while True:
        log.info(f"queue size: {global_queue.qsize()}")
        try:
            frame = global_queue.get()
            log.info(f"frame: {len(frame)}")
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            log.error(e)

@app.route('/video_feed')
def video_feed():
    log.info("in video_feed")
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def main():
    app.run(host='0.0.0.0', port=8083)
