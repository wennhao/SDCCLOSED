# statemachine.py

class LaneFollowingState:
    """
    Handles basic lane following logic.
    """

    def __init__(self):
        # Possible states: searching_lane, driving_straight, turning_left, turning_right
        self.state = "searching_lane"

    def update(self, steering_command: str) -> str:
        """
        Update the lane following state based on the steering command.
        """
        match steering_command:
            case "turning_left":
                self.state = "turning_left"
            case "turning_right":
                self.state = "turning_right"
            case "driving_straight":
                self.state = "driving_straight"
            case _:
                self.state = "searching_lane"
        return self.state


class MasterStateManager:
    """
    Combines lane-following logic with simple obstacle override (e.g., zebra crossings).
    """

    def __init__(self):
        self.lane_state = LaneFollowingState()
        self.override = False

    def update_states(self, steering_cmd: str, detection_label: str = None, confidence: float = 0.0) -> dict:
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

        # Override logic: stop at zebra crossings
        if detection_label == 'zebra-crossing' and confidence > 0.6:
            self.override = True
        else:
            self.override = False

        return {
            'lane_state': lane_state,
            'override': self.override
        }
