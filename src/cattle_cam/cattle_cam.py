import queue
import threading

import cv2
from ultralytics import YOLO
import logging
import time
import signal
import sys


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


# Load model (detects 'cow' class by default if COCO)
# model = YOLO("yolov8n.pt")
model = YOLO("/app/src/cattle_cam/yolov8n.pt")
# model = YOLO("/app/src/cattle_cam/yolov8n-pose.pt")
# model = YOLO("yolov8n-pose.pt")  # or yolov8m/l/x-pose.pt

global_queue = queue.Queue()


class VideoCapture:
    def __init__(self, name):
        self.cap = cv2.VideoCapture(name, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()  # discard previous (unprocessed) frame
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        frame = self.q.get()
        new_height = int(frame.shape[0] * (640 / frame.shape[1]))
        resized_frame = cv2.resize(frame, (640, new_height))
        return resized_frame


def stream(rtsp_url: str, process_rate_hz: float = 1):
    cap = VideoCapture(
        rtsp_url,
    )

    # # Print details of the video
    frame_count = 0
    #
    stream_width = int(cap.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    stream_height = int(cap.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    stream_fps = int(cap.cap.get(cv2.CAP_PROP_FPS))
    print(f"Stream Width: {stream_width}, Height: {stream_height}, FPS: {stream_fps}")

    frame_process_interval = int(cap.cap.get(cv2.CAP_PROP_FPS) / process_rate_hz)

    from .flask_app import main

    thread = threading.Thread(target=main)
    thread.daemon = True
    thread.start()

    # hls_streamer = HlsStreamer(
    #     width=1280,
    #     height=720,
    #     fps=1,
    #     viewer_port=8082
    # )
    # hls_streamer.start()

    def cleanup_and_exit(sig, frame):
        print(f"\n=== Received signal {sig}, shutting down gracefully ===")
        # hls_streamer.stop()
        # cap.release()
        print("=== Cleanup complete, exiting ===")
        sys.exit(0)

    # Register handlers for both Ctrl+C and Docker stop
    signal.signal(signal.SIGINT, cleanup_and_exit)  # Ctrl+C
    signal.signal(signal.SIGTERM, cleanup_and_exit)  # Docker stop

    # session = requests.Session()
    # session.auth = HTTPDigestAuth('admin', '19HandleyDrive')
    # url = "http://192.168.0.78/cgi-bin/snapshot.cgi?channel=1"

    while True:
        # s = time.perf_counter()
        # frame = session.get(url).content
        # f = time.perf_counter()
        # log.info(f"Got frame in {(f - s)*1000}ms")

        # s = time.perf_counter()
        # data = BytesIO(frame)
        # img = Image.open(data)
        # log.info(f"Opened image in {(time.perf_counter() - s)*1000}ms")
        s = time.perf_counter()
        try:
            frame = cap.read()
            # if not ret:
            #     print("No frame")
            #     continue
        except Exception as e:
            print(f"Error reading frame: {e}")
            continue
        log.info(f"Read frame in {(time.perf_counter() - s) * 1000}ms")

        # only process every 15th frame
        # frame_count += 1
        # if frame_count % frame_process_interval != 0:
        #     continue

        print("Processing frame")
        s = time.perf_counter()
        results = model(frame)
        f = time.perf_counter()
        log.info(f"Processed frame in {(f - s) * 1000}ms")
        # for r in results:
        #     for c in r.boxes.cls:
        #         print(model.names[int(c)])

        # Optional: show live preview with bounding boxes drawn on the frame
        # frame = results[0].plot()
        # cv2.imshow("Stream", frame)
        # if cv2.waitKey(1) & 0xFF == ord("q"):
        #     break

        s = time.perf_counter()
        res = results[0].plot()
        out = cv2.imencode(".jpg", res)[1].tobytes()
        global_queue.put(out)
        log.info(f"queue size: {global_queue.qsize()}")

        # hls_streamer.write(results[0].plot())
        f = time.perf_counter()
        log.info(f"Wrote frame in {(f - s) * 1000}ms")

        # time.sleep(0)

    # hls_streamer.stop()


def main():
    # RTSP stream URL
    logging.basicConfig(level=logging.INFO)

    RTSP_URL = "rtsp://admin:19HandleyDrive@192.168.0.78:554/live"
    stream(RTSP_URL)


if __name__ == "__main__":
    main()
