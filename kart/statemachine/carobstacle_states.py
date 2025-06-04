from enum import Enum, auto
from abc import ABC, abstractmethod

class CarObstacleStateEnum(Enum):
    CRASHPREVENTION = auto()
    DETECTED = auto()
    OVERTAKING_LEFT = auto()
    OVERTAKING_STRAIGHT = auto()
    OVERTAKING_RIGHT = auto()
    OVERTAKEN = auto()
    SEARCHING = auto()

class CarObstacleState(ABC):
    @abstractmethod
    def act(self, controller):
        pass

def PreventCrash(CarObstacleState):
    def act(self, controller):
        controller.stop() # Stop the kart to prevent collision

def Searching(CarObstacleState):
    def act(self, controller):
        controller.steer(0.2)
        controller.drive(20)

def Detected(CarObstacleState):
    def act(self, controller):
        controller.steer(0.0)
        controller.drive(0)  # Stop the kart to prevent collision
    
def OvertakingLeft(CarObstacleState):
    def act(self, controller):
        controller.steer(-0.65)  # Steer to the left to overtake
        controller.drive(60)  # Drive at a higher speed to overtake

def OvertakingStraight(CarObstacleState):
    def act(self, controller):
        controller.steer(0.0)  # Keep the kart straight while overtaking
        controller.drive(60)  # Drive at a higher speed to overtake

def OvertakingRight(CarObstacleState):
    def act(self, controller):
        controller.steer(0.65)  # Keep the kart straight while overtaking
        controller.drive(60)  # Drive at a higher speed to overtake