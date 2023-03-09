from core import *
from single_matcher import *
import json

from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from uutil import *


class CardNameLine(QLineEdit):
    def __init__(self, card_names: list[str]):
        super().__init__()

        self.setPlaceholderText('Enter card name')
        card_name_completer = QCompleter(card_names)
        self.setCompleter(card_name_completer)


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


class SelectorTemplateEditArea(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self._parent = parent
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # TODO

        self.setLayout(layout)

# TODO not tested
class SingleMatcherEditArea(QWidget):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self._parent = parent
        self._single_matcher: SingleMatcherNode = None

        self.init_ui()
        self.implemented_radio_box_action()


        # self.setEnabled(False)

    def init_ui(self):
        layout = QFormLayout()

        self.implemented_radio_button = QRadioButton()
        self.implemented_radio_button.clicked.connect(self.implemented_radio_box_action)

        self.template_combo_box = QComboBox()
        self.template_combo_box.addItems(list(IMPLEMENTED_SINGLE_MATCHERS.keys()))

        self.placeholder_name_edit = QLineEdit()

        self.mid_label = QStackedWidget()
        self.mid_other = QStackedWidget()
        self.variations = {
            # TODO too big for some reason
            True: (QLabel('Template:'), self.template_combo_box),
            False: (QLabel('Placeholder name: '), self.placeholder_name_edit)
        }

        for pair in self.variations.values():
            self.mid_label.addWidget(pair[0])
            self.mid_other.addWidget(pair[1])

        layout.addRow('Implemented:', self.implemented_radio_button)
        layout.addRow(self.mid_label, self.mid_other)

        self.setLayout(layout)

    def set_single_matcher(self, matcher: SingleMatcherNode):
        self._single_matcher = matcher

        self.implemented_radio_button.setChecked(matcher.implemented)
        self.template_combo_box.setCurrentText(matcher.template_name)
        self.placeholder_name_edit.setText(matcher.template_name)

    # actions
    def implemented_radio_box_action(self):
        checked = self.implemented_radio_button.isChecked()
        pair = self.variations[checked]
        self.mid_label.setCurrentWidget(pair[0])
        self.mid_other.setCurrentWidget(pair[1])

        if not self._single_matcher: return
        self._single_matcher.implemented = checked

# test_element(SingleMatcherEditArea)