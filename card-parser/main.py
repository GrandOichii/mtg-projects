from termcolor import colored
from parsers import *
from util import *
import re

CARDNAME_TEXT = '[CARDNAME]'
# cards = read_cards('../oracle_cards.json')
# save_cards('test_cards.json', cards[:1000])

WHENEVER_IF_MATCHER = 'whenever (.*), if (.*), (.*)'
WHENEVER_MATCHER = 'whenever (.*), (.*)'
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

def basic_replace(text: str, words: list[str], format: str):
    result = text
    for word in words:
        r = f'\\b{word}\\b'

        fmt = format.format(word)
        # print('\t', r, fmt)
        result = re.sub(r, fmt, result)
        # result = result.replace(f'{word} ', f'{fmt} ').replace(f'{word}\n', f'{fmt}\n').replace(']s', ']')
    return result

def remove_reminder_text(card: dict, text: str) -> str:
    m = re.findall(REMINDER_TEXT_FINDER, text)
    if not m: return text

    for rt in m:
        text = text.replace(rt, '')
    return text

def replace_creature_types(card: dict, text: str) -> str:
    return basic_replace(text, CREATURE_TYPES, '[creature_type:{}]')

def replace_land_types(card: dict, text: str) -> str:
    return basic_replace(text, LAND_TYPES, '[land_type:{}]')

def format_keyword_abilities(card: dict, text: str) -> str:
    return basic_replace(text, KEYWORD_ABILITIES, '[keyword_ability:{}]')

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

# parsed_count = 0
# for card in cards[:amount]:
#     result = parse_card(card)
#     if not result:
#         print(colored('Failed to parse', 'red'), colored(card['name'], 'yellow'))
#         continue
#     parsed_count += 1
#     print(colored('Parsed card', 'green'), colored(card['name'], 'yellow'))
#     print(json.dumps(result, indent=4))
# len = 50
# good = int(parsed_count / amount * len)
# print('Parsed: ', colored('|' * good, 'green'), colored('|' * (len - good), 'red'), f' ({amount})', sep='')

def f(item: dict):
    if not 'oracle_text' in item: return True

    orig_text = item['oracle_text']
    fmt_text = text_pipeline.get_fmt_text(orig_text, item)
    if ']s' in fmt_text:
        print(fmt_text)
    double_text = text_pipeline.get_orig_text(fmt_text, item)
    result = orig_text == double_text
    
    if not result:
        print(colored(orig_text, 'green'))
        print(colored(double_text, 'red'))
        print()
    return result

# print_correctness(cards[:amount], lambda item: parse_card(item) != None, 50)
print_correctness(cards[:100], f, 50)
    # text = tp.do(card)
    # if not 'oracle_text' in card: continue
    # # if not 'where x is ' in text: continue


    # for line in text.split('\n'):
    #     when_t = None
    #     condition_t = None
    #     effect_t = None

    #     m = re.match(WHENEVER_IF_MATCHER, line)
    #     if m:
    #         print('\t', line)
    #         print(m.groups())
    #     else:
    #         m = re.match(WHENEVER_MATCHER, line)
    #         if m:
    #             print('\t', line)
    #             print(m.groups())
    # print(text)
    # print('======')