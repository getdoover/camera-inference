import threading

from queue import Queue, Empty

import cv2


class VideoCapture:
    def __init__(self, rtsp_uri, resize_width: int = None):
        self.resize_width = resize_width
        self.cap = cv2.VideoCapture(rtsp_uri, cv2.CAP_FFMPEG)
        self.q = Queue()

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
                except Empty:
                    pass
            self.q.put(frame)

    def read(self):
        frame = self.q.get()
        if self.resize_width:
            height = int(frame.shape[0] * (self.resize_width / frame.shape[1]))
            frame = cv2.resize(frame, (self.resize_width, height))
        return frame
