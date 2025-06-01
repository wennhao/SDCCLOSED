from enum import Enum, auto

class LaneState(Enum):
    SEARCHING = auto()
    STRAIGHT = auto()
    LEFT = auto()
    RIGHT = auto()
    SHARPLEFT = auto()
    SHARPRIGHT = auto()

class CrossState(Enum):
    SEARCHING = auto()
    READYTOCROSS = auto()
    CROSSING = auto()
    CROSSED = auto()

class LaneFollowingState:
    """
    Handles basic lane following logic.
    """

    def __init__(self):
        # Possible states: searching_lane, driving_straight, turning_left, turning_right
        self.state = LaneState.SEARCHING

    def update(self, steering_command: str) -> str:
        """
        Update the lane following state based on the steering command.
        """
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
    Combines lane-following logic with simple obstacle override (e.g., zebra crossings).
    """

    def __init__(self):
        self.lane_state = LaneFollowingState()
        self.override = False
        self.cross_bool = False
        self.cross_state = CrossState.SEARCHING

    def check_if_crossing(self, manbox_position, crossbox_position):
        print(manbox_position, crossbox_position)
        print(self.cross_state)
        match self.cross_state:
            case CrossState.SEARCHING:
                if manbox_position[0] < crossbox_position[0] or manbox_position[2] > crossbox_position[2]: #partly outside of crossing
                    self.cross_state = CrossState.READYTOCROSS
                    return True
                elif manbox_position[0] > crossbox_position[0] and manbox_position[2] < crossbox_position[2]: #fully inside crossing
                    self.cross_state = CrossState.CROSSING
                    return True
                else:
                    return False
            case CrossState.READYTOCROSS:
                if manbox_position[0] > crossbox_position[0] and manbox_position[2] < crossbox_position[2]: #fully inside crossing
                    self.cross_state = CrossState.CROSSING
                return True
            case CrossState.CROSSING:
                if manbox_position[0] < crossbox_position[0] or manbox_position[2] > crossbox_position[2]: #partly outside of crossing
                    self.cross_state = CrossState.CROSSED
                    return False
                else:
                    return True
            case CrossState.CROSSED:
                return False
            case _:
                return False
            
    def crossed(self):
        return self.cross_state == CrossState.CROSSED

    def reset_crossing(self):
        self.cross_state = CrossState.SEARCHING
        self.override = False


    def update_states(self, steering_cmd: str, manbox_position, crossbox_position, traffic_light_red) -> dict:
        """
        Updates the lane state and applies override logic based on object detection.

        Args:
            steering_cmd: command from lane detection (turning_left, turning_right, driving_straight, etc.)
            detection_label: label from object detection (e.g., 'zebra-crossing')
            confidence: confidence for the detected label

        Returns:
            dict containing:
                - 'lane_state': current lane following state
                - 'override': whether an override (stop) is active
        """
        # Update lane state
        lane_state = self.lane_state.update(steering_cmd)
        if (manbox_position != [] and crossbox_position != []):
            self.cross_bool = self.check_if_crossing(manbox_position, crossbox_position)
        else:
            self.cross_bool = False
        
        self.override = self.cross_bool or traffic_light_red #add other situations

        return {
            'lane_state': lane_state,
            'override': self.override
        }
        
