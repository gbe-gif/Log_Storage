from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class ImageCard(QWidget):
    def __init__(self, turn, files, pixmap):
        super().__init__()
        
        self.turn = turn
        self.files = files
        # 반복적인 리사이즈에도 화질 저하를 막기 위해 원본 픽스맵 보관
        self.original_pixmap = pixmap 
        
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(5)
        
        turn_label = QLabel(f"Turn {self.turn}")
        font = turn_label.font()
        font.setBold(True)
        font.setPointSize(11)
        turn_label.setFont(font)
        
        # 멤버 변수로 승격하여 외부에서 픽스맵을 교체할 수 있도록 함
        self.image_label = QLabel()
        self.image_label.setPixmap(self.original_pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(turn_label)
        layout.addWidget(self.image_label)

    def set_display_width(self, width):
        """
        주어진 가로 폭(width)에 맞춰 원본 픽스맵을 축소하여 표시합니다.
        원본보다 넓은 공간이 주어지면 확대하지 않고 원본 크기를 유지합니다.
        """
        if self.original_pixmap.width() > width:
            # 원본보다 작은 경우에만 축소 적용 (SmoothTransformation으로 화질 유지)
            scaled_pixmap = self.original_pixmap.scaledToWidth(
                width, Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            # 공간이 충분하면 원본 그대로 출력
            self.image_label.setPixmap(self.original_pixmap)