import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtCore import QByteArray
from engine.midi_engine import MidiEngine
from engine.audio_engine import AudioEngine
from models.project import Project
from ui.main_window import MainWindow

APP_KEY = "com.mfernandezfunes.launchpad-sampler"


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Launchpad Mini MK2 Sampler")
    app.setOrganizationName("mfernandezfunes")

    # Singleton: si ya hay una instancia, activarla y salir
    socket = QLocalSocket()
    socket.connectToServer(APP_KEY)
    if socket.waitForConnected(500):
        socket.write(QByteArray(b"activate"))
        socket.flush()
        socket.waitForBytesWritten(1000)
        socket.disconnectFromServer()
        sys.exit(0)

    server = QLocalServer()
    QLocalServer.removeServer(APP_KEY)
    server.listen(APP_KEY)

    project = Project.new()
    midi_engine = MidiEngine()
    audio_engine = AudioEngine()

    window = MainWindow(
        project=project,
        midi_engine=midi_engine,
        audio_engine=audio_engine,
    )
    window.show()

    def on_new_connection():
        conn = server.nextPendingConnection()
        if conn:
            window.raise_()
            window.activateWindow()
            conn.disconnectFromServer()

    server.newConnection.connect(on_new_connection)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
