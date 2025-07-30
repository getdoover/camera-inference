from pydoover.docker import run_app

from .application import CattleCamApplication
from .app_config import CattleCamConfig

def main():
    """
    Run the application.
    """
    run_app(CattleCamApplication(config=CattleCamConfig()))
