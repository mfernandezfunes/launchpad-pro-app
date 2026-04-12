from __future__ import annotations
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QComboBox, QSlider, QLabel
)
from PyQt6.QtCore import Qt
from models.project import Settings

MODES = {"oneshot": "Una vez", "loop": "Bucle", "toggle": "Alternar"}
MODES_INV = {v: k for k, v in MODES.items()}


class SettingsPanel(QWidget):
    settings_changed = pyqtSignal(Settings)

    def __init__(
        self,
        settings: Settings,
        midi_devices: list[str],
        audio_devices: list[str],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._settings = settings
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.combo_midi_in = QComboBox()
        self.combo_midi_in.addItems(midi_devices)
        idx = self.combo_midi_in.findText(settings.midi_input)
        if idx >= 0:
            self.combo_midi_in.setCurrentIndex(idx)
        self.combo_midi_in.currentTextChanged.connect(self._on_change)
        form.addRow("MIDI Entrada:", self.combo_midi_in)

        self.combo_midi_out = QComboBox()
        self.combo_midi_out.addItems(midi_devices)
        idx = self.combo_midi_out.findText(settings.midi_output)
        if idx >= 0:
            self.combo_midi_out.setCurrentIndex(idx)
        self.combo_midi_out.currentTextChanged.connect(self._on_change)
        form.addRow("MIDI Salida:", self.combo_midi_out)

        self.combo_audio = QComboBox()
        self.combo_audio.addItems(audio_devices)
        idx = self.combo_audio.findText(settings.audio_output)
        if idx >= 0:
            self.combo_audio.setCurrentIndex(idx)
        self.combo_audio.currentTextChanged.connect(self._on_change)
        form.addRow("Audio Salida:", self.combo_audio)

        self.combo_mode = QComboBox()
        self.combo_mode.addItems(list(MODES.values()))
        self.combo_mode.setCurrentText(MODES.get(settings.play_mode, "Una vez"))
        self.combo_mode.currentTextChanged.connect(self._on_change)
        form.addRow("Modo reproducción:", self.combo_mode)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(settings.volume * 100))
        self.volume_slider.valueChanged.connect(self._on_change)
        form.addRow("Volumen:", self.volume_slider)

        layout.addLayout(form)
        layout.addStretch()

    def _on_change(self) -> None:
        settings = Settings(
            midi_input=self.combo_midi_in.currentText(),
            midi_output=self.combo_midi_out.currentText(),
            audio_output=self.combo_audio.currentText(),
            volume=self.volume_slider.value() / 100.0,
            play_mode=MODES_INV.get(self.combo_mode.currentText(), "oneshot"),
        )
        self._settings = settings
        self.settings_changed.emit(settings)
