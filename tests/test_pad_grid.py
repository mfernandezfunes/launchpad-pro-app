import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from ui.pad_grid import PadGrid

LP_COLORS = {0: "#000000", 3: "#FF0000", 5: "#00FF00", 9: "#FFFF00"}


@pytest.fixture
def grid(qapp):
    g = PadGrid(color_palette=LP_COLORS)
    return g


def test_grid_creates_64_buttons(grid):
    assert len(grid.buttons) == 64


def test_pad_without_config_appears_dark(grid):
    # pad (0,0) → sin config → color oscuro (#1a1a1a)
    btn = grid.buttons[(0, 0)]
    assert "1a1a1a" in btn.styleSheet().lower() or "background" in btn.styleSheet()


def test_set_pad_color_updates_button(grid):
    grid.set_pad_color(row=0, col=0, color=3)
    btn = grid.buttons[(0, 0)]
    assert "ff0000" in btn.styleSheet().lower()


def test_click_pad_emits_signal(grid, qtbot):
    signals = []
    grid.pad_selected.connect(lambda r, c: signals.append((r, c)))
    btn = grid.buttons[(2, 3)]
    qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
    assert signals == [(2, 3)]


def test_select_pad_marks_border(grid):
    grid.select(row=1, col=2)
    btn = grid.buttons[(1, 2)]
    assert "border" in btn.styleSheet()
