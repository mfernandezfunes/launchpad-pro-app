import json
import pytest
from pathlib import Path
from models.project import PadConfig, Bank, Settings, Project
from config.project_file import save_project, load_project


@pytest.fixture
def project_with_pads():
    p = Project.new()
    p.banks[0].pads[11] = PadConfig(audio_file="/audio/kick.wav", color=3)
    p.banks[0].pads[12] = PadConfig(audio_file="/audio/snare.wav", color=5)
    return p


def test_save_and_load_roundtrip(tmp_path, project_with_pads):
    path = tmp_path / "test.lpsampler"
    save_project(project_with_pads, path)
    loaded = load_project(path)
    assert loaded.banks[0].name == "A"
    assert loaded.banks[0].pads[11].audio_file == "/audio/kick.wav"
    assert loaded.banks[0].pads[11].color == 3
    assert loaded.settings.volume == pytest.approx(0.8)
    assert loaded.settings.play_mode == "oneshot"


def test_file_is_valid_json(tmp_path, project_with_pads):
    path = tmp_path / "test.lpsampler"
    save_project(project_with_pads, path)
    content = json.loads(path.read_text())
    assert "banks" in content
    assert "settings" in content


def test_load_missing_file_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_project(tmp_path / "missing.lpsampler")


def test_multiple_banks_roundtrip(tmp_path):
    p = Project.new()
    p.banks.append(Bank(name="B"))
    p.banks[1].pads[21] = PadConfig(audio_file="/audio/hihat.wav", color=9)
    path = tmp_path / "test.lpsampler"
    save_project(p, path)
    loaded = load_project(path)
    assert len(loaded.banks) == 2
    assert loaded.banks[1].pads[21].audio_file == "/audio/hihat.wav"
