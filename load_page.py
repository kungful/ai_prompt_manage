import os
import shutil
import uuid

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtWidgets import QFrame


class LoadPage(QWidget):
    data_saved = Signal()

    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.current_image_path = ""
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; }
            QLabel { color: #ddd; background-color: transparent; }
            QLineEdit {
                background: #333;
                color: #fff;
                border: 1px solid #555;
                padding: 8px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
            QTextEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                font-family: "Microsoft YaHei", "SimSun", sans-serif;
                font-size: 13px;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
            }
            QTextEdit:focus {
                border: 1px solid #0078d4;
            }
            QPushButton {
                background: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1084d8;
            }
            QPushButton#btn_clear {
                background: #444;
                color: #ddd;
            }
            QPushButton#btn_clear:hover {
                background: #555;
            }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        from main import DropZone

        title_label = QLabel("导入图片")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #fff;")
        left_panel.addWidget(title_label)

        self.drop_zone = DropZone()
        self.drop_zone.setFixedSize(350, 350)
        self.drop_zone.image_dropped.connect(self._on_image_dropped)
        self.drop_zone.mousePressEvent = lambda event: self.select_image()
        left_panel.addWidget(self.drop_zone, 0, Qt.AlignmentFlag.AlignTop)

        hint_label = QLabel("支持拖拽或点击选择 PNG/JPG/BMP/GIF 图片")
        hint_label.setStyleSheet("color: #888; font-size: 12px;")
        left_panel.addWidget(hint_label)

        left_panel.addStretch()

        main_layout.addLayout(left_panel, 1)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        right_title = QLabel("填写信息")
        right_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #fff;")
        right_panel.addWidget(right_title)

        title_row = QHBoxLayout()
        title_row.addWidget(QLabel("标题:"))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("输入标题...")
        title_row.addWidget(self.title_edit)
        right_panel.addLayout(title_row)

        prompt_row = QVBoxLayout()
        prompt_label_row = QHBoxLayout()
        prompt_label_row.addWidget(QLabel("提示词 (Prompt):"))
        prompt_label_row.addStretch()
        prompt_row.addLayout(prompt_label_row)
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("输入AI提示词...")
        self.prompt_edit.setMinimumHeight(200)
        self.prompt_edit.setMaximumHeight(300)
        self.prompt_edit.setAcceptRichText(False)
        self._fix_textedit_palette()
        prompt_row.addWidget(self.prompt_edit)
        right_panel.addLayout(prompt_row)

        tags_row = QHBoxLayout()
        tags_row.addWidget(QLabel("标签:"))
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("标签1, 标签2, 标签3...")
        tags_row.addWidget(self.tags_edit)
        right_panel.addLayout(tags_row)

        right_panel.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        self.btn_save = QPushButton("保存")
        self.btn_save.setFixedHeight(45)
        self.btn_save.clicked.connect(self.save_data)
        btn_layout.addWidget(self.btn_save)

        self.btn_clear = QPushButton("清空")
        self.btn_clear.setObjectName("btn_clear")
        self.btn_clear.setFixedHeight(45)
        self.btn_clear.clicked.connect(self.clear_form)
        btn_layout.addWidget(self.btn_clear)

        right_panel.addLayout(btn_layout)

        main_layout.addLayout(right_panel, 2)

    def _fix_textedit_palette(self):
        from PySide6.QtGui import QPalette, QColor

        palette = self.prompt_edit.palette()
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 212))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.prompt_edit.setPalette(palette)

    def select_image(self, event=None):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.current_image_path = self._copy_image_to_local(file_path)
            self.update_preview()

    def _on_image_dropped(self, file_path):
        if file_path:
            self.current_image_path = self._copy_image_to_local(file_path)
            self.update_preview()

    def _copy_image_to_local(self, source_path):
        if not os.path.isabs(source_path):
            return source_path

        ext = os.path.splitext(source_path)[1]
        new_name = f"{uuid.uuid4().hex}{ext}"
        dest_path = os.path.join(self.data_manager.images_folder, new_name)

        try:
            shutil.copy2(source_path, dest_path)
            return dest_path
        except Exception as e:
            QMessageBox.warning(self, "错误", f"复制图片失败: {e}")
            return source_path

    def update_preview(self):
        if self.current_image_path and os.path.exists(self.current_image_path):
            pixmap = QPixmap(self.current_image_path)
            scaled = pixmap.scaled(
                330,
                330,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.drop_zone.label.setPixmap(scaled)
            self.drop_zone.label.setText("")
            self.drop_zone.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def save_data(self):
        if not self.current_image_path:
            QMessageBox.warning(self, "警告", "请先选择图片!")
            return

        prompt_text = self.prompt_edit.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "警告", "请输入提示词!")
            return

        from main import PromptItem

        item = PromptItem(
            image_path=self.current_image_path,
            prompt=prompt_text,
            tags=self.tags_edit.text().strip(),
            title=self.title_edit.text().strip(),
        )

        self.data_manager.add_item(item)
        self.data_saved.emit()
        QMessageBox.information(self, "成功", "数据已保存!")
        self.clear_form()

    def clear_form(self):
        self.current_image_path = ""
        self.title_edit.clear()
        self.prompt_edit.clear()
        self.tags_edit.clear()
        self.drop_zone.label.setText("拖拽图片到这里\n或点击选择")
        self.drop_zone.label.setPixmap(QPixmap())
        self.drop_zone.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._fix_textedit_palette()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
