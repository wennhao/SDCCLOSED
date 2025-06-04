from enum import Enum, auto

class CrossStateEnum(Enum):
    SEARCHING = auto()
    READYTOCROSS = auto()
    CROSSING = auto()
    CROSSED = auto()

class CrossManager:
    def __init__(self):
        self.state = CrossStateEnum.SEARCHING

    def update(self, manbox, crossbox):
        if not manbox or not crossbox:
            return False

        man_x1, _, man_x2, _ = manbox
        cross_x1, _, cross_x2, _ = crossbox

        if self.state == CrossStateEnum.SEARCHING:
            if man_x1 < cross_x1 or man_x2 > cross_x2:
                self.state = CrossStateEnum.READYTOCROSS
            elif cross_x1 < man_x1 < man_x2 < cross_x2:
                self.state = CrossStateEnum.CROSSING

        elif self.state == CrossStateEnum.READYTOCROSS:
            if cross_x1 < man_x1 < man_x2 < cross_x2:
                self.state = CrossStateEnum.CROSSING

        elif self.state == CrossStateEnum.CROSSING:
            if man_x1 < cross_x1 or man_x2 > cross_x2:
                self.state = CrossStateEnum.CROSSED

        return self.state in [CrossStateEnum.READYTOCROSS, CrossStateEnum.CROSSING]

    def reset(self):
        self.state = CrossStateEnum.SEARCHING
    
    def alreadycrossed(self):
        self.state = CrossStateEnum.CROSSED

    def waiting(self):
        return self.state == CrossStateEnum.READYTOCROSS

    def crossed(self):
        return self.state == CrossStateEnum.CROSSED