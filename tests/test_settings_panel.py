import pytest
from models.project import Settings
from ui.settings_panel import SettingsPanel


@pytest.fixture
def settings():
    return Settings(
        midi_input="Launchpad Mini MK2",
        midi_output="Launchpad Mini MK2",
        audio_output="Built-in Audio",
        volume=0.8,
        play_mode="oneshot",
    )


def test_panel_loads_settings(qapp, settings):
    panel = SettingsPanel(
        settings=settings,
        midi_devices=["Launchpad Mini MK2", "Otro"],
        audio_devices=["Built-in Audio", "Externo"],
    )
    assert panel.combo_midi_in.currentText() == "Launchpad Mini MK2"
    assert panel.combo_audio.currentText() == "Built-in Audio"
    assert panel.combo_mode.currentText() == "Una vez"


def test_panel_emits_changes(qapp, settings, qtbot):
    panel = SettingsPanel(
        settings=settings,
        midi_devices=["Launchpad Mini MK2"],
        audio_devices=["Built-in Audio"],
    )
    signals = []
    panel.settings_changed.connect(signals.append)
    panel.volume_slider.setValue(60)
    assert len(signals) == 1
    assert signals[0].volume == pytest.approx(0.6)
