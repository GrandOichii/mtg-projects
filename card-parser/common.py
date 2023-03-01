from util import read_cards
import re

class JSONObject:
    def to_json(self):
        raise Exception('NOT IMPLEMENTED: to_json')

    def from_json(j: dict):
        raise Exception('NOT IMPLEMENTED: from_json')

class MTGObject(JSONObject):
    ...

class Effect(JSONObject):
    def __init__(self) -> None:
        super().__init__()
        # TODO

class Trigger(MTGObject):
    def __init__(self) -> None:
        super().__init__()

class Effect(MTGObject):
    def __init__(self) -> None:
        super().__init__()

class ActivatedAbility(MTGObject):
    def __init__(self) -> None:
        super().__init__()

class CardObject(MTGObject):
    def __init__(self) -> None:
        super().__init__()

        self.effect: Effect = None
        self.triggers: list[Trigger] = []
        self.activated_abilities: list[ActivatedAbility] = []

    def to_json(self):
        return None
        # return super().to_json()

def whenever_matcher(text: str, result: CardObject, args: list) -> CardObject:
    print(args)
    print()
    return result

def whenever_if_matcher(text: str, result: CardObject, args: list) -> CardObject:
    print(args)
    return result

m = {
    'Whenever (.*), (.*).': whenever_matcher,
    'Whenever (.*), if (.*), (.*)': whenever_if_matcher,
    'When (.*), (.*).': whenever_matcher,
    'When (.*), if (.*), (.*)': whenever_if_matcher,
}

def parse(text: str, result: CardObject=None) -> CardObject:
    if not result:
        result = CardObject()
    for line in text.split('\n'):
        for pattern, matcher in m.items():
            matches = re.match(pattern, line)
            if not matches: continue
            result = matcher(text, result, matches.groups())
            break
    return result


start = 10
amount = 10
for card in read_cards('test_cards.json')[start:start+amount]:
    if not 'oracle_text' in card: continue
    # print(card['oracle_text'])
    parsed = parse(card['oracle_text'])
    print('===')
    # print(parsed.to_json())
