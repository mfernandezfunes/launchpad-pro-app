from __future__ import annotations
import os
from typing import Optional
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QSlider, QToolButton, QFileDialog, QMessageBox,
    QStackedWidget, QStatusBar,
)
from models.project import PadConfig, Bank, Project
from engine.audio_engine import AudioEngine
from engine.midi_engine import MidiEngine, pad_to_note, note_to_pad, list_midi_devices
from ui.pad_grid import PadGrid
from ui.bank_selector import BankSelector
from ui.pad_config_panel import PadConfigPanel
from ui.settings_panel import SettingsPanel
from ui.pad_config_dialog import PadConfigDialog
from ui.about_dialog import AboutDialog
from ui.color_palette import LP_COLORS
import sounddevice as sd


PROJECT_FILTER = "Proyecto LP Sampler (*.lpsampler)"


class MainWindow(QMainWindow):
    def __init__(
        self,
        project: Project,
        midi_engine: MidiEngine,
        audio_engine: AudioEngine,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.project = project
        self.midi_engine = midi_engine
        self.audio_engine = audio_engine
        self.assignment_mode_active = False
        self._project_path: Optional[str] = None

        self.setWindowTitle("Launchpad Mini MK2 Sampler")
        self.resize(720, 520)
        self._build_ui()
        self._build_menu()
        self._connect_midi()
        self._update_grid_bank()

    # ── Construcción de UI ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(4)
        main_layout.setContentsMargins(8, 8, 8, 4)

        # Fila superior: bancos + botón modo asignación
        bank_row = QHBoxLayout()
        names = [b.name for b in self.project.banks]
        self.bank_selector = BankSelector(names=names)
        self.bank_selector.bank_changed.connect(self.on_bank_changed)
        self.bank_selector.add_bank_requested.connect(self._on_add_bank)
        bank_row.addWidget(self.bank_selector, 1)

        self.btn_assignment_mode = QToolButton()
        self.btn_assignment_mode.setText("⚡ Modo Asignación")
        self.btn_assignment_mode.setCheckable(True)
        self.btn_assignment_mode.clicked.connect(self.toggle_assignment_mode)
        bank_row.addWidget(self.btn_assignment_mode)
        main_layout.addLayout(bank_row)

        # Área central: grid + panel derecho
        center_area = QHBoxLayout()
        self.grid = PadGrid(color_palette=LP_COLORS)
        self.grid.pad_selected.connect(self.on_pad_click_ui)
        center_area.addWidget(self.grid, 1)

        # Panel derecho apilado: config pad / ajustes
        self.stack_panel = QStackedWidget()
        self.stack_panel.setMinimumWidth(200)
        self.stack_panel.setMaximumWidth(240)

        self.config_panel = PadConfigPanel()
        self.config_panel.color_changed.connect(self.on_color_changed)
        self.config_panel.audio_changed.connect(self.on_audio_changed)
        self.stack_panel.addWidget(self.config_panel)  # índice 0

        midi_devices = list_midi_devices()
        audio_devices = [d["name"] for d in sd.query_devices()
                         if d.get("max_output_channels", 0) > 0]
        self.settings_panel = SettingsPanel(
            settings=self.project.settings,
            midi_devices=midi_devices,
            audio_devices=audio_devices,
        )
        self.settings_panel.settings_changed.connect(self.on_settings_changed)
        self.stack_panel.addWidget(self.settings_panel)  # índice 1

        center_area.addWidget(self.stack_panel)
        main_layout.addLayout(center_area, 1)

        # Barra de estado
        self.label_status = QLabel("● Sin conexión")
        self.statusBar().addWidget(self.label_status, 1)

        self.label_note = QLabel("")
        self.statusBar().addPermanentWidget(self.label_note)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.project.settings.volume * 100))
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self._on_volume_slider)
        self.statusBar().addPermanentWidget(QLabel("Vol:"))
        self.statusBar().addPermanentWidget(self.volume_slider)

    def _build_menu(self) -> None:
        mb = self.menuBar()

        m_file = mb.addMenu("Archivo")
        m_file.addAction("Nuevo", self.new_project)
        m_file.addAction("Abrir...", self.open_project)
        m_file.addAction("Guardar", self.save_project)
        m_file.addAction("Guardar como...", self.save_project_as)
        m_file.addSeparator()
        m_file.addAction("Salir", self.close)

        m_config = mb.addMenu("Configuración")
        m_config.addAction("Ajustes", self.show_settings)

        m_help = mb.addMenu("Ayuda")
        m_help.addAction("Acerca de", self.show_about)

    # ── MIDI ────────────────────────────────────────────────────────────

    def _connect_midi(self) -> None:
        self.midi_engine.set_callback_pad(self.on_physical_pad)
        self.midi_engine.set_callback_scene(self.on_bank_changed)
        if self.midi_engine.connect():
            self.label_status.setText("● Launchpad conectado")
            self.midi_engine.update_bank_leds(
                self.project.active_bank,
                self.project.active_bank_index,
                self.project.banks,
            )
        else:
            self.label_status.setText("● Sin conexión — abrí Configuración > Ajustes")
            self.show_settings()

    def _show_note(self, pad_id: int) -> None:
        row, col = note_to_pad(pad_id)
        self.label_note.setText(f"Nota: {pad_id}  (R{row+1} C{col+1})")

    def on_physical_pad(self, pad_id: int) -> None:
        """Llamado desde hilo MIDI cuando se presiona un pad físico."""
        self._show_note(pad_id)
        if self.assignment_mode_active:
            current_config = self.project.active_bank.pads.get(pad_id)
            dialog = PadConfigDialog(pad_id=pad_id, current_config=current_config, parent=self)
            if dialog.exec():
                new_config = dialog.get_config()
                if new_config:
                    self.project.active_bank.pads[pad_id] = new_config
                    self.midi_engine.set_pad_color(pad_id, new_config.color)
                    row, col = note_to_pad(pad_id)
                    self.grid.set_pad_color(row, col, new_config.color)
        else:
            config = self.project.active_bank.pads.get(pad_id)
            if config and os.path.exists(config.audio_file):
                self.midi_engine.start_blink(pad_id, config.color)
                self.audio_engine.play(
                    config.audio_file,
                    volume=self.project.settings.volume,
                    mode=self.project.settings.play_mode,
                    pad_id=pad_id,
                    on_complete=lambda pid: self.midi_engine.stop_blink(
                        pid, self.project.active_bank.pads.get(pid, PadConfig("", 0)).color
                    ),
                )

    def on_pad_click_ui(self, row: int, col: int) -> None:
        """Selección desde la UI (click en grid)."""
        pad_id = pad_to_note(row, col)
        self._show_note(pad_id)
        config = self.project.active_bank.pads.get(pad_id)
        self.config_panel.show_pad(pad_id, config)
        self.stack_panel.setCurrentIndex(0)

    def on_color_changed(self, pad_id: int, color: int) -> None:
        config = self.project.active_bank.pads.get(pad_id)
        if config:
            config.color = color
        else:
            self.project.active_bank.pads[pad_id] = PadConfig(audio_file="", color=color)
        row, col = note_to_pad(pad_id)
        self.grid.set_pad_color(row, col, color)
        self.midi_engine.set_pad_color(pad_id, color)

    def on_audio_changed(self, pad_id: int, path: str) -> None:
        config = self.project.active_bank.pads.get(pad_id)
        if config:
            config.audio_file = path
        else:
            self.project.active_bank.pads[pad_id] = PadConfig(audio_file=path, color=0)

    def on_bank_changed(self, index: int) -> None:
        if index < 0 or index >= len(self.project.banks):
            return
        self.project.active_bank_index = index
        self.bank_selector.setCurrentIndex(index)
        self._update_grid_bank()
        self.midi_engine.update_bank_leds(
            self.project.active_bank, index, self.project.banks
        )

    def _on_add_bank(self) -> None:
        from ui.bank_selector import BANK_NAMES, MAX_BANKS
        count = len(self.project.banks)
        if count >= MAX_BANKS:
            return
        name = BANK_NAMES[count]
        self.project.banks.append(Bank(name=name))
        self.bank_selector.add_bank(name)
        self.on_bank_changed(count)

    def on_settings_changed(self, settings) -> None:
        self.project.settings = settings
        self.volume_slider.setValue(int(settings.volume * 100))

    def toggle_assignment_mode(self) -> None:
        self.assignment_mode_active = not self.assignment_mode_active
        self.btn_assignment_mode.setChecked(self.assignment_mode_active)

    def show_settings(self) -> None:
        self.stack_panel.setCurrentIndex(1)

    def show_about(self) -> None:
        dialog = AboutDialog(
            connected_device=self.midi_engine.device_name,
            parent=self,
        )
        dialog.exec()

    # ── Archivo ─────────────────────────────────────────────────────────

    def new_project(self) -> None:
        self.project = Project.new()
        self._project_path = None
        self._update_grid_bank()

    def open_project(self) -> None:
        from config.project_file import load_project
        path, _ = QFileDialog.getOpenFileName(self, "Abrir proyecto", "", PROJECT_FILTER)
        if path:
            try:
                self.project = load_project(path)
                self._project_path = path
                self._update_grid_bank()
                self.midi_engine.update_bank_leds(
                    self.project.active_bank,
                    self.project.active_bank_index,
                    self.project.banks,
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el proyecto:\n{e}")

    def save_project(self) -> None:
        if self._project_path:
            self._save_to(self._project_path)
        else:
            self.save_project_as()

    def save_project_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Guardar proyecto", "", PROJECT_FILTER)
        if path:
            if not path.endswith(".lpsampler"):
                path += ".lpsampler"
            self._save_to(path)

    def _save_to(self, path: str) -> None:
        from config.project_file import save_project
        try:
            save_project(self.project, path)
            self._project_path = path
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")

    # ── Helpers ─────────────────────────────────────────────────────────

    def _update_grid_bank(self) -> None:
        bank = self.project.active_bank
        for row in range(8):
            for col in range(8):
                note = pad_to_note(row, col)
                config = bank.pads.get(note)
                color = config.color if config else 0
                self.grid.set_pad_color(row, col, color)

    def _on_volume_slider(self, value: int) -> None:
        self.project.settings.volume = value / 100.0

    def closeEvent(self, event) -> None:
        self.audio_engine.stop_all()
        self.midi_engine.disconnect()
        super().closeEvent(event)
