import asyncio
import logging

from pydoover.docker import Application


from .app_config import CameraInferenceConfig
from .cam_inference import CamInference
from .web_viewer import CamServer
from .video_capture import VideoCapture

log = logging.getLogger()


class CameraInferenceApplication(Application):
    config: CameraInferenceConfig  # not necessary, but helps your IDE provide autocomplete!

    async def setup(self):
        # this starts a thread to read frames from the camera, we can then get the latest frame with self.capture.read().
        self.capture = VideoCapture(
            self.config.rtsp_uri.value, self.config.resize_width.value
        )

        self.result_queue = asyncio.Queue()
        self.inference_enabled = asyncio.Event()

        self.inference = CamInference(
            self.config,
            self.result_queue,
            self.inference_enabled,
            self.capture,
        )
        self.inference_task = asyncio.create_task(self.inference.run())

        if self.config.viewer_port.value > 0:
            web_server = CamServer(
                self.config.viewer_port.value, self.result_queue
            )
            await web_server.start()

    async def main_loop(self):
        log.info(f"State is: {'on' if self.inference_enabled.is_set() else 'off'}")
        if self.get_tag("inference_enabled", default=True):
            self.inference_enabled.set()
        else:
            self.inference_enabled.clear()
