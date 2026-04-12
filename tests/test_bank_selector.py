import pytest
from ui.bank_selector import BankSelector


@pytest.fixture
def selector(qapp):
    return BankSelector(names=["A", "B", "C"])


def test_shows_initial_banks(selector):
    assert selector.count() == 3


def test_add_bank(selector):
    selector.add_bank("D")
    assert selector.count() == 4


def test_bank_change_emits_signal(selector, qtbot):
    signals = []
    selector.bank_changed.connect(signals.append)
    selector.setCurrentIndex(1)
    assert 1 in signals


def test_active_bank_index(selector):
    selector.setCurrentIndex(2)
    assert selector.active_bank == 2
