from termcolor import colored
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


# class CardTransformer(Transformer):
#     def __init__(self):
#         super().__init__()

#     def get_text(self, j: dict, card: dict):
#         # TODO
#         pass

#     def get_json(self, text: str, card: dict):
#         # TODO
#         pass


class TextTransformer(Transformer):
    def __init__(self):
        super().__init__()

    def get_orig_text(self, text: str, card: dict) -> str:
        raise Exception('NOT IMPLEMENTED: get_orig_text')

    def get_fmt_text(self, text: str, card: dict) -> str:
        raise Exception('NOT IMPLEMENTED: get_fmt_text')


class BasicFormatter(TextTransformer):
    def __init__(self, words_path: str, format: str):
        super().__init__()
        self.format: str = format

        self.pairs = []
        words = open(words_path, 'r').read().split('\n')
        for word in words:
            # pattern = re.compile(f'\\b{word}\\b')
            pattern = f'\\b{word}\\b'
            self.pairs += [(word, pattern)]

    def get_fmt_text(self, text: str, card: dict) -> str:
        result = str(text)
        for word, pattern in self.pairs:
            fmt = self.format.format(word)
            print(fmt)
            result = re.sub(pattern, fmt, result)
        return result

    def get_orig_text(self, text: str, card: dict) -> str:
        result = str(text)
        for word, pattern in self.pairs:
            result = re.sub(f'\\b{word}\\b', pattern, result)
        return result

class TextPipeline(Transformer):
    def __init__(self, stages: list[TextTransformer]=None) -> None:
        super().__init__()
        self.stages: list[TextTransformer] = stages
        if not stages:
            self.stages = []

    def _get(self, text: str, card: dict, method):
        result = str(text)
        for i, stage in enumerate(self.stages):
            result = method(stage, result, card)
            # result = stage.__dict__[method](result, card)
        return result

    def get_orig_text(self, text: str, card: dict) -> str:
        return self._get(text, card, lambda stage, text, card: stage.get_orig_text(text, card))

    def get_fmt_text(self, text: str, card: str) -> str:
        return self._get(text, card, lambda stage, text, card: stage.get_fmt_text(text, card))

        # return self._get(text, card, 'get_fmt_text')

text_pipeline = TextPipeline([
    BasicFormatter('creature_types.txt', '[creature_type:{}]'),
    BasicFormatter('keyword_abilities.txt', '[keyword_ability:{}]')
])

def parse_card(card: dict) -> dict:

    # return {'amogus': 'sus'}
    return None