from core import *

class SingleMatcher(Matcher):
    def __init__(self) -> None:
        super().__init__()


class TestSingleMatcher(SingleMatcher):
    def __init__(self) -> None:
        super().__init__()


IMPLEMENTED_SINGLE_MATCHERS = {
    'SM1': TestSingleMatcher()
}


class SingleMatcherNode:
    def __init__(self) -> None:
        self.placeholder_name: str = ''

        self.implemented: bool = False

        self.template_name: str = ''