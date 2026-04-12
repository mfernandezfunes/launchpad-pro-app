from __future__ import annotations
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton

# Paleta nativa Launchpad Mini MK2: índice (velocity) → hex RGB aproximado
LP_COLORS: dict[int, str] = {
    0: "#000000", 1: "#1E1E1E", 2: "#7F7F7F", 3: "#FFFFFF",
    4: "#FF4D4D", 5: "#FF0000", 6: "#590000", 7: "#170000",
    8: "#FFBD6E", 9: "#FF5400", 10: "#591D00", 11: "#271B00",
    12: "#FFFF4D", 13: "#FFFF00", 14: "#595900", 15: "#171700",
    16: "#88FF4D", 17: "#54FF00", 18: "#1D5900", 19: "#142B00",
    20: "#4DFF4D", 21: "#00FF00", 22: "#005900", 23: "#001700",
    24: "#4DFF5E", 25: "#00FF19", 26: "#00590D", 27: "#001702",
    28: "#4DFF88", 29: "#00FF55", 30: "#00591D", 31: "#001711",
    32: "#4DFFB8", 33: "#00FF99", 34: "#005935", 35: "#001718",
    36: "#4DC3FF", 37: "#00A9FF", 38: "#004152", 39: "#001019",
    40: "#4D83FF", 41: "#0055FF", 42: "#001D59", 43: "#000819",
    44: "#4D4DFF", 45: "#0000FF", 46: "#000059", 47: "#000019",
    48: "#874DFF", 49: "#5400FF", 50: "#190064", 51: "#0F0030",
    52: "#FF4DFF", 53: "#FF00FF", 54: "#590059", 55: "#190019",
    56: "#FF4D87", 57: "#FF0054", 58: "#59001C", 59: "#220013",
    60: "#FF1500", 61: "#993500", 62: "#795100", 63: "#436400",
}


class ColorPalette(QWidget):
    color_selected = pyqtSignal(int)  # índice de color (0-63)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._active_color: int | None = None
        self.buttons: dict[int, QPushButton] = {}
        layout = QGridLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(2, 2, 2, 2)
        for idx in range(64):
            row, col = divmod(idx, 8)
            btn = QPushButton()
            btn.setFixedSize(22, 22)
            hex_c = LP_COLORS.get(idx, "#000000")
            btn.setStyleSheet(
                f"background-color: {hex_c}; border: 1px solid #333; border-radius: 2px;"
            )
            btn.clicked.connect(lambda _, i=idx: self._on_click(i))
            layout.addWidget(btn, row, col)
            self.buttons[idx] = btn

    def _on_click(self, index: int) -> None:
        self.set_active_color(index)
        self.color_selected.emit(index)

    def set_active_color(self, index: int) -> None:
        if self._active_color is not None:
            prev = self._active_color
            hex_c = LP_COLORS.get(prev, "#000000")
            self.buttons[prev].setStyleSheet(
                f"background-color: {hex_c}; border: 1px solid #333; border-radius: 2px;"
            )
        self._active_color = index
        hex_c = LP_COLORS.get(index, "#000000")
        self.buttons[index].setStyleSheet(
            f"background-color: {hex_c}; border: 2px solid #ffffff; border-radius: 2px;"
        )
