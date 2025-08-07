"""
Basic tests for an application.

This ensures all modules are importable and that the config is valid.
"""

def test_import_app():
    from camera_inference.application import CameraInferenceConfig
    assert CameraInferenceConfig

def test_config():
    from camera_inference.app_config import CameraInferenceConfig

    config = CameraInferenceConfig()
    assert isinstance(config.to_dict(), dict)

# def test_ui():
#     from cattle_cam.app_ui import CattleCamUI
#     assert CattleCamUI

def test_state():
    from camera_inference.app_state import CameraInferenceState
    assert CameraInferenceState