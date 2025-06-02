from statemachine.lane_states import *
from statemachine.cross_states import CrossManager
from statemachine.trafficlight_states import TrafficLightManager, TrafficLightState

class MasterStateManager:
    def __init__(self):
        self.cross_manager = CrossManager()
        self.lane_state: LaneState = Searching()
        self.traffic_manager = TrafficLightManager()
        self.override = False

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

    def update(self, steering_cmd, manbox, crossbox, detected_red: bool, detected_green: bool):
        self.update_lane_state(steering_cmd)

        crossing_override = self.cross_manager.update(manbox, crossbox)
        
        self.traffic_manager.update(detected_red, detected_green)
        traffic_override = self.traffic_manager.is_red()

        self.override = crossing_override or traffic_override

        return {
            'lane_state': self.lane_state,
            'override': self.override,
            'traffic_state': self.traffic_manager.state
        }

    def reset_crossing(self):
        self.cross_manager.reset()

    def alreadycrossed(self):
        self.cross_manager.alreadycrossed()

    def waiting(self):
        return self.cross_manager.waiting()

    def crossed(self):
        return self.cross_manager.crossed()
