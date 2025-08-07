import asyncio
import logging
import time
from typing import TYPE_CHECKING

import cv2
from ultralytics import YOLO


if TYPE_CHECKING:
    from .video_capture import VideoCapture
    from .app_config import CattleCamConfig

log = logging.getLogger(__name__)

class CamInference:
    def __init__(self, config: "CattleCamConfig", result_queue: asyncio.Queue, run_event: asyncio.Event, cap: "VideoCapture"):
        self.run_event = run_event
        self.result_queue = result_queue
        self.cap = cap
        self.config = config

        self.loop = asyncio.get_running_loop()

        model_name = config.model_name.value
        if model_name in ("yolo11n", "yolov8n", "yolov8n-pose"):
            model_name = f"/app/models/{model_name}_ncnn_model"
        else:
            log.info("Using unknown model, this download may take a while...")

        self.model = YOLO(model_name)

    def run_inference(self, frame):
        s = time.perf_counter()
        results = self.model.predict(frame, classes=self.config.whitelist_ids, conf=self.config.confidence_threshold.value / 100)
        log.info(f"Processed frame in {(time.perf_counter() - s) * 1000}ms")
        return results

    def plot_results(self, results):
        s = time.perf_counter()
        res = results[0].plot()
        out = cv2.imencode(".jpg", res)[1].tobytes()
        log.info(f"Encoded frame in {(time.perf_counter() - s) * 1000}ms")
        return out

    async def run(self):
        while True:
            await self.run_event.wait()

            # get latest frame
            s = time.perf_counter()
            try:
                frame = self.cap.read()
            except Exception as e:
                log.error(f"Error reading frame: {e}")
                continue
            log.info(f"Read frame in {(time.perf_counter() - s) * 1000}ms")

            log.info("Processing frame")
            results = await self.loop.run_in_executor(None, self.run_inference, frame)

            log.info("Plotting frame")
            out = await self.loop.run_in_executor(None, self.plot_results, results)

            await self.result_queue.put(out)
            if self.result_queue.full():
                self.result_queue.get_nowait()

            await asyncio.sleep(0.2)
