from __future__ import annotations
from typing import Optional
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
)
from models.project import PadConfig
from ui.color_palette import ColorPalette


AUDIO_FILTER = "Audio (*.wav *.mp3 *.ogg *.flac)"


class PadConfigPanel(QWidget):
    color_changed = pyqtSignal(int, int)   # pad_id, color
    audio_changed = pyqtSignal(int, str)   # pad_id, path

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._pad_id: Optional[int] = None
        layout = QVBoxLayout(self)

        self.label_title = QLabel("Seleccioná un pad")
        layout.addWidget(self.label_title)

        self.palette = ColorPalette()
        self.palette.color_selected.connect(self._on_color)
        layout.addWidget(self.palette)

        self.btn_select = QPushButton("Seleccionar audio...")
        self.btn_select.clicked.connect(self._on_select_audio)
        layout.addWidget(self.btn_select)

        self.label_file = QLabel("Sin audio")
        self.label_file.setWordWrap(True)
        layout.addWidget(self.label_file)

        layout.addStretch()

    def show_pad(self, pad_id: int, config: Optional[PadConfig]) -> None:
        self._pad_id = pad_id
        self.label_title.setText(f"Pad {pad_id}")
        if config:
            import os
            self.label_file.setText(os.path.basename(config.audio_file))
            self.palette.set_active_color(config.color)
        else:
            self.label_file.setText("Sin audio")

    def _on_color(self, color: int) -> None:
        if self._pad_id is not None:
            self.color_changed.emit(self._pad_id, color)

    def _on_select_audio(self) -> None:
        if self._pad_id is None:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar audio", "", AUDIO_FILTER)
        if path:
            import os
            self.label_file.setText(os.path.basename(path))
            self.audio_changed.emit(self._pad_id, path)
