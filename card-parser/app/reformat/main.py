from graph.area import * 

class PP:
    def __init__(self) -> None:
        self.parent = None

class P:
    def __init__(self) -> None:
        self.main = PP()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = GraphArea(P(), None)
    w.show()
    sys.exit(app.exec_())