from pydoover.docker import run_app

from .application import CameraInferenceApplication
from .app_config import CameraInferenceConfig

def main():
    """
    Run the application.
    """
    run_app(CameraInference(config=CameraInferenceConfig()))
