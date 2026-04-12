from __future__ import annotations
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QTabBar

BANK_NAMES = list("ABCDEFGH")
MAX_BANKS = 8


class BankSelector(QTabBar):
    bank_changed = pyqtSignal(int)
    add_bank_requested = pyqtSignal()

    def __init__(self, names: list[str], parent=None) -> None:
        super().__init__(parent)
        self._bank_count = 0
        for name in names:
            self.addTab(name)
            self._bank_count += 1
        self._update_plus_tab()
        self.currentChanged.connect(self._on_tab_changed)

    def add_bank(self, name: str) -> None:
        self.blockSignals(True)
        self.removeTab(self.count() - 1)  # quitar "+"
        self.addTab(name)
        self._bank_count += 1
        self._update_plus_tab()
        self.blockSignals(False)

    def _update_plus_tab(self) -> None:
        if self._bank_count < MAX_BANKS:
            self.addTab("+")

    def _on_tab_changed(self, index: int) -> None:
        if self._bank_count < MAX_BANKS and index == self.count() - 1:
            self.add_bank_requested.emit()
        else:
            self.bank_changed.emit(index)

    @property
    def active_bank(self) -> int:
        return self.currentIndex()
