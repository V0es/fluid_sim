from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QSlider, QSizePolicy


class ToolWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout()

        self.x_coord_label = QLabel('X координата')
        self.y_coord_label = QLabel('Y координата')

        self.width_label = QLabel('Ширина')
        self.height_label = QLabel('Высота')

        self.x_coord_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_coord_slider.setMinimum(0)
        self.x_coord_slider.setMaximum(100)

        self.y_coord_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_coord_slider.setMinimum(0)
        self.y_coord_slider.setMaximum(100)

        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setMinimum(0)
        self.width_slider.setMaximum(100)

        self.height_slider = QSlider(Qt.Orientation.Horizontal)
        self.height_slider.setMinimum(0)
        self.height_slider.setMaximum(100)

        layout.addWidget(self.x_coord_label, 0, 0)
        layout.addWidget(self.y_coord_label, 1, 0)
        layout.addWidget(self.width_label, 2, 0)
        layout.addWidget(self.height_label, 3, 0)
        layout.addWidget(self.x_coord_slider, 0, 1)
        layout.addWidget(self.y_coord_slider, 1, 1)
        layout.addWidget(self.width_slider, 2, 1)
        layout.addWidget(self.height_slider, 3, 1)
        self.setLayout(layout)

        self.setSizePolicy(
            QSizePolicy(
                QSizePolicy.Policy.MinimumExpanding,
                QSizePolicy.Policy.Maximum
            )
        )
        self.connect_signals()

    def connect_signals(self):
        self.x_coord_slider.valueChanged.connect(self.x_coord_changed)
        self.y_coord_slider.valueChanged.connect(self.y_coord_changed)
        self.width_slider.valueChanged.connect(self.width_changed)
        self.height_slider.valueChanged.connect(self.height_changed)

    def x_coord_changed(self, new_x: int):
        self.x_coord_label.setText(
            'X: ' + f'{new_x / 100}'
        )

    def y_coord_changed(self, new_y: int):
        self.y_coord_label.setText(
            'Y: ' + f'{new_y / 100}'
        )

    def width_changed(self, new_w: int):
        self.width_label.setText(
            'Ширина: ' + f'{new_w / 100}'
        )

    def height_changed(self, new_h: int):
        self.height_label.setText(
            'Высота: ' + f'{new_h / 100}'
        )
