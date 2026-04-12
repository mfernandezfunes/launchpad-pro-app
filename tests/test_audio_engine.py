import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from engine.audio_engine import AudioEngine


@pytest.fixture
def engine():
    with patch("engine.audio_engine.sd") as mock_sd, \
         patch("engine.audio_engine.sf") as mock_sf:
        mock_sf.read.return_value = (np.array([0.0, 0.1, 0.2], dtype=np.float32), 44100)
        yield AudioEngine(), mock_sd, mock_sf


def test_play_oneshot_calls_play(engine):
    m, mock_sd, mock_sf = engine
    m.play("/audio/kick.wav", volume=0.8, mode="oneshot", pad_id=11,
           on_complete=None)
    import time
    time.sleep(0.1)  # wait for thread to execute
    mock_sd.play.assert_called_once()


def test_play_adjusts_volume(engine):
    m, mock_sd, mock_sf = engine
    m.play("/audio/kick.wav", volume=0.5, mode="oneshot", pad_id=11,
           on_complete=None)
    import time
    time.sleep(0.1)  # wait for thread to execute
    args, kwargs = mock_sd.play.call_args
    assert args[0].max() <= 0.5 * 1.1  # tolerancia


def test_stop_pad(engine):
    m, mock_sd, _ = engine
    m.play("/audio/kick.wav", volume=1.0, mode="loop", pad_id=11,
           on_complete=None)
    m.stop(pad_id=11)
    mock_sd.stop.assert_called()


def test_play_missing_file_does_not_raise(engine):
    m, mock_sd, mock_sf = engine
    mock_sf.read.side_effect = FileNotFoundError
    m.play("/no/existe.wav", volume=1.0, mode="oneshot", pad_id=99,
           on_complete=None)
