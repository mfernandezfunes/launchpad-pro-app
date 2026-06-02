import pytest
from ui.color_palette import ColorPalette, LP_COLORS, CURATED_COLORS


def test_palette_has_128_entries():
    assert len(LP_COLORS) == 128


def test_color_0_is_black():
    assert LP_COLORS[0].lower() == "#000000"


def test_palette_widget_creates_curated_buttons(qapp):
    palette = ColorPalette()
    assert len(palette.buttons) == len(CURATED_COLORS)


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
