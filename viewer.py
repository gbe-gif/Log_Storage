import sys
import os
import subprocess
import PySide6
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QStatusBar, QSplitter,
    QListWidget, QScrollArea, QLabel, QVBoxLayout, QWidget, QFrame,
    QFileDialog, QInputDialog, QMessageBox, QHBoxLayout, QToolButton, QMenu,
    QLineEdit, QDialog, QGroupBox, QPushButton, QListWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon

import image_loader
import image_merger
import image_converter
import image_card
import project_manager
import config_manager


# ==========================================
# 설정 창 다이얼로그
# ==========================================
class SettingsDialog(QDialog):
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.setWindowTitle("설정")
        self.resize(500, 400)
        self.config = config
        
        main_layout = QVBoxLayout(self)
        
        # 1. 프로그램 정보
        info_group = QGroupBox("프로그램 정보")
        info_layout = QVBoxLayout(info_group)
        info_layout.addWidget(QLabel("<b>PR Log Image Storage</b>"))
        info_layout.addWidget(QLabel("Version: v1.9"))
        info_layout.addWidget(QLabel("Developer: -"))
        info_layout.addWidget(QLabel("Build: 2026.07"))
        info_layout.addWidget(QLabel(f"Python Version: {sys.version.split()[0]}"))
        info_layout.addWidget(QLabel(f"PySide Version: {PySide6.__version__}"))
        main_layout.addWidget(info_group)
        
        # 2. 기본 저장소 설정
        storage_group = QGroupBox("기본 저장소 설정")
        storage_layout = QVBoxLayout(storage_group)
        self.storage_label = QLabel(self.config.get("storage_root", ""))
        self.storage_label.setWordWrap(True)
        self.storage_label.setStyleSheet("color: #A0A0A0;")
        
        btn_layout1 = QHBoxLayout()
        btn_layout1.addWidget(self.storage_label)
        change_btn1 = QPushButton("변경...")
        change_btn1.clicked.connect(self.change_storage)
        btn_layout1.addWidget(change_btn1)
        storage_layout.addLayout(btn_layout1)
        main_layout.addWidget(storage_group)
        
        # 3. v1.9 추가: RP Preview Studio 설정
        rp_group = QGroupBox("RP Preview Studio 경로 설정")
        rp_layout = QVBoxLayout(rp_group)
        self.rp_label = QLabel(self.config.get("rp_preview_studio_path", "등록된 경로가 없습니다."))
        self.rp_label.setWordWrap(True)
        self.rp_label.setStyleSheet("color: #A0A0A0;")
        
        btn_layout2 = QHBoxLayout()
        btn_layout2.addWidget(self.rp_label)
        change_btn2 = QPushButton("찾아보기...")
        change_btn2.clicked.connect(self.change_rp_path)
        btn_layout2.addWidget(change_btn2)
        rp_layout.addLayout(btn_layout2)
        main_layout.addWidget(rp_group)
        
        main_layout.addStretch()
        
        close_btn = QPushButton("닫기")
        close_btn.setFixedWidth(80)
        close_btn.clicked.connect(self.accept)
        main_layout.addWidget(close_btn, alignment=Qt.AlignRight)

    def change_storage(self):
        current_root = self.config.get("storage_root", "")
        new_dir = QFileDialog.getExistingDirectory(self, "기본 저장소 선택", current_root)
        if new_dir:
            self.config["storage_root"] = new_dir
            self.storage_label.setText(new_dir)
            config_manager.save_config(self.config)

    def change_rp_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "RP Preview Studio 실행 파일 선택", "", "Executable (*.exe);;All Files (*)")
        if path:
            self.config["rp_preview_studio_path"] = path
            self.rp_label.setText(path)
            config_manager.save_config(self.config)


# ==========================================
# v1.9 추가: 휴지통 다이얼로그
# ==========================================
class TrashDialog(QDialog):
    def __init__(self, base_folder, parent=None):
        super().__init__(parent)
        self.setWindowTitle("휴지통 관리")
        self.resize(500, 350)
        self.base_folder = base_folder
        
        layout = QVBoxLayout(self)
        
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        self.btn_restore = QPushButton("복원")
        self.btn_delete = QPushButton("영구 삭제")
        self.btn_empty = QPushButton("휴지통 비우기")
        
        btn_layout.addWidget(self.btn_restore)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_empty)
        
        layout.addLayout(btn_layout)
        
        self.btn_restore.clicked.connect(self.restore_selected)
        self.btn_delete.clicked.connect(self.delete_selected)
        self.btn_empty.clicked.connect(self.empty_all)
        
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        trashed_items = project_manager.get_trashed_projects(self.base_folder)
        for item_data in trashed_items:
            text = f"{item_data['original_name']}  (삭제일: {item_data['deleted_at']})"
            list_item = QListWidgetItem(text)
            list_item.setData(Qt.UserRole, item_data)
            self.list_widget.addItem(list_item)

    def restore_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "경고", "복원할 항목을 선택해주세요.")
            return
            
        data = item.data(Qt.UserRole)
        success = project_manager.restore_from_trash(self.base_folder, data['trashed_name'], data['original_name'])
        if success:
            QMessageBox.information(self, "복원", f"'{data['original_name']}' 복원이 완료되었습니다.")
            self.refresh_list()
        else:
            QMessageBox.warning(self, "오류", "복원 중 문제가 발생했습니다.")

    def delete_selected(self):
        item = self.list_widget.currentItem()
        if not item:
            return
            
        data = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "영구 삭제", f"'{data['original_name']}'을(를) 영구 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.", QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success = project_manager.permanent_delete(self.base_folder, data['trashed_name'])
            if success:
                self.refresh_list()
            else:
                QMessageBox.warning(self, "오류", "삭제 중 문제가 발생했습니다.")

    def empty_all(self):
        if self.list_widget.count() == 0:
            return
            
        reply = QMessageBox.question(self, "휴지통 비우기", "휴지통의 모든 항목을 영구 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다.", QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success = project_manager.empty_trash(self.base_folder)
            if success:
                self.refresh_list()
            else:
                QMessageBox.warning(self, "오류", "휴지통 비우기 중 문제가 발생했습니다.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("PR Log Image Storage")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        
        # v1.9: 프로그램 아이콘 적용
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.config = config_manager.load_config()

        self.current_folder = None
        self.current_project = None  
        self.image_cards = []
        self.turn_map = {}
        
        self._setup_ui()

    def _setup_ui(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        action_open = QAction("📂 폴더 열기", self)
        action_new = QAction("📁 새 작품", self)
        action_add = QAction("📥 이미지 추가", self)
        action_refresh = QAction("🔄 새로고침", self)
        action_rp_studio = QAction("🚀 RP Preview Studio", self)
        action_trash = QAction("🗑 휴지통", self)
        action_settings = QAction("⚙ 설정", self)

        action_open.triggered.connect(self.open_folder)
        action_new.triggered.connect(self.create_new_project)
        action_add.triggered.connect(self.add_images_to_project)
        action_refresh.triggered.connect(self.on_action_refresh)
        action_rp_studio.triggered.connect(self.launch_rp_studio)
        action_trash.triggered.connect(self.open_trash_dialog)
        action_settings.triggered.connect(self.open_settings_dialog)

        toolbar.addAction(action_open)
        toolbar.addAction(action_new)
        toolbar.addAction(action_add)
        toolbar.addAction(action_refresh)
        toolbar.addSeparator()
        toolbar.addAction(action_rp_studio)
        toolbar.addSeparator()
        toolbar.addAction(action_trash)
        toolbar.addAction(action_settings)

        splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(splitter)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(8)

        header_layout = QHBoxLayout()
        title_label = QLabel("작품 목록")
        font = title_label.font()
        font.setBold(True)
        title_label.setFont(font)
        
        self.project_menu_btn = QToolButton()
        self.project_menu_btn.setText("⋮")
        self.project_menu_btn.setPopupMode(QToolButton.InstantPopup)
        self.project_menu_btn.setEnabled(False)
        
        project_menu = QMenu(self)
        action_open_folder = QAction("📂 프로젝트 폴더 열기", self)
        action_rename = QAction("✏ 프로젝트 이름 변경", self)
        action_delete = QAction("🗑 프로젝트 삭제", self)
        
        action_open_folder.triggered.connect(self.open_current_project_folder)
        action_rename.triggered.connect(self.rename_current_project)
        action_delete.triggered.connect(self.delete_current_project)
        
        project_menu.addAction(action_open_folder)
        project_menu.addSeparator()
        project_menu.addAction(action_rename)
        project_menu.addAction(action_delete)
        
        self.project_menu_btn.setMenu(project_menu)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.project_menu_btn)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("SeparatorLine")

        self.project_list = QListWidget()
        self.project_list.currentItemChanged.connect(self.on_project_changed)

        left_layout.addLayout(header_layout)
        left_layout.addWidget(line)
        left_layout.addWidget(self.project_list)

        turn_title_label = QLabel("Turn 목록")
        turn_title_label.setFont(font)
        turn_line = QFrame()
        turn_line.setFrameShape(QFrame.HLine)
        turn_line.setFrameShadow(QFrame.Sunken)
        turn_line.setObjectName("SeparatorLine")
        
        self.turn_search_input = QLineEdit()
        self.turn_search_input.setPlaceholderText("🔍 Turn 검색...")
        self.turn_search_input.textChanged.connect(self.filter_turns)

        self.turn_list = QListWidget()
        self.turn_list.currentItemChanged.connect(self.on_turn_changed)

        left_layout.addWidget(turn_title_label)
        left_layout.addWidget(self.turn_search_input)
        left_layout.addWidget(turn_line)
        left_layout.addWidget(self.turn_list)

        info_line = QFrame()
        info_line.setFrameShape(QFrame.HLine)
        info_line.setFrameShadow(QFrame.Sunken)
        info_line.setObjectName("SeparatorLine")
        
        self.info_label = QLabel("프로젝트 정보가 없습니다.")
        self.info_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        left_layout.addWidget(info_line)
        left_layout.addWidget(self.info_label)

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
        
        self.turn_search_input.blockSignals(True)
        self.turn_search_input.clear()
        self.turn_search_input.blockSignals(False)
        
        self.viewer_label.show()
        self.info_label.setText("프로젝트 정보가 없습니다.")

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

    def open_settings_dialog(self):
        dialog = SettingsDialog(self, self.config)
        dialog.exec()

    # ==========================================
    # v1.9: 휴지통 & 프로그램 연동 기능
    # ==========================================
    def open_trash_dialog(self):
        if not self.current_folder:
            QMessageBox.warning(self, "경고", "먼저 '📂 폴더 열기'를 통해 기본 저장소를 선택해주세요.")
            return
            
        dialog = TrashDialog(self.current_folder, self)
        dialog.exec()
        # 다이얼로그 종료 후 프로젝트 복원이 있을 수 있으므로 리스트 새로고침
        self.on_action_refresh()

    def launch_rp_studio(self):
        path = self.config.get("rp_preview_studio_path", "")
        if not path:
            QMessageBox.information(self, "안내", "RP Preview Studio 경로가 설정되어 있지 않습니다.\n설정 창에서 실행 파일(.exe)을 먼저 지정해주세요.")
            self.open_settings_dialog()
            return
            
        if not os.path.exists(path):
            QMessageBox.warning(self, "경고", "설정된 경로에 RP Preview Studio 파일이 존재하지 않습니다.\n경로를 다시 확인해주세요.")
            self.open_settings_dialog()
            return
            
        try:
            subprocess.Popen([path])
            self.status_bar.showMessage("RP Preview Studio를 실행했습니다.")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"프로그램을 실행하는 중 문제가 발생했습니다:\n{e}")

    def open_folder(self):
        start_dir = self.config.get("storage_root", "")
        folder_path = QFileDialog.getExistingDirectory(self, "저장소 폴더 선택", start_dir)
        
        if folder_path:
            self.current_folder = folder_path
            self.current_project = None
            self.project_menu_btn.setEnabled(False)
            self.clear_image_cards()
            
            self.reload_project_list()
            
            count = self.project_list.count()
            if count > 0:
                self.status_bar.showMessage(f"작품 {count}개를 불러왔습니다.")
            else:
                self.status_bar.showMessage("작품이 없습니다.")

    def _check_project_selected(self):
        if not self.current_folder or not self.current_project:
            QMessageBox.information(self, "안내", "먼저 관리할 작품(프로젝트)을 선택해주세요.")
            return False
        return True

    def open_current_project_folder(self):
        if not self._check_project_selected():
            return
            
        project_path = os.path.join(self.current_folder, self.current_project)
        success = project_manager.open_project_folder(project_path)
        if not success:
            QMessageBox.warning(self, "오류", "프로젝트 폴더를 열 수 없습니다.")

    def rename_current_project(self):
        if not self._check_project_selected():
            return

        new_name, ok = QInputDialog.getText(self, "프로젝트 이름 변경", "새 이름을 입력하세요:", text=self.current_project)
        if not ok:
            return
        new_name = new_name.strip()
        if not new_name:
            QMessageBox.warning(self, "경고", "프로젝트 이름이 비어있습니다.")
            return
        if new_name == self.current_project:
            return
        if project_manager.project_exists(self.current_folder, new_name):
            QMessageBox.warning(self, "경고", f"'{new_name}'(은)는 이미 존재하는 프로젝트명입니다.")
            return
            
        success = project_manager.rename_project(self.current_folder, self.current_project, new_name)
        if success:
            self.reload_project_list(select_name=new_name)
            self.status_bar.showMessage(f"프로젝트 이름이 '{new_name}'(으)로 변경되었습니다.")
        else:
            QMessageBox.warning(self, "오류", "이름 변경 중 오류가 발생했습니다. 권한이나 파일 잠금을 확인하세요.")

    def delete_current_project(self):
        if not self._check_project_selected():
            return

        project_path = os.path.join(self.current_folder, self.current_project)
        info = project_manager.get_project_summary(project_path)

        preview_text = (
            f"'{self.current_project}' 프로젝트를 휴지통으로 이동하시겠습니까?\n\n"
            f"Turn: {info['turn_count']}\n"
            f"이미지: {info['image_count']}"
        )

        reply = QMessageBox.question(self, "프로젝트 삭제", preview_text, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return
            
        # v1.9: 휴지통으로 이동
        success = project_manager.move_to_trash(self.current_folder, self.current_project)
        if success:
            self.current_project = None
            self.project_menu_btn.setEnabled(False)
            self.clear_image_cards()
            self.reload_project_list()
            self.status_bar.showMessage("프로젝트가 휴지통으로 이동되었습니다.")
        else:
            QMessageBox.warning(self, "오류", "휴지통 이동 중 오류가 발생했습니다. 권한이나 열려있는 파일을 확인하세요.")


    def _process_import_dialog(self, target_project_name):
        files, _ = QFileDialog.getOpenFileNames(
            self, "이미지 선택", "", "PNG Images (*.png *.PNG)"
        )
        if not files:
            return None

        result = project_manager.analyze_import_files(files)
        valid_files = result["valid_files"]
        invalid_files = result["invalid_files"]
        turns = result["turns"]
        turn_ranges = result["turn_ranges"]

        if not valid_files:
            QMessageBox.warning(self, "경고", "가져올 수 있는 정상적인 이미지 파일이 없습니다.")
            return None

        merge_preview_lines = []
        for r in turn_ranges:
            if r["start"] == r["end"]:
                merge_preview_lines.append(f"Turn {r['start']} | {r['count']}장")
            else:
                merge_preview_lines.append(f"Turn {r['start']} ~ Turn {r['end']} | {r['count']}장")
        
        merge_preview_str = "\n".join(merge_preview_lines) if merge_preview_lines else "없음"
        preview_text = (
            f"작품명\n{target_project_name}\n────────────\n"
            f"선택 이미지\n{len(files)}장\n정상 파일\n{len(valid_files)}장\n────────────\n"
            f"예상 Turn\n{len(turns)}개\n────────────\n"
            f"예상 병합 결과\n{merge_preview_str}\n"
        )
        if invalid_files:
            preview_text += f"────────────\n인식 불가 파일\n" + "\n".join(invalid_files)

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("가져오기 확인")
        msg_box.setText(preview_text)
        btn_cancel = msg_box.addButton("취소", QMessageBox.RejectRole)
        btn_import = msg_box.addButton("가져오기", QMessageBox.AcceptRole)
        msg_box.exec()
        
        if msg_box.clickedButton() == btn_cancel:
            return None
        return valid_files


    def create_new_project(self):
        if not self.current_folder:
            QMessageBox.warning(self, "경고", "먼저 '📂 폴더 열기'를 통해 저장소 폴더를 선택해주세요.")
            return

        name, ok = QInputDialog.getText(self, "새 작품 생성", "작품명을 입력하세요:")
        if not ok: return
        name = name.strip()
        if not name:
            QMessageBox.warning(self, "경고", "작품명이 비어있습니다.")
            return
        if project_manager.project_exists(self.current_folder, name):
            QMessageBox.warning(self, "경고", f"'{name}'(은)는 이미 존재하는 작품명입니다.")
            return

        valid_files = self._process_import_dialog(name)
        if not valid_files:
            return
            
        project_path = project_manager.create_project(self.current_folder, name)
        project_manager.copy_images(project_path, valid_files)
        
        self.reload_project_list(select_name=name)
        self.status_bar.showMessage(f"'{name}' 프로젝트를 생성했습니다.")

    def add_images_to_project(self):
        if not self._check_project_selected():
            return
            
        valid_files = self._process_import_dialog(self.current_project)
        if not valid_files:
            return
            
        project_path = os.path.join(self.current_folder, self.current_project)
        project_manager.copy_images(project_path, valid_files)
        
        self.refresh_project()
        self.status_bar.showMessage(f"'{self.current_project}'에 이미지를 추가했습니다.")

    def filter_turns(self, text):
        for i in range(self.turn_list.count()):
            item = self.turn_list.item(i)
            if text in item.text(): item.setHidden(False)
            else: item.setHidden(True)

    def on_project_changed(self, current, previous):
        if not current or not self.current_folder:
            self.project_menu_btn.setEnabled(False)
            return
            
        self.project_menu_btn.setEnabled(True)
        self.current_project = current.text()
        self.turn_search_input.blockSignals(True)
        self.turn_search_input.clear()
        self.turn_search_input.blockSignals(False)
        self.refresh_project()

    def on_turn_changed(self, current, previous):
        if not current: return
        try:
            turn_num = int(current.text().replace("Turn ", ""))
            if turn_num in self.turn_map:
                card = self.turn_map[turn_num]
                self.scroll_area.ensureWidgetVisible(card)
        except ValueError:
            pass

    def on_action_refresh(self):
        if self.current_folder:
            self.reload_project_list(select_name=self.current_project)
        if self.current_project:
            self.refresh_project()
            self.status_bar.showMessage(f"새로고침 완료: '{self.current_project}' - {len(self.image_cards)}개의 Turn을 불러왔습니다.")

    def refresh_project(self):
        if not self.current_folder or not self.current_project:
            self.status_bar.showMessage("먼저 작품을 선택하세요.")
            return
            
        current_turn_item = self.turn_list.currentItem()
        selected_turn_text = current_turn_item.text() if current_turn_item else None
        
        project_path = os.path.join(self.current_folder, self.current_project)
        
        info = project_manager.get_project_summary(project_path)
        info_text = (
            f"프로젝트\n{self.current_project}\n────────────\n"
            f"Turn\n{info['turn_count']}\n이미지\n{info['image_count']}\n"
            f"마지막 수정\n{info['last_modified']}"
        )
        self.info_label.setText(info_text)
        
        images = image_loader.load_images(project_path)
        merged_data_list = image_merger.merge_images(project_path, images)
        
        self.display_images(merged_data_list, self.current_project)
        
        if selected_turn_text:
            items = self.turn_list.findItems(selected_turn_text, Qt.MatchExactly)
            if items:
                self.turn_list.setCurrentItem(items[0])

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
            card = image_card.ImageCard(turn=turn_num, files=data["files"], pixmap=pixmap)
            card.set_display_width(available_width)
            
            insert_index = self.scroll_layout.count() - 1
            self.scroll_layout.insertWidget(insert_index, card)
            self.image_cards.append(card)
            self.turn_map[turn_num] = card
            self.turn_list.addItem(f"Turn {turn_num}")
            
        self.turn_list.blockSignals(False)
        
        current_filter = self.turn_search_input.text()
        if current_filter:
            self.filter_turns(current_filter)
            
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