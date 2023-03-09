from core import *
from selector import *

class MultipleMatcher(Matcher):
    def __init__(self, pattern: str='', selectors: list[Selector]=None) -> None:
        super().__init__()

        self.pattern: str = pattern
        
        if not selectors: selectors = []
        self.selectors: list[Selector] = selectors
