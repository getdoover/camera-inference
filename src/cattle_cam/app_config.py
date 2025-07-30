from pathlib import Path

from pydoover import config


class CattleCamConfig(config.Schema):
    def __init__(self):
        self.rtsp_uri = config.String("RTSP URI", description="RTSP URI of the camera to analyse")


def export():
    CattleCamConfig().export(Path(__file__).parents[2] / "doover_config.json", "cattle_cam")

if __name__ == "__main__":
    export()
