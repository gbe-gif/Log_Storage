import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar, QSplitter,
    QListWidget, QScrollArea, QLabel, QVBoxLayout, QWidget, QFrame,
    QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

# 새로 추가된 image_loader 모듈 임포트
import image_loader

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 윈도우 기본 설정
        self.setWindowTitle("PR Log Image Storage")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

        # 상태 관리를 위한 멤버 변수 추가
        self.current_folder = None
        
        self._setup_ui()

    def _setup_ui(self):
        # 1. 툴바 (Toolbar)
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        action_open = QAction("📂 폴더 열기", self)
        action_refresh = QAction("🔄 새로고침", self)
        action_settings = QAction("⚙ 설정", self)

        # '폴더 열기' 액션에 메서드 연결
        action_open.triggered.connect(self.open_folder)

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
        line.setObjectName("SeparatorLine")

        # 지역 변수에서 멤버 변수로 승격
        self.project_list = QListWidget()

        left_layout.addWidget(title_label)
        left_layout.addWidget(line)
        left_layout.addWidget(self.project_list)

        # 2-2. 우측 패널 (이미지 뷰어) - v0.3 구조 유지
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        viewer_label = QLabel("이미지를 불러오세요.")
        viewer_label.setAlignment(Qt.AlignCenter)
        
        scroll_layout.addWidget(viewer_label)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)

        splitter.addWidget(left_panel)
        splitter.addWidget(scroll_area)
        splitter.setSizes([220, 980])

        # 3. 상태바 (Status Bar)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("준비 완료")


    def open_folder(self):
        """
        QFileDialog를 열어 폴더를 선택하고,
        image_loader를 통해 하위 폴더(작품)를 읽어와 QListWidget에 표시합니다.
        """
        folder_path = QFileDialog.getExistingDirectory(self, "저장소 폴더 선택", "")
        
        if folder_path:
            # 1. 멤버 변수에 경로 저장
            self.current_folder = folder_path
            print(f"선택한 폴더: {self.current_folder}")
            
            # 2. image_loader를 사용하여 프로젝트 목록 불러오기
            projects = image_loader.load_projects(self.current_folder)
            
            # 3. 기존 리스트 초기화 후 새로 추가
            self.project_list.clear()
            for project in projects:
                self.project_list.addItem(project)
                
            # 4. 결과에 따라 상태바 업데이트
            if len(projects) > 0:
                self.status_bar.showMessage(f"작품 {len(projects)}개를 불러왔습니다.")
            else:
                self.status_bar.showMessage("작품이 없습니다.")


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