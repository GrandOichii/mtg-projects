from util import *
import re

CARDNAME_TEXT = '[CARDNAME]'
# cards = read_cards('../oracle_cards.json')
# save_cards('test_cards.json', cards[:1000])

WHENEVER_IF_MATCHER = 'Whenever (.*), if (.*), (.*)'
WHENEVER_MATCHER = 'Whenever (.*), (.*)'
REMINDER_TEXT_FINDER = '(\(.*\))'

FLAVOR_WORDS = open('flavor_words.txt', 'r').read().split('\n')
CREATURE_TYPES = open('creature_types.txt', 'r').read().split('\n')
LAND_TYPES = open('land_types.txt', 'r').read().split('\n')
KEYWORD_ABILITIES = open('keyword_abilities.txt', 'r').read().split('\n')

cards = read_cards('test_cards.json')
# for card in cards:
#     if not 'oracle_text' in card: continue

#     t = card['oracle_text']
#     m = re.match(WHENEVER_IF_MATCHER, t)
#     if m:
#         print(t)
#         print(m.groups())
#         print()
#         print()
#     else:
#         m = re.match(WHENEVER_MATCHER, t)
#         if not m: continue
#         print(t)
#         print(m.groups())
#         print()
        

def replace_cardname(card: dict, text: str) -> str:
    return text.replace(card['name'].lower(), CARDNAME_TEXT)

def remove_flavor_words(card: dict, text: str) -> str:
    lines = text.split('\n')
    result = []
    for line in lines:
        r = line
        for fw in FLAVOR_WORDS:
            fwf = f'{fw} — '
            if not line.startswith(fw): continue
            r = line[len(fwf):]
            break
        result += [r]
    return '\n'.join(result)

def remove_reminder_text(card: dict, text: str) -> str:
    m = re.findall(REMINDER_TEXT_FINDER, text)
    if not m: return text

    for rt in m:
        text = text.replace(rt, '')
    return text

def replace_creature_types(card: dict, text: str) -> str:
    result = text
    for ct in CREATURE_TYPES:
        fmt = f'[creature_type:{ct}] '
        result = result.replace(f'{ct} ', fmt).replace(']s', ']')
    return result

def replace_land_types(card: dict, text: str) -> str:
    result = text
    for ct in LAND_TYPES:
        fmt = f'[land_type:{ct}] '
        result = result.replace(f'{ct} ', fmt).replace(']s', ']')
    return result

def format_keyword_abilities(card: dict, text: str) -> str:
    result = text
    for ct in KEYWORD_ABILITIES:
        fmt = f'[keyword_ability:{ct}] '
        result = result.replace(f'{ct} ', fmt).replace(']s', ']')
    return result

class Pipeline:
    def __init__(self, stages: list[tuple[str, any]]) -> None:
        self.stages = stages

class TextPipeline(Pipeline):
    def __init__(self, stages: list[tuple[str, any]]) -> None:
        super().__init__(stages)

    def do(self, card: dict):
        if not 'oracle_text' in card: return ''
        text = card['oracle_text'].lower()
        # print(text)
        for pair in self.stages:
            # print('Pipeline stage: ', pair[0])
            text = pair[1](card, text)
        return text

tp = TextPipeline([
    ('card name replacement', replace_cardname),
    ('flavor words removal', remove_flavor_words),
    ('reminder text removal', remove_reminder_text),
    ('creature types replacement', replace_creature_types),
    ('land types replacement', replace_land_types),
    ('keyword ability formatting', format_keyword_abilities)
])


for card in cards:
    text = tp.do(card)
    if not 'oracle_text' in card: continue
    if not 'where x is ' in text: continue

    print(text)
    print()