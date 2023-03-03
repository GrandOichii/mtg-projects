from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys

def add_to_qlist(list: QListWidget, item: QListWidgetItem, widget: QWidget):
    list.addItem(item)
    list.setItemWidget(item, widget)

def test_element(w_type):
    app = QApplication(sys.argv)
    w = w_type(None)
    w.show()
    sys.exit(app.exec_())