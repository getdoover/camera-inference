import cv2
from ultralytics import YOLO
from .hls_streamer import HlsStreamer
import logging
import time

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


# Load model (detects 'cow' class by default if COCO)
model = YOLO("yolov8n.pt")
# model = YOLO("yolov8n-pose.pt")  # or yolov8m/l/x-pose.pt


def stream(rtsp_url: str, process_rate_hz: float = 1):
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    # Print details of the video
    frame_count = 0

    stream_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    stream_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    stream_fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"Stream Width: {stream_width}, Height: {stream_height}, FPS: {stream_fps}")

    frame_process_interval = int(cap.get(cv2.CAP_PROP_FPS) / process_rate_hz)

    hls_streamer = HlsStreamer(
        width=stream_width,
        height=stream_height,
        fps=process_rate_hz
    )
    hls_streamer.start()

    def cleanup_and_exit(sig, frame):
        print(f"\n=== Received signal {sig}, shutting down gracefully ===")
        hls_streamer.stop()
        cap.release()
        print("=== Cleanup complete, exiting ===")
        sys.exit(0)
    
    # Register handlers for both Ctrl+C and Docker stop
    signal.signal(signal.SIGINT, cleanup_and_exit)   # Ctrl+C
    signal.signal(signal.SIGTERM, cleanup_and_exit)  # Docker stop


    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                print("No frame")
                continue
        except Exception as e:
            print(f"Error reading frame: {e}")
            continue

        ## only process every 15th frame
        frame_count += 1
        if frame_count % frame_process_interval != 0:
            continue

        print("Processing frame")
        results = model(frame)
        # for r in results:
        #     for c in r.boxes.cls:
        #         print(model.names[int(c)])

        # Optional: show live preview with bounding boxes drawn on the frame
        # frame = results[0].plot()
        # cv2.imshow("Stream", frame)
        # if cv2.waitKey(1) & 0xFF == ord("q"):
        #     break

        hls_streamer.write(results[0].plot())

        time.sleep(0.01)

    hls_streamer.stop()

if __name__ == "__main__":
    # RTSP stream URL
    RTSP_URL = "rtsp://admin:admin@192.168.50.129:8554/live"
    stream(RTSP_URL)