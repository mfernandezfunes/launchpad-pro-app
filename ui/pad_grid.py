from __future__ import annotations
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton


class PadGrid(QWidget):
    pad_selected = pyqtSignal(int, int)  # row, col

    def __init__(self, color_palette: dict[int, str], parent=None) -> None:
        super().__init__(parent)
        self._color_palette = color_palette
        self._current_colors: dict[tuple[int, int], int] = {}
        self._selected: tuple[int, int] | None = None
        self.buttons: dict[tuple[int, int], QPushButton] = {}
        layout = QGridLayout(self)
        layout.setSpacing(3)
        layout.setContentsMargins(4, 4, 4, 4)
        for row in range(8):
            for col in range(8):
                btn = QPushButton()
                btn.setFixedSize(44, 44)
                btn.setStyleSheet(self._pad_style(color=0, selected=False))
                btn.clicked.connect(lambda _, r=row, c=col: self._on_click(r, c))
                layout.addWidget(btn, row, col)
                self.buttons[(row, col)] = btn

    def set_pad_color(self, row: int, col: int, color: int) -> None:
        self._current_colors[(row, col)] = color
        selected = self._selected == (row, col)
        self.buttons[(row, col)].setStyleSheet(
            self._pad_style(color=color, selected=selected)
        )

    def select(self, row: int, col: int) -> None:
        if self._selected:
            r0, c0 = self._selected
            prev_color = self._current_colors.get((r0, c0), 0)
            self.buttons[(r0, c0)].setStyleSheet(
                self._pad_style(color=prev_color, selected=False)
            )
        self._selected = (row, col)
        color = self._current_colors.get((row, col), 0)
        self.buttons[(row, col)].setStyleSheet(
            self._pad_style(color=color, selected=True)
        )

    def _on_click(self, row: int, col: int) -> None:
        self.select(row, col)
        self.pad_selected.emit(row, col)

    def _pad_style(self, color: int, selected: bool) -> str:
        hex_color = self._color_palette.get(color, "#1a1a1a")
        border = "2px solid #ffffff" if selected else "1px solid #333333"
        return (
            f"background-color: {hex_color};"
            f"border: {border};"
            f"border-radius: 4px;"
        )
