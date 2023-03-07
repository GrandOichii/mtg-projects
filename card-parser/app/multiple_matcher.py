from core import *
from selector import *

class MultipleMatcher(Matcher):
    def __init__(self) -> None:
        super().__init__()

        self.pattern: str = ''
        
        self.selectors: list[Selector] = []
