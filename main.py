import sys
import json
import os
import shutil
import uuid
from pathlib import Path


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)


from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFrame,
    QScrollArea,
    QListWidget,
    QListWidgetItem,
    QFileDialog,
    QMessageBox,
    QDialog,
    QTextEdit,
    QGroupBox,
    QCheckBox,
    QComboBox,
    QStackedWidget,
    QListView,
    QToolButton,
    QSlider,
)
from PySide6.QtCore import Qt, QSize, Signal, QMimeData
from PySide6.QtGui import (
    QPixmap,
    QDrag,
    QIcon,
    QColor,
    QFont,
    QPalette,
    QDragEnterEvent,
    QDropEvent,
)
from PySide6.QtCore import QUrl


class DropZone(QFrame):
    image_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #aaa;
                background-color: #2a2a2a;
            }
            QFrame:hover {
                border: 2px dashed #0078d4;
                background-color: #333;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label = QLabel("拖拽图片到这里\n或点击选择")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: #888;")
        layout.addWidget(self.label)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(
                    (".png", ".jpg", ".jpeg", ".bmp", ".gif")
                ):
                    self.image_dropped.emit(file_path)
                    event.accept()
                    break
            else:
                event.ignore()
        else:
            event.ignore()


DATA_FILE = "prompts_data.json"
IMAGES_FOLDER = "images"


class PromptItem:
    def __init__(self, image_path="", prompt="", tags="", title="", favorite=False):
        self.image_path = image_path
        self.prompt = prompt
        self.tags = tags
        self.title = title
        self.favorite = favorite

    def to_dict(self):
        return {
            "image_path": self.image_path,
            "prompt": self.prompt,
            "tags": self.tags,
            "title": self.title,
            "favorite": self.favorite,
        }

    @staticmethod
    def from_dict(d):
        return PromptItem(
            image_path=d.get("image_path", ""),
            prompt=d.get("prompt", ""),
            tags=d.get("tags", ""),
            title=d.get("title", ""),
            favorite=d.get("favorite", False),
        )


class DataManager:
    def __init__(self):
        self.data_file = DATA_FILE
        self.images_folder = IMAGES_FOLDER
        self.items = []
        self._ensure_images_folder()
        self.load_data()

    def _ensure_images_folder(self):
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.items = [PromptItem.from_dict(d) for d in data]
            except:
                self.items = []

    def save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(
                [item.to_dict() for item in self.items], f, ensure_ascii=False, indent=2
            )

    def add_item(self, item):
        self.items.append(item)
        self.save_data()

    def remove_item(self, index):
        if 0 <= index < len(self.items):
            del self.items[index]
            self.save_data()

    def update_item(self, index, item):
        if 0 <= index < len(self.items):
            self.items[index] = item
            self.save_data()

    def get_favorites(self):
        return [item for item in self.items if item.favorite]

    def search(self, query):
        query = query.lower()
        return [
            item
            for item in self.items
            if query in item.prompt.lower()
            or query in item.tags.lower()
            or query in item.title.lower()
        ]


class ImageCard(QFrame):
    clicked = Signal(int)
    favorite_clicked = Signal(int)
    selection_changed = Signal(int, bool)

    def __init__(
        self,
        item,
        index,
        adapt_size=False,
        parent=None,
        dark_theme=False,
        show_checkbox=False,
        card_size=200,
    ):
        super().__init__(parent)
        self.item = item
        self.index = index
        self.adapt_size = adapt_size
        self.dark_theme = dark_theme
        self.show_checkbox = show_checkbox
        self.card_size = card_size
        self._selected = False
        self.setup_ui()

    def setup_ui(self):
        if self.dark_theme:
            self.setStyleSheet("""
                QFrame {
                    border: 1px solid #444;
                    border-radius: 4px;
                    background-color: #2a2a2a;
                    margin: 1px;
                }
                QFrame:hover {
                    border: 2px solid #0078d4;
                    background-color: #333;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    border: 1px solid #ccc;
                    border-radius: 6px;
                    background-color: white;
                    margin: 2px;
                }
                QFrame:hover {
                    border: 2px solid #0078d4;
                }
            """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(3, 3, 3, 3)
        main_layout.setSpacing(0)

        if self.show_checkbox:
            top_layout = QHBoxLayout()
            top_layout.setContentsMargins(0, 0, 0, 0)

            self.check_btn = QToolButton()
            self.check_btn.setCheckable(True)
            self.check_btn.setText("")
            self.check_btn.setFixedSize(24, 24)
            self.check_btn.setStyleSheet("""
                QToolButton {
                    border: 2px solid #888;
                    border-radius: 12px;
                    background-color: transparent;
                }
                QToolButton:checked {
                    background-color: #0078d4;
                    border: 2px solid #0078d4;
                }
            """)
            self.check_btn.clicked.connect(lambda: self._on_check_changed())
            top_layout.addWidget(self.check_btn)
            top_layout.addStretch()
            main_layout.addLayout(top_layout)

        img_w = int(self.card_size * 0.95)
        img_h = int(self.card_size * 0.8)

        image_container = QFrame()
        image_container.setFixedSize(img_w, img_h)
        image_container.setStyleSheet("border: none;")
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("border: none;")

        if self.item.image_path and os.path.exists(self.item.image_path):
            pixmap = QPixmap(self.item.image_path)
            if self.adapt_size:
                w, h = pixmap.width(), pixmap.height()
                max_w, max_h = img_w, img_h
                if w > h:
                    new_w = min(w, max_w)
                    new_h = int(h * new_w / w)
                else:
                    new_h = min(h, max_h)
                    new_w = int(w * new_h / h)
                image_label.setFixedSize(max(80, new_w), max(60, new_h))
                scaled = pixmap.scaled(
                    image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            else:
                image_label.setFixedSize(img_w, img_h)
                scaled = pixmap.scaled(
                    img_w,
                    img_h,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            image_label.setPixmap(scaled)
        else:
            image_label.setFixedSize(img_w, img_h)
            image_label.setText("No Image")
            image_label.setStyleSheet("border: none; color: gray; background: #f0f0f0;")

        image_layout.addWidget(image_label, 0, Qt.AlignmentFlag.AlignCenter)

        info_overlay = QFrame()
        info_overlay.setFixedHeight(40)
        info_bg = "#2a2a2a" if self.dark_theme else "#f0f0f0"
        info_overlay.setStyleSheet(f"background-color: {info_bg}; border: none;")
        info_layout = QHBoxLayout(info_overlay)
        info_layout.setContentsMargins(5, 2, 5, 2)

        title_label = QLabel(self.item.title if self.item.title else "Untitled")
        title_color = "#fff" if self.dark_theme else "#000"
        title_label.setStyleSheet(
            f"border: none; font-weight: bold; font-size: 11px; color: {title_color};"
        )
        title_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        title_label.setFixedWidth(img_w // 2)
        title_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )
        title_label.setOpenExternalLinks(False)
        info_layout.addWidget(title_label)

        tags_label = QLabel(
            self.item.tags[:15] + ".." if len(self.item.tags) > 15 else self.item.tags
        )
        tags_color = "#888" if self.dark_theme else "#666"
        tags_label.setStyleSheet(f"border: none; color: {tags_color}; font-size: 10px;")
        tags_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        info_layout.addWidget(tags_label, 1)

        fav_symbol = "★" if self.item.favorite else "☆"
        fav_btn = QToolButton()
        fav_btn.setText(fav_symbol)
        fav_btn.setFont(QFont("Arial", 12))
        fav_btn.setStyleSheet(
            "color: #ff9800; border: none; background: transparent; padding: 0;"
        )
        fav_btn.clicked.connect(lambda: self.favorite_clicked.emit(self.index))
        info_layout.addWidget(fav_btn)

        image_layout.addWidget(info_overlay)

        main_layout.addWidget(image_container, 0, Qt.AlignmentFlag.AlignCenter)

        if self.item.prompt:
            prompt_color = "#aaa" if self.dark_theme else "#666"
            prompt_label = QLabel(
                self.item.prompt[:50] + ".."
                if len(self.item.prompt) > 50
                else self.item.prompt
            )
            prompt_label.setStyleSheet(
                f"border: none; color: {prompt_color}; font-size: 10px;"
            )
            prompt_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            prompt_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextBrowserInteraction
            )
            main_layout.addWidget(prompt_label)

        card_w = self.card_size
        card_h = (
            img_h
            + 40
            + (20 if self.show_checkbox else 0)
            + (30 if self.item.prompt else 0)
        )
        self.setFixedSize(card_w, card_h)

    def _on_checkbox_changed(self, state):
        self._selected = state == 2
        self.selection_changed.emit(self.index, self._selected)

    def _on_check_changed(self):
        self._selected = self.check_btn.isChecked()
        self.selection_changed.emit(self.index, self._selected)

    def set_selected(self, selected):
        self._selected = selected
        if self.show_checkbox and hasattr(self, "check_btn"):
            self.check_btn.setChecked(selected)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.index)


class ListCard(QFrame):
    clicked = Signal(int)
    favorite_clicked = Signal(int)
    selection_changed = Signal(int, bool)

    def __init__(self, item, index, parent=None, show_checkbox=False, card_size=200):
        super().__init__(parent)
        self.item = item
        self.index = index
        self.show_checkbox = show_checkbox
        self.card_size = card_size
        self._selected = False
        self.setup_ui()

    def setup_ui(self):
        self.update_style()

    def update_style(self):
        if self._selected:
            self.setStyleSheet("""
                QFrame {
                    border: 3px solid #0078d4;
                    border-radius: 6px;
                    background-color: #1a3a5a;
                    margin: 2px;
                }
                QLabel { color: #ddd; }
                QPushButton { color: #ddd; background: transparent; border: none; }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    border: 1px solid #444;
                    border-radius: 6px;
                    background-color: #2a2a2a;
                    margin: 2px;
                }
                QFrame:hover {
                    border: 2px solid #0078d4;
                    background-color: #333;
                }
                QLabel { color: #ddd; }
                QPushButton { color: #ddd; background: transparent; border: none; }
            """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        if self.show_checkbox:
            self.check_btn = QToolButton()
            self.check_btn.setCheckable(True)
            self.check_btn.setText("")
            self.check_btn.setFixedSize(24, 24)
            self.check_btn.setStyleSheet("""
                QToolButton {
                    border: 2px solid #888;
                    border-radius: 12px;
                    background-color: transparent;
                }
                QToolButton:checked {
                    background-color: #0078d4;
                    border: 2px solid #0078d4;
                }
            """)
            self.check_btn.clicked.connect(lambda: self._on_check_changed())
            layout.addWidget(self.check_btn)

        img_w = int(self.card_size * 0.6)
        img_h = int(self.card_size * 0.5)
        img_label = QLabel()
        if self.item.image_path and os.path.exists(self.item.image_path):
            pixmap = QPixmap(self.item.image_path)
            scaled = pixmap.scaled(
                img_w,
                img_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            img_label.setPixmap(scaled)
        else:
            img_label.setText("No Image")
            img_label.setStyleSheet("color: gray; background: #f0f0f0;")
        img_label.setFixedSize(img_w, img_h)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(img_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(1)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        title_label = QLabel(self.item.title if self.item.title else "Untitled")
        title_label.setStyleSheet("font-weight: bold; font-size: 13px; color: #fff;")
        title_label.setMinimumHeight(20)
        title_label.setMaximumHeight(24)
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label, 1)

        tags_text = f"#{self.item.tags}" if self.item.tags else ""
        tags_label = QLabel(tags_text)
        tags_label.setStyleSheet("color: #888; font-size: 11px;")
        tags_label.setMinimumHeight(20)
        tags_label.setMaximumHeight(24)
        header_layout.addWidget(tags_label)

        info_layout.addLayout(header_layout)

        prompt_label = QLabel(self.item.prompt if self.item.prompt else "")
        prompt_label.setStyleSheet("color: #aaa; font-size: 11px;")
        prompt_label.setWordWrap(True)
        info_layout.addWidget(prompt_label, 1)

        bottom_layout = QHBoxLayout()
        fav_symbol = "★" if self.item.favorite else "☆"
        fav_btn = QToolButton()
        fav_btn.setText(fav_symbol)
        fav_btn.setFont(QFont("Arial", 14))
        fav_btn.setStyleSheet("color: #ff9800; border: none; background: transparent;")
        fav_btn.clicked.connect(lambda: self.favorite_clicked.emit(self.index))
        bottom_layout.addWidget(fav_btn)
        bottom_layout.addStretch()

        info_layout.addLayout(bottom_layout)

        layout.addLayout(info_layout, 1)

        self.setMinimumHeight(max(80, int(self.card_size * 0.6)))

    def _on_check_changed(self):
        self._selected = self.check_btn.isChecked()
        self.selection_changed.emit(self.index, self._selected)
        self.update_style()

    def set_selected(self, selected):
        self._selected = selected
        if self.show_checkbox and hasattr(self, "check_btn"):
            self.check_btn.setChecked(selected)
        self.update_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.index)


class HomePage(QWidget):
    item_selected = Signal(int)

    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.current_items = []
        self.is_favorites_view = False
        self.layout_mode = "flow"
        self.dark_theme = True
        self._image_size = 200
        self._card_size = 200
        self.select_mode = False
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(5, 0, 5, 2)

        self.icon_bar = QHBoxLayout()
        self.icon_bar.setSpacing(5)
        self.icon_bar.setContentsMargins(0, 2, 0, 2)

        self.label_list = QLabel("标签:")
        self.label_list.setStyleSheet("font-weight: bold;")
        self.icon_bar.addWidget(self.label_list)

        self.tags_list = []
        self.tag_buttons = []

        for i in range(6):
            btn = QPushButton(f"标签{i + 1}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self.on_tag_clicked(idx))
            self.tag_buttons.append(btn)
            self.icon_bar.addWidget(btn)

        self.btn_all = QPushButton("全部")
        self.btn_all.setCheckable(True)
        self.btn_all.setChecked(True)
        self.btn_all.clicked.connect(self.show_all_items)
        self.icon_bar.addWidget(self.btn_all)

        self.icon_bar.addStretch()

        self.select_mode_btn = QPushButton("多选")
        self.select_mode_btn.setCheckable(True)
        self.select_mode_btn.clicked.connect(self.toggle_select_mode)
        self.icon_bar.addWidget(self.select_mode_btn)

        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_all_btn.setVisible(False)
        self.icon_bar.addWidget(self.select_all_btn)

        self.batch_delete_btn = QPushButton("删除选中")
        self.batch_delete_btn.clicked.connect(self.delete_selected)
        self.batch_delete_btn.setVisible(False)
        self.icon_bar.addWidget(self.batch_delete_btn)

        self.batch_export_btn = QPushButton("导出选中")
        self.batch_export_btn.clicked.connect(self.export_selected)
        self.batch_export_btn.setVisible(False)
        self.icon_bar.addWidget(self.batch_export_btn)

        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(100)
        self.size_slider.setMaximum(400)
        self.size_slider.setValue(200)
        self.size_slider.setFixedWidth(100)
        self.size_slider.setToolTip("图片大小")
        self.size_slider.valueChanged.connect(self.on_size_changed)
        self.icon_bar.addWidget(QLabel("大小:"))
        self.icon_bar.addWidget(self.size_slider)

        self.layout_toggle_btn = QPushButton("平铺模式")
        self.layout_toggle_btn.clicked.connect(self.toggle_layout)
        self.icon_bar.addWidget(self.layout_toggle_btn)

        main_layout.addLayout(self.icon_bar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(4)
        self.cards_layout.setContentsMargins(5, 5, 5, 5)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.cards_container)
        main_layout.addWidget(scroll)

        self.load_items(self.data_manager.items)

    def update_tags(self):
        all_tags = set()
        for item in self.data_manager.items:
            if item.tags:
                for tag in item.tags.split(","):
                    all_tags.add(tag.strip())

        for i, btn in enumerate(self.tag_buttons):
            if i < len(all_tags):
                tags_list = list(all_tags)
                btn.setText(tags_list[i])
                btn.setVisible(True)
            else:
                btn.setVisible(False)

    def show_all_items(self):
        for btn in self.tag_buttons:
            btn.setChecked(False)
        self.btn_all.setChecked(True)
        self.load_items(self.data_manager.items)

    def show_all(self):
        self.show_all_items()

    def on_tag_clicked(self, idx):
        tag_text = self.tag_buttons[idx].text()
        if tag_text.startswith("标签"):
            return

        if self.tag_buttons[idx].isChecked():
            self.btn_all.setChecked(False)
            filtered = [
                item for item in self.data_manager.items if tag_text in item.tags
            ]
            self.load_items(filtered if filtered else self.data_manager.items)
        else:
            self.load_items(self.data_manager.items)

    def toggle_layout(self):
        if self.layout_mode == "flow":
            self.layout_mode = "grid"
            self.layout_toggle_btn.setText("列表模式")
        else:
            self.layout_mode = "flow"
            self.layout_toggle_btn.setText("平铺模式")
        self.load_items(self.current_items)

    def load_items(self, items):
        self.current_items = items
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        card_size = self._card_size
        show_checkbox = self.select_mode

        if self.layout_mode == "grid":
            grid_widget = QWidget()
            from PySide6.QtWidgets import QGridLayout

            grid_layout = QGridLayout(grid_widget)
            grid_layout.setSpacing(4)

            cols = 4
            for i, item in enumerate(items):
                row = i // cols
                col = i % cols
                card = ImageCard(
                    item,
                    i,
                    adapt_size=True,
                    dark_theme=self.dark_theme,
                    show_checkbox=show_checkbox,
                    card_size=card_size,
                )
                card.setFixedSize(card_size, card_size + 40)
                card.clicked.connect(self.on_card_clicked)
                card.favorite_clicked.connect(self.on_favorite_clicked)
                card.selection_changed.connect(self.on_selection_changed)
                grid_layout.addWidget(card, row, col)

            self.cards_layout.addWidget(grid_widget)
        else:
            for i, item in enumerate(items):
                card = ListCard(
                    item, i, show_checkbox=show_checkbox, card_size=card_size
                )
                card.clicked.connect(self.on_card_clicked)
                card.favorite_clicked.connect(self.on_favorite_clicked)
                card.selection_changed.connect(self.on_selection_changed)
                self.cards_layout.addWidget(card)

    def on_selection_changed(self, index, selected):
        pass

    def on_card_clicked(self, index):
        self.item_selected.emit(index)

    def on_favorite_clicked(self, index):
        if 0 <= index < len(self.current_items):
            item = self.current_items[index]
            item.favorite = not item.favorite

            actual_index = self.data_manager.items.index(item)
            self.data_manager.update_item(actual_index, item)

            self.load_items(self.current_items)

    def refresh(self):
        self.update_tags()
        self.load_items(
            self.data_manager.items
            if not self.is_favorites_view
            else self.data_manager.get_favorites()
        )

    def set_dark_theme(self, enabled):
        self.dark_theme = enabled
        self.load_items(self.current_items)

    def on_size_changed(self, value):
        self._image_size = value
        self._card_size = value
        self.load_items(self.current_items)

    def toggle_select_mode(self):
        self.select_mode = self.select_mode_btn.isChecked()
        if self.select_mode:
            self.select_mode_btn.setText("取消多选")
            self.select_all_btn.setVisible(True)
            self.batch_delete_btn.setVisible(True)
            self.batch_export_btn.setVisible(True)
        else:
            self.select_mode_btn.setText("多选")
            self.select_all_btn.setVisible(False)
            self.batch_delete_btn.setVisible(False)
            self.batch_export_btn.setVisible(False)
            if self.layout_mode == "grid":
                for i in range(self.cards_layout.count()):
                    grid_widget = self.cards_layout.itemAt(i).widget()
                    if grid_widget is None:
                        continue
                    grid_layout = grid_widget.layout()
                    if grid_layout:
                        for j in range(grid_layout.count()):
                            card = grid_layout.itemAt(j).widget()
                            if card and hasattr(card, "set_selected"):
                                card.set_selected(False)
            else:
                for i in range(self.cards_layout.count()):
                    widget = self.cards_layout.itemAt(i).widget()
                    if hasattr(widget, "set_selected"):
                        widget.set_selected(False)
        self.load_items(self.current_items)

    def delete_selected(self):
        selected_items = []

        if self.layout_mode == "grid":
            for i in range(self.cards_layout.count()):
                grid_widget = self.cards_layout.itemAt(i).widget()
                if grid_widget is None:
                    continue
                grid_layout = grid_widget.layout()
                if grid_layout:
                    for j in range(grid_layout.count()):
                        card = grid_layout.itemAt(j).widget()
                        if card and hasattr(card, "_selected") and card._selected:
                            selected_items.append(card.item)
        else:
            for i in range(self.cards_layout.count()):
                widget = self.cards_layout.itemAt(i).widget()
                if hasattr(widget, "_selected") and widget._selected:
                    selected_items.append(widget.item)

        if not selected_items:
            QMessageBox.warning(None, "警告", "请先选择要删除的项目")
            return

        reply = QMessageBox.question(
            None,
            "确认",
            f"确定要删除选中的 {len(selected_items)} 个项目吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            for item in selected_items:
                if item in self.data_manager.items:
                    idx = self.data_manager.items.index(item)
                    self.data_manager.remove_item(idx)
            self.refresh()
            self.toggle_select_mode()

    def select_all(self):
        for i in range(self.cards_layout.count()):
            widget = self.cards_layout.itemAt(i).widget()
            if widget is None:
                continue
            if hasattr(widget, "set_selected"):
                widget.set_selected(True)
            elif self.layout_mode == "grid":
                grid_layout = widget.layout()
                if grid_layout:
                    for j in range(grid_layout.count()):
                        card = grid_layout.itemAt(j).widget()
                        if card and hasattr(card, "set_selected"):
                            card.set_selected(True)

    def export_selected(self):
        selected_items = []

        if self.layout_mode == "grid":
            for i in range(self.cards_layout.count()):
                grid_widget = self.cards_layout.itemAt(i).widget()
                if grid_widget is None:
                    continue
                grid_layout = grid_widget.layout()
                if grid_layout:
                    for j in range(grid_layout.count()):
                        card = grid_layout.itemAt(j).widget()
                        if card and hasattr(card, "_selected") and card._selected:
                            selected_items.append(card.item)
        else:
            for i in range(self.cards_layout.count()):
                widget = self.cards_layout.itemAt(i).widget()
                if hasattr(widget, "_selected") and widget._selected:
                    selected_items.append(widget.item)

        if not selected_items:
            QMessageBox.warning(None, "警告", "请先选择要导出的项目")
            return

        folder = QFileDialog.getExistingDirectory(None, "选择导出文件夹")
        if not folder:
            return

        try:
            export_dir = os.path.join(folder, "prompts_export")
            images_dir = os.path.join(export_dir, "images")
            os.makedirs(images_dir, exist_ok=True)

            for item in selected_items:
                new_path = item.image_path
                if item.image_path and os.path.exists(item.image_path):
                    filename = os.path.basename(item.image_path)
                    new_filename = f"{uuid.uuid4().hex}_{filename}"
                    new_path = os.path.join(images_dir, new_filename)
                    shutil.copy2(item.image_path, new_path)

            export_items = [
                {
                    "image_path": os.path.relpath(item.image_path, export_dir)
                    if item.image_path and os.path.exists(item.image_path)
                    else "",
                    "prompt": item.prompt,
                    "tags": item.tags,
                    "title": item.title,
                    "favorite": item.favorite,
                }
                for item in selected_items
            ]

            with open(
                os.path.join(export_dir, "data.json"), "w", encoding="utf-8"
            ) as f:
                json.dump(export_items, f, ensure_ascii=False, indent=2)

            QMessageBox.information(
                None, "成功", f"已导出 {len(selected_items)} 个项目到: {export_dir}"
            )
            self.toggle_select_mode()
        except Exception as e:
            QMessageBox.warning(None, "错误", f"导出失败: {e}")


class FavoritesPage(QWidget):
    item_selected = Signal(int)

    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.current_items = []
        self.layout_mode = "flow"
        self.dark_theme = True
        self._card_size = 200
        self.select_mode = False
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()

        title = QLabel("我的收藏")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #fff;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.select_mode_btn = QPushButton("多选")
        self.select_mode_btn.setCheckable(True)
        self.select_mode_btn.clicked.connect(self.toggle_select_mode)
        header_layout.addWidget(self.select_mode_btn)

        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_all_btn.setVisible(False)
        header_layout.addWidget(self.select_all_btn)

        self.batch_delete_btn = QPushButton("删除选中")
        self.batch_delete_btn.clicked.connect(self.delete_selected)
        self.batch_delete_btn.setVisible(False)
        header_layout.addWidget(self.batch_delete_btn)

        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(100)
        self.size_slider.setMaximum(400)
        self.size_slider.setValue(200)
        self.size_slider.setFixedWidth(100)
        self.size_slider.setToolTip("图片大小")
        self.size_slider.valueChanged.connect(self.on_size_changed)
        header_layout.addWidget(QLabel("大小:"))
        header_layout.addWidget(self.size_slider)

        self.layout_toggle_btn = QPushButton("平铺模式")
        self.layout_toggle_btn.clicked.connect(self.toggle_layout)
        header_layout.addWidget(self.layout_toggle_btn)

        main_layout.addLayout(header_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(4)
        self.cards_layout.setContentsMargins(5, 5, 5, 5)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.cards_container)
        main_layout.addWidget(scroll)

        self.load_items(self.data_manager.get_favorites())

    def on_size_changed(self, value):
        self._card_size = value
        self.load_items(self.current_items)

    def toggle_select_mode(self):
        self.select_mode = self.select_mode_btn.isChecked()
        if self.select_mode:
            self.select_mode_btn.setText("取消多选")
            self.select_all_btn.setVisible(True)
            self.batch_delete_btn.setVisible(True)
        else:
            self.select_mode_btn.setText("多选")
            self.select_all_btn.setVisible(False)
            self.batch_delete_btn.setVisible(False)
            if self.layout_mode == "grid":
                for i in range(self.cards_layout.count()):
                    grid_widget = self.cards_layout.itemAt(i).widget()
                    if grid_widget is None:
                        continue
                    grid_layout = grid_widget.layout()
                    if grid_layout:
                        for j in range(grid_layout.count()):
                            card = grid_layout.itemAt(j).widget()
                            if card and hasattr(card, "set_selected"):
                                card.set_selected(False)
            else:
                for i in range(self.cards_layout.count()):
                    widget = self.cards_layout.itemAt(i).widget()
                    if hasattr(widget, "set_selected"):
                        widget.set_selected(False)
        self.load_items(self.current_items)

    def select_all(self):
        if self.layout_mode == "grid":
            for i in range(self.cards_layout.count()):
                grid_widget = self.cards_layout.itemAt(i).widget()
                if grid_widget is None:
                    continue
                grid_layout = grid_widget.layout()
                if grid_layout:
                    for j in range(grid_layout.count()):
                        card = grid_layout.itemAt(j).widget()
                        if card and hasattr(card, "set_selected"):
                            card.set_selected(True)
        else:
            for i in range(self.cards_layout.count()):
                widget = self.cards_layout.itemAt(i).widget()
                if widget is None:
                    continue
                if hasattr(widget, "set_selected"):
                    widget.set_selected(True)

    def delete_selected(self):
        selected_items = []

        if self.layout_mode == "grid":
            for i in range(self.cards_layout.count()):
                grid_widget = self.cards_layout.itemAt(i).widget()
                if grid_widget is None:
                    continue
                grid_layout = grid_widget.layout()
                if grid_layout:
                    for j in range(grid_layout.count()):
                        card = grid_layout.itemAt(j).widget()
                        if card and hasattr(card, "_selected") and card._selected:
                            selected_items.append(card.item)
        else:
            for i in range(self.cards_layout.count()):
                widget = self.cards_layout.itemAt(i).widget()
                if hasattr(widget, "_selected") and widget._selected:
                    selected_items.append(widget.item)

        if not selected_items:
            QMessageBox.warning(None, "警告", "请先选择要删除的项目")
            return

        reply = QMessageBox.question(
            None,
            "确认",
            f"确定要删除选中的 {len(selected_items)} 个项目吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            for item in selected_items:
                if item in self.data_manager.items:
                    idx = self.data_manager.items.index(item)
                    self.data_manager.remove_item(idx)
            self.refresh()
            self.toggle_select_mode()

    def toggle_layout(self):
        if self.layout_mode == "flow":
            self.layout_mode = "grid"
            self.layout_toggle_btn.setText("列表模式")
        else:
            self.layout_mode = "flow"
            self.layout_toggle_btn.setText("平铺模式")
        self.load_items(self.current_items)

    def load_items(self, items):
        self.current_items = items
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        card_size = self._card_size
        show_checkbox = self.select_mode

        if self.layout_mode == "grid":
            grid_widget = QWidget()
            from PySide6.QtWidgets import QGridLayout

            grid_layout = QGridLayout(grid_widget)
            grid_layout.setSpacing(4)

            cols = 4
            for i, item in enumerate(items):
                row = i // cols
                col = i % cols
                card = ImageCard(
                    item,
                    i,
                    adapt_size=True,
                    dark_theme=self.dark_theme,
                    show_checkbox=show_checkbox,
                    card_size=card_size,
                )
                card.setFixedSize(card_size, card_size + 40)
                card.clicked.connect(self.on_card_clicked)
                card.favorite_clicked.connect(self.on_favorite_clicked)
                card.selection_changed.connect(self.on_selection_changed)
                grid_layout.addWidget(card, row, col)

            self.cards_layout.addWidget(grid_widget)
        else:
            for i, item in enumerate(items):
                card = ListCard(
                    item, i, show_checkbox=show_checkbox, card_size=card_size
                )
                card.clicked.connect(self.on_card_clicked)
                card.favorite_clicked.connect(self.on_favorite_clicked)
                card.selection_changed.connect(self.on_selection_changed)
                self.cards_layout.addWidget(card)

    def on_selection_changed(self, index, selected):
        pass

    def on_card_clicked(self, index):
        self.item_selected.emit(index)

    def on_favorite_clicked(self, index):
        if 0 <= index < len(self.current_items):
            item = self.current_items[index]
            item.favorite = not item.favorite

            actual_index = self.data_manager.items.index(item)
            self.data_manager.update_item(actual_index, item)

            self.load_items(self.current_items)

    def refresh(self):
        self.load_items(self.data_manager.get_favorites())

    def set_dark_theme(self, enabled):
        self.dark_theme = enabled
        self.load_items(self.current_items)


from load_page import LoadPage


class SettingsPage(QWidget):
    theme_changed = Signal(str)

    def __init__(self, data_manager=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.current_theme = "dark"
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QLabel { color: #ddd; }
            QGroupBox { color: #ddd; border: 1px solid #555; }
            QPushButton { 
                background: #444; 
                color: #ddd; 
                border: 1px solid #555;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background: #555; }
            QComboBox { 
                background: #333; 
                color: #ddd; 
                border: 1px solid #555;
                padding: 5px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("设置")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #fff;")
        layout.addWidget(title)
        layout.addSpacing(20)

        group = QGroupBox("外观")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(8)

        theme_label = QLabel("主题风格:")
        theme_label.setStyleSheet("color: #ddd;")
        group_layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["深色", "浅色"])
        self.theme_combo.setCurrentText("深色")
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        group_layout.addWidget(self.theme_combo)

        group.setLayout(group_layout)
        layout.addWidget(group)
        layout.addSpacing(10)

        data_group = QGroupBox("数据")
        data_layout = QVBoxLayout()
        data_layout.setSpacing(8)

        self.export_btn = QPushButton("导出ZIP")
        self.export_btn.clicked.connect(self.export_data)
        data_layout.addWidget(self.export_btn)

        self.import_btn = QPushButton("导入ZIP")
        self.import_btn.clicked.connect(self.import_data)
        data_layout.addWidget(self.import_btn)

        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        layout.addStretch()

    def on_theme_changed(self, theme):
        self.current_theme = theme
        self.theme_changed.emit(theme)

    def export_data(self):
        if not self.data_manager:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出数据", "prompts_data.zip", "ZIP Files (*.zip)"
        )
        if not file_path:
            return

        if not file_path.endswith(".zip"):
            file_path += ".zip"

        try:
            import zipfile

            with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for item in self.data_manager.items:
                    image_name = ""
                    if item.image_path and os.path.exists(item.image_path):
                        filename = os.path.basename(item.image_path)
                        image_name = f"images/{uuid.uuid4().hex}_{filename}"
                        zf.write(item.image_path, image_name)

                    export_item = {
                        "image_path": image_name,
                        "prompt": item.prompt,
                        "tags": item.tags,
                        "title": item.title,
                        "favorite": item.favorite,
                    }
                    zf.writestr(
                        f"items/{uuid.uuid4().hex}.json",
                        json.dumps(export_item, ensure_ascii=False, indent=2),
                    )

                manifest = {
                    "version": "1.0",
                    "item_count": len(self.data_manager.items),
                }
                zf.writestr(
                    "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2)
                )

            QMessageBox.information(self, "成功", f"数据已导出到: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导出失败: {e}")

    def import_data(self):
        if not self.data_manager:
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入数据", "", "ZIP Files (*.zip)"
        )
        if not file_path:
            return

        try:
            import zipfile

            with zipfile.ZipFile(file_path, "r") as zf:
                if "manifest.json" not in zf.namelist():
                    QMessageBox.warning(self, "错误", "无效的数据包文件")
                    return

                import_items = []
                item_files = [f for f in zf.namelist() if f.startswith("items/")]

                for item_file in item_files:
                    item_data = json.loads(zf.read(item_file).decode("utf-8"))

                    image_name = item_data.get("image_path", "")
                    new_path = ""

                    if image_name and image_name in zf.namelist():
                        image_data = zf.read(image_name)
                        ext = os.path.splitext(image_name)[1]
                        new_filename = f"{uuid.uuid4().hex}{ext}"
                        new_path = os.path.join(
                            self.data_manager.images_folder, new_filename
                        )
                        with open(new_path, "wb") as img_file:
                            img_file.write(image_data)

                    import_items.append(
                        PromptItem(
                            image_path=new_path,
                            prompt=item_data.get("prompt", ""),
                            tags=item_data.get("tags", ""),
                            title=item_data.get("title", ""),
                            favorite=item_data.get("favorite", False),
                        )
                    )

                self.data_manager.items.extend(import_items)
                self.data_manager.save_data()
                QMessageBox.information(
                    self, "成功", f"已导入 {len(import_items)} 条数据!"
                )
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导入失败: {e}")


class HelpPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("帮助")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        help_text = QLabel("""
        <h3>Prompt Manager 使用说明</h3>
        <p><b>首页:</b> 查看所有已保存的图片和提示词，支持搜索和标签筛选。</p>
        <p><b>收藏:</b> 点击图片下方的★图标收藏图片，点击顶部⭐查看收藏列表。</p>
        <p><b>载入:</b> 导入新的图片，填写提示词和标签后保存。</p>
        <p><b>设置:</b> 更改主题风格，导出/导入数据。</p>
        <p><b>搜索:</b> 在搜索框输入关键词可搜索提示词、标题和标签。</p>
        """)
        help_text.setTextFormat(Qt.TextFormat.RichText)
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        layout.addStretch()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI提示词管理器")
        self.setWindowIcon(QIcon(resource_path("66.ico")))
        self.resize(1000, 700)

        self.data_manager = DataManager()

        self.setup_ui()
        self.show_home()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        nav_widget = QWidget()
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setSpacing(15)
        nav_layout.setContentsMargins(20, 5, 20, 5)

        self.btn_home = QLabel("首页")
        self.btn_home.setStyleSheet(
            "font-weight: bold; font-size: 14px; cursor: pointer;"
        )
        self.btn_home.mousePressEvent = lambda e: self.show_home()
        nav_layout.addWidget(self.btn_home)

        self.btn_load = QLabel("载入")
        self.btn_load.setStyleSheet(
            "font-weight: bold; font-size: 14px; cursor: pointer;"
        )
        self.btn_load.mousePressEvent = lambda e: self.show_load()
        nav_layout.addWidget(self.btn_load)

        self.btn_settings = QLabel("设置")
        self.btn_settings.setStyleSheet(
            "font-weight: bold; font-size: 14px; cursor: pointer;"
        )
        self.btn_settings.mousePressEvent = lambda e: self.show_settings()
        nav_layout.addWidget(self.btn_settings)

        self.btn_help = QLabel("帮助")
        self.btn_help.setStyleSheet(
            "font-weight: bold; font-size: 14px; cursor: pointer;"
        )
        self.btn_help.mousePressEvent = lambda e: self.show_help()
        nav_layout.addWidget(self.btn_help)

        self.btn_favorites = QLabel("收藏夹")
        self.btn_favorites.setStyleSheet(
            "font-weight: bold; font-size: 14px; cursor: pointer;"
        )
        self.btn_favorites.mousePressEvent = self.show_favorites
        nav_layout.addWidget(self.btn_favorites)

        self.btn_sponsor = QLabel("赞助")
        self.btn_sponsor.setStyleSheet(
            "font-weight: bold; font-size: 14px; cursor: pointer; color: #ff9800;"
        )
        self.btn_sponsor.mousePressEvent = lambda e: self.show_sponsor_dialog()
        nav_layout.addWidget(self.btn_sponsor)

        nav_layout.addStretch()

        main_layout.addWidget(nav_widget)

        self.search_widget = QWidget()
        search_layout = QHBoxLayout(self.search_widget)
        search_layout.setContentsMargins(10, 5, 10, 10)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索提示词、标签、标题...")
        self.search_edit.setMinimumWidth(400)
        self.search_edit.returnPressed.connect(self.on_search)
        search_layout.addWidget(self.search_edit)

        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.on_search)
        search_layout.addWidget(self.search_btn)

        main_layout.addWidget(self.search_widget)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self.home_page = HomePage(self.data_manager)
        self.home_page.item_selected.connect(self.show_item_detail)
        self.stack.addWidget(self.home_page)

        self.favorites_page = FavoritesPage(self.data_manager)
        self.favorites_page.item_selected.connect(self.show_item_detail_from_favorites)
        self.stack.addWidget(self.favorites_page)

        self.load_page = LoadPage(self.data_manager)
        self.load_page.data_saved.connect(self.on_data_saved)
        self.stack.addWidget(self.load_page)

        self.settings_page = SettingsPage(self.data_manager)
        self.settings_page.theme_changed.connect(self.change_theme)
        self.stack.addWidget(self.settings_page)

        self.help_page = HelpPage()
        self.stack.addWidget(self.help_page)

        self.change_theme("dark")

    def show_home(self):
        self.search_widget.setVisible(True)
        self.stack.setCurrentIndex(0)
        self.home_page.show_all()
        self.home_page.refresh()

    def show_load(self):
        self.search_widget.setVisible(False)
        self.stack.setCurrentIndex(2)

    def show_settings(self):
        self.search_widget.setVisible(False)
        self.stack.setCurrentIndex(3)

    def show_help(self):
        self.search_widget.setVisible(False)
        self.stack.setCurrentIndex(4)

    def show_favorites(self, event=None):
        self.search_widget.setVisible(True)
        self.stack.setCurrentIndex(1)
        self.favorites_page.refresh()

    def change_theme(self, theme):
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow { background-color: #1e1e1e; }
                QWidget { background-color: #1e1e1e; color: #ddd; }
                QPushButton { 
                    background: #333; 
                    color: #ddd; 
                    border: 1px solid #555;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover { background: #444; }
                QLineEdit { 
                    background: #333; 
                    color: #ddd; 
                    border: 1px solid #555;
                    padding: 5px;
                }
                QLabel { color: #ddd; }
                QScrollArea { background-color: #1e1e1e; border: none; }
                QStackedWidget { background-color: #1e1e1e; }
                QTextEdit { 
                    background-color: #333 !important;
                    color: #fff !important; 
                    border: 1px solid #555;
                    padding: 5px;
                }
                QTextEdit QScrollBar {
                    background: #333;
                }
                QGroupBox { 
                    color: #ddd; 
                    border: 1px solid #555;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title { color: #ddd; }
                QComboBox { 
                    background: #333; 
                    color: #ddd; 
                    border: 1px solid #555;
                    padding: 5px;
                }
            """)
        else:
            self.setStyleSheet("")

        self.home_page.set_dark_theme(theme == "dark")
        self.favorites_page.set_dark_theme(theme == "dark")

    def on_search(self):
        query = self.search_edit.text()
        if query:
            results = self.data_manager.search(query)
            self.home_page.load_items(results)
            self.stack.setCurrentIndex(0)
        else:
            self.home_page.load_items(self.data_manager.items)

    def on_data_saved(self):
        self.home_page.refresh()

    def show_item_detail(self, index):
        item = self.home_page.current_items[index]
        self._show_detail_dialog(item)

    def show_item_detail_from_favorites(self, index):
        item = self.favorites_page.current_items[index]
        self._show_detail_dialog(item)

    def _show_detail_dialog(self, item):
        dialog = QDialog(self)
        dialog.setWindowTitle(item.title if item.title else "编辑详情")
        dialog.resize(650, 600)

        layout = QVBoxLayout(dialog)

        if item.image_path and os.path.exists(item.image_path):
            img_label = QLabel()
            pixmap = QPixmap(item.image_path)
            scaled = pixmap.scaled(550, 350, Qt.AspectRatioMode.KeepAspectRatio)
            img_label.setPixmap(scaled)
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(img_label)

        layout.addWidget(QLabel("<b>标题:</b>"))
        title_edit = QLineEdit(item.title if item.title else "")
        layout.addWidget(title_edit)

        layout.addWidget(QLabel("<b>标签:</b>"))
        tags_edit = QLineEdit(item.tags if item.tags else "")
        layout.addWidget(tags_edit)

        layout.addWidget(QLabel("<b>Prompt:</b>"))
        prompt_text = QTextEdit()
        prompt_text.setPlainText(item.prompt)
        prompt_text.setMinimumHeight(150)
        layout.addWidget(prompt_text)

        btn_layout = QHBoxLayout()

        save_btn = QPushButton("保存修改")
        save_btn.clicked.connect(
            lambda: self._save_item_edit(
                item,
                title_edit.text(),
                tags_edit.text(),
                prompt_text.toPlainText(),
                dialog,
            )
        )
        btn_layout.addWidget(save_btn)

        copy_btn = QPushButton("复制Prompt")
        copy_btn.clicked.connect(lambda: self.copy_to_clipboard(item.prompt))
        btn_layout.addWidget(copy_btn)

        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(lambda: self._delete_current_item(item, dialog))
        btn_layout.addWidget(delete_btn)

        layout.addLayout(btn_layout)

        dialog.exec()

    def _save_item_edit(self, item, title, tags, prompt, dialog):
        item.title = title
        item.tags = tags
        item.prompt = prompt

        if item in self.data_manager.items:
            index = self.data_manager.items.index(item)
            self.data_manager.update_item(index, item)

        self.home_page.refresh()
        self.favorites_page.refresh()
        QMessageBox.information(self, "成功", "修改已保存!")
        dialog.close()

    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "成功", "Prompt已复制到剪贴板!")

    def _delete_current_item(self, item, dialog):
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要删除这个项目吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if item in self.data_manager.items:
                index = self.data_manager.items.index(item)
                self.data_manager.remove_item(index)
            self.home_page.refresh()
            self.favorites_page.refresh()
            dialog.close()

    def show_sponsor_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("支持该项目")
        dialog.resize(400, 450)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)

        title = QLabel("感谢您的支持!")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sponsor_img_path = resource_path("赞赏码.jpg")
        if os.path.exists(sponsor_img_path):
            img_label = QLabel()
            pixmap = QPixmap(sponsor_img_path)
            scaled = pixmap.scaled(
                300,
                300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            img_label.setPixmap(scaled)
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(img_label)
        else:
            no_img_label = QLabel("赞助码图片未找到")
            no_img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_img_label.setStyleSheet("color: #888; padding: 50px;")
            layout.addWidget(no_img_label)

        message = QLabel(
            "如果你喜欢这个项目，但是没有办法给出金钱上的支持，那也没关系。"
            "还有其他简单的方法可以支持该项目并表达您的感激之情，我也非常高兴，"
            "例如给这个项目加星标！⭐"
        )
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message.setStyleSheet("color: #555; padding: 10px;")
        layout.addWidget(message)

        link_label = QLabel(
            '<a href="https://github.com/kungful/ai_prompt_manage.git" style="color: #0078d4;">点击访问 GitHub 仓库</a>'
        )
        link_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        link_label.setOpenExternalLinks(True)
        layout.addWidget(link_label)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
