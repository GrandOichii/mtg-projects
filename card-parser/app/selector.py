from core import *

class Selector:
    def __init__(self) -> None:
        self.name: str = ''
        self.matchers: list[Matcher] = []
