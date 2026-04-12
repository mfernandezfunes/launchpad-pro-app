import pytest
from unittest.mock import MagicMock, patch
from models.project import Project, Bank
from ui.main_window import MainWindow


@pytest.fixture
def window(qapp):
    midi_engine = MagicMock()
    midi_engine.connected = False
    midi_engine.device_name = "Sin conexión"
    midi_engine.connect.return_value = False
    audio_engine = MagicMock()
    project = Project.new()
    with patch("ui.main_window.list_midi_devices", return_value=[]), \
         patch("ui.main_window.sd.query_devices", return_value=[]):
        return MainWindow(project=project, midi_engine=midi_engine, audio_engine=audio_engine)


def test_window_has_title(window):
    assert "Launchpad" in window.windowTitle()


def test_status_bar_shows_disconnected(window):
    assert "Desconectado" in window.label_status.text() or \
           "Sin conexión" in window.label_status.text()


def test_assignment_mode_starts_disabled(window):
    assert window.assignment_mode_active is False


def test_toggle_assignment_mode(window):
    window.toggle_assignment_mode()
    assert window.assignment_mode_active is True
    window.toggle_assignment_mode()
    assert window.assignment_mode_active is False


def test_change_bank_updates_grid(window):
    window.project.banks.append(Bank(name="B"))
    window.on_bank_changed(1)
    assert window.project.active_bank_index == 1
