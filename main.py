import sys
from PySide6.QtWidgets import QApplication

from viewer import Viewer


def main():
    app = QApplication(sys.argv)

    window = Viewer()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()