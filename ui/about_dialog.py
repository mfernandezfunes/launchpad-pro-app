from __future__ import annotations
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

VERSION = "1.0.0"


class AboutDialog(QDialog):
    def __init__(self, connected_device: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Acerca de")
        self.setFixedWidth(320)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        title = QLabel("<h2>Launchpad Mini MK2 Sampler</h2>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.label_info = QLabel(
            f"<p><b>Versión:</b> {VERSION}</p>"
            f"<p><b>Controladora:</b> {connected_device}</p>"
            f"<p><b>Desarrollado por:</b> Martin Fernandez Funes</p>"
        )
        self.label_info.setWordWrap(True)
        self.label_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_info)

        btn = QPushButton("Cerrar")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
