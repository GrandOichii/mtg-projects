from math import ceil
from termcolor import colored
import json

def read_cards(path: str):
    return json.loads(open(path, 'r', encoding='utf-8').read())

def save_cards(path: str, cards: list[dict]):
    open(path, 'w').write(json.dumps(cards, indent=4))

def filter_and_save_cards(method, save_path: str, src_path: str='../oracle_cards.json', amount: int=-1):
    cards = read_cards(src_path)
    result = []
    for card in cards:
        if method(card):
            result += [card]
    if amount == -1:
        save_cards(save_path, result)
        return
    save_cards(save_path, result[:amount])

def get_correctness_count(data: list, method) -> tuple[int, int]:
    result = 0
    exceptions = 0
    for i, item in enumerate(data):
        try:
            if method(item):
                result += 1
        except Exception as e:
            exceptions += 1
            print('Exception', e)
    return result, exceptions

def print_correctness(data: list, method, l: int):
    # TODO will sometimes print the wrong number of lines, when bad rounding
    good, exceptions = get_correctness_count(data, method)
    count = len(data)
    def f(c):
        return ceil(c / count * l)
    good_p = f(good)
    exceptions_p = f(exceptions)
    bad_p = l - good_p - exceptions_p
    print('Parsed: ', colored('|' * good_p, 'green'), colored('|' * bad_p, 'red'), colored('|' * exceptions_p, 'magenta'), sep='')
    print('Good:      ', good)
    print('Bad:       ', count - good - exceptions)
    print('Exceptions:', exceptions)
