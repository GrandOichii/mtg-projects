

from graph.graph import *
from graph.graph_el import *
from graph.tree import *

class MTGTree(Tree):
    def __init__(self, area: 'GraphArea') -> None:
        super().__init__(area)

    def get_pipeline(self):
        # TODO
        result = None

        return result


class MTGTreeNode(TreeNode):
    def __init__(self, area: 'GraphArea', tree: 'MTGTree', text: str = '', parent: 'TreeNode' = None, 
                 interactable: bool=True,
                 movable: bool=True,
                 disconnectable: bool=True) -> None:
        super().__init__(area, tree, text, parent, interactable, movable, disconnectable)

        self.box = TextBox(area, text)
        # self.box = MultiTextBox(area)
        # for i in range(random.randint(1, 4)):
        #     self.box.sub_boxes += [TextBox(area, random_node_name())]
        # self.box = ProgressWraper(TextBox(area, text), random.randint(0, 100), filled_color='red')
        # self.box = ProgressTextBox(area, text, random.randint(0, 100), filled_color='red')

    
        def dc():
            nd = MTGTreeNode(self.area, self.tree, random_node_name(), self)
            nd.x = self.x
            nd.y = self.y + self.box.height() + BETWEEN_Y
            self.children += [nd]

        self.on_double_click = dc

        self.on_click = lambda: self.area.parent_w.set_current_node(self)


class MTGTreeMultNode(MTGTreeNode):
    def __init__(self, area: 'GraphArea', tree: 'MTGTree', text: str = '', parent: 'TreeNode' = None, sub_nodes: list[MTGTreeNode] = None) -> None:
        super().__init__(area, tree, text, parent)
        if not sub_nodes: sub_nodes = []

        self.box = MultiTextBox(area, text)

        self.sub_nodes: list[MTGTreeNode] = []

        for node in sub_nodes:
            self.add_node(node)

        # self.sub_nodes: list[MTGTreeNode] = sub_nodes

    def add_node(self, node: MTGTreeNode):
        self.sub_nodes += [node]
        # node.x = 110/
        # node.y = 110

        # self.box.add_sub_box(node.box)
        self.box.sub_boxes += [node.box]

    def set_initial_loc(self, x: int, y: int, between: tuple[int, int]) -> int:
        super().set_initial_loc(x, y, between)

        y += self.box.height() - TextBox.height(self.box)

        for child in self.sub_nodes:
            child.set_initial_loc(x, y, between, False)
            x += child.box.width()

    def draw(self, painter: QPainter):
        super().draw(painter)

        for child in self.sub_nodes:
            child.draw(painter)

    def move(self, xdiff: int, ydiff: int):
        super().move(xdiff, ydiff)
        for child in self.sub_nodes:
            child.move(xdiff, ydiff)
