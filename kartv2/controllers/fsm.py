# controllers/fsm.py
"""
FSM using the `transitions` library for lane following,
traffic-light, and pedestrian-crossing control.
"""
from transitions import Machine
from enum import Enum, auto

class TrafficLightState(Enum):
    NONE = auto()
    RED = auto()
    GREEN = auto()

class KartFSM:
    """
    Finite State Machine for kart control.
    Defines states and transitions via the `transitions` library.
    """
    states = [
        'search_lane',       # looking for lane
        'follow_lane',       # driving along lane
        'stopped_for_light', # waiting at red light
        'stopped_for_ped'    # waiting for pedestrian
    ]

    transitions = [
        # lane detection
        {'trigger': 'see_lane', 'source': 'search_lane', 'dest': 'follow_lane', 'after': 'on_start_follow'},
        {'trigger': 'lose_lane','source': 'follow_lane','dest': 'search_lane','after': 'on_start_search'},
        # red/green light
        {'trigger': 'see_red',  'source': 'follow_lane','dest': 'stopped_for_light','after':'on_red_light'},
        {'trigger': 'see_green','source': 'stopped_for_light','dest': 'follow_lane','after':'on_green_light'},
        # pedestrian
        {'trigger': 'ped_on_zebra','source': 'follow_lane','dest': 'stopped_for_ped','after':'on_pedestrian'},
        {'trigger': 'ped_clear',  'source': 'stopped_for_ped', 'dest': 'follow_lane','after':'on_ped_clear'}
    ]

    def __init__(self, steer_fn, forward_fn, brake_fn):
        # Action callbacks
        self.steer   = steer_fn
        self.forward = forward_fn
        self.brake   = brake_fn

        # Initialize machine
        self.machine = Machine(model=self,
                               states=KartFSM.states,
                               transitions=KartFSM.transitions,
                               initial='search_lane')

    # Callback methods
    def on_start_follow(self):
        # begin driving at default speed
        self.forward(30)

    def on_start_search(self):
        # stop movement and center steer
        self.forward(0)
        self.steer(0.0)

    def on_red_light(self):
        self.brake(100)

    def on_green_light(self):
        self.forward(30)

    def on_pedestrian(self):
        self.brake(100)

    def on_ped_clear(self):
        self.forward(30)

    def update(self, lane_found: bool,
                     light_state: TrafficLightState,
                     ped_on_cross: bool):
        """
        Send sensor events to advance the FSM.
        Returns the current state name.
        """
        # lane
        if lane_found:
            if self.state == 'search_lane':
                self.see_lane()
        else:
            if self.state == 'follow_lane':
                self.lose_lane()

        # traffic light
        if light_state == TrafficLightState.RED and self.state == 'follow_lane':
            self.see_red()
        elif light_state == TrafficLightState.GREEN and self.state == 'stopped_for_light':
            self.see_green()

        # pedestrian
        if ped_on_cross and self.state == 'follow_lane':
            self.ped_on_zebra()
        elif not ped_on_cross and self.state == 'stopped_for_ped':
            self.ped_clear()

        return self.state
