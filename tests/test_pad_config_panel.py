import pytest
from unittest.mock import patch
from models.project import PadConfig
from ui.pad_config_panel import PadConfigPanel


@pytest.fixture
def panel(qapp):
    return PadConfigPanel()


def test_panel_shows_empty_pad(panel):
    panel.show_pad(pad_id=11, config=None)
    assert panel.label_file.text() == "Sin audio"


def test_panel_shows_pad_with_config(panel):
    config = PadConfig(audio_file="/path/kick.wav", color=3)
    panel.show_pad(pad_id=11, config=config)
    assert "kick.wav" in panel.label_file.text()


def test_color_change_emits_signal(panel, qtbot):
    panel.show_pad(pad_id=11, config=None)
    signals = []
    panel.color_changed.connect(lambda pad, color: signals.append((pad, color)))
    panel.palette.color_selected.emit(5)
    assert signals == [(11, 5)]


def test_select_audio_emits_signal(panel, qtbot):
    panel.show_pad(pad_id=11, config=None)
    signals = []
    panel.audio_changed.connect(lambda pad, path: signals.append((pad, path)))
    with patch("ui.pad_config_panel.QFileDialog.getOpenFileName",
               return_value=("/path/kick.wav", "")):
        panel.btn_select.click()
    assert signals == [(11, "/path/kick.wav")]
