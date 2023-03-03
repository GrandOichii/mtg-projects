import json

from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from uutil import *

class _CardLI(QListWidgetItem):
    def __init__(self, card: dict):
        super().__init__()

        self.wid = QLabel()
        self.set_card(card)

    def set_card(self, card: dict):
        self.card = card
        self.wid.setText(card['name'])

class CardListWithTextBox(QWidget):
    def __init__(self, parent, mid_text: str='Original', cards: list[dict]=None) -> None:
        super().__init__(parent)    
        if cards is None:
            cards = json.loads(open('../test_cards.json', 'r', encoding='utf-8').read())

        self.selected_card = pyqtSignal(dict)

        # self.cards = cards

        self._parent = parent

        self.init_ui()

        for card in cards:
            li = _CardLI(card)
            add_to_qlist(self._card_list, li, li.wid)

        self._mid_label.setText(mid_text)

    def init_ui(self):
        layout = QVBoxLayout()

        self._card_list = QListWidget()
        self._card_list.clicked.connect(self.selected_card_changed)

        self._mid_label = QLabel()
        
        self._text_box = QTextEdit()
        self._text_box.setReadOnly(True)

        layout.addWidget(self._card_list)
        layout.addWidget(self._mid_label)
        layout.addWidget(self._text_box)

        self.setLayout(layout)

    # actions
    def selected_card_changed(self):
        items = self._card_list.selectedItems()
        if len(items) != 1: return
        item: _CardLI = items[0]
        card = item.card

        self._text_box.setText(card['oracle_text'] if 'oracle_text' in card else '')

test_element(CardListWithTextBox)