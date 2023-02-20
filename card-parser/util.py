import json

def read_cards(path: str):
    return json.loads(open(path, 'r').read())

def save_cards(path: str, cards: list[dict]):
    open(path, 'w').write(json.dumps(cards, indent=4))