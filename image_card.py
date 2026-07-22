from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class ImageCard(QWidget):
    def __init__(self, turn, files, pixmap):
        super().__init__()
        
        self.turn = turn
        self.files = files
        self.original_pixmap = pixmap 
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(5)
        
        # v1.2 변경: 멤버 변수로 승격
        self.turn_label = QLabel(f"Turn {self.turn}")
        font = self.turn_label.font()
        font.setBold(True)
        font.setPointSize(11)
        self.turn_label.setFont(font)
        
        self.image_label = QLabel()
        self.image_label.setPixmap(self.original_pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.turn_label)
        layout.addWidget(self.image_label)

    def set_display_width(self, width):
        if self.original_pixmap.width() > width:
            scaled_pixmap = self.original_pixmap.scaledToWidth(
                width, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setPixmap(self.original_pixmap)