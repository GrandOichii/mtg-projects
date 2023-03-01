from parsers import *
from effect import *

class When(MTGObject):
    def __init__(self):
        super().__init__()


class Condition(MTGObject):
    def __init__(self):
        super().__init__()


class Triger(MTGObject):
    def __init__(self):
        super().__init__()

        self.when: When = None
        self.condition: Condition = None
        self.effect: Effect = None
        # TODO add where

    def from_json(j: dict):
        # TODO
        return super().from_json()