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
        
        # v1.3 추가: Turn 번호와 ImageCard를 매핑할 딕셔너리
        self.turn_map = {}
        
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
        action_refresh.triggered.connect(self.on_action_refresh)

        toolbar.addAction(action_open)
        toolbar.addAction(action_refresh)
        toolbar.addAction(action_settings)

        # 2. 중앙 레이아웃 (Splitter)
        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        # 2-1. 좌측 패널 (작품 목록 & Turn 목록)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(8)

        # -- 작품 목록 UI --
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

        # -- v1.3 추가: Turn 목록 UI --
        turn_title_label = QLabel("Turn 목록")
        turn_font = turn_title_label.font()
        turn_font.setBold(True)
        turn_title_label.setFont(turn_font)

        turn_line = QFrame()
        turn_line.setFrameShape(QFrame.HLine)
        turn_line.setFrameShadow(QFrame.Sunken)
        turn_line.setObjectName("SeparatorLine")

        self.turn_list = QListWidget()
        self.turn_list.currentItemChanged.connect(self.on_turn_changed)

        # 레이아웃에 Turn 목록 위젯들 추가
        left_layout.addWidget(turn_title_label)
        left_layout.addWidget(turn_line)
        left_layout.addWidget(self.turn_list)

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


    def clear_image_cards(self):
        """현재 출력된 모든 ImageCard를 제거하고 뷰어 및 Turn 목록을 초기 상태로 되돌립니다."""
        for card in self.image_cards:
            self.scroll_layout.removeWidget(card)
            card.deleteLater()
            
        self.image_cards.clear()
        
        # v1.3 추가: Turn 목록 및 매핑 딕셔너리 초기화
        self.turn_map.clear()
        self.turn_list.blockSignals(True)
        self.turn_list.clear()
        self.turn_list.blockSignals(False)
        
        self.viewer_label.show()


    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "저장소 폴더 선택", "")
        
        if folder_path:
            self.current_folder = folder_path
            
            self.current_project = None
            self.clear_image_cards()
            
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
            
        self.current_project = current.text()
        self.refresh_project()


    # ==========================================
    # v1.3 추가: Turn 목록 아이템 클릭 시 해당 위치로 스크롤
    # ==========================================
    def on_turn_changed(self, current, previous):
        if not current:
            return
            
        text = current.text()
        try:
            # "Turn 15" -> 15 추출
            turn_num = int(text.replace("Turn ", ""))
            if turn_num in self.turn_map:
                card = self.turn_map[turn_num]
                # 지정된 위젯이 화면에 보이도록 스크롤 이동
                self.scroll_area.ensureWidgetVisible(card)
        except ValueError:
            pass


    def on_action_refresh(self):
        self.refresh_project()
        
        if self.current_folder and self.current_project:
            self.status_bar.showMessage(f"새로고침 완료: '{self.current_project}' - {len(self.image_cards)}개의 Turn을 불러왔습니다.")


    def refresh_project(self):
        if not self.current_folder or not self.current_project:
            self.status_bar.showMessage("먼저 작품을 선택하세요.")
            return
            
        project_path = os.path.join(self.current_folder, self.current_project)
        
        images = image_loader.load_images(project_path)
        merged_data_list = image_merger.merge_images(project_path, images)
        
        self.display_images(merged_data_list, self.current_project)


    def display_images(self, merged_data_list, project_name):
        self.clear_image_cards()

        if not merged_data_list:
            self.status_bar.showMessage(f"'{project_name}'에 표시할 이미지가 없습니다.")
            return
            
        self.viewer_label.hide()
        available_width = self.get_available_width()
        
        # Turn 목록 추가 중 이벤트가 발생하지 않도록 차단
        self.turn_list.blockSignals(True)
        
        for data in merged_data_list:
            pil_img = data["image"]
            pixmap = image_converter.pil_to_pixmap(pil_img)
            turn_num = data["turn"]
            
            card = image_card.ImageCard(
                turn=turn_num,
                files=data["files"],
                pixmap=pixmap
            )
            card.set_display_width(available_width)
            
            insert_index = self.scroll_layout.count() - 1
            self.scroll_layout.insertWidget(insert_index, card)
            
            self.image_cards.append(card)
            
            # v1.3 추가: Turn 목록에 추가 및 맵핑 등록
            self.turn_map[turn_num] = card
            self.turn_list.addItem(f"Turn {turn_num}")
            
        self.turn_list.blockSignals(False)
            
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