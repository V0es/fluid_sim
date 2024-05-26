from src.ui import SimulationWindow

from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication([])
    sim = SimulationWindow()

    sim.show()
    app.exec()


if __name__ == '__main__':
    main()