import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar, QSplitter,
    QListWidget, QScrollArea, QLabel, QVBoxLayout, QWidget, QFrame,
    QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QImage, QPixmap

import image_loader
import image_merger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PR Log Image Storage")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

        self.current_folder = None
        self.image_labels = []  # 동적으로 추가된 이미지 QLabel들을 추적하는 리스트
        
        self._setup_ui()

    def _setup_ui(self):
        # 1. 툴바 (Toolbar)
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        action_open = QAction("📂 폴더 열기", self)
        action_refresh = QAction("🔄 새로고침", self)
        action_settings = QAction("⚙ 설정", self)

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

        self.project_list = QListWidget()
        self.project_list.currentItemChanged.connect(self.on_project_changed)

        left_layout.addWidget(title_label)
        left_layout.addWidget(line)
        left_layout.addWidget(self.project_list)

        # 2-2. 우측 패널 (이미지 뷰어) - 멤버 변수로 승격
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        
        self.viewer_label = QLabel("이미지를 불러오세요.")
        self.viewer_label.setAlignment(Qt.AlignCenter)
        
        self.scroll_layout.addWidget(self.viewer_label)
        self.scroll_layout.addStretch()  # Stretch는 항상 마지막에 위치해야 함
        
        self.scroll_area.setWidget(self.scroll_widget)

        splitter.addWidget(left_panel)
        splitter.addWidget(self.scroll_area)
        splitter.setSizes([220, 980])

        # 3. 상태바 (Status Bar)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("준비 완료")


    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "저장소 폴더 선택", "")
        
        if folder_path:
            self.current_folder = folder_path
            
            self.project_list.blockSignals(True)
            self.project_list.clear()
            
            projects = image_loader.load_projects(self.current_folder)
            
            for project in projects:
                self.project_list.addItem(project)
                
            self.project_list.blockSignals(False)
                
            if len(projects) > 0:
                self.status_bar.showMessage(f"작품 {len(projects)}개를 불러왔습니다.")
            else:
                self.status_bar.showMessage("작품이 없습니다.")


    def on_project_changed(self, current, previous):
        if not current or not self.current_folder:
            return
            
        project_name = current.text()
        project_path = os.path.join(self.current_folder, project_name)
        
        # 1. 파일 시스템에서 이미지 목록 가져오기
        images = image_loader.load_images(project_path)
        
        # 2. 이미지 병합 로직 수행
        merged_data_list = image_merger.merge_images(project_path, images)
        
        # 3. 기존에 출력되어 있던 이미지 라벨들 제거 (placeholder와 stretch 제외)
        for lbl in self.image_labels:
            self.scroll_layout.removeWidget(lbl)
            lbl.deleteLater()
        self.image_labels.clear()

        # 4. 출력할 이미지가 없으면 Placeholder 표시 후 종료
        if not merged_data_list:
            self.viewer_label.show()
            self.status_bar.showMessage(f"'{project_name}'에 표시할 이미지가 없습니다.")
            return
            
        self.viewer_label.hide()
        
        # 가로 폭 계산 (스크롤바 등 여백을 고려해 Viewport 가로 크기에서 패딩을 뺌)
        available_width = self.scroll_area.viewport().width() - 40
        
        # 5. PIL -> QPixmap 변환 및 출력
        for data in merged_data_list:
            pil_img = data["image"]
            
            # [PIL.Image -> QImage] 변환 (raw bytes 추출)
            raw_data = pil_img.tobytes("raw", "RGBA")
            qimg = QImage(raw_data, pil_img.width, pil_img.height, QImage.Format_RGBA8888)
            
            # [QImage -> QPixmap] 변환
            pixmap = QPixmap.fromImage(qimg)
            
            # 가로 폭에 맞게 축소 (원본이 작으면 확대하지 않음)
            if pixmap.width() > available_width:
                pixmap = pixmap.scaledToWidth(available_width, Qt.SmoothTransformation)
                
            # QLabel에 Pixmap 세팅
            lbl = QLabel()
            lbl.setPixmap(pixmap)
            lbl.setAlignment(Qt.AlignCenter)
            
            # Stretch(여백 위젯) 바로 앞에 위젯을 삽입 (순서 유지)
            insert_index = self.scroll_layout.count() - 1
            self.scroll_layout.insertWidget(insert_index, lbl)
            
            self.image_labels.append(lbl)
            
        self.status_bar.showMessage(f"'{project_name}' - {len(merged_data_list)}개의 이미지 턴을 불러왔습니다.")


if __name__ == "__main__":
    app = QApplication(sys.argv)

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