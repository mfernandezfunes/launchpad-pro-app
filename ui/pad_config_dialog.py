from __future__ import annotations
import os
from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QDialogButtonBox,
)
from models.project import PadConfig
from ui.color_palette import ColorPalette

AUDIO_FILTER = "Audio (*.wav *.mp3 *.ogg *.flac)"


class PadConfigDialog(QDialog):
    def __init__(
        self,
        pad_id: int,
        current_config: Optional[PadConfig],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._pad_id = pad_id
        self._audio_path: str = current_config.audio_file if current_config else ""
        self._color: int = current_config.color if current_config else 0
        self.setWindowTitle(f"Configurar Pad {pad_id}")
        self.setMinimumWidth(280)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"<b>Pad {pad_id}</b>"))

        # Audio
        layout.addWidget(QLabel("Archivo de audio:"))
        audio_row = QHBoxLayout()
        name = os.path.basename(self._audio_path) if self._audio_path else "Sin audio"
        self.label_file = QLabel(name)
        audio_row.addWidget(self.label_file, 1)
        self.btn_select = QPushButton("Seleccionar...")
        self.btn_select.clicked.connect(self._on_select)
        audio_row.addWidget(self.btn_select)
        layout.addLayout(audio_row)

        # Color
        layout.addWidget(QLabel("Color del pad:"))
        self.palette = ColorPalette()
        self.palette.color_selected.connect(self._on_color)
        if current_config:
            self.palette.set_active_color(current_config.color)
        layout.addWidget(self.palette)

        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Guardar")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_select(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar audio", "", AUDIO_FILTER)
        if path:
            self._audio_path = path
            self.label_file.setText(os.path.basename(path))

    def _on_color(self, color: int) -> None:
        self._color = color

    def get_config(self) -> Optional[PadConfig]:
        if self.result() != QDialog.DialogCode.Accepted:
            return None
        if not self._audio_path:
            return None
        return PadConfig(audio_file=self._audio_path, color=self._color)
