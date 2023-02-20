import copy
import re
import json

class JSONObject:
    def to_json(self) -> dict:
        raise Exception('NOT IMPLEMENTED: TO JSON')

    def from_json(j):
        raise Exception('NOT IMPLEMENTED: FROM JSON')


class MTGObject(JSONObject):
    def __init__(self):
        pass
        # TODO


class Effect(JSONObject):
    def __init__(self):
        super().__init__()
        # TODO


class Condition(JSONObject):
    def __init__(self):
        super().__init__()
        # TODO


class When(JSONObject):
    def __init__(self):
        super().__init__()
        # TODO


class Transformer:
    def __init__(self):
        # TODO
        pass

    def get_text(self, j: dict, orig_j: dict):
        # TODO
        pass

    def get_json(self, text: str, orig_text: str):
        # TODO
        pass

class Pipeline(Transformer):
    def __init__(self) -> None:
        super().__init__()
        self.stages: list[Transformer] = []

    def get_text(self, j: dict, orig_j: dict):
        result = copy.deepcopy(j)
        for i, stage in enumerate(self.stages):
            result = stage.get_text(result, orig_j)
        return result

    def get_json(self, text: str, orig_text: str):
        result = str(text)
        for i, stage in enumerate(self.stages):
            result = stage.get_json(result, orig_text)
        return result

def parse_card(card: dict) -> dict:

    return {'amogus': 'sus'}
    # return None