from models.project import PadConfig, Bank, Settings, Project


def test_pad_config_defaults():
    pad = PadConfig(audio_file="/path/kick.wav", color=3)
    assert pad.audio_file == "/path/kick.wav"
    assert pad.color == 3


def test_bank_empty_pads():
    bank = Bank(name="A")
    assert bank.pads == {}


def test_bank_add_pad():
    bank = Bank(name="A")
    bank.pads[11] = PadConfig(audio_file="/path/snare.wav", color=5)
    assert 11 in bank.pads
    assert bank.pads[11].color == 5


def test_project_initial_banks():
    project = Project.new()
    assert len(project.banks) == 1
    assert project.banks[0].name == "A"


def test_project_active_bank():
    project = Project.new()
    assert project.active_bank_index == 0


def test_settings_play_mode():
    settings = Settings(
        midi_input="",
        midi_output="",
        audio_output="",
        volume=0.8,
        play_mode="oneshot",
    )
    assert settings.play_mode == "oneshot"
