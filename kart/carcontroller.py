class CarController:
    def __init__(self, bus, debug=False):
        self.bus = bus
        self.debug = debug

    def drive(self, speed: int):
        if not self.debug:
            self.bus.send(forward_message(speed))

    def steer(self, angle: float):
        if not self.debug:
            self.bus.send(steer_message(angle))

    def brake(self, force: int = 100):
        if not self.debug:
            self.bus.send(set_brake_force_message(force))

    def stop(self):
        self.drive(0)
        self.brake()
