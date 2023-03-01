from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# def average_mid()

class Box:
    def __init__(self, parent: QPixmap, size: tuple[int, int], label=None) -> None:
        self.parent: QPixmap = parent

        self.label: str = label
        if not label: self.label = ''

        self.width: int = size[0]
        self.height: int = size[1]

    def draw_mid_text(self, painter: QPainter, x: int, y: int, text: str):
        t = QStaticText(text)
        ts = t.size()
        tw, th = int(ts.width()), int(ts.height())
        painter.drawStaticText(x + (self.width - tw) // 2, y + (self.height - th) // 2, t)

    # override this
    def draw(self, painter: QPainter, x: int, y: int):
        painter.drawRect(x, y, self.width, self.height)
        self.draw_mid_text(painter, x, y, self.label)

