from PySide6.QtWidgets import QMainWindow


class Viewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PR Log Image Storage")

        self.resize(1200, 800)

        self.setMinimumSize(800, 600)