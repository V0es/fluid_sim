from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QGridLayout, QPushButton
from .scene import Scene
from .tool_widget import ToolWidget


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.tool_widget = ToolWidget(self)
        layout.addWidget(self.tool_widget)

        self.scene = Scene(self)

        layout.addWidget(self.scene)

        self.setLayout(layout)
        self.connect_signals()

    def connect_signals(self):
        self.tool_widget.x_coord_slider.valueChanged.connect(
            self.scene.x_coord_change
        )

        self.tool_widget.y_coord_slider.valueChanged.connect(
            self.scene.y_coord_change
        )

        self.tool_widget.width_slider.valueChanged.connect(
            self.scene.width_change
        )

        self.tool_widget.height_slider.valueChanged.connect(
            self.scene.height_change
        )




