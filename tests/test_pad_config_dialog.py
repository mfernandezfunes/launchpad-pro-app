import pytest
from unittest.mock import patch
from models.project import PadConfig
from ui.pad_config_dialog import PadConfigDialog


@pytest.fixture
def empty_dialog(qapp):
    return PadConfigDialog(pad_id=11, current_config=None)


@pytest.fixture
def dialog_with_config(qapp):
    config = PadConfig(audio_file="/path/kick.wav", color=3)
    return PadConfigDialog(pad_id=11, current_config=config)


def test_empty_dialog_shows_no_audio(empty_dialog):
    assert empty_dialog.label_file.text() == "Sin audio"


def test_dialog_loads_existing_config(dialog_with_config):
    assert "kick.wav" in dialog_with_config.label_file.text()


def test_save_returns_pad_config(empty_dialog, qtbot):
    with patch("ui.pad_config_dialog.QFileDialog.getOpenFileName",
               return_value=("/path/snare.wav", "")):
        empty_dialog.btn_select.click()
    empty_dialog.palette.color_selected.emit(7)
    empty_dialog.accept()  # Accept the dialog before getting config
    result = empty_dialog.get_config()
    assert result is not None
    assert result.audio_file == "/path/snare.wav"
    assert result.color == 7


def test_cancel_returns_none(empty_dialog):
    empty_dialog.reject()
    # get_config luego de reject debe retornar None
    assert empty_dialog.result() == 0
