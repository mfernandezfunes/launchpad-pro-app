from __future__ import annotations
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QTabBar


class BankSelector(QTabBar):
    bank_changed = pyqtSignal(int)

    def __init__(self, names: list[str], parent=None) -> None:
        super().__init__(parent)
        for name in names:
            self.addTab(name)
        self.currentChanged.connect(self.bank_changed)

    def add_bank(self, name: str) -> None:
        self.addTab(name)

    @property
    def active_bank(self) -> int:
        return self.currentIndex()
