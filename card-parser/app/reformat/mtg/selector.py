from core import *

class Selector(MTGObject):
    def __init__(self, name: str='', matchers: list[Matcher]=None) -> None:
        if matchers is None: matchers = []

        self.name: str = name
        self.matchers: list[Matcher] = matchers

