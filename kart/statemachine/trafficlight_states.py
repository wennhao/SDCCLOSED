from enum import Enum, auto

class TrafficLightState(Enum):
    UNKNOWN = auto()
    RED = auto()
    GREEN = auto()

class TrafficLightManager:
    def __init__(self):
        self.state = TrafficLightState.UNKNOWN

    def update(self, detected_red: bool, detected_green: bool):
        if detected_red:
            self.state = TrafficLightState.RED
        elif detected_green:
            self.state = TrafficLightState.GREEN
        else:
            self.state = TrafficLightState.UNKNOWN

    def is_red(self):
        return self.state == TrafficLightState.RED

    def is_green(self):
        return self.state == TrafficLightState.GREEN
