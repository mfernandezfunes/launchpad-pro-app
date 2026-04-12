import pytest
from ui.color_palette import ColorPalette, LP_COLORS


def test_palette_has_64_entries():
    assert len(LP_COLORS) == 64


def test_color_0_is_black():
    assert LP_COLORS[0].lower() == "#000000"


def test_palette_widget_creates_64_buttons(qapp):
    palette = ColorPalette()
    assert len(palette.buttons) == 64


def test_click_color_emits_signal(qapp, qtbot):
    palette = ColorPalette()
    signals = []
    palette.color_selected.connect(signals.append)
    from PyQt6.QtCore import Qt
    qtbot.mouseClick(palette.buttons[3], Qt.MouseButton.LeftButton)
    assert signals == [3]


def test_mark_active_color(qapp):
    palette = ColorPalette()
    palette.set_active_color(5)
    assert "border: 2px solid" in palette.buttons[5].styleSheet()
