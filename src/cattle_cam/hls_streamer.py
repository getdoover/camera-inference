import subprocess
import numpy as np
import http.server
import socketserver
import threading
import os
import logging
import uuid

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class SimpleHlsWebViewer:
    def __init__(self, port: int = 8080, static_dir: str = None, stream_file: str = None, page_title: str = "Live Stream"):
        self.port = port
        self.static_dir = static_dir
        
        # Get only the filename from the full path
        self.stream_file = os.path.basename(stream_file)
        self.page_title = page_title

        self.server = None
        self.thread = None

    def start(self):
        # Create HTML content with video.js player
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.page_title}</title>
            <link href="https://vjs.zencdn.net/8.10.0/video-js.css" rel="stylesheet" />
            <style>
                body {{ margin: 0; padding: 20px; background: #1a1a1a; color: white; font-family: Arial, sans-serif; }}
                .container {{ width: 100%; margin: 0 auto; }}
                h1 {{ text-align: center; margin-bottom: 20px; }}
                .video-container {{ width: 100%; }}
                video {{ width: 100%; height: auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{self.page_title}</h1>
                <div class="video-container">
                    <video id="my-video" style="width: 100%; max-height: 80vh;" class="video-js vjs-default-skin" controls preload="auto" data-setup="{{}}">
                        <source src="{self.stream_file}" type="application/x-mpegURL">
                        <p class="vjs-no-js">To view this video please enable JavaScript, and consider upgrading to a web browser that supports HTML5 video.</p>
                    </video>
                </div>
            </div>
            <script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
            <script>
                var player = videojs('my-video');
            </script>
        </body>
        </html>
        """
        
        # Create a simple HTTP server
        class HlsHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(http_self, *args, **kwargs):
                super().__init__(*args, directory=self.static_dir, **kwargs)

            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                    self.send_header('Pragma', 'no-cache')
                    self.send_header('Expires', '0')
                    self.end_headers()
                    self.wfile.write(html_content.encode())
                else:
                    # Fall back to configured directory
                    super().do_GET()

        
        # Start server in a separate thread
        self.server = socketserver.TCPServer(
            ("0.0.0.0", self.port),
            HlsHandler,
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        
        # Get local IP address for network access
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print("Web viewer started at:")
        print(f"  Local: http://localhost:{self.port}")
        print(f"  Network: http://{local_ip}:{self.port}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server = None


class HlsStreamer:
    def __init__(
            self,
            width: int = 1920,
            height: int = 1080,
            fps: int = 25,
            output_file: str = None,
            viewer_port: int = 8080,
        ):
        self.width = width
        self.height = height
        self.fps = fps

        self.output_file = output_file

        self._viewer = None
        self.viewer_port = viewer_port

        self._process = None

    def start(self):
        if self._process is not None:
            return

        self.setup_output_file()

        if self.viewer_port is not None:
            self._viewer = SimpleHlsWebViewer(
                port=self.viewer_port,
                static_dir=self.output_dir,
                stream_file=self.output_file
            )
            self._viewer.start()

        print(f"Output file: {self.output_file}")
        print(f"Output directory: {self.output_dir}")

        # Create FFmpeg command
        ffmpeg_cmd = [
            'ffmpeg',
            # '-loglevel', 'error',  # Only show errors
            # '-v', 'debug',
            '-y',  # Overwrite output
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-s', f'{self.width}x{self.height}',  # Frame size
            '-r', str(self.fps),       # FPS
            '-i', '-',        # Input from stdin
            # '-probesize', '100M',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-tune', 'zerolatency',
            # GOP settings for low latency
            '-g', str(self.fps),  # GOP size = framerate (1 second)
            '-keyint_min', str(self.fps),  # Minimum keyframe interval
            '-sc_threshold', '0',  # Disable scene change detection
            # Low latency HLS settings
            '-f', 'hls',
            '-hls_time', '1',
            # '-hls_part_time', '0.125', 
            # '-hls_segment_options', 'mpegts_flags=+initial_discontinuity'             # Reduced to 1 second segments
            '-hls_list_size', '3',         # Keep 3 segments (3 second buffer)
            # '-hls_flags', 'delete_segments+independent_segments+split_by_time',
            '-hls_segment_type', 'mpegts',  # Use MPEG-TS for better compatibility
            '-hls_delete_threshold', '1',
            '-force_key_frames', 'expr:gte(t,n_forced*1)',  # Keyframe every 1 second
            # Low latency streaming optimizations
            '-flush_packets', '1',
            '-fflags', '+genpts+flush_packets',
            '-max_delay', '0',
            '-avioflags', 'direct',
            self.output_file
        ]

        # Start FFmpeg process
        print(f"Running FFmpeg command: {' '.join(ffmpeg_cmd)}")
        self._process = subprocess.Popen(
            ffmpeg_cmd, 
            stdin=subprocess.PIPE,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE
        )
        
        # Check if process started successfully
        if self._process.poll() is not None:
            stdout, stderr = self._process.communicate()
            print("FFmpeg failed to start:")
            print(f"stdout: {stdout.decode()}")
            print(f"stderr: {stderr.decode()}")
            raise RuntimeError("FFmpeg failed to start")
        
        print(f"FFmpeg process started with PID: {self._process.pid}")
        
        # Wait a moment and check if files are being created
        import time
        time.sleep(1)
        if os.path.exists(self.output_file):
            print(f"HLS playlist file created: {self.output_file}")
        else:
            print(f"Warning: HLS playlist file not yet created: {self.output_file}")

    def setup_output_file(self):
        if self.output_file is None:
            self.output_file = f"/tmp/hls_{str(uuid.uuid4())}/hls_stream.m3u8"
        self.output_dir = os.path.dirname(self.output_file)
        print(f"Output directory: {self.output_dir}")
        # log.info(f"Output directory: {self.output_dir}")
        os.makedirs(self.output_dir, exist_ok=True)
        # remove any existing files in the output directory
        for file in os.listdir(self.output_dir):
            os.remove(os.path.join(self.output_dir, file))

    def write(self, frame: np.ndarray):
        ## resize frame to width and height
        # frame = cv2.resize(frame, (self.width, self.height))
        self._process.stdin.write(frame.tobytes())
        self._process.stdin.flush()

    def stop(self):
        if self._process is not None:
            self._process.terminate()
            self._process = None

        if self._viewer is not None:
            self._viewer.stop()
            self._viewer = None