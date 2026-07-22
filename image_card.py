from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class ImageCard(QWidget):
    def __init__(self, turn, files, pixmap):
        super().__init__()

        self.turn = turn
        self.files = files
        self.original_pixmap = pixmap

        self._current_width = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(5)

        self.turn_label = QLabel(f"Turn {self.turn}")
        font = self.turn_label.font()
        font.setBold(True)
        font.setPointSize(11)
        self.turn_label.setFont(font)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.turn_label)
        layout.addWidget(self.image_label)

        self.image_label.setPixmap(self.original_pixmap)

    def set_display_width(self, width):
        # 같은 크기로 또 스케일링하지 않음
        if width == self._current_width:
            return

        self._current_width = width

        # 원본보다 크게 확대하지 않음
        target_width = min(width, self.original_pixmap.width())

        # FastTransformation이 텍스트를 더 또렷하게 유지하는 경우가 많음
        scaled = self.original_pixmap.scaled(
            target_width,
            self.original_pixmap.height(),
            Qt.KeepAspectRatio,
            Qt.FastTransformation
        )

        self.image_label.setPixmap(scaled)