from ui.about_dialog import AboutDialog


def test_shows_developer(qapp):
    d = AboutDialog(connected_device="Sin conexión")
    assert "Martin Fernandez Funes" in d.label_info.text()


def test_shows_connected_device(qapp):
    d = AboutDialog(connected_device="Launchpad Mini MK2")
    assert "Launchpad Mini MK2" in d.label_info.text()


def test_shows_no_connection(qapp):
    d = AboutDialog(connected_device="Sin conexión")
    assert "Sin conexión" in d.label_info.text()
