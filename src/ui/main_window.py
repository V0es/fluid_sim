from PyQt6.QtWidgets import QMainWindow

from .main_widget import MainWidget


class SimulationWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Fluid Simulation')
        self.setGeometry(0, 0, 1000, 700)
        self.main_widget = MainWidget(self)
        self.setCentralWidget(self.main_widget)







