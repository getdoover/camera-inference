"""
Basic tests for an application.

This ensures all modules are importable and that the config is valid.
"""

def test_import_app():
    from cattle_cam.application import CattleCamApplication
    assert CattleCamApplication

def test_config():
    from cattle_cam.app_config import CattleCamConfig

    config = CattleCamConfig()
    assert isinstance(config.to_dict(), dict)

def test_ui():
    from cattle_cam.app_ui import CattleCamUI
    assert CattleCamUI

def test_state():
    from cattle_cam.app_state import CattleCamState
    assert CattleCamState