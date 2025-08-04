import logging
import time

from pydoover.docker import Application


from .app_config import CattleCamConfig

log = logging.getLogger()


class CattleCamApplication(Application):
    config: CattleCamConfig  # not necessary, but helps your IDE provide autocomplete!

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.started: float = time.time()
        # self.ui: CattleCamUI = None
        # self.state: CattleCamState = None

    async def setup(self):
        pass
        # self.ui = CattleCamUI()
        # self.state = CattleCamState()
        # self.ui_manager.add_children(*self.ui.fetch())

    async def main_loop(self):
        log.info(f"State is: {self.state.state}")

        # self.ui.update(
        #     True,
        #     random_value,
        #     time.time() - self.started,
        # )