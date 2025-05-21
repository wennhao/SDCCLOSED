# statemachine/detector_manager.py
"""
Detection manager that processes lane, traffic-light, and pedestrian/zebra crossings
and produces simple flags for driving logic.
"""
from enum import Enum, auto

class LaneState(Enum):
    SEARCHING = auto()
    STRAIGHT = auto()
    LEFT = auto()
    RIGHT = auto()
    SHARPLEFT = auto()
    SHARPRIGHT = auto()

class TrafficLightState(Enum):
    NONE = auto()
    RED = auto()
    GREEN = auto()

class LaneFollowingState:
    """
    Handles basic lane following logic based on steering commands.
    """
    def __init__(self):
        self.state = LaneState.SEARCHING

    def update(self, steering_command: str) -> LaneState:
        match steering_command:
            case "turning_left":
                self.state = LaneState.LEFT
            case "turning_right":
                self.state = LaneState.RIGHT
            case "driving_straight":
                self.state = LaneState.STRAIGHT
            case "turning_left_sharp":
                self.state = LaneState.SHARPLEFT
            case "turning_right_sharp":
                self.state = LaneState.SHARPRIGHT
            case _:
                self.state = LaneState.SEARCHING
        return self.state

class MasterStateManager:
    """
    Combines lane state, traffic-light detection, and pedestrian-on-zebra detection
    into simple flags for override and current lane state.
    """
    def __init__(self):
        self.lane_state = LaneFollowingState()
        self.trafficstate = TrafficLightState.NONE
        self.override = False

    @staticmethod
    def _normalize_detections(detections):
        """
        Convert raw detection tuples into unified format:
        (label, box1, box2, info_dict)
        where info_dict contains 'confidence' and optional 'color'.
        """
        normalized = []
        for det in detections:
            if len(det) == 4:
                label, conf, box1, box2 = det
                info = {'confidence': conf}
                # optionally include color if provided as 5th element
            elif len(det) == 5:
                label, conf, box1, box2, info = det
            else:
                # skip unexpected formats
                continue
            normalized.append((label, box1, box2, info))
        return normalized

    @staticmethod
    def _detect_pedestrian_on_zebra(norm_dets):
        """
        Return True if a person overlaps a zebra-crossing box.
        Uses axis-aligned bounding-box overlap.
        """
        zebra_box = None
        ped_box = None
        for label, (x1, y1), (x2, y2), info in norm_dets:
            if label == 'zebra-crossing' and info.get('confidence', 0) > 0.6:
                zebra_box = (x1, y1, x2, y2)
            elif label == 'person' and info.get('confidence', 0) > 0.6:
                ped_box = (x1, y1, x2, y2)
        if zebra_box and ped_box:
            zx1, zy1, zx2, zy2 = zebra_box
            px1, py1, px2, py2 = ped_box
            # check overlap
            return not (px2 < zx1 or px1 > zx2 or py2 < zy1 or py1 > zy2)
        return False

    @staticmethod
    def _update_traffic_state(norm_dets):
        """
        Select the highest-confidence traffic-light detection and return its state.
        Expects info_dict to contain 'color' = 'red'|'green'.
        """
        best_conf = 0.0
        best_state = TrafficLightState.NONE
        for label, _, _, info in norm_dets:
            if label == 'traffic-light' and info.get('confidence', 0) > best_conf:
                best_conf = info['confidence']
                color = info.get('color')
                if color == 'red':
                    best_state = TrafficLightState.RED
                elif color == 'green':
                    best_state = TrafficLightState.GREEN
        return best_state

    def update_states(self, steering_cmd: str, detections: list) -> dict:
        """
        Update lane following, traffic light, and pedestrian-on-zebra flags.

        Args:
            steering_cmd: output from lane detection ('driving_straight', etc.)
            detections: list of raw tuples from object detector
                        each as (label, confidence, (x1,y1), (x2,y2)[, info_dict])
        Returns:
            dict with keys:
              - 'lane_state': current LaneState
              - 'traffic_state': current TrafficLightState
              - 'override': True if must stop (red light or ped-on-zebra)
        """
        # 1) Lane update
        lane = self.lane_state.update(steering_cmd)

        # 2) Normalize raw detections
        norm = self._normalize_detections(detections)

        # 3) Update traffic light state
        self.trafficstate = self._update_traffic_state(norm)

        # 4) Check pedestrian-on-zebra
        ped_on_zebra = self._detect_pedestrian_on_zebra(norm)

        # 5) Override if red light OR pedestrian on zebra
        self.override = (
            self.trafficstate == TrafficLightState.RED
            or ped_on_zebra
        )

        return {
            'lane_state':    lane,
            'traffic_state': self.trafficstate,
            'override':      self.override
        }
