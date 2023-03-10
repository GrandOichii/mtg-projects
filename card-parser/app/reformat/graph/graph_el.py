from PyQt5.QtWidgets import *
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from graph import *
# def average_mid()

def center_pos(x: int, y: int, width: int, height: int, inner_width: int, inner_height: int):
    return x + (width - inner_width) // 2, y + (height - inner_height) // 2


class Box:
    def __init__(self) -> None:
        pass

    def draw(self, painter: QPainter, x: int, y: int):
        pass

    def width(self) -> int:
        return 0
    
    def height(self) -> int:
        return 0
    

class MovableBox(Box):
    def __init__(self) -> None:
        super().__init__()
        self.is_moving: bool = False


class TextBox(MovableBox):
    fill_color = Qt.green

    HOR_PADDING = 10
    VER_PADDING = 5


    # TODO why can't detect? (sometimes)
    def __init__(self, parent: 'GraphArea', label:str=None) -> None:
        super().__init__()

        if not label: label = ''

        self.clicked = None

        self.parent: GraphArea = parent
        
        self.label: QStaticText = QStaticText()

        self.set_text(label)

    def set_text(self, text: str):
        self.label.setText(text)
        ts = self.label.size()
        self.text_width, self.text_height = int(ts.width()), int(ts.height())

    def draw_mid_text(self, painter: QPainter, x: int, y: int, text: str):
        t = QStaticText(text)
        c_pos = center_pos(x, y, self.width(), self.height(), self.text_width, self.text_height)
        painter.drawStaticText(c_pos[0], y + TextBox.VER_PADDING, t)

    # override this
    def draw(self, painter: QPainter, x: int, y: int):
        o_pen = painter.pen()
        pen = QPen()

        # mx, my = -1, -1
        # m: ModMouseEvent = None
        # if self.parent.last_mouse_state:
        #     # sp = self.parent.screen().pos
        #     m = self.parent.last_mouse_state
        #     # mp = m.e.pos() + self.parent.pos()
        #     mp = m.e.pos()
        #     mx, my = mp.x(), mp.y()
        
        w = self.width()
        h = self.height()
        # # fill background
        # # print(x)
        # inside = x < mx < x + w and y < my < y + h
        # c = Qt.red if inside else TextBox.fill_color
        c = Qt.red if self.is_moving else TextBox.fill_color
        painter.fillRect(x, y, w, h, c)
        # # outline
        # if m is not None and inside and m.clicked:
        #     if self.clicked: self.clicked()
        #     pen.setColor(Qt.blue)
        #     pen.setWidth(3)
        painter.setPen(pen)
        painter.drawRect(x, y, w, h)
        painter.setPen(o_pen)
        self.draw_mid_text(painter, x, y, self.label)

    def height(self):
        return self.text_height + 2 * TextBox.VER_PADDING
    
    def width(self):
        return self.text_width + 2 * TextBox.HOR_PADDING


class ProgressWraper(Box):
    def __init__(self, box: Box, value: int=0, max_value: int=100, filled_color: str='green', blank_color: str='gray'):
        super().__init__()

        self._box = box

        self.filled_c = QColor(filled_color)
        self.blank_c = QColor(blank_color)

        self.value = value
        self.max_value = max_value

    def bar_height(self):
        return self._box.height() // 4

    def height(self):
        return self._box.height() + self.bar_height()
    
    def draw(self, painter: QPainter, x: int, y: int):
        self._box.draw(painter, x, y)

        # draw progress bar
        bh = self.bar_height()
        sy = y + self._box.height()
        w = self.width()
        # draw blank
        painter.fillRect(x, sy, w, bh, self.blank_c)
        # draw filled
        painter.fillRect(x, sy, w * self.value // self.max_value, bh, self.filled_c)
        # draw border
        painter.drawRect(x, sy, w, bh)


class ProgressTextBox(TextBox):
    def __init__(self, parent: 'GraphArea', label: str=None, value: int=0, max_value: int=100, filled_color: str='green', blank_color: str='gray') -> None:
        super().__init__(parent, label)

        self.filled_c = QColor(filled_color)
        self.blank_c = QColor(blank_color)

        self.value = value
        self.max_value = max_value

    def bar_height(self):
        return super().height() // 4

    def height(self):
        return super().height() + self.bar_height()
    
    def draw(self, painter: QPainter, x: int, y: int):
        super().draw(painter, x, y)

        # draw progress bar
        bh = self.bar_height()
        sy = y + self._box.height()
        w = self.width()
        # draw blank
        painter.fillRect(x, sy, w, bh, self.blank_c)
        # draw filled
        painter.fillRect(x, sy, w * self.value // self.max_value, bh, self.filled_c)
        # draw border
        painter.drawRect(x, sy, w, bh)


# TODO if text is longer than children, children look weird
class MultiTextBox(TextBox):
    def __init__(self, parent: 'GraphArea', label: str = None) -> None:
        super().__init__(parent, label)

        self.sub_boxes: list[TextBox] = []

    def draw(self, painter: QPainter, x: int, y: int):
        super().draw(painter, x, y)

        y += super().height()
        for child in self.sub_boxes:
            child.draw(painter, x, y)
            x += child.width()

    def height(self):
        return super().height() + self.children_height()

    def children_height(self):
        result = 0
        for child in self.sub_boxes:
            result = max(child.height(), result)
        return result
    
    def width(self):
        result = 0
        for child in self.sub_boxes:
            result += child.width()
        return max(result, super().width())