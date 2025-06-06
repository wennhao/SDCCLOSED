from enum import Enum, auto
from abc import ABC, abstractmethod

class CarObstacleStateEnum(Enum):
    OVERTAKING_LEFT = auto()
    OVERTAKING_STRAIGHT = auto()
    OVERTAKING_RIGHT = auto()
    OVERTAKEN = auto()
    SEARCHING = auto()

front_detection_distance = 1000
left_detection_distance = 0
right_detection_distance = 2000

steer_frame_amount = 200
straight_frame_amount = 100

class CarObstacleManager():
    def __init__(self):
        self.state = CarObstacleStateEnum.SEARCHING
        self.counter = 0

    def update(self, detected_car, dist_front, dist_left, dist_right):
        if self.state == CarObstacleStateEnum.SEARCHING and detected_car and dist_front < front_detection_distance:
            self.state = CarObstacleStateEnum.OVERTAKING_LEFT
            self.counter = 0
            return "overtaking left"
        elif self.state == CarObstacleStateEnum.OVERTAKING_LEFT:
            self.counter += 1
            if self.counter > steer_frame_amount:
                self.state = CarObstacleStateEnum.OVERTAKING_STRAIGHT
                self.counter = 0
            return "overtaking left"
        elif self.state == CarObstacleStateEnum.OVERTAKING_STRAIGHT:
            if dist_right > right_detection_distance:
                self.counter += 1
                if self.counter > straight_frame_amount:
                    self.state = CarObstacleStateEnum.OVERTAKING_RIGHT
                    self.counter = 0
            return False
        elif self.state == CarObstacleStateEnum.OVERTAKING_RIGHT:
            self.counter += 1
            if self.counter > steer_frame_amount:
                self.state = CarObstacleStateEnum.OVERTAKEN
                self.counter = 0
            return "overtaking right"
        elif self.state == CarObstacleStateEnum.OVERTAKEN:
            self.state = CarObstacleStateEnum.SEARCHING
            return False
        return False
    
    def overtaking(self):
        return self.state == CarObstacleStateEnum.OVERTAKING_LEFT or self.state == CarObstacleStateEnum.OVERTAKING_STRAIGHT or self.state == CarObstacleStateEnum.OVERTAKING_RIGHT