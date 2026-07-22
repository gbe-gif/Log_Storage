import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar, QSplitter,
    QListWidget, QScrollArea, QLabel, QVBoxLayout, QWidget, QFrame,
    QFileDialog, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

import image_loader
import image_merger
import image_converter
import image_card
import project_manager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PR Log Image Storage")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

        self.current_folder = None
        self.current_project = None  
        self.image_cards = []
        self.turn_map = {}
        
        self._setup_ui()

    def _setup_ui(self):
        # 1. 툴바 (Toolbar)
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        action_open = QAction("📂 폴더 열기", self)
        action_new = QAction("📁 새 작품", self)
        action_refresh = QAction("🔄 새로고침", self)
        action_settings = QAction("⚙ 설정", self)

        action_open.triggered.connect(self.open_folder)
        action_new.triggered.connect(self.create_new_project)
        action_refresh.triggered.connect(self.on_action_refresh)

        toolbar.addAction(action_open)
        toolbar.addAction(action_new)
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

        # -- Turn 목록 UI --
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
        return self.scroll_area.viewport().width() - 40


    def clear_image_cards(self):
        for card in self.image_cards:
            self.scroll_layout.removeWidget(card)
            card.deleteLater()
            
        self.image_cards.clear()
        self.turn_map.clear()
        
        self.turn_list.blockSignals(True)
        self.turn_list.clear()
        self.turn_list.blockSignals(False)
        
        self.viewer_label.show()


    def reload_project_list(self, select_name=None):
        self.project_list.blockSignals(True)
        self.project_list.clear()
        
        projects = image_loader.load_projects(self.current_folder)
        for project in projects:
            self.project_list.addItem(project)
            
        self.project_list.blockSignals(False)
        
        if select_name:
            items = self.project_list.findItems(select_name, Qt.MatchExactly)
            if items:
                self.project_list.setCurrentItem(items[0])


    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "저장소 폴더 선택", "")
        
        if folder_path:
            self.current_folder = folder_path
            self.current_project = None
            self.clear_image_cards()
            
            self.reload_project_list()
            
            count = self.project_list.count()
            if count > 0:
                self.status_bar.showMessage(f"작품 {count}개를 불러왔습니다.")
            else:
                self.status_bar.showMessage("작품이 없습니다.")


    # ==========================================
    # v1.4.2 개선: 분석 모듈 연동 및 미리보기/예외처리 고도화
    # ==========================================
    def create_new_project(self):
        if not self.current_folder:
            QMessageBox.warning(self, "경고", "먼저 '📂 폴더 열기'를 통해 저장소 폴더를 선택해주세요.")
            return

        name, ok = QInputDialog.getText(self, "새 작품 생성", "작품명을 입력하세요:")
        if not ok:
            return
            
        name = name.strip()
        if not name:
            QMessageBox.warning(self, "경고", "작품명이 비어있습니다.")
            return

        if project_manager.project_exists(self.current_folder, name):
            QMessageBox.warning(self, "경고", f"'{name}'(은)는 이미 존재하는 작품명입니다.")
            return

        files, _ = QFileDialog.getOpenFileNames(
            self, "이미지 선택", "", "PNG Images (*.png *.PNG)"
        )
        if not files:
            return

        # 개선된 분석 로직 호출
        result = project_manager.analyze_import_files(files)
        valid_files = result["valid_files"]
        invalid_files = result["invalid_files"]
        turns = result["turns"]
        turn_ranges = result["turn_ranges"]

        # 정상 파일이 하나도 없는 경우 프로젝트 생성 중단
        if not valid_files:
            QMessageBox.warning(self, "경고", "가져올 수 있는 정상적인 이미지 파일(형식: 숫자_숫자.png)이 하나도 없습니다.")
            return

        # 연속 구간(Range)으로 압축된 예상 병합 결과 문구 조립
        merge_preview_lines = []
        for r in turn_ranges:
            if r["start"] == r["end"]:
                merge_preview_lines.append(f"Turn {r['start']} | {r['count']}장")
            else:
                merge_preview_lines.append(f"Turn {r['start']} ~ Turn {r['end']} | {r['count']}장")
        
        merge_preview_str = "\n".join(merge_preview_lines) if merge_preview_lines else "없음"

        # 미리보기 텍스트 구성
        preview_text = (
            f"작품명\n{name}\n"
            f"────────────\n"
            f"선택 이미지\n{len(files)}장\n"
            f"정상 파일\n{len(valid_files)}장\n"
            f"────────────\n"
            f"예상 Turn\n{len(turns)}개\n"
            f"────────────\n"
            f"예상 병합 결과\n{merge_preview_str}\n"
        )
        
        # 인식 불가 파일 출력 (존재할 경우만)
        if invalid_files:
            preview_text += (
                f"────────────\n"
                f"인식 불가 파일\n" + "\n".join(invalid_files)
            )

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("가져오기 확인")
        msg_box.setText(preview_text)
        
        btn_cancel = msg_box.addButton("취소", QMessageBox.RejectRole)
        btn_import = msg_box.addButton("가져오기", QMessageBox.AcceptRole)
        
        msg_box.exec()
        
        if msg_box.clickedButton() == btn_cancel:
            return
            
        # 정상 파일만 복사 후 새로고침
        project_path = project_manager.create_project(self.current_folder, name)
        project_manager.copy_images(project_path, valid_files)
        
        self.reload_project_list(select_name=name)
        self.status_bar.showMessage(f"'{name}' 프로젝트를 생성했습니다.")


    def on_project_changed(self, current, previous):
        if not current or not self.current_folder:
            return
            
        self.current_project = current.text()
        self.refresh_project()


    def on_turn_changed(self, current, previous):
        if not current:
            return
            
        text = current.text()
        try:
            turn_num = int(text.replace("Turn ", ""))
            if turn_num in self.turn_map:
                card = self.turn_map[turn_num]
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