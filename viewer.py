import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar, QSplitter,
    QListWidget, QScrollArea, QLabel, QVBoxLayout, QWidget, QFrame,
    QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

import image_loader
import image_merger
import image_converter  # 새로 추가된 변환 모듈

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PR Log Image Storage")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

        self.current_folder = None
        self.image_labels = []
        
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

        # 2-2. 우측 패널 (이미지 뷰어)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        
        self.viewer_label = QLabel("이미지를 불러오세요.")
        self.viewer_label.setAlignment(Qt.AlignCenter)
        
        self.scroll_layout.addWidget(self.viewer_label)
        self.scroll_layout.addStretch()
        
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
        
        # 1. 프로젝트 경로 생성
        project_path = os.path.join(self.current_folder, project_name)
        
        # 2. 이미지 목록 로드
        images = image_loader.load_images(project_path)
        
        # 3. 이미지 병합
        merged_data_list = image_merger.merge_images(project_path, images)
        
        # 4. 이미지 출력 로직 호출
        self.display_images(merged_data_list, project_name)


    def display_images(self, merged_data_list, project_name):
        """
        병합된 이미지 데이터를 UI(ScrollArea)에 출력합니다.
        """
        # 기존 라벨 모두 제거
        for lbl in self.image_labels:
            self.scroll_layout.removeWidget(lbl)
            lbl.deleteLater()
        self.image_labels.clear()

        # 이미지가 없을 경우 처리
        if not merged_data_list:
            self.viewer_label.show()
            self.status_bar.showMessage(f"'{project_name}'에 표시할 이미지가 없습니다.")
            return
            
        self.viewer_label.hide()
        
        available_width = self.scroll_area.viewport().width() - 40
        
        # 변환 모듈을 이용한 Pixmap 출력
        for data in merged_data_list:
            pil_img = data["image"]
            
            # image_converter를 통해 변환
            pixmap = image_converter.pil_to_pixmap(pil_img)
            
            # 가로 폭에 맞게 축소
            if pixmap.width() > available_width:
                pixmap = pixmap.scaledToWidth(available_width, Qt.SmoothTransformation)
                
            lbl = QLabel()
            lbl.setPixmap(pixmap)
            lbl.setAlignment(Qt.AlignCenter)
            
            # Stretch 앞에 삽입
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