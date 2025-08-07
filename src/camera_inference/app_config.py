from pathlib import Path

from pydoover import config


# this is a mapping of the valid object IDs of both yolo8n and yolo8n.
# it would be more future proof for the user to be able to add custom ones,
# but I figure important for the user to know which objects are available, too...
OPTIONS = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    4: "airplane",
    5: "bus",
    6: "train",
    7: "truck",
    8: "boat",
    9: "traffic light",
    10: "fire hydrant",
    11: "stop sign",
    12: "parking meter",
    13: "bench",
    14: "bird",
    15: "cat",
    16: "dog",
    17: "horse",
    18: "sheep",
    19: "cow",
    20: "elephant",
    21: "bear",
    22: "zebra",
    23: "giraffe",
    24: "backpack",
    25: "umbrella",
    26: "handbag",
    27: "tie",
    28: "suitcase",
    29: "frisbee",
    30: "skis",
    31: "snowboard",
    32: "sports ball",
    33: "kite",
    34: "baseball bat",
    35: "baseball glove",
    36: "skateboard",
    37: "surfboard",
    38: "tennis racket",
    39: "bottle",
    40: "wine glass",
    41: "cup",
    42: "fork",
    43: "knife",
    44: "spoon",
    45: "bowl",
    46: "banana",
    47: "apple",
    48: "sandwich",
    49: "orange",
    50: "broccoli",
    51: "carrot",
    52: "hot dog",
    53: "pizza",
    54: "donut",
    55: "cake",
    56: "chair",
    57: "couch",
    58: "potted plant",
    59: "bed",
    60: "dining table",
    61: "toilet",
    62: "tv",
    63: "laptop",
    64: "mouse",
    65: "remote",
    66: "keyboard",
    67: "cell phone",
    68: "microwave",
    69: "oven",
    70: "toaster",
    71: "sink",
    72: "refrigerator",
    73: "book",
    74: "clock",
    75: "vase",
    76: "scissors",
    77: "teddy bear",
    78: "hair drier",
    79: "toothbrush",
    80: "",
}


class CameraInferenceConfig(config.Schema):
    def __init__(self):
        self.model_name = config.String(
            "Model",
            description="Model to use for inference. Common choices are yolo11n, yolov8n and yolov8n-pose",
            default="yolo11n",
        )

        self.rtsp_uri = config.String(
            "RTSP URI", description="RTSP URI of the camera to analyse"
        )
        self.resize_width = config.Integer(
            "Resize Width",
            description="Width to resize the camera feed to. 0 to disable.",
            default=0,
        )

        self.viewer_port = config.Integer(
            "Viewer Port",
            description="Port to serve the live viewer on. 0 to disable.",
            default=8080,
        )

        self.confidence_threshold = config.Integer(
            "Confidence Threshold",
            description="The confidence threshold for detection",
            minimum=1,
            maximum=100,
            default=70,
        )

        self.whitelist = config.Array(
            "Object Whitelist",
            description="List of object names to track. Empty to track all.",
            element=config.Enum(
                "Name",
                description="Name of the object to track",
                choices=[*OPTIONS.values()],
                default="",
            ),
        )
        # self.blacklist = config.Array(
        #     "Object Blacklist",
        #     description="List of objects to ignore.",
        #     element=config.Enum(
        #         "Name",
        #         description="Name of the object to track",
        #         choices=[*OPTIONS.values()],
        #         default="",
        #     ),
        # )

    @property
    def whitelist_ids(self):
        inv = {v: k for k, v in OPTIONS.items()}
        return [inv[x.value] for x in self.whitelist.elements]


def export():
    CameraInferenceConfig().export(
        Path(__file__).parents[2] / "doover_config.json", "camera_inference"
    )


if __name__ == "__main__":
    export()
