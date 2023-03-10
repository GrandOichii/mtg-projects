import json

class MTGObject:
    def __init__(self) -> None:
        pass

class Matcher(MTGObject):
    def __init__(self, name: str='') -> None:
        self.name: str = name

