import os
from PySide6.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QRect, QRectF, QTimer
from PySide6.QtGui import QImage, QPainter, QColor, QPen

class CropWidget(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        
        # 1. 원본 이미지 로드 및 유효성 검사
        original_image = QImage(image_path)
        self.is_valid = not original_image.isNull() and original_image.width() > 0 and original_image.height() > 0
        
        if self.is_valid:
            # 2. 가로폭 1200 이상일 경우 1200 기준으로 축소 (비율 유지)
            if original_image.width() > 1200:
                self.image = original_image.scaledToWidth(1200)
            
        else:
            self.image = QImage()
        
        self.target_ratio = 6.0  # 6:1 비율 고정
        self.scale = 1.0
        self.img_x = 0
        self.img_y = 0
        self.last_mouse_pos = None
        self._initialized = False
        self.setMinimumSize(600, 400)
        self.setMouseTracking(True)

    def resizeEvent(self, event):
        if not self.is_valid:
            super().resizeEvent(event)
            return
            
        self._calc_crop_box()
        if not self._initialized:
            self._fit_image()
            self._initialized = True
        super().resizeEvent(event)

    def _calc_crop_box(self):
        margin = 40
        w = self.width() - margin * 2
        h = self.height() - margin * 2
        if w <= 0 or h <= 0: return

        if w / h > self.target_ratio:
            w = h * self.target_ratio
        else:
            h = w / self.target_ratio

        self.crop_w = w
        self.crop_h = h
        self.crop_x = (self.width() - w) / 2
        self.crop_y = (self.height() - h) / 2
        
        # 1200px(또는 그 이하)로 맞춰진 self.image를 기준으로 최소 스케일 계산
        self.min_scale = max(self.crop_w / self.image.width(), self.crop_h / self.image.height())
        self.clamp_bounds()

    def _fit_image(self):
        self.scale = self.min_scale
        self.img_x = self.crop_x + (self.crop_w - self.image.width() * self.scale) / 2
        self.img_y = self.crop_y + (self.crop_h - self.image.height() * self.scale) / 2

    def clamp_bounds(self):
        if self.scale < self.min_scale:
            self.scale = self.min_scale

        scaled_w = self.image.width() * self.scale
        scaled_h = self.image.height() * self.scale

        if self.img_x > self.crop_x: 
            self.img_x = self.crop_x
        if self.img_y > self.crop_y: 
            self.img_y = self.crop_y
        if self.img_x + scaled_w < self.crop_x + self.crop_w:
            self.img_x = self.crop_x + self.crop_w - scaled_w
        if self.img_y + scaled_h < self.crop_y + self.crop_h:
            self.img_y = self.crop_y + self.crop_h - scaled_h

    def wheelEvent(self, event):
        if not self.is_valid: return
        
        delta = event.angleDelta().y()
        factor = 1.1 if delta > 0 else (1 / 1.1)

        mx = event.position().x()
        my = event.position().y()

        ix = (mx - self.img_x) / self.scale
        iy = (my - self.img_y) / self.scale

        self.scale *= factor
        if self.scale < self.min_scale:
            self.scale = self.min_scale

        self.img_x = mx - ix * self.scale
        self.img_y = my - iy * self.scale
        self.clamp_bounds()
        self.update()

    def mousePressEvent(self, event):
        if not self.is_valid: return
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.position()

    def mouseMoveEvent(self, event):
        if not self.is_valid: return
        if self.last_mouse_pos is not None:
            dx = event.position().x() - self.last_mouse_pos.x()
            dy = event.position().y() - self.last_mouse_pos.y()
            self.img_x += dx
            self.img_y += dy
            self.last_mouse_pos = event.position()
            self.clamp_bounds()
            self.update()

    def mouseReleaseEvent(self, event):
        if not self.is_valid: return
        self.last_mouse_pos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # 배경
        painter.fillRect(self.rect(), QColor(30, 30, 30))

        if not self.is_valid:
            return # 이미지가 비정상적이면 배경만 칠하고 종료

        # 확대/축소 및 이동된 이미지 드로잉
        target_rect = QRectF(self.img_x, self.img_y, self.image.width() * self.scale, self.image.height() * self.scale)
        painter.drawImage(target_rect, self.image)

        # 크롭 영역 외곽 어둡게 처리
        overlay = QColor(0, 0, 0, 180)
        painter.fillRect(QRectF(0, 0, self.width(), self.crop_y), overlay)
        painter.fillRect(QRectF(0, self.crop_y + self.crop_h, self.width(), self.height() - (self.crop_y + self.crop_h)), overlay)
        painter.fillRect(QRectF(0, self.crop_y, self.crop_x, self.crop_h), overlay)
        painter.fillRect(QRectF(self.crop_x + self.crop_w, self.crop_y, self.width() - (self.crop_x + self.crop_w), self.crop_h), overlay)

        # 크롭 영역 안내선
        painter.setPen(QPen(Qt.white, 2))
        painter.drawRect(QRectF(self.crop_x, self.crop_y, self.crop_w, self.crop_h))

    def get_cropped_image(self):
        if not self.is_valid: return QImage()
        
        # 화면상의 크롭 영역을 1200px(또는 이하) 기준의 self.image 스케일에 맞춰 매핑
        src_x = (self.crop_x - self.img_x) / self.scale
        src_y = (self.crop_y - self.img_y) / self.scale
        src_w = self.crop_w / self.scale
        src_h = self.crop_h / self.scale

        src_rect = QRect(int(src_x), int(src_y), int(src_w), int(src_h))
        cropped = self.image.copy(src_rect)
        
        # 3. 내부 표준 규격인 1200x200으로 강제 리사이징 (크롭 박스가 정확히 6:1이므로 비율 왜곡 없음)
        if cropped.width() != 1200 or cropped.height() != 200:
           cropped = cropped.scaled(1200, 200, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

        return cropped


class CropDialog(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("커버 이미지 크롭 (6:1)")
        self.resize(800, 600)
        
        self.crop_widget = CropWidget(image_path, self)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 안내 문구
        guide_label = QLabel("마우스 휠로 확대/축소, 드래그하여 위치를 이동하세요.")
        guide_label.setAlignment(Qt.AlignCenter)
        guide_label.setStyleSheet("color: #EAEAEA; font-size: 13px; padding-bottom: 5px;")
        layout.addWidget(guide_label)
        
        layout.addWidget(self.crop_widget, stretch=1)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("취소")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)
        
        self.apply_btn = QPushButton("적용")
        self.apply_btn.setFixedWidth(100)
        self.apply_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.apply_btn)
        layout.addLayout(btn_layout)

        # 이미지 로드 실패 시 에러 처리
        if not self.crop_widget.is_valid:
            self.apply_btn.setEnabled(False)
            QTimer.singleShot(0, self.handle_invalid_image)

    def handle_invalid_image(self):
        QMessageBox.critical(self, "오류", "이미지를 불러올 수 없거나 손상된 파일입니다.")
        self.reject()
        
    def get_cropped_image(self):
        return self.crop_widget.get_cropped_image()