import logging
from pathlib import Path

import jinja2
from aiohttp import web
import aiohttp_jinja2

log = logging.getLogger(__name__)


class CamServer:
    def __init__(self, port, output_queue):
        self.port = port
        self.output_queue = output_queue

    async def start(self):
        log.info(f"Starting web server on port {self.port}")
        app = web.Application()
        app.router.add_get("/", self.index)
        app.router.add_get("/video_feed", self.video_feed)

        log.info("Setting up template engine")
        aiohttp_jinja2.setup(
            app,
            loader=jinja2.FileSystemLoader(
                str(Path(__file__).resolve().parents[2] / "templates")
            ),
        )

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", self.port)
        await site.start()

    async def index(self, request):
        return aiohttp_jinja2.render_template("index.html", request, {})

    async def video_feed(self, request):
        response = web.StreamResponse(
            status=200,
            reason="OK",
            headers={"Content-Type": "multipart/x-mixed-replace; boundary=frame"},
        )
        await response.prepare(request)

        while True:
            log.info(f"queue size: {self.output_queue.qsize()}")
            try:
                frame = await self.output_queue.get()
                log.info(f"frame: {len(frame)}")
                frame = b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                await response.write(frame)
            except Exception as e:
                log.error(e)
                break

        await response.write_eof()
        return response
