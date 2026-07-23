import sys
import os
import subprocess
import PySide6
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QSplitter,
    QListWidget, QScrollArea, QLabel, QVBoxLayout, QWidget, QFrame,
    QFileDialog, QInputDialog, QMessageBox, QHBoxLayout, QToolButton, QMenu,
    QLineEdit, QDialog, QGroupBox, QPushButton, QListWidgetItem, QComboBox, QCheckBox, QTextBrowser, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QImage, QPixmap

import image_loader
import image_merger
import image_converter
import image_card
import project_manager
import config_manager
from crop_dialog import CropDialog
import status_manager

# ==========================================
# 프로그램 상수 정의
# ==========================================
APP_VERSION = "2.2.1"
APP_BUILD = "2026.07.24"
APP_DEVELOPER = "게으른굼벵이"
COVER_HEIGHT = 250  # 고정된 커버 영역 높이


# ==========================================
# 도움말 다이얼로그
# ==========================================
class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("도움말")
        self.resize(550, 600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet("background-color: #252526; border: 1px solid #3C3C3C; border-radius: 4px; padding: 10px;")
        
        html_content = """
        <h2 style='color:#EAEAEA; margin-top: 0;'>Log Storage 사용 안내</h2>
        <hr style='border: 1px solid #3C3C3C;'/>
        
        <h3 style='color:#4DAAFA;'>📥 이미지 추가 방법</h3>
        <ul style='color:#D4D4D4;'>
            <li>작품을 선택한 후 상단의 <b>[이미지 추가]</b> 버튼을 누르세요.</li>
            <li><b>지원 형식:</b> PNG / JPG / JPEG / WEBP / BMP / GIF</li>
            <li>파일명 규칙만 맞으면 확장자와 관계없이 가져올 수 있습니다.</li>
        </ul>
        
        <h3 style='color:#4DAAFA;'>📝 이미지 파일명 규칙</h3>
        <ul style='color:#D4D4D4;'>
            <li>반드시 <b>Turn_순번.확장자</b> 형식이어야 합니다.</li>
            <li>예) <code>1_1.png</code>, <code>1_2.webp</code>, <code>2_1.jpg</code></li>
            <li>규칙에 맞지 않는 파일은 가져오기 과정에서 안전하게 제외됩니다.</li>
        </ul>
        
        <h3 style='color:#4DAAFA;'>↔️ 화면 분할 조절</h3>
        <ul style='color:#D4D4D4;'>
            <li>좌측(목록)과 우측(이미지) 패널 사이의 <b>경계선을 드래그</b>하여 폭을 조절할 수 있습니다.</li>
            <li>조절된 폭은 <b>자동으로 저장</b>되어 다음 실행 시에도 유지됩니다.</li>
        </ul>
        
        <h3 style='color:#4DAAFA;'>🖱️ 우클릭 메뉴</h3>
        <ul style='color:#D4D4D4;'>
            <li><b>프로젝트 목록:</b> 우클릭하여 ⭐ 즐겨찾기 설정, 이름 변경, 삭제를 할 수 있습니다.</li>
            <li><b>Turn 목록:</b> 우클릭하여 ✏️ 표시 이름(별칭) 변경, ⭐ 북마크 추가/삭제를 할 수 있습니다.</li>
        </ul>
        
        <h3 style='color:#4DAAFA;'>🔍 검색 및 필터</h3>
        <ul style='color:#D4D4D4;'>
            <li><b>작품 검색:</b> 작품 이름으로 검색하거나 즐겨찾기한 작품만 모아볼 수 있습니다.</li>
            <li><b>Turn/북마크 검색:</b> 특정 Turn 번호나 사용자가 지정한 북마크 이름으로 빠르게 검색할 수 있습니다.</li>
        </ul>
        
        <h3 style='color:#4DAAFA;'>🖼️ 저장소 커버</h3>
        <ul style='color:#D4D4D4;'>
            <li>커버 등록 시 원하는 영역을 <b>직접 크롭</b>할 수 있습니다.</li>
            <li>편집 창에서 마우스 휠로 <b>확대·축소 및 위치 이동</b>이 가능합니다.</li>
            <li>최종 커버 이미지는 프로그램 내부에서 <b>6:1 비율(1200x200)로 통일되어 저장</b>됩니다.</li>
            <li>원본 이미지는 변경되지 않으며, [▼ Cover] 버튼으로 <b>접기/펼치기</b>가 가능합니다.</li>
        </ul>
        """
        browser.setHtml(html_content)
        layout.addWidget(browser)
        
        close_btn = QPushButton("닫기")
        close_btn.setFixedWidth(80)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)


# ==========================================
# 설정 창 다이얼로그 
# ==========================================
class SettingsDialog(QDialog):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.setWindowTitle("설정")
        self.resize(500, 650)
        self.config = config
        self.parent = parent
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        info_group = QGroupBox("프로그램 정보")
        info_layout = QVBoxLayout(info_group)
        info_layout.addWidget(QLabel("<b style='font-size:16px;'>Log Storage</b>"))
        info_layout.addWidget(QLabel("Personal RP Archive Manager"))
        info_layout.addWidget(QLabel(f"Version : v{APP_VERSION}"))
        info_layout.addWidget(QLabel(f"Developer : {APP_DEVELOPER}"))
        info_layout.addWidget(QLabel(f"Build : {APP_BUILD}"))
        layout.addWidget(info_group)
        
        storage_group = QGroupBox("기본 저장소")
        storage_layout = QVBoxLayout(storage_group)
        self.storage_label = QLabel(self.config.get("storage_root", "지정되지 않음"))
        self.storage_label.setStyleSheet("color: #A0A0A0;")
        
        btn_layout1 = QHBoxLayout()
        btn_layout1.addWidget(self.storage_label)
        change_btn1 = QPushButton("변경...")
        change_btn1.setFixedWidth(80)
        change_btn1.clicked.connect(self.change_storage)
        btn_layout1.addWidget(change_btn1)
        storage_layout.addLayout(btn_layout1)
        layout.addWidget(storage_group)
        
        cover_group = QGroupBox("저장소 커버")
        cover_layout = QVBoxLayout(cover_group)
        
        self.cover_name_label = QLabel()
        self.cover_name_label.setStyleSheet("color: #A0A0A0;")
        cover_layout.addWidget(self.cover_name_label)
        
        cover_btn_layout = QHBoxLayout()
        self.btn_change_cover = QPushButton("커버 변경")
        self.btn_delete_cover = QPushButton("커버 삭제")
        self.btn_change_cover.clicked.connect(self.change_cover)
        self.btn_delete_cover.clicked.connect(self.delete_cover)
        
        cover_btn_layout.addWidget(self.btn_change_cover)
        cover_btn_layout.addWidget(self.btn_delete_cover)
        cover_btn_layout.addStretch()
        
        self.chk_expand_cover = QCheckBox("프로그램 시작 시 펼치기")
        self.chk_expand_cover.setChecked(self.config.get("cover_expand_on_startup", False))
        self.chk_expand_cover.stateChanged.connect(self.toggle_cover_startup)
        
        hint_label = QLabel("※ 등록 시 내장된 편집기로 이미지를 6:1 비율로 자동 크롭합니다.")
        hint_label.setStyleSheet("color: #094771; font-size: 11px;")
        
        cover_layout.addLayout(cover_btn_layout)
        cover_layout.addWidget(self.chk_expand_cover)
        cover_layout.addWidget(hint_label)
        layout.addWidget(cover_group)
        
        rp_group = QGroupBox("RP Preview Studio")
        rp_layout = QVBoxLayout(rp_group)
        self.rp_label = QLabel(self.config.get("rp_preview_studio_path", "등록된 경로가 없습니다."))
        self.rp_label.setStyleSheet("color: #A0A0A0;")
        
        btn_layout2 = QHBoxLayout()
        btn_layout2.addWidget(self.rp_label)
        change_btn2 = QPushButton("찾아보기...")
        change_btn2.setFixedWidth(80)
        change_btn2.clicked.connect(self.change_rp_path)
        btn_layout2.addWidget(change_btn2)
        rp_layout.addLayout(btn_layout2)
        layout.addWidget(rp_group)
        
        sort_group = QGroupBox("프로젝트 정렬")
        sort_layout = QVBoxLayout(sort_group)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["최근 수정순", "이름순"])
        self.sort_combo.setCurrentIndex(0 if self.config.get("project_sort", "modified") == "modified" else 1)
        self.sort_combo.currentIndexChanged.connect(self.change_sort)
        sort_layout.addWidget(self.sort_combo)
        layout.addWidget(sort_group)
        
        layout.addStretch()
        close_btn = QPushButton("닫기")
        close_btn.setFixedWidth(80)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)

        self.update_cover_info()

    def update_cover_info(self):
        root = self.config.get("storage_root", "")
        if not root:
            self.cover_name_label.setText("현재 커버: 없음")
            self.btn_delete_cover.setEnabled(False)
            return

        cover_path = project_manager.get_cover_path(root)
        if cover_path:
            self.cover_name_label.setText("현재 커버: cover.png (내부 크롭 6:1)")
            self.btn_delete_cover.setEnabled(True)
        else:
            self.cover_name_label.setText("등록된 커버가 없습니다.")
            self.btn_delete_cover.setEnabled(False)

    def change_storage(self):
        current_root = self.config.get("storage_root", "")
        new_dir = QFileDialog.getExistingDirectory(self, "기본 저장소 선택", current_root)
        if new_dir:
            self.config["storage_root"] = new_dir
            self.storage_label.setText(new_dir)
            config_manager.save_config(self.config)
            self.update_cover_info()
            if new_dir != self.parent.current_folder:
                if self.parent.show_confirm("저장소 변경", "저장소가 변경되었습니다.\n새 저장소를 지금 열겠습니까?"):
                    self.parent.open_specific_folder(new_dir)

    def change_cover(self):
        if not self.config.get("storage_root"):
            self.parent.show_warning("경고", "기본 저장소가 먼저 설정되어야 합니다.")
            return
            
        path, _ = QFileDialog.getOpenFileName(self, "커버 이미지 선택", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif)")
        if path:
            dialog = CropDialog(path, self)
            if dialog.exec() == QDialog.Accepted:
                cropped_img = dialog.get_cropped_image()
                if cropped_img.isNull():
                    return
                
                # 기존 커버 삭제 후 6:1 저장
                project_manager.delete_cover_image(self.config["storage_root"])
                save_path = os.path.join(self.config["storage_root"], "cover.png")
                
                if cropped_img.save(save_path, "PNG"):
                    self.parent.update_status("저장소 커버가 성공적으로 등록되었습니다.")
                    self.update_cover_info()
                    self.parent.load_cover_image()
                else:
                    self.parent.show_error("오류", "커버 이미지를 저장할 수 없습니다.")

    def delete_cover(self):
        if not self.config.get("storage_root"): return
        if self.parent.show_confirm("커버 삭제", "커버 이미지를 삭제하시겠습니까?"):
            if project_manager.delete_cover_image(self.config["storage_root"]):
                self.parent.update_status("저장소 커버가 삭제되었습니다.")
                self.update_cover_info()
                self.parent.load_cover_image()

    def toggle_cover_startup(self, state):
        self.config["cover_expand_on_startup"] = (state == Qt.Checked.value)
        config_manager.save_config(self.config)

    def change_rp_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "RP Preview Studio 실행 파일 선택", "", "Executable (*.exe);;All Files (*)")
        if path:
            self.config["rp_preview_studio_path"] = path
            self.rp_label.setText(path)
            config_manager.save_config(self.config)

    def change_sort(self, index):
        sort_method = "modified" if index == 0 else "name"
        self.config["project_sort"] = sort_method
        config_manager.save_config(self.config)
        if self.parent.current_folder:
            self.parent.reload_project_list(select_name=self.parent.current_project)


# ==========================================
# 휴지통 다이얼로그
# ==========================================
class TrashDialog(QDialog):
    def __init__(self, base_folder, parent=None):
        super().__init__(parent)
        self.setWindowTitle("휴지통 관리")
        self.resize(550, 400)
        self.base_folder = base_folder
        self.parent = parent
        layout = QVBoxLayout(self)
        
        content_layout = QHBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        content_layout.addWidget(self.list_widget, stretch=2)
        
        self.detail_label = QLabel("항목을 선택하면\n상세 정보가 표시됩니다.")
        self.detail_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.detail_label.setStyleSheet("padding: 10px; background-color: #2D2D30; border-radius: 4px;")
        content_layout.addWidget(self.detail_label, stretch=1)
        layout.addLayout(content_layout)
        
        self.empty_label = QLabel("휴지통이 비어 있습니다.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #A0A0A0;")
        layout.addWidget(self.empty_label)
        
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
        if not trashed_items:
            self.empty_label.show()
            self.btn_empty.setEnabled(False)
        else:
            self.empty_label.hide()
            self.btn_empty.setEnabled(True)
        for item_data in trashed_items:
            text = f"{item_data['original_name']} ({item_data['deleted_at'][:10]})"
            list_item = QListWidgetItem(text)
            list_item.setData(Qt.UserRole, item_data)
            self.list_widget.addItem(list_item)
        self.on_selection_changed()

    def on_selection_changed(self):
        item = self.list_widget.currentItem()
        if not item:
            self.btn_restore.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.detail_label.setText("항목을 선택하면\n상세 정보가 표시됩니다.")
            return
        self.btn_restore.setEnabled(True)
        self.btn_delete.setEnabled(True)
        data = item.data(Qt.UserRole)
        detail_text = (
            f"<b style='font-size:14px; color:#EAEAEA;'>{data['original_name']}</b><br><br>"
            f"Turn: {data.get('turn_count', 0)}<br>Image: {data.get('image_count', 0)}<br>"
            f"마지막 수정: {data.get('last_modified', '-')}<br>삭제일: {data.get('deleted_at', '-')}"
        )
        self.detail_label.setText(detail_text)

    def restore_selected(self):
        item = self.list_widget.currentItem()
        if not item: return
        data = item.data(Qt.UserRole)
        if project_manager.restore_from_trash(self.base_folder, data['trashed_name'], data['original_name']):
            self.parent.update_status(f"'{data['original_name']}' 복원이 완료되었습니다.")
            self.refresh_list()

    def delete_selected(self):
        item = self.list_widget.currentItem()
        if not item: return
        data = item.data(Qt.UserRole)
        if self.parent.show_confirm("영구 삭제", f"'{data['original_name']}'을(를) 영구 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다."):
            if project_manager.permanent_delete(self.base_folder, data['trashed_name']):
                self.parent.update_status(f"'{data['original_name']}' 영구 삭제가 완료되었습니다.")
                self.refresh_list()

    def empty_all(self):
        if self.list_widget.count() == 0: return
        if self.parent.show_confirm("휴지통 비우기", "휴지통의 모든 항목을 영구 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다."):
            if project_manager.empty_trash(self.base_folder):
                self.parent.update_status("휴지통을 모두 비웠습니다.")
                self.refresh_list()


# ==========================================
# Main Window
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log Storage")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.config = config_manager.load_config()
        self.current_folder = None
        self.current_project = None  
        self.image_cards = []
        self.turn_map = {}
        
        self.is_cover_expanded = self.config.get("cover_expanded", self.config.get("cover_expand_on_startup", False))
        
        self._setup_ui()
        self.update_action_states()
        
        QTimer.singleShot(100, self.check_initial_setup)

    def check_initial_setup(self):
        if not self.config.get("storage_root"):
            self.show_info("안내", "작업을 시작하기 위해 기본 저장소를 선택해주세요.")
            folder_path = QFileDialog.getExistingDirectory(self, "기본 저장소 선택", "")
            if folder_path:
                self.config["storage_root"] = folder_path
                config_manager.save_config(self.config)
                self.open_specific_folder(folder_path)
            else:
                self.show_warning("경고", "저장소가 선택되지 않았습니다.\n[⚙ 설정]에서 저장소를 먼저 지정해주세요.")
        else:
            self.open_specific_folder(self.config["storage_root"])

    def show_info(self, title, msg): QMessageBox.information(self, title, msg)
    
    def show_warning(self, title, msg): 
        self.status.warning(msg)
        QMessageBox.warning(self, title, msg)
        
    def show_error(self, title, msg): 
        self.status.error(msg)
        QMessageBox.critical(self, title, msg)
        
    def show_confirm(self, title, msg): 
        return QMessageBox.question(self, title, msg, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes
        
    def update_status(self, msg): 
        self.status.success(msg)

    def update_action_states(self):
        has_storage = bool(self.current_folder)
        has_project = bool(self.current_project)
        self.action_add.setEnabled(has_storage)
        self.action_trash.setEnabled(has_storage)
        self.menu_btn.setEnabled(has_storage and has_project)

    def _setup_ui(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.action_new = QAction("📁 새 작품", self)
        self.action_add = QAction("📥 이미지 추가", self)
        self.action_refresh = QAction("🔄 새로고침", self)
        self.action_rp_studio = QAction("🚀 RP Preview Studio", self)
        self.action_trash = QAction("🗑 휴지통", self)
        self.action_help = QAction("❓ 도움말", self)
        self.action_settings = QAction("⚙ 설정", self)

        self.action_new.triggered.connect(self.create_new_project)
        self.action_add.triggered.connect(self.add_images_to_project)
        self.action_refresh.triggered.connect(self.on_action_refresh)
        self.action_rp_studio.triggered.connect(self.launch_rp_studio)
        self.action_trash.triggered.connect(self.open_trash_dialog)
        self.action_help.triggered.connect(self.open_help_dialog)
        self.action_settings.triggered.connect(self.open_settings_dialog)

        toolbar.addAction(self.action_new)
        toolbar.addAction(self.action_add)
        toolbar.addAction(self.action_refresh)
        toolbar.addSeparator()
        toolbar.addAction(self.action_rp_studio)
        toolbar.addSeparator()
        toolbar.addAction(self.action_trash)
        toolbar.addAction(self.action_help)
        toolbar.addAction(self.action_settings)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #EAEAEA; font-size: 13px; padding-right: 15px; opacity: 0.85;")
        toolbar.addWidget(self.status_label)
        
        self.status = status_manager.StatusManager(self.status_label)

        self.splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        # ---------------------------------------------------------
        # 좌측 패널 구성
        # ---------------------------------------------------------
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(8)

        self.recent_label = QLabel("최근 연 작품")
        font = self.recent_label.font()
        font.setBold(True)
        self.recent_label.setFont(font)
        
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(80) 
        self.recent_list.itemClicked.connect(self.on_recent_clicked)
        
        left_layout.addWidget(self.recent_label)
        left_layout.addWidget(self.recent_list)

        header_layout = QHBoxLayout()
        title_label = QLabel("작품 목록")
        title_label.setFont(font)
        
        self.menu_btn = QToolButton()
        self.menu_btn.setText("⋮")
        self.menu_btn.setPopupMode(QToolButton.InstantPopup)
        
        menu = QMenu(self)
        action_toggle_fav = QAction("⭐ 즐겨찾기 설정/해제", self)
        action_open_folder = QAction("📂 프로젝트 폴더 열기", self)
        action_rename = QAction("✏ 프로젝트 이름 변경", self)
        action_delete = QAction("🗑 프로젝트 삭제", self)
        
        action_toggle_fav.triggered.connect(self.toggle_current_project_favorite)
        action_open_folder.triggered.connect(self.open_current_project_folder)
        action_rename.triggered.connect(self.rename_current_project)
        action_delete.triggered.connect(self.delete_current_project)
        
        menu.addAction(action_toggle_fav)
        menu.addSeparator()
        menu.addAction(action_open_folder)
        menu.addAction(action_rename)
        menu.addAction(action_delete)
        self.menu_btn.setMenu(menu)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.menu_btn)
        
        project_search_layout = QHBoxLayout()
        self.project_search_input = QLineEdit()
        self.project_search_input.setPlaceholderText("🔍 작품 검색...")
        self.project_search_input.textChanged.connect(self.filter_projects)
        
        self.project_filter_combo = QComboBox()
        self.project_filter_combo.addItems(["전체", "즐겨찾기"])
        self.project_filter_combo.currentIndexChanged.connect(self.filter_projects)
        
        project_search_layout.addWidget(self.project_search_input)
        project_search_layout.addWidget(self.project_filter_combo)

        self.project_list = QListWidget()
        self.project_list.currentItemChanged.connect(self.on_project_changed)
        self.project_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.project_list.customContextMenuRequested.connect(self.show_project_context_menu)

        left_layout.addLayout(header_layout)
        left_layout.addLayout(project_search_layout)
        left_layout.addWidget(self.project_list)

        turn_title_label = QLabel("Turn 목록")
        turn_title_label.setFont(font)
        
        turn_search_layout = QHBoxLayout()
        self.turn_search_input = QLineEdit()
        self.turn_search_input.setPlaceholderText("🔍 검색...")
        self.turn_search_input.textChanged.connect(self.filter_turns)
        
        self.turn_filter_combo = QComboBox()
        self.turn_filter_combo.addItems(["Turn", "북마크"])
        self.turn_filter_combo.currentIndexChanged.connect(self.filter_turns)
        
        turn_search_layout.addWidget(self.turn_search_input)
        turn_search_layout.addWidget(self.turn_filter_combo)

        self.turn_list = QListWidget()
        self.turn_list.currentItemChanged.connect(self.on_turn_changed)
        self.turn_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.turn_list.customContextMenuRequested.connect(self.show_turn_context_menu)

        left_layout.addWidget(turn_title_label)
        left_layout.addLayout(turn_search_layout)
        left_layout.addWidget(self.turn_list)

        info_line = QFrame()
        info_line.setFrameShape(QFrame.HLine)
        info_line.setFrameShadow(QFrame.Sunken)
        self.info_label = QLabel("프로젝트 정보가 없습니다.")
        self.info_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        left_layout.addWidget(info_line)
        left_layout.addWidget(self.info_label)

        # ---------------------------------------------------------
        # 우측 패널 구성
        # ---------------------------------------------------------
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        self.cover_widget = QWidget()
        self.cover_widget.setStyleSheet("background-color: #1E1E1E;")
        cover_layout = QVBoxLayout(self.cover_widget)
        cover_layout.setContentsMargins(0, 0, 0, 0)
        cover_layout.setSpacing(0)
        
        self.btn_cover_toggle = QPushButton("▼ Cover")
        self.btn_cover_toggle.setFlat(True)
        self.btn_cover_toggle.setStyleSheet("text-align: left; padding: 5px; color: #A0A0A0;")
        self.btn_cover_toggle.clicked.connect(self.toggle_cover)
        
        self.cover_image_label = QLabel()
        self.cover_image_label.setAlignment(Qt.AlignCenter)
        
        self.cover_image_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.cover_image_label.setFixedHeight(COVER_HEIGHT)
        
        cover_layout.addWidget(self.btn_cover_toggle)
        cover_layout.addWidget(self.cover_image_label)

        right_layout.addWidget(self.cover_widget)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.viewer_label = QLabel("이미지를 불러오세요.")
        self.viewer_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.viewer_label)
        self.scroll_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_widget)
        
        right_layout.addWidget(self.scroll_area)

        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(right_panel)

        saved_sizes = self.config.get("splitter_sizes", [220, 980])
        self.splitter.setSizes(saved_sizes)
        self.splitter.splitterMoved.connect(self.on_splitter_moved)

        self.status.reset()

    # ==========================================
    # 렌더링 및 UI 관리 로직
    # ==========================================
    def on_splitter_moved(self, pos, index):
        self.config["splitter_sizes"] = self.splitter.sizes()
        config_manager.save_config(self.config)

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
        self.info_label.setText("프로젝트 정보가 없습니다.")
        self.current_project = None
        self.update_action_states()

    def update_recent_projects_ui(self):
        self.recent_list.clear()
        recents = self.config.get("recent_projects", [])
        
        if self.project_search_input.text().strip():
            self.recent_list.hide()
            self.recent_label.hide()
            return
            
        if not recents:
            self.recent_list.hide()
            self.recent_label.hide()
            return
            
        self.recent_list.show()
        self.recent_label.show()
        for p in recents:
            self.recent_list.addItem(f"🕘 {p}")

    def on_recent_clicked(self, item):
        project_name = item.text().replace("🕘 ", "")
        items = self.project_list.findItems(project_name, Qt.MatchContains)
        for p_item in items:
            p_name = p_item.data(Qt.UserRole)
            if p_name == project_name:
                self.project_list.setCurrentItem(p_item)
                break

    def load_cover_image(self):
        if not self.current_folder:
            self.cover_widget.hide()
            return
            
        cover_path = project_manager.get_cover_path(self.current_folder)
        if not cover_path:
            self.cover_widget.hide()
            return
            
        self.cover_widget.show()
        if self.is_cover_expanded:
            self.btn_cover_toggle.setText("▼ Cover")
            self.cover_image_label.show()
            self._render_cover(cover_path)
        else:
            self.btn_cover_toggle.setText("▶ Cover")
            self.cover_image_label.hide()

    def _render_cover(self, path):
        width = self.cover_widget.width()
        height = COVER_HEIGHT

        if width < 10:
           return

        pix = QPixmap(path)
        if pix.isNull():
            return

        pix = pix.scaled(
            width,
            height,
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation
        )

        self.cover_image_label.setPixmap(pix)

    def toggle_cover(self):
        self.is_cover_expanded = not self.is_cover_expanded
        self.config["cover_expanded"] = self.is_cover_expanded
        config_manager.save_config(self.config)
        self.load_cover_image()

    def reload_project_list(self, select_name=None):
        self.project_list.blockSignals(True)
        self.project_list.clear()
        
        sort_method = self.config.get("project_sort", "modified")
        projects = image_loader.load_projects(self.current_folder, sort_method)
        
        recents = self.config.get("recent_projects", [])
        valid_recents = [p for p in recents if p in projects]
        if recents != valid_recents:
            self.config["recent_projects"] = valid_recents
            config_manager.save_config(self.config)
        
        for project in projects:
            meta = project_manager.get_project_meta(os.path.join(self.current_folder, project))
            prefix = "⭐ " if meta.get("favorite", False) else ""
            item = QListWidgetItem(f"{prefix}{project}")
            item.setData(Qt.UserRole, project)
            self.project_list.addItem(item)
            
        self.project_list.blockSignals(False)
        self.filter_projects()
        
        if select_name:
            for i in range(self.project_list.count()):
                if self.project_list.item(i).data(Qt.UserRole) == select_name:
                    self.project_list.setCurrentItem(self.project_list.item(i))
                    break

        self.update_recent_projects_ui()
        self.load_cover_image()

    # ==========================================
    # 상호작용 및 다이얼로그 호출
    # ==========================================
    def open_settings_dialog(self):
        dialog = SettingsDialog(self, self.config)
        dialog.exec()

    def open_help_dialog(self):
        dialog = HelpDialog(self)
        dialog.exec()

    def open_trash_dialog(self):
        dialog = TrashDialog(self.current_folder, self)
        dialog.exec()
        self.on_action_refresh()

    def launch_rp_studio(self):
        path = self.config.get("rp_preview_studio_path", "")
        if not path or not os.path.exists(path):
            if self.show_confirm("경로 미지정", "RP Preview Studio 경로가 설정되어 있지 않거나 존재하지 않습니다.\n지금 실행 파일을 선택하시겠습니까?"):
                path, _ = QFileDialog.getOpenFileName(self, "RP Preview Studio 실행 파일 선택", "", "Executable (*.exe);;All Files (*)")
                if path:
                    self.config["rp_preview_studio_path"] = path
                    config_manager.save_config(self.config)
                    self.update_status("RP Preview Studio 경로를 저장했습니다.")
                else: return
            else: return
        try:
            subprocess.Popen([path])
            self.update_status("RP Preview Studio를 실행했습니다.")
        except Exception as e:
            self.show_error("오류", f"프로그램을 실행하는 중 문제가 발생했습니다:\n{e}")

    def open_specific_folder(self, folder_path):
        self.current_folder = folder_path
        self.clear_image_cards()
        self.reload_project_list()
        self.update_action_states()
        
        count = self.project_list.count()
        if count > 0: self.update_status(f"저장소 연결 완료: 작품 {count}개를 불러왔습니다.")
        else: self.update_status("저장소 연결 완료: 작품이 없습니다.")

    # ==========================================
    # 프로젝트 관리
    # ==========================================
    def show_project_context_menu(self, pos):
        item = self.project_list.itemAt(pos)
        if not item: return
        
        self.project_list.setCurrentItem(item)
        menu = QMenu(self)
        action_toggle_fav = QAction("⭐ 즐겨찾기 설정/해제", self)
        action_open_folder = QAction("📂 프로젝트 폴더 열기", self)
        action_rename = QAction("✏ 프로젝트 이름 변경", self)
        action_delete = QAction("🗑 프로젝트 삭제", self)
        
        action_toggle_fav.triggered.connect(self.toggle_current_project_favorite)
        action_open_folder.triggered.connect(self.open_current_project_folder)
        action_rename.triggered.connect(self.rename_current_project)
        action_delete.triggered.connect(self.delete_current_project)
        
        menu.addAction(action_toggle_fav)
        menu.addSeparator()
        menu.addAction(action_open_folder)
        menu.addAction(action_rename)
        menu.addAction(action_delete)
        
        menu.exec(self.project_list.mapToGlobal(pos))

    def toggle_current_project_favorite(self):
        if not self.current_project or not self.current_folder: return
        project_path = os.path.join(self.current_folder, self.current_project)
        meta = project_manager.get_project_meta(project_path)
        meta["favorite"] = not meta.get("favorite", False)
        if project_manager.save_project_meta(project_path, meta):
            self.reload_project_list(select_name=self.current_project)

    def open_current_project_folder(self):
        if not self.current_project: return
        project_path = os.path.join(self.current_folder, self.current_project)
        if not project_manager.open_project_folder(project_path):
            self.show_error("오류", "프로젝트 폴더를 열 수 없습니다.")

    def rename_current_project(self):
        if not self.current_project: return
        new_name, ok = QInputDialog.getText(self, "프로젝트 이름 변경", "새 이름을 입력하세요:", text=self.current_project)
        if not ok: return
        new_name = new_name.strip()
        if not new_name or new_name == self.current_project: return
        if project_manager.project_exists(self.current_folder, new_name):
            self.show_warning("경고", f"'{new_name}'(은)는 이미 존재하는 프로젝트명입니다.")
            return
            
        recents = self.config.get("recent_projects", [])
        if self.current_project in recents:
            recents[recents.index(self.current_project)] = new_name
            self.config["recent_projects"] = recents
            config_manager.save_config(self.config)
            
        if project_manager.rename_project(self.current_folder, self.current_project, new_name):
            self.reload_project_list(select_name=new_name)
            self.update_status(f"프로젝트 이름이 '{new_name}'(으)로 변경되었습니다.")
        else:
            self.show_error("오류", "이름 변경 중 오류가 발생했습니다. 권한이나 파일 잠금을 확인하세요.")

    def delete_current_project(self):
        if not self.current_project: return
        project_path = os.path.join(self.current_folder, self.current_project)
        info = project_manager.get_project_summary(project_path)
        preview_text = (
            f"'{self.current_project}' 프로젝트를 휴지통으로 이동하시겠습니까?\n\n"
            f"Turn: {info['turn_count']}\n이미지: {info['image_count']}"
        )
        if self.show_confirm("프로젝트 삭제", preview_text):
            recents = self.config.get("recent_projects", [])
            if self.current_project in recents:
                recents.remove(self.current_project)
                config_manager.save_config(self.config)
                
            if project_manager.move_to_trash(self.current_folder, self.current_project):
                self.clear_image_cards()
                self.reload_project_list()
                self.update_status("프로젝트가 휴지통으로 이동되었습니다.")
            else:
                self.show_error("오류", "휴지통 이동 중 오류가 발생했습니다.")

    # ==========================================
    # 검색 및 필터 
    # ==========================================
    def filter_projects(self):
        text = self.project_search_input.text().lower()
        filter_type = self.project_filter_combo.currentText()
        
        if text:
            self.recent_label.hide()
            self.recent_list.hide()
        else:
            self.update_recent_projects_ui()
                
        for i in range(self.project_list.count()):
            item = self.project_list.item(i)
            original_name = item.data(Qt.UserRole)
            display_name = item.text()
            
            is_match_text = text in original_name.lower()
            is_match_fav = True
            
            if filter_type == "즐겨찾기" and "⭐" not in display_name:
                is_match_fav = False
                
            item.setHidden(not (is_match_text and is_match_fav))

    def filter_turns(self):
        text = self.turn_search_input.text().lower()
        search_type = self.turn_filter_combo.currentText()
        
        for i in range(self.turn_list.count()):
            item = self.turn_list.item(i)
            display_text = item.text().lower()
            
            if not text:
                item.setHidden(False)
                continue

            if search_type == "Turn":
                turn_str = display_text.split("⭐")[0] if "⭐" in display_text else display_text
                item.setHidden(text not in turn_str)
            else: 
                if "⭐" not in display_text:
                    item.setHidden(True)
                else:
                    bm_str = display_text.split("⭐")[1]
                    item.setHidden(text not in bm_str)

    # ==========================================
    # Turn 컨텍스트 메뉴 (북마크/이름 변경)
    # ==========================================
    def show_turn_context_menu(self, pos):
        item = self.turn_list.itemAt(pos)
        if not item or not self.current_project: return
        
        turn_num = item.data(Qt.UserRole)
        menu = QMenu(self)
        
        action_rename = QAction("✏ Turn 표시 이름 변경", self)
        action_add = QAction("⭐ 북마크 추가/수정", self)
        action_remove = QAction("북마크 삭제", self)
        
        action_rename.triggered.connect(lambda: self.rename_turn_alias(turn_num))
        action_add.triggered.connect(lambda: self.add_bookmark(turn_num))
        action_remove.triggered.connect(lambda: self.remove_bookmark(turn_num))
        
        menu.addAction(action_rename)
        menu.addSeparator()
        menu.addAction(action_add)
        menu.addAction(action_remove)
        menu.exec(self.turn_list.mapToGlobal(pos))
        
    def rename_turn_alias(self, turn_num):
        project_path = os.path.join(self.current_folder, self.current_project)
        meta = project_manager.get_project_meta(project_path)
        aliases = meta.get("turn_aliases", {})
        
        current_alias = aliases.get(str(turn_num), f"Turn {turn_num}")
        new_alias, ok = QInputDialog.getText(self, "Turn 이름 변경", f"Turn {turn_num} 표시 이름:", text=current_alias)
        if ok and new_alias.strip():
            aliases[str(turn_num)] = new_alias.strip()
            meta["turn_aliases"] = aliases
            if project_manager.save_project_meta(project_path, meta):
                self.refresh_project()

    def add_bookmark(self, turn_num):
        project_path = os.path.join(self.current_folder, self.current_project)
        meta = project_manager.get_project_meta(project_path)
        bms = meta.get("bookmarks", {})
        
        current_bm = bms.get(str(turn_num), "")
        new_title, ok = QInputDialog.getText(self, "북마크 설정", f"Turn {turn_num} 북마크 제목:", text=current_bm)
        if ok and new_title.strip():
            bms[str(turn_num)] = new_title.strip()
            meta["bookmarks"] = bms
            if project_manager.save_project_meta(project_path, meta):
                self.refresh_project()

    def remove_bookmark(self, turn_num):
        project_path = os.path.join(self.current_folder, self.current_project)
        meta = project_manager.get_project_meta(project_path)
        bms = meta.get("bookmarks", {})
        if str(turn_num) in bms:
            del bms[str(turn_num)]
            meta["bookmarks"] = bms
            if project_manager.save_project_meta(project_path, meta):
                self.refresh_project()

    # ==========================================
    # 이미지 불러오기 및 에러 메시지
    # ==========================================
    def _process_import_dialog(self, target_project_name):
        files, _ = QFileDialog.getOpenFileNames(
            self, "이미지 선택", "", 
            "Image Files (*.png *.jpg *.jpeg *.webp *.bmp *.gif);;All Files (*)"
        )
        if not files: return None
        
        result = project_manager.analyze_import_files(files)
        valid_files = result["valid_files"]
        
        if not valid_files:
            self.show_warning("경고", "가져올 수 있는 정상적인 이미지 파일이 없습니다.")
            return None
            
        merge_lines = [
            f"Turn {r['start']} | {r['count']}장" if r['start'] == r['end'] else f"Turn {r['start']} ~ Turn {r['end']} | {r['count']}장" 
            for r in result["turn_ranges"]
        ]
        merge_str = "\n".join(merge_lines) if merge_lines else "없음"
        
        preview_text = (
            f"작품명\n{target_project_name}\n────────────\n"
            f"선택 이미지\n{len(files)}장\n정상 파일\n{len(valid_files)}장\n────────────\n"
            f"예상 Turn\n{len(result['turns'])}개\n────────────\n"
            f"예상 병합 결과\n{merge_str}\n"
        )
        
        if result["invalid_files"]:
            invalid_count = len(result["invalid_files"])
            if invalid_count > 10:
                invalid_list_str = "\n".join(result["invalid_files"][:10]) + "\n..."
            else:
                invalid_list_str = "\n".join(result["invalid_files"])
                
            preview_text += (
                f"\n────────────\n\n"
                f"인식되지 않은 이미지 : {invalid_count}개\n\n"
                f"{invalid_list_str}\n\n"
                f"────────────\n\n"
                f"파일명 규칙\n\n"
                f"Turn_순번.확장자\n\n"
                f"예)\n\n"
                f"1_1.png\n"
                f"1_2.webp\n"
                f"2_1.jpg\n\n"
                f"숫자_숫자 형식의 이미지 파일만 가져올 수 있습니다.\n\n"
                f"────────────\n\n"
                f"파일명이 올바르지 않은 이미지는 가져오지 않습니다."
            )
            
        if self.show_confirm("가져오기 확인", preview_text):
            return valid_files
        return None

    def create_new_project(self):
        if not self.current_folder:
            self.show_warning("경고", "먼저 기본 저장소를 설정해주세요.")
            return
        name, ok = QInputDialog.getText(self, "새 작품 생성", "작품명을 입력하세요:")
        if not ok: return
        name = name.strip()
        if not name:
            self.show_warning("경고", "작품명이 비어있습니다.")
            return
        if project_manager.project_exists(self.current_folder, name):
            self.show_warning("경고", f"'{name}'(은)는 이미 존재하는 프로젝트명입니다.")
            return
        valid_files = self._process_import_dialog(name)
        if not valid_files: return
            
        project_path = project_manager.create_project(self.current_folder, name)
        project_manager.copy_images(project_path, valid_files)
        self.reload_project_list(select_name=name)
        self.update_status(f"'{name}' 프로젝트를 생성했습니다.")

    def add_images_to_project(self):
        valid_files = self._process_import_dialog(self.current_project)
        if not valid_files: return
        project_path = os.path.join(self.current_folder, self.current_project)
        project_manager.copy_images(project_path, valid_files)
        self.refresh_project()
        self.update_status(f"'{self.current_project}'에 이미지를 추가했습니다.")

    def on_project_changed(self, current, previous):
        if not current or not self.current_folder:
            self.current_project = None
            self.update_action_states()
            return
            
        self.current_project = current.data(Qt.UserRole)
        self.update_action_states()
        
        recents = self.config.get("recent_projects", [])
        if self.current_project in recents:
            recents.remove(self.current_project)
        recents.insert(0, self.current_project)
        self.config["recent_projects"] = recents[:5]
        config_manager.save_config(self.config)
        self.update_recent_projects_ui()
        
        self.turn_search_input.blockSignals(True)
        self.turn_search_input.clear()
        self.turn_search_input.blockSignals(False)
        self.refresh_project()

    def on_turn_changed(self, current, previous):
        if not current: return
        turn_num = current.data(Qt.UserRole)
        if turn_num in self.turn_map:
            card = self.turn_map[turn_num]
            self.scroll_area.ensureWidgetVisible(card)

    def on_action_refresh(self):
        if self.current_folder:
            self.reload_project_list(select_name=self.current_project)
        if self.current_project:
            self.refresh_project()
            self.update_status(f"새로고침 완료: '{self.current_project}' - {len(self.image_cards)}개의 Turn을 불러왔습니다.")

    def refresh_project(self):
        if not self.current_folder or not self.current_project:
            return
            
        current_turn_item = self.turn_list.currentItem()
        selected_turn_num = current_turn_item.data(Qt.UserRole) if current_turn_item else None
        
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
        
        meta = project_manager.get_project_meta(project_path)
        self.display_images(merged_data_list, self.current_project, meta)
        
        if selected_turn_num:
            for i in range(self.turn_list.count()):
                if self.turn_list.item(i).data(Qt.UserRole) == selected_turn_num:
                    self.turn_list.setCurrentItem(self.turn_list.item(i))
                    break

    def display_images(self, merged_data_list, project_name, meta):
        for card in self.image_cards:
            self.scroll_layout.removeWidget(card)
            card.deleteLater()
            
        self.image_cards.clear()
        self.turn_map.clear()
        
        self.turn_list.blockSignals(True)
        self.turn_list.clear()

        if not merged_data_list:
            self.viewer_label.show()
            self.turn_list.blockSignals(False)
            return
            
        self.viewer_label.hide()
        available_width = self.get_available_width()
        
        bookmarks = meta.get("bookmarks", {})
        aliases = meta.get("turn_aliases", {})
        
        for data in merged_data_list:
            pil_img = data["image"]
            pixmap = image_converter.pil_to_pixmap(pil_img)
            
            if pixmap.width() > available_width:
                pixmap = pixmap.scaledToWidth(available_width, Qt.SmoothTransformation)
                
            turn_num = data["turn"]
            card = image_card.ImageCard(turn=turn_num, files=data["files"], pixmap=pixmap)
            card.set_display_width(available_width)
            
            insert_index = self.scroll_layout.count() - 1
            self.scroll_layout.insertWidget(insert_index, card)
            self.image_cards.append(card)
            self.turn_map[turn_num] = card
            
            alias_name = aliases.get(str(turn_num), f"Turn {turn_num}")
            bm_title = bookmarks.get(str(turn_num), "")
            item_text = f"{alias_name}" + (f" ⭐ {bm_title}" if bm_title else "")
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, turn_num)
            self.turn_list.addItem(item)
            
        self.turn_list.blockSignals(False)
        self.filter_turns()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'scroll_area') and self.image_cards:
            available_width = self.get_available_width()
            for card in self.image_cards:
                card.set_display_width(available_width)
        
        if hasattr(self, 'cover_widget') and self.cover_widget.isVisible() and self.is_cover_expanded:
            cover_path = project_manager.get_cover_path(self.current_folder)
            if cover_path:
                self._render_cover(cover_path)

def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qss_path = resource_path("assets/dark.qss")

    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
          app.setStyleSheet(f.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec())