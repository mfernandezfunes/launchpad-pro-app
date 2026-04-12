import sys
from PyQt6.QtWidgets import QApplication
from engine.midi_engine import MidiEngine
from engine.audio_engine import AudioEngine
from models.project import Project
from ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Launchpad Mini MK2 Sampler")
    app.setOrganizationName("mfernandezfunes")

    project = Project.new()
    midi_engine = MidiEngine()
    audio_engine = AudioEngine()

    window = MainWindow(
        project=project,
        midi_engine=midi_engine,
        audio_engine=audio_engine,
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
