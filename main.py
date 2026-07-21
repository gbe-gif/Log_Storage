import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar, QSplitter,
    QListWidget, QScrollArea, QLabel, QVBoxLayout, QWidget, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 윈도우 기본 설정
        self.setWindowTitle("PR Log Image Storage")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

        self._setup_ui()

    def _setup_ui(self):
        # 1. 툴바 (Toolbar)
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        action_open = QAction("📂 폴더 열기", self)
        action_refresh = QAction("🔄 새로고침", self)
        action_settings = QAction("⚙ 설정", self)

        toolbar.addAction(action_open)
        toolbar.addAction(action_refresh)
        toolbar.addAction(action_settings)

        # 2. 중앙 레이아웃 (Splitter)
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        # 2-1. 좌측 패널 (작품 목록)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(8)

        title_label = QLabel("작품 목록")
        font = title_label.font()
        font.setBold(True)
        title_label.setFont(font)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("SeparatorLine") # QSS 적용을 위한 ObjectName 설정

        list_widget = QListWidget()

        left_layout.addWidget(title_label)
        left_layout.addWidget(line)
        left_layout.addWidget(list_widget)

        # 2-2. 우측 패널 (이미지 뷰어)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        viewer_label = QLabel("이미지를 불러오세요.")
        viewer_label.setAlignment(Qt.AlignCenter)
        
        scroll_area.setWidget(viewer_label)

        # 스플리터에 위젯 추가
        splitter.addWidget(left_panel)
        splitter.addWidget(scroll_area)

        # 좌측 패널 폭 약 220px 설정 (비율 조정)
        splitter.setSizes([220, 980])

        # 3. 상태바 (Status Bar)
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("준비 완료")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # assets/dark.qss 파일 읽기 및 스타일 적용
    current_dir = os.path.dirname(os.path.abspath(__file__))
    qss_path = os.path.join(current_dir, "assets", "dark.qss")
    
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"[경고] 테마 파일을 찾을 수 없습니다: {qss_path}")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())