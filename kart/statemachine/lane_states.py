from enum import Enum, auto
from abc import ABC, abstractmethod

class LaneStateEnum(Enum):
    SEARCHING = auto()
    STRAIGHT = auto()
    LEFT = auto()
    RIGHT = auto()
    SHARPLEFT = auto()
    SHARPRIGHT = auto()


class LaneState(ABC):
    @abstractmethod
    def act(self, controller):
        pass


class Searching(LaneState):
    def act(self, controller):
        controller.steer(0.2)
        controller.drive(20)

class Straight(LaneState):
    def act(self, controller):
        controller.steer(0.0)
        controller.drive(60)

class Left(LaneState):
    def act(self, controller):
        controller.steer(-0.65)
        controller.drive(70)

class Right(LaneState):
    def act(self, controller):
        controller.steer(0.65)
        controller.drive(30)

class SharpLeft(LaneState):
    def act(self, controller):
        controller.steer(-1.2)
        controller.drive(70)

class SharpRight(LaneState):
    def act(self, controller):
        controller.steer(1.2)
        controller.drive(30)
