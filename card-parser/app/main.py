from termcolor import colored
import os.path as path
import re
import sys
import json

from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from graph import *
from uutil import *
from elements import *
# internal movement in list:
# <list_name>.setDragDropMode(<list_name>.InternalMove)


DEFAULT_TEXT_TRANSFORMER_NAME = 'Text Transfomer'



class JSONObject:
    def to_json(self) -> dict:
        raise Exception('NOT IMPLEMENTED: to_json')
    
    def from_json(j: dict):
        raise Exception('NOT IMPLEMENTED: from_json')


# TODO find better solution
class OneWayTextTransformer(JSONObject):
    def __init__(self) -> None:
        super().__init__()

    def parse(self, text: str, details: dict) -> tuple[str, dict]:
        raise Exception('NOT IMPLEMENTED: parse')
    
    def to_json(self) -> dict:
        # TODO
        return super().to_json()
    

class TextLowerTransformer(OneWayTextTransformer):
    def parse(self, text: str, details: dict) -> tuple[str, dict]:
        return text.lower(), details
    

class TextTransformer(OneWayTextTransformer):
    def __init__(self, args: dict) -> None:
        self.args = args

        self.name: str = ''
        self.type_str: str = ''

    def to_text(self, text: str, details: dict) -> str:
        raise Exception('NOT IMPLEMENTED: to_text')

    def to_json(self) -> dict:
        # TODO
        return super().to_json()
    
    def from_json(j: dict):
        # TODO
        return super().from_json()


class TextPipeline:
    def __init__(self, steps: list[TextTransformer]=None) -> None:
        self.steps: list[TextTransformer] = []

        if steps:
            self.steps = steps

    def parse(self, text: str) -> tuple[str, dict]:
        result = str(text)
        details = {}

        for i, step in enumerate(self.steps):
            result, details = step.parse(result, details)

        return result, details
    
    def to_text(self, text: str, details: dict) -> str:
        result = str(text)

        for i, step in enumerate(self.steps):
            result = step.to_text(result, details)

        return result


class BasicFormatter(TextTransformer):
    # def __init__(self, words_path: str, format: str):
    def __init__(self, args: dict):
        super().__init__(args)

        self.format: str = args['Format']
        words_path = args['Words file path']

        self.pairs = []
        words = open(words_path, 'r').read().split('\n')
        for word in words:
            # pattern = re.compile(f'\\b{word}\\b')
            pattern = f'\\b{word}\\b'
            self.pairs += [(word, pattern)]

    def parse(self, text: str, details: dict):
        result = str(text)
        for word, pattern in self.pairs:
            fmt = self.format.format(word)
            result = re.sub(pattern, fmt, result)
            # TODO replace with separate text transformer
            result = re.sub(pattern.lower(), fmt, result)
        return result, details

    def to_text(self, text: str, card: dict) -> str:
        # TODO not finished
        result = str(text)
        for word, pattern in self.pairs:
            # p = f'\\b{self.format.format(word)}\\b'
            p = self.format.format(word)
            # if p in result:
            #     print(result)
            #     print(p, word)
            result = result.replace(p, word)
            # print(word)
            # result = re.sub(p, word, result)
        return result


class PrefixFormatter(TextTransformer):
    def __init__(self, args: dict) -> None:
        super().__init__(args)
        self.prefix = args['Prefix']

    def parse(self, text: str, details: dict) -> tuple[str, dict]:
        return self.prefix + text, details
    
    def to_text(self, text: str, details: dict) -> str:
        return text[len(self.prefix):]


TEXT_FORMATTERS = {
    'Basic word formatter': {
        'type': BasicFormatter,
        'args': {
            'Words file path': {
                'type': 'file_path',
                'default': 'C:\\Users\\ihawk\\code\\mtg-projects\\card-parser\\creature_types.txt'
            },
            'Format': {
                'type': 'str',
                'default': '[creature_type:{}]'
            },
        }
    },
    'Prefix Formatter (Test)': {
        'type': PrefixFormatter,
        'args': {
            'Prefix': {
                'type': 'str'
            }
        }
    }
}


CARDS_PATH = '../test_cards.json'


class TextTransformerLI(QListWidgetItem):
    def __init__(self, transformer: TextTransformer):
        super().__init__()

        self.transformer = transformer

        self.wid = QLabel()
        self.update_widget()

    def update_widget(self):
        self.wid.setText(self.transformer.name)
        # self.wid = QLabel(self.transformer.name)


class ArgWidget:
    def reset(self):
        raise Exception('NOT IMPLEMENTED: reset')
    
    def get_value(self) -> tuple[str, bool]:
        raise Exception('NOT IMPLEMENTED: get value')

    def set_value(self, value: str):
        raise Exception('NOT IMPLEMENTED: set_value')


class StrArgWidget(ArgWidget, QLineEdit):
    def __init__(self) -> None:
        QLineEdit.__init__(self)

    def reset(self):
        self.setText('')

    def get_value(self) -> tuple[str, bool]:
        return self.text(), True

    def set_value(self, value: str):
        self.setText(value)


class FilePathArgWidget(ArgWidget, QPushButton):
    def __init__(self) -> None:
        super().__init__()
        self.file_loc: str = None

        self.clicked.connect(self.clicked_action)

        self.setText('Choose file')

    def clicked_action(self):
        result = QFileDialog.getOpenFileName(self, 'Choose file')[0]
        if result == '': return
        self.set_value(result)

    def get_value(self) -> tuple[str, bool]:
        result = self.file_loc
        if not result:
            QMessageBox.warning(self, 'File path', f'Enter file path')
            return '', False
        if not path.exists(result):
            QMessageBox.warning(self, 'File path', f'File path {result} doesn\'t exist')
            return '', False
        return result, True

    def set_value(self, value: str):
        self.file_loc = value
        self.setText(path.basename(value))


ARG_WIDGET_TYPES = {
    'str': StrArgWidget,
    'file_path': FilePathArgWidget
}


class ArgsLayout(QFormLayout):
    def __init__(self, details: dict):
        super().__init__()
        self.type_str: str = ''
        self.arg_type = details['type']
        args = details['args']
        self.d = {}
        for name, arg_detail in args.items():
            t = arg_detail['type']
            w = ARG_WIDGET_TYPES[t]()
            if 'default' in arg_detail:
                w.set_value(arg_detail['default'])

            self.d[name] = w
            self.addRow(QLabel(name), w)


    def reset_all(self):
        for w in self.d.values():
            w.reset()

    def get_values(self) -> tuple[dict, bool]:
        result = {}
        for name, w in self.d.items():
            value, done = w.get_value()
            if not done:
                return {}, False
            result[name] = value
        return result, True

    def set_values(self, args: dict):
        for arg_name, value in args.items():
            w = self.d[arg_name]
            w.set_value(value)

class TextTransformerEditor(QDialog):

    def __init__(self, parent, transformer: TextTransformer=None) -> None:
        super().__init__(parent)

        self.saved: bool = False
        self.result_tt: TextTransformer = None
        self.variants: dict = {}

        self.init_ui(transformer)

    def init_ui(self, transformer: TextTransformer):
        self.create_variants()
        layout = QVBoxLayout()

        top_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setText(DEFAULT_TEXT_TRANSFORMER_NAME)
        self.type_combo_box = QComboBox()
        self.type_combo_box.setCurrentText('')
        self.type_combo_box.addItems(list(TEXT_FORMATTERS.keys()))
        self.type_combo_box.currentTextChanged.connect(self.type_changed_action)

        top_layout.addRow(QLabel('Name:'), self.name_edit)
        top_layout.addRow(QLabel('Type:'), self.type_combo_box)

        self.mid_widget = QStackedWidget()
        for w in self.variants.values():
            self.mid_widget.addWidget(w)

        bottom_layout = QHBoxLayout()
        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_action)
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.close)
        bottom_layout.addWidget(self.save_button)
        bottom_layout.addWidget(self.cancel_button)

        layout.addLayout(top_layout)
        layout.addWidget(self.mid_widget)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

        self.type_changed_action()

        if transformer is None: return

        self.name_edit.setText(transformer.name)
        self.type_combo_box.setCurrentText(transformer.type_str)
        self.mid_widget.currentWidget().layout().set_values(transformer.args)

    def create_variants(self) -> dict:
        for var_type, details in TEXT_FORMATTERS.items():
            wid = QWidget()
            l = ArgsLayout(details)
            l.type_str = var_type
            wid.setLayout(l)

            self.variants[var_type] = wid

    def do(parent: 'MainWindow', transformer: TextTransformer=None) -> tuple[TextTransformer, bool]:
        w = TextTransformerEditor(parent, transformer)
        w.exec_()
        if not w.saved: return None, False
        return w.result_tt, True

    # actions
    def type_changed_action(self):
        self.mid_widget.setCurrentWidget(self.variants[self.type_combo_box.currentText()])

    def save_action(self):
        # TODO check for same text transformer name
        tname = self.name_edit.text()
        if not tname:
            QMessageBox.warning(self, 'Text transformer name', 'Enter text transformer name')
        l: ArgsLayout = self.mid_widget.currentWidget().layout()
        values, done = l.get_values()
        if not done: return
        self.result_tt = l.arg_type(values)
        self.result_tt.type_str = l.type_str
        self.result_tt.name = tname
        self.saved = True
        print(self.result_tt.type_str)
        self.close()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.load_cards()
        self.init_ui()

    # ui init
    def init_ui(self):
        self.init_tabs()

    def init_tabs(self):
        self.tabs = QTabWidget()
        self.init_graph_tab()
        self.init_text_transformers_tab()

        self.setCentralWidget(self.tabs)

    def init_graph_tab(self):
        wid = GraphWidget(self)

        self.tabs.addTab(wid, 'Selector Graph')

    def init_text_transformers_tab(self):
        wid = QWidget()

        layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)

        self.text_transformers_list = QListWidget()
        add_text_transformer_button = QPushButton('Add')
        add_text_transformer_button.clicked.connect(self.add_text_transformer_action)
        edit_text_transformer_button = QPushButton('Edit')
        edit_text_transformer_button.clicked.connect(self.edit_text_transformer_action)
        delete_text_transformer_button = QPushButton('Delete')
        delete_text_transformer_button.clicked.connect(self.delete_text_transformer_action)

        left_layout.addWidget(self.text_transformers_list)
        left_layout.addWidget(add_text_transformer_button)
        left_layout.addWidget(edit_text_transformer_button)
        left_layout.addWidget(delete_text_transformer_button)

        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        test_text_transformers_button = QPushButton('Test all cards')

        frame_layout = QVBoxLayout()
        frame.setLayout(frame_layout)


        # self.text_transformer_card_search_edit = QLineEdit()
        # self.text_transformer_card_search_edit.setPlaceholderText('Enter card name')
        # # TODO move to thread of card loading
        # card_name_completer = QCompleter(list(self.name_dict.keys()))
        self.text_transformer_card_search_edit = CardNameLine(list(self.name_dict.keys()))
        # self.text_transformer_card_search_edit.setCompleter(card_name_completer)
        self.text_transformer_card_search_edit.textChanged.connect(self.text_transformer_card_search_text_changed_action)
        parse_button = QPushButton('Parse')
        parse_button.clicked.connect(self.parse_card_text_action)

        self.original_text_box = QTextEdit()
        self.parsed_text_box = QTextEdit()
        self.details_text_block = QTextEdit()

        frame_layout.addWidget(self.text_transformer_card_search_edit)
        frame_layout.addWidget(QLabel('Original:'))
        frame_layout.addWidget(self.original_text_box)
        frame_layout.addWidget(parse_button)
        frame_layout.addWidget(QLabel('Parsed:'))
        frame_layout.addWidget(self.parsed_text_box)
        frame_layout.addWidget(QLabel('Details:'))
        frame_layout.addWidget(self.details_text_block)

        right_layout.addWidget(frame)
        right_layout.addWidget(test_text_transformers_button)

        wid.setLayout(layout)

        self.tabs.addTab(wid, 'Text Transformers')

    # methods
    def create_text_pipeline(self) -> TextPipeline:
        steps = []
        for i in range(self.text_transformers_list.count()):
            item: TextTransformerLI = self.text_transformers_list.item(i)
            steps += [item.transformer]
        return TextPipeline(steps)

    # card loading
    def load_cards(self):
        # TODO move to different thread
        
        # self.all_cards = json.loads(open(CARDS_PATH, 'r', encoding='utf-8').read())
        self.all_cards = []

        # indexes
        self.name_dict = {}
        for card in self.all_cards: self.name_dict[card['name']] = card

    # actions
    def parse_card_text_action(self):
        pipeline = self.create_text_pipeline()
        result, details = pipeline.parse(self.original_text_box.toPlainText())
        self.parsed_text_box.setText(result)
        self.details_text_block.setText(json.dumps(details, indent=4))

    def text_transformer_card_search_text_changed_action(self):
        text = self.text_transformer_card_search_edit.text()
        if not text in self.name_dict: return
        card = self.name_dict[text]
        if not 'oracle_text' in card: return
        self.original_text_box.setText(card['oracle_text'])

    def add_text_transformer_action(self):
        transformer, done = TextTransformerEditor.do(self)
        if not done: return

        li = TextTransformerLI(transformer)
        add_to_qlist(self.text_transformers_list, li, li.wid)

    def delete_text_transformer_action(self):
        i_s = self.text_transformers_list.selectedIndexes()
        if len(i_s) != 1: return
        i = i_s[0].row()
        item: TextTransformerLI = self.text_transformers_list.item(i)
        if QMessageBox.question(self, 'Text transformer deletion', f'Delete text transformer {item.transformer.name}?', QMessageBox.Yes|QMessageBox.No) == QMessageBox.No: return

        self.text_transformers_list.takeItem(i)

    def edit_text_transformer_action(self):
        i_s = self.text_transformers_list.selectedIndexes()
        if len(i_s) != 1: return
        i = i_s[0].row()
        item: TextTransformerLI = self.text_transformers_list.item(i)
        transformer, done = TextTransformerEditor.do(self, item.transformer)
        if not done: return
        item.transformer = transformer
        item.update_widget()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())