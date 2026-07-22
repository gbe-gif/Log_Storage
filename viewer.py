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
import image_converter
import image_card

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PR Log Image Storage")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

        self.current_folder = None
        self.current_project = None  
        self.image_cards = []
        
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
        # 새로고침 래퍼 메서드로 연결하여 UX 문구 처리 분리
        action_refresh.triggered.connect(self.on_action_refresh)

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


    def get_available_width(self):
        """ScrollArea의 사용 가능한 가로 폭(패딩 포함)을 계산합니다."""
        return self.scroll_area.viewport().width() - 40


    # ==========================================
    # v1.2.1 추가: 초기화 로직 캡슐화
    # ==========================================
    def clear_image_cards(self):
        """현재 출력된 모든 ImageCard를 제거하고 뷰어를 초기 상태로 되돌립니다."""
        for card in self.image_cards:
            self.scroll_layout.removeWidget(card)
            card.deleteLater()
            
        self.image_cards.clear()
        self.viewer_label.show()


    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "저장소 폴더 선택", "")
        
        if folder_path:
            self.current_folder = folder_path
            
            # v1.2.1 개선: 새 폴더를 열면 프로젝트를 초기화하고 화면 정리
            self.current_project = None
            self.clear_image_cards()
            
            self.project_list.blockSignals(True)
            self.project_list.clear()
            
            projects = image_loader.load_projects(self.current_folder)
            
            for project in projects:
                self.project_list.addItem(project)
                
            self.project_list.blockSignals(False)
                
            # v1.2.1 개선: 상태바 문구를 기본 상태로 전환
            if len(projects) > 0:
                self.status_bar.showMessage(f"작품 {len(projects)}개를 불러왔습니다.")
            else:
                self.status_bar.showMessage("작품이 없습니다.")


    def on_project_changed(self, current, previous):
        if not current or not self.current_folder:
            return
            
        self.current_project = current.text()
        self.refresh_project()


    # ==========================================
    # v1.2.1 개선: 새로고침 버튼 UX 전용 래퍼
    # ==========================================
    def on_action_refresh(self):
        """툴바의 새로고침 버튼 클릭 시 실행됩니다."""
        self.refresh_project()
        
        # 새로고침이 성공적으로 완료되었을 때만 완료 안내 문구 표시
        if self.current_folder and self.current_project:
            self.status_bar.showMessage(f"새로고침 완료: '{self.current_project}' - {len(self.image_cards)}개의 Turn을 불러왔습니다.")


    def refresh_project(self):
        """현재 선택된 프로젝트의 이미지를 디스크에서 다시 읽어와 재출력합니다."""
        # v1.2.1 개선: 안내 메시지를 띄우고 자연스럽게 종료
        if not self.current_folder or not self.current_project:
            self.status_bar.showMessage("먼저 작품을 선택하세요.")
            return
            
        project_path = os.path.join(self.current_folder, self.current_project)
        
        images = image_loader.load_images(project_path)
        merged_data_list = image_merger.merge_images(project_path, images)
        
        self.display_images(merged_data_list, self.current_project)


    def display_images(self, merged_data_list, project_name):
        # v1.2.1 개선: 중복된 삭제 로직 대신 메서드 호출
        self.clear_image_cards()

        if not merged_data_list:
            self.status_bar.showMessage(f"'{project_name}'에 표시할 이미지가 없습니다.")
            return
            
        # 데이터가 있으므로 Placeholder 숨김
        self.viewer_label.hide()
        
        available_width = self.get_available_width()
        
        for data in merged_data_list:
            pil_img = data["image"]
            pixmap = image_converter.pil_to_pixmap(pil_img)
            
            card = image_card.ImageCard(
                turn=data["turn"],
                files=data["files"],
                pixmap=pixmap
            )
            card.set_display_width(available_width)
            
            insert_index = self.scroll_layout.count() - 1
            self.scroll_layout.insertWidget(insert_index, card)
            
            self.image_cards.append(card)
            
        # v1.2.1 개선: 문구를 조금 더 부드럽게 통일
        self.status_bar.showMessage(f"'{project_name}' - {len(merged_data_list)}개의 Turn을 불러왔습니다.")


    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        if hasattr(self, 'scroll_area') and self.image_cards:
            available_width = self.get_available_width()
            for card in self.image_cards:
                card.set_display_width(available_width)


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