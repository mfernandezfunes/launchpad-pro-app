from __future__ import annotations
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton

# Paleta completa de 128 colores del Launchpad Mini MK2 / Pro
# Índice (velocity 0-127) → hex RGB aproximado según Novation Programmer's Reference
LP_COLORS: dict[int, str] = {
    0: "#000000", 1: "#1C1C1C", 2: "#7C7C7C", 3: "#FCFCFC",
    4: "#FF4E48", 5: "#FE0A00", 6: "#590000", 7: "#190000",
    8: "#FFBC63", 9: "#FF5700", 10: "#591D00", 11: "#271B00",
    12: "#FDFD21", 13: "#FDFD00", 14: "#585800", 15: "#181800",
    16: "#81FD2B", 17: "#40FD00", 18: "#165800", 19: "#132B00",
    20: "#34FD2B", 21: "#00FD00", 22: "#005800", 23: "#001800",
    24: "#33FD46", 25: "#00FD00", 26: "#005800", 27: "#001800",
    28: "#32FD7E", 29: "#00FD3A", 30: "#005814", 31: "#001C0F",
    32: "#2FFCB0", 33: "#00FC6E", 34: "#005831", 35: "#001810",
    36: "#39BEF8", 37: "#00A7F9", 38: "#004051", 39: "#001018",
    40: "#4186F8", 41: "#0050F9", 42: "#001A59", 43: "#000819",
    44: "#4747F8", 45: "#0000F9", 46: "#000058", 47: "#000018",
    48: "#8347F8", 49: "#5000F9", 50: "#1A0059", 51: "#0F0030",
    52: "#FF48FE", 53: "#FF00FE", 54: "#590058", 55: "#190018",
    56: "#FF4E83", 57: "#FF0753", 58: "#59001C", 59: "#220013",
    60: "#FF1500", 61: "#993500", 62: "#795100", 63: "#436400",
    64: "#033900", 65: "#005735", 66: "#00547E", 67: "#0000FE",
    68: "#00454F", 69: "#2500CC", 70: "#7F7F7F", 71: "#202020",
    72: "#FF0A00", 73: "#BAFD00", 74: "#AAED00", 75: "#56FD00",
    76: "#008800", 77: "#00FC7A", 78: "#00A7F9", 79: "#001AFE",
    80: "#3500FF", 81: "#7800FF", 82: "#B4177E", 83: "#412000",
    84: "#FF4A00", 85: "#82E100", 86: "#66FD00", 87: "#00FD00",
    88: "#00FD00", 89: "#45FD61", 90: "#00FCCA", 91: "#5086F9",
    92: "#274DC8", 93: "#847ADE", 94: "#D30CFF", 95: "#FF065A",
    96: "#FF7900", 97: "#E8FF00", 98: "#7BFF00", 99: "#01FF24",
    100: "#3FFF7F", 101: "#35FFAF", 102: "#25E7FF", 103: "#8498FF",
    104: "#7291FF", 105: "#B35AFF", 106: "#EB50FF", 107: "#FF1A70",
    108: "#FF6E22", 109: "#E8FF3A", 110: "#B6FF58", 111: "#5AFF54",
    112: "#6AFF96", 113: "#6AFFC2", 114: "#77E3FF", 115: "#A2C1FF",
    116: "#8C98FF", 117: "#9E73FF", 118: "#FF55FF", 119: "#FF3E7D",
    120: "#FF8547", 121: "#FFD215", 122: "#B4FF3D", 123: "#8FFF49",
    124: "#00FF00", 125: "#19FF5C", 126: "#03D8A7", 127: "#00FFD0",
}

# Subconjunto curado de colores distinguibles para el selector UI
# Cada valor es el índice MIDI real que se envía al hardware
CURATED_COLORS: list[int] = [
    0,          # off/negro
    3,          # blanco
    5,          # rojo
    72,         # rojo brillante
    9,          # naranja
    84,         # naranja brillante
    96,         # naranja claro
    12,         # amarillo
    13,         # amarillo puro
    121,        # amarillo dorado
    17,         # verde lima
    21,         # verde
    76,         # verde oscuro
    124,        # verde brillante
    33,         # verde menta
    125,        # verde esmeralda
    126,        # turquesa
    90,         # cyan
    78,         # cyan claro
    37,         # azul claro
    41,         # azul
    45,         # azul puro
    67,         # azul intenso
    79,         # azul profundo
    92,         # azul marino
    49,         # violeta
    81,         # púrpura
    69,         # púrpura oscuro
    94,         # magenta
    53,         # fucsia
    118,        # rosa
    57,         # rosa fuerte
    95,         # rosa rojo
    82,         # borgoña
    2,          # gris
    70,         # gris medio
    71,         # gris oscuro
]


class ColorPalette(QWidget):
    color_selected = pyqtSignal(int)  # índice de color MIDI (0-127)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._active_color: int | None = None
        self.buttons: dict[int, QPushButton] = {}
        layout = QGridLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(2, 2, 2, 2)
        cols = 6
        for pos, color_idx in enumerate(CURATED_COLORS):
            row, col = divmod(pos, cols)
            btn = QPushButton()
            btn.setFixedSize(20, 20)
            hex_c = LP_COLORS.get(color_idx, "#000000")
            btn.setStyleSheet(
                f"background-color: {hex_c}; border: 1px solid #333; border-radius: 2px;"
            )
            btn.clicked.connect(lambda _, i=color_idx: self._on_click(i))
            layout.addWidget(btn, row, col)
            self.buttons[color_idx] = btn

    def _on_click(self, index: int) -> None:
        self.set_active_color(index)
        self.color_selected.emit(index)

    def set_active_color(self, index: int) -> None:
        if self._active_color is not None:
            prev = self._active_color
            hex_c = LP_COLORS.get(prev, "#000000")
            if prev in self.buttons:
                self.buttons[prev].setStyleSheet(
                    f"background-color: {hex_c}; border: 1px solid #333; border-radius: 2px;"
                )
        self._active_color = index
        hex_c = LP_COLORS.get(index, "#000000")
        if index in self.buttons:
            self.buttons[index].setStyleSheet(
                f"background-color: {hex_c}; border: 2px solid #ffffff; border-radius: 2px;"
            )
