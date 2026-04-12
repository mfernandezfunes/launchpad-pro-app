import pytest
from unittest.mock import patch, MagicMock, call
from engine.midi_engine import MidiEngine, pad_to_note, note_to_pad, SCENE_NOTES


def test_pad_to_note_top_left_corner():
    # Fila visual 0 (arriba), col 0 → nota MIDI 81
    assert pad_to_note(0, 0) == 81


def test_pad_to_note_bottom_right_corner():
    # Fila visual 7 (abajo), col 7 → nota MIDI 18
    assert pad_to_note(7, 7) == 18


def test_note_to_pad_roundtrip():
    for row in range(8):
        for col in range(8):
            note = pad_to_note(row, col)
            r2, c2 = note_to_pad(note)
            assert (r2, c2) == (row, col)


def test_scene_notes_are_8():
    assert len(SCENE_NOTES) == 8


def test_list_midi_devices_calls_rtmidi():
    with patch("engine.midi_engine.rtmidi.MidiIn") as mock_in:
        mock_in.return_value.get_ports.return_value = ["Launchpad Mini", "otro"]
        from engine.midi_engine import list_midi_devices
        devices = list_midi_devices()
        assert "Launchpad Mini" in devices


def test_connect_detects_launchpad():
    engine = MidiEngine()
    with patch.object(engine, "_midi_in") as mock_in, \
         patch.object(engine, "_midi_out") as mock_out:
        mock_in.get_ports.return_value = ["Launchpad Mini MK2", "otro"]
        mock_out.get_ports.return_value = ["Launchpad Mini MK2", "otro"]
        result = engine.connect()
        assert result is True


def test_set_pad_color_sends_note_on():
    engine = MidiEngine()
    mock_out = MagicMock()
    engine._midi_out = mock_out
    engine._connected = True
    engine.set_pad_color(pad_id=11, color=3)
    # note_on ch1 (0x90), nota 11, velocity 3
    mock_out.send_message.assert_called_with([0x90, 11, 3])


def test_set_pad_color_turns_off_with_0():
    engine = MidiEngine()
    mock_out = MagicMock()
    engine._midi_out = mock_out
    engine._connected = True
    engine.set_pad_color(pad_id=11, color=0)
    mock_out.send_message.assert_called_with([0x90, 11, 0])
