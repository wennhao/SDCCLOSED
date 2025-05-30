from statemachine.lane_states import *
from statemachine.cross_states import CrossManager

class MasterStateManager:
    def __init__(self):
        self.cross_manager = CrossManager()
        self.lane_state: LaneState = Searching()

    def update_lane_state(self, steering_cmd):
        match steering_cmd:
            case "driving_straight":
                self.lane_state = Straight()
            case "turning_left":
                self.lane_state = Left()
            case "turning_right":
                self.lane_state = Right()
            case "turning_left_sharp":
                self.lane_state = SharpLeft()
            case "turning_right_sharp":
                self.lane_state = SharpRight()
            case _:
                self.lane_state = Searching()

    def update(self, steering_cmd, manbox, crossbox, traffic_light_red):
        self.update_lane_state(steering_cmd)
        crossing_override = self.cross_manager.update(manbox, crossbox)
        override = crossing_override or traffic_light_red
        return {
            "override": override,
            "lane_state": self.lane_state
        }

    def reset_crossing(self):
        self.cross_manager.reset()

    def crossed(self):
        return self.cross_manager.crossed()