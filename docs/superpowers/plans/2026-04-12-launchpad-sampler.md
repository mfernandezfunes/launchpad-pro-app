# Launchpad Mini MK2 Sampler — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir una app de escritorio standalone (Windows + macOS) en español que convierte el Novation Launchpad Mini MK2 en un sampler configurable con colores por pad, múltiples bancos y feedback visual vía LEDs.

**Architecture:** PyQt6 para la UI, python-rtmidi para comunicación MIDI bidireccional con el LP Mini MK2, y sounddevice+soundfile para reproducción de audio. La app se divide en: capa de modelos (dataclasses puras), motores (MIDI + audio, sin dependencia de UI), y widgets PyQt6 que orquestan todo.

**Tech Stack:** Python 3.11+, PyQt6 6.6+, python-rtmidi 1.5+, sounddevice 0.4+, soundfile 0.12+, pytest, PyInstaller 6+

---

## Mapa de archivos

| Archivo | Responsabilidad |
|---|---|
| `main.py` | Punto de entrada, inicializa QApplication y MainWindow |
| `models/project.py` | Dataclasses: PadConfig, Bank, Settings, Project |
| `config/project_file.py` | Serialización/deserialización JSON (.lpsampler) |
| `engine/audio_engine.py` | Reproducción de audio con sounddevice (modos: oneshot, loop, toggle) |
| `engine/midi_engine.py` | Conexión MIDI, recepción de note_on, envío de colores y parpadeo |
| `ui/pad_grid.py` | Widget 8x8 grid de pads con colores y selección visual |
| `ui/bank_selector.py` | Tabs A-H para seleccionar banco activo |
| `ui/pad_config_panel.py` | Panel derecho: paleta de colores + selector de audio (y panel de ajustes) |
| `ui/pad_config_dialog.py` | Diálogo de asignación de audio + color (para Modo Asignación) |
| `ui/about_dialog.py` | Diálogo "Acerca de" con info de app y developer |
| `ui/main_window.py` | Ventana principal: orquesta todos los widgets, Modo Asignación, menú |
| `tests/conftest.py` | Fixtures de pytest: QApplication, proyecto de prueba |
| `launchpad-sampler.spec` | Configuración de PyInstaller |

## Referencia: MIDI Launchpad Mini MK2

```
Notas del grid 8x8:
  Fila visual 0 (arriba):  81, 82, 83, 84, 85, 86, 87, 88
  Fila visual 1:           71, 72, 73, 74, 75, 76, 77, 78
  ...
  Fila visual 7 (abajo):   11, 12, 13, 14, 15, 16, 17, 18

Botones de escena (fila superior del LP, CC 104-111):
  CC 104 = Banco A, CC 105 = Banco B, ..., CC 111 = Banco H

Colores:
  Ch 1 (0x90): color estático — velocity = índice de color (0=apagado, 1-63)
  Ch 2 (0x91): color titilante — velocity = índice de color
```

---

## Tarea 1: Setup del proyecto

**Archivos:**
- Crear: `pyproject.toml`
- Crear: `.gitignore`
- Crear: `README.md`
- Crear: `models/__init__.py`, `engine/__init__.py`, `ui/__init__.py`, `config/__init__.py`, `tests/__init__.py`

- [ ] **Paso 1: Inicializar git y estructura de directorios**

```bash
cd /Users/martin.fernandez/Documents/repos_personal/launchpad-pro-app
git init
git remote add origin git@github.com:mfernandezfunes/launchpad-pro-app.git
mkdir -p models engine ui config tests
touch models/__init__.py engine/__init__.py ui/__init__.py config/__init__.py tests/__init__.py
```

- [ ] **Paso 2: Crear pyproject.toml**

```toml
[project]
name = "launchpad-sampler"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "PyQt6>=6.6",
    "python-rtmidi>=1.5",
    "sounddevice>=0.4",
    "soundfile>=0.12",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-qt>=4.4",
]

[build-system]
build-backend = "setuptools.build_meta"
requires = ["setuptools>=68"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Paso 3: Crear .gitignore**

```
__pycache__/
*.pyc
*.pyo
.venv/
venv/
dist/
build/
*.spec.bak
.DS_Store
*.lpsampler
```

- [ ] **Paso 4: Crear README.md**

```markdown
# Launchpad Mini MK2 Sampler

App de escritorio standalone para configurar el Novation Launchpad Mini MK2 como sampler de audio.

![Novation Launchpad Mini MK2](https://http2.mlstatic.com/D_NQ_NP_2X_674503-MLU72636681781_112023-F.webp)

## Instalación

```bash
pip install -e ".[dev]"
```

## Uso

```bash
python main.py
```

## Desarrollado por

Martin Fernandez Funes
```

- [ ] **Paso 5: Instalar dependencias**

```bash
pip install -e ".[dev]"
```

Verificar: `python -c "import PyQt6; import rtmidi; import sounddevice; import soundfile; print('OK')`

- [ ] **Paso 6: Commit inicial**

```bash
git add pyproject.toml .gitignore README.md models/ engine/ ui/ config/ tests/
git commit -S -m "chore: setup inicial del proyecto"
```

---

## Tarea 2: Modelos de datos

**Archivos:**
- Crear: `models/project.py`
- Crear: `tests/test_models.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_models.py`:

```python
from models.project import PadConfig, Bank, Settings, Project


def test_pad_config_defaults():
    pad = PadConfig(audio_file="/path/kick.wav", color=3)
    assert pad.audio_file == "/path/kick.wav"
    assert pad.color == 3


def test_bank_empty_pads():
    bank = Bank(name="A")
    assert bank.pads == {}


def test_bank_add_pad():
    bank = Bank(name="A")
    bank.pads[11] = PadConfig(audio_file="/path/snare.wav", color=5)
    assert 11 in bank.pads
    assert bank.pads[11].color == 5


def test_project_initial_banks():
    project = Project.new()
    assert len(project.banks) == 1
    assert project.banks[0].name == "A"


def test_project_active_bank():
    project = Project.new()
    assert project.active_bank_index == 0


def test_settings_play_mode():
    settings = Settings(
        midi_input="",
        midi_output="",
        audio_output="",
        volume=0.8,
        play_mode="oneshot",
    )
    assert settings.play_mode == "oneshot"
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_models.py -v
```

Esperado: `ModuleNotFoundError: No module named 'models.project'`

- [ ] **Paso 3: Implementar models/project.py**

```python
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class PadConfig:
    audio_file: str
    color: int  # velocidad MIDI 1-63, 0 = apagado


@dataclass
class Bank:
    name: str
    pads: dict[int, PadConfig] = field(default_factory=dict)


@dataclass
class Settings:
    midi_input: str
    midi_output: str
    audio_output: str
    volume: float  # 0.0-1.0
    play_mode: str  # "oneshot" | "loop" | "toggle"


@dataclass
class Project:
    banks: list[Bank]
    settings: Settings
    active_bank_index: int = 0

    @classmethod
    def new(cls) -> Project:
        return cls(
            banks=[Bank(name="A")],
            settings=Settings(
                midi_input="",
                midi_output="",
                audio_output="",
                volume=0.8,
                play_mode="oneshot",
            ),
        )

    @property
    def active_bank(self) -> Bank:
        return self.banks[self.active_bank_index]
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_models.py -v
```

Esperado: 6 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add models/project.py tests/test_models.py
git commit -S -m "feat: data models (PadConfig, Bank, Settings, Project)"
```

---

## Tarea 3: Serialización del proyecto (JSON)

**Archivos:**
- Crear: `config/project_file.py`
- Crear: `tests/test_project_file.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_project_file.py`:

```python
import json
import pytest
from pathlib import Path
from models.project import PadConfig, Bank, Settings, Project
from config.project_file import save_project, load_project


@pytest.fixture
def project_with_pads():
    p = Project.new()
    p.banks[0].pads[11] = PadConfig(audio_file="/audio/kick.wav", color=3)
    p.banks[0].pads[12] = PadConfig(audio_file="/audio/snare.wav", color=5)
    return p


def test_save_and_load_roundtrip(tmp_path, project_with_pads):
    path = tmp_path / "test.lpsampler"
    save_project(project_with_pads, path)
    loaded = load_project(path)
    assert loaded.banks[0].name == "A"
    assert loaded.banks[0].pads[11].audio_file == "/audio/kick.wav"
    assert loaded.banks[0].pads[11].color == 3
    assert loaded.settings.volume == pytest.approx(0.8)
    assert loaded.settings.play_mode == "oneshot"


def test_file_is_valid_json(tmp_path, project_with_pads):
    path = tmp_path / "test.lpsampler"
    save_project(project_with_pads, path)
    content = json.loads(path.read_text())
    assert "banks" in content
    assert "settings" in content


def test_load_missing_file_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_project(tmp_path / "missing.lpsampler")


def test_multiple_banks_roundtrip(tmp_path):
    p = Project.new()
    p.banks.append(Bank(name="B"))
    p.banks[1].pads[21] = PadConfig(audio_file="/audio/hihat.wav", color=9)
    path = tmp_path / "test.lpsampler"
    save_project(p, path)
    loaded = load_project(path)
    assert len(loaded.banks) == 2
    assert loaded.banks[1].pads[21].audio_file == "/audio/hihat.wav"
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_project_file.py -v
```

Esperado: `ModuleNotFoundError: No module named 'config.project_file'`

- [ ] **Paso 3: Implementar config/project_file.py**

```python
from __future__ import annotations
import json
from pathlib import Path
from models.project import PadConfig, Bank, Settings, Project


def save_project(project: Project, path: Path) -> None:
    data = {
        "active_bank_index": project.active_bank_index,
        "banks": [
            {
                "name": bank.name,
                "pads": {
                    str(note): {"audio_file": pad.audio_file, "color": pad.color}
                    for note, pad in bank.pads.items()
                },
            }
            for bank in project.banks
        ],
        "settings": {
            "midi_input": project.settings.midi_input,
            "midi_output": project.settings.midi_output,
            "audio_output": project.settings.audio_output,
            "volume": project.settings.volume,
            "play_mode": project.settings.play_mode,
        },
    }
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False))


def load_project(path: Path) -> Project:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")
    data = json.loads(path.read_text())
    banks = [
        Bank(
            name=b["name"],
            pads={
                int(note): PadConfig(
                    audio_file=pad["audio_file"],
                    color=pad["color"],
                )
                for note, pad in b["pads"].items()
            },
        )
        for b in data["banks"]
    ]
    a = data["settings"]
    settings = Settings(
        midi_input=a["midi_input"],
        midi_output=a["midi_output"],
        audio_output=a["audio_output"],
        volume=a["volume"],
        play_mode=a["play_mode"],
    )
    return Project(
        banks=banks,
        settings=settings,
        active_bank_index=data.get("active_bank_index", 0),
    )
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_project_file.py -v
```

Esperado: 4 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add config/project_file.py tests/test_project_file.py
git commit -S -m "feat: project serialization to JSON (.lpsampler)"
```

---

## Tarea 4: Motor de audio

**Archivos:**
- Crear: `engine/audio_engine.py`
- Crear: `tests/test_audio_engine.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_audio_engine.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
from engine.audio_engine import AudioEngine


@pytest.fixture
def engine():
    with patch("engine.audio_engine.sd") as mock_sd, \
         patch("engine.audio_engine.sf") as mock_sf:
        mock_sf.read.return_value = ([0.0, 0.1, 0.2], 44100)
        yield AudioEngine(), mock_sd, mock_sf


def test_play_oneshot_calls_play(engine):
    m, mock_sd, mock_sf = engine
    m.play("/audio/kick.wav", volume=0.8, mode="oneshot", pad_id=11,
           on_complete=None)
    mock_sd.play.assert_called_once()


def test_play_adjusts_volume(engine):
    m, mock_sd, mock_sf = engine
    m.play("/audio/kick.wav", volume=0.5, mode="oneshot", pad_id=11,
           on_complete=None)
    args, kwargs = mock_sd.play.call_args
    # el primer argumento es el array de audio * volume
    import numpy as np
    assert args[0].max() <= 0.5 * 1.1  # tolerancia


def test_stop_pad(engine):
    m, mock_sd, _ = engine
    m.play("/audio/kick.wav", volume=1.0, mode="loop", pad_id=11,
           on_complete=None)
    m.stop(pad_id=11)
    mock_sd.stop.assert_called()


def test_play_missing_file_does_not_raise(engine):
    m, mock_sd, mock_sf = engine
    mock_sf.read.side_effect = FileNotFoundError
    # No debe propagar la excepción
    m.play("/no/existe.wav", volume=1.0, mode="oneshot", pad_id=99,
           on_complete=None)
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_audio_engine.py -v
```

Esperado: `ModuleNotFoundError: No module named 'engine.audio_engine'`

- [ ] **Paso 3: Implementar engine/audio_engine.py**

```python
from __future__ import annotations
import logging
import threading
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
import soundfile as sf

logger = logging.getLogger(__name__)


class AudioEngine:
    def __init__(self) -> None:
        self._active: dict[int, threading.Thread] = {}
        self._stop_flags: dict[int, threading.Event] = {}

    def play(
        self,
        audio_file: str,
        volume: float,
        mode: str,
        pad_id: int,
        on_complete: Optional[Callable[[int], None]],
        device: Optional[str] = None,
    ) -> None:
        """Reproduce audio para un pad. mode: 'oneshot' | 'loop' | 'toggle'"""
        if mode == "toggle" and pad_id in self._active:
            self.stop(pad_id)
            return

        self.stop(pad_id)
        flag = threading.Event()
        self._stop_flags[pad_id] = flag

        thread = threading.Thread(
            target=self._play_thread,
            args=(audio_file, volume, mode, pad_id, flag, on_complete, device),
            daemon=True,
        )
        self._active[pad_id] = thread
        thread.start()

    def _play_thread(
        self,
        audio_file: str,
        volume: float,
        mode: str,
        pad_id: int,
        flag: threading.Event,
        on_complete: Optional[Callable[[int], None]],
        device: Optional[str],
    ) -> None:
        try:
            data, samplerate = sf.read(audio_file, dtype="float32")
            data = data * volume
            kwargs: dict = {"samplerate": samplerate}
            if device:
                kwargs["device"] = device
            while not flag.is_set():
                sd.play(data, **kwargs)
                sd.wait()
                if mode != "loop" or flag.is_set():
                    break
        except FileNotFoundError:
            logger.warning("Archivo de audio no encontrado: %s", audio_file)
        except Exception as e:
            logger.error("Error reproduciendo %s: %s", audio_file, e)
        finally:
            self._active.pop(pad_id, None)
            self._stop_flags.pop(pad_id, None)
            if on_complete:
                on_complete(pad_id)

    def stop(self, pad_id: int) -> None:
        flag = self._stop_flags.get(pad_id)
        if flag:
            flag.set()
            sd.stop()

    def stop_all(self) -> None:
        for pad_id in list(self._stop_flags):
            self.stop(pad_id)

    def is_playing(self, pad_id: int) -> bool:
        return pad_id in self._active
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_audio_engine.py -v
```

Esperado: 4 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add engine/audio_engine.py tests/test_audio_engine.py
git commit -S -m "feat: audio engine with oneshot, loop and toggle modes"
```

---

## Tarea 5: Motor MIDI

**Archivos:**
- Crear: `engine/midi_engine.py`
- Crear: `tests/test_midi_engine.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_midi_engine.py`:

```python
import pytest
from unittest.mock import patch, MagicMock, call
from engine.midi_engine import MidiEngine, pad_to_note, note_to_pad, SCENE_NOTES


def test_pad_to_note_top_left_corner():
    # Fila visual 0 (arriba), col 0 → nota MIDI 81
    assert pad_to_note(0, 0) == 81


def test_pad_to_note_bottom_right_corner():
    # Fila visual 7 (abajo), col 7 → nota MIDI 18
    assert pad_to_note(7, 7) == 18


def test_note_to_pad_roundtrip():
    for row in range(8):
        for col in range(8):
            note = pad_to_note(row, col)
            r2, c2 = note_to_pad(note)
            assert (r2, c2) == (row, col)


def test_scene_notes_are_8():
    assert len(SCENE_NOTES) == 8


def test_list_midi_devices_calls_rtmidi():
    with patch("engine.midi_engine.rtmidi.MidiIn") as mock_in:
        mock_in.return_value.get_ports.return_value = ["Launchpad Mini", "otro"]
        from engine.midi_engine import list_midi_devices
        devices = list_midi_devices()
        assert "Launchpad Mini" in devices


def test_connect_detects_launchpad():
    engine = MidiEngine()
    with patch.object(engine, "_midi_in") as mock_in, \
         patch.object(engine, "_midi_out") as mock_out:
        mock_in.get_ports.return_value = ["Launchpad Mini MK2", "otro"]
        mock_out.get_ports.return_value = ["Launchpad Mini MK2", "otro"]
        result = engine.connect()
        assert result is True


def test_set_pad_color_sends_note_on():
    engine = MidiEngine()
    mock_out = MagicMock()
    engine._midi_out = mock_out
    engine._connected = True
    engine.set_pad_color(pad_id=11, color=3)
    # note_on ch1 (0x90), nota 11, velocity 3
    mock_out.send_message.assert_called_with([0x90, 11, 3])


def test_set_pad_color_turns_off_with_0():
    engine = MidiEngine()
    mock_out = MagicMock()
    engine._midi_out = mock_out
    engine._connected = True
    engine.set_pad_color(pad_id=11, color=0)
    mock_out.send_message.assert_called_with([0x90, 11, 0])
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_midi_engine.py -v
```

Esperado: `ModuleNotFoundError: No module named 'engine.midi_engine'`

- [ ] **Paso 3: Implementar engine/midi_engine.py**

```python
from __future__ import annotations
import logging
import threading
import time
from typing import Callable, Optional

import rtmidi

logger = logging.getLogger(__name__)

# Notas de escena: CC 104-111 (fila superior del LP Mini MK2)
SCENE_NOTES = list(range(104, 112))


def pad_to_note(row: int, col: int) -> int:
    """Convierte posición visual del grid (row 0=arriba) a nota MIDI."""
    midi_row = 8 - row  # fila visual 0 → fila MIDI 8 (notas 81-88)
    return midi_row * 10 + (col + 1)


def note_to_pad(note: int) -> tuple[int, int]:
    """Convierte nota MIDI a posición visual del grid (row 0=arriba)."""
    midi_row = note // 10
    col = (note % 10) - 1
    row = 8 - midi_row
    return row, col


def list_midi_devices() -> list[str]:
    midi_in = rtmidi.MidiIn()
    return midi_in.get_ports()


class MidiEngine:
    def __init__(self) -> None:
        self._midi_in = rtmidi.MidiIn()
        self._midi_out = rtmidi.MidiOut()
        self._connected = False
        self._callback_pad: Optional[Callable[[int], None]] = None
        self._callback_scene: Optional[Callable[[int], None]] = None
        self._blinks: dict[int, threading.Event] = {}

    def connect(self, device_name: str = "Launchpad") -> bool:
        ports_in = self._midi_in.get_ports()
        ports_out = self._midi_out.get_ports()
        idx_in = next(
            (i for i, p in enumerate(ports_in) if device_name.lower() in p.lower()),
            None,
        )
        idx_out = next(
            (i for i, p in enumerate(ports_out) if device_name.lower() in p.lower()),
            None,
        )
        if idx_in is None or idx_out is None:
            logger.warning("Launchpad no encontrado en puertos MIDI")
            return False
        self._midi_in.open_port(idx_in)
        self._midi_out.open_port(idx_out)
        self._midi_in.set_callback(self._on_message)
        self._connected = True
        logger.info("Launchpad conectado: %s", ports_in[idx_in])
        return True

    def disconnect(self) -> None:
        self.stop_all_blinks()
        if self._midi_in.is_port_open():
            self._midi_in.close_port()
        if self._midi_out.is_port_open():
            self._midi_out.close_port()
        self._connected = False

    def set_callback_pad(self, callback: Callable[[int], None]) -> None:
        """callback(pad_id: int) llamado al presionar un pad del grid."""
        self._callback_pad = callback

    def set_callback_scene(self, callback: Callable[[int], None]) -> None:
        """callback(bank_index: int) llamado al presionar botón de escena."""
        self._callback_scene = callback

    def set_pad_color(self, pad_id: int, color: int) -> None:
        """Envía color estático a un pad. color=0 apaga."""
        if not self._connected:
            return
        self._midi_out.send_message([0x90, pad_id, color])

    def start_blink(self, pad_id: int, color: int) -> None:
        """Hace parpadear un pad usando canal 2 (0x91) del LP Mini MK2."""
        if not self._connected:
            return
        self.stop_blink(pad_id)
        self._midi_out.send_message([0x91, pad_id, color])

    def stop_blink(self, pad_id: int, color: int = 0) -> None:
        """Detiene el parpadeo y restaura color estático."""
        if not self._connected:
            return
        self._midi_out.send_message([0x90, pad_id, color])

    def stop_all_blinks(self) -> None:
        for flag in self._blinks.values():
            flag.set()
        self._blinks.clear()

    def set_scene_color(self, bank_index: int, color: int) -> None:
        """Envía color a un botón de escena (CC 104-111)."""
        if not self._connected:
            return
        cc = 104 + bank_index
        self._midi_out.send_message([0xB0, cc, color])

    def update_bank_leds(self, bank, active_bank_index: int, all_banks: list) -> None:
        """Actualiza todos los LEDs del LP para el banco dado."""
        # Apagar todos los pads del grid
        for row in range(8):
            for col in range(8):
                note = pad_to_note(row, col)
                self.set_pad_color(note, 0)
        # Iluminar pads del banco activo
        for note, pad_config in bank.pads.items():
            self.set_pad_color(note, pad_config.color)
        # Actualizar botones de escena
        for i, b in enumerate(all_banks):
            if i == active_bank_index:
                self.start_scene_blink(i, color=3)  # titila verde
            elif b.pads:
                self.set_scene_color(i, color=1)  # iluminado fijo bajo
            else:
                self.set_scene_color(i, color=0)  # apagado

    def start_scene_blink(self, bank_index: int, color: int) -> None:
        cc = 104 + bank_index
        if self._connected:
            self._midi_out.send_message([0xB1, cc, color])  # canal 2 = titila

    def _on_message(self, message, data=None) -> None:
        msg, _ = message
        status, note, velocity = msg[0], msg[1], msg[2]
        if velocity == 0:
            return
        channel = status & 0x0F
        msg_type = status & 0xF0
        if msg_type == 0x90 and channel == 0:  # note_on canal 1
            if 11 <= note <= 88 and note % 10 != 9:  # pad del grid
                if self._callback_pad:
                    self._callback_pad(note)
        elif msg_type == 0xB0:  # control change (botones de escena)
            if note in SCENE_NOTES and self._callback_scene:
                self._callback_scene(note - 104)

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def device_name(self) -> str:
        if not self._connected:
            return "Sin conexión"
        ports = self._midi_in.get_ports()
        return ports[0] if ports else "Desconocido"
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_midi_engine.py -v
```

Esperado: 8 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add engine/midi_engine.py tests/test_midi_engine.py
git commit -S -m "feat: MIDI engine — connection, colors, blink LP Mini MK2"
```

---

## Tarea 6: Fixtures de Qt para tests de UI

**Archivos:**
- Crear: `tests/conftest.py`

- [ ] **Paso 1: Crear conftest.py**

```python
import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
```

- [ ] **Paso 2: Verificar que pytest puede importar PyQt6**

```bash
pytest --collect-only 2>&1 | head -5
```

Esperado: sin errores de importación

- [ ] **Paso 3: Commit**

```bash
git add tests/conftest.py
git commit -S -m "test: QApplication fixture for UI tests"
```

---

## Tarea 7: Widget Grid de Pads

**Archivos:**
- Crear: `ui/pad_grid.py`
- Crear: `tests/test_pad_grid.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_pad_grid.py`:

```python
import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from ui.pad_grid import PadGrid

LP_COLORS = {0: "#000000", 3: "#FF0000", 5: "#00FF00", 9: "#FFFF00"}


@pytest.fixture
def grid(qapp):
    g = PadGrid(color_palette=LP_COLORS)
    return g


def test_grid_creates_64_buttons(grid):
    assert len(grid.buttons) == 64


def test_pad_without_config_appears_dark(grid):
    # pad (0,0) → sin config → color oscuro (#1a1a1a)
    btn = grid.buttons[(0, 0)]
    assert "1a1a1a" in btn.styleSheet().lower() or "background" in btn.styleSheet()


def test_set_pad_color_updates_button(grid):
    grid.set_pad_color(row=0, col=0, color=3)
    btn = grid.buttons[(0, 0)]
    assert "ff0000" in btn.styleSheet().lower()


def test_click_pad_emits_signal(grid, qtbot):
    signals = []
    grid.pad_selected.connect(lambda r, c: signals.append((r, c)))
    btn = grid.buttons[(2, 3)]
    qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
    assert signals == [(2, 3)]


def test_select_pad_marks_border(grid):
    grid.select(row=1, col=2)
    btn = grid.buttons[(1, 2)]
    assert "border" in btn.styleSheet()
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_pad_grid.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.pad_grid'`

- [ ] **Paso 3: Implementar ui/pad_grid.py**

```python
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
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_pad_grid.py -v
```

Esperado: 5 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add ui/pad_grid.py tests/test_pad_grid.py
git commit -S -m "feat: 8x8 pad grid widget with colors and selection"
```

---

## Tarea 8: Selector de bancos

**Archivos:**
- Crear: `ui/bank_selector.py`
- Crear: `tests/test_bank_selector.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_bank_selector.py`:

```python
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
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_bank_selector.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.bank_selector'`

- [ ] **Paso 3: Implementar ui/bank_selector.py**

```python
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
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_bank_selector.py -v
```

Esperado: 4 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add ui/bank_selector.py tests/test_bank_selector.py
git commit -S -m "feat: bank selector widget (tabs A-H)"
```

---

## Tarea 9: Paleta de colores LP Mini MK2

**Archivos:**
- Crear: `ui/color_palette.py`
- Crear: `tests/test_color_palette.py`

> Esta paleta es compartida por `pad_config_panel.py` y `pad_config_dialog.py`.

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_color_palette.py`:

```python
import pytest
from ui.color_palette import ColorPalette, LP_COLORS


def test_palette_has_64_entries():
    assert len(LP_COLORS) == 64


def test_color_0_is_black():
    assert LP_COLORS[0].lower() == "#000000"


def test_palette_widget_creates_64_buttons(qapp):
    palette = ColorPalette()
    assert len(palette.buttons) == 64


def test_click_color_emits_signal(qapp, qtbot):
    palette = ColorPalette()
    signals = []
    palette.color_selected.connect(signals.append)
    from PyQt6.QtCore import Qt
    qtbot.mouseClick(palette.buttons[3], Qt.MouseButton.LeftButton)
    assert signals == [3]


def test_mark_active_color(qapp):
    palette = ColorPalette()
    palette.set_active_color(5)
    assert "border: 2px solid" in palette.buttons[5].styleSheet()
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_color_palette.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.color_palette'`

- [ ] **Paso 3: Implementar ui/color_palette.py**

```python
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
                f"background-color:{hex_c}; border:1px solid #333; border-radius:2px;"
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
                f"background-color:{hex_c}; border:1px solid #333; border-radius:2px;"
            )
        self._active_color = index
        hex_c = LP_COLORS.get(index, "#000000")
        self.buttons[index].setStyleSheet(
            f"background-color:{hex_c}; border:2px solid #ffffff; border-radius:2px;"
        )
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_color_palette.py -v
```

Esperado: 5 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add ui/color_palette.py tests/test_color_palette.py
git commit -S -m "feat: 64 native LP Mini MK2 color palette"
```

---

## Tarea 10: Panel de configuración de pad

**Archivos:**
- Crear: `ui/pad_config_panel.py`
- Crear: `tests/test_pad_config_panel.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_pad_config_panel.py`:

```python
import pytest
from unittest.mock import patch
from models.project import PadConfig
from ui.pad_config_panel import PadConfigPanel


@pytest.fixture
def panel(qapp):
    return PadConfigPanel()


def test_panel_shows_empty_pad(panel):
    panel.show_pad(pad_id=11, config=None)
    assert panel.label_file.text() == "Sin audio"


def test_panel_shows_pad_with_config(panel):
    config = PadConfig(audio_file="/path/kick.wav", color=3)
    panel.show_pad(pad_id=11, config=config)
    assert "kick.wav" in panel.label_file.text()


def test_color_change_emits_signal(panel, qtbot):
    panel.show_pad(pad_id=11, config=None)
    signals = []
    panel.color_changed.connect(lambda pad, color: signals.append((pad, color)))
    panel.palette.color_selected.emit(5)
    assert signals == [(11, 5)]


def test_select_audio_emits_signal(panel, qtbot):
    panel.show_pad(pad_id=11, config=None)
    signals = []
    panel.audio_changed.connect(lambda pad, path: signals.append((pad, path)))
    with patch("ui.pad_config_panel.QFileDialog.getOpenFileName",
               return_value=("/path/kick.wav", "")):
        panel.btn_select.click()
    assert signals == [(11, "/path/kick.wav")]
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_pad_config_panel.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.pad_config_panel'`

- [ ] **Paso 3: Implementar ui/pad_config_panel.py**

```python
from __future__ import annotations
from typing import Optional
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
)
from models.project import PadConfig
from ui.color_palette import ColorPalette


AUDIO_FILTER = "Audio (*.wav *.mp3 *.ogg *.flac)"


class PadConfigPanel(QWidget):
    color_changed = pyqtSignal(int, int)   # pad_id, color
    audio_changed = pyqtSignal(int, str)   # pad_id, path

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._pad_id: Optional[int] = None
        layout = QVBoxLayout(self)

        self.label_title = QLabel("Seleccioná un pad")
        layout.addWidget(self.label_title)

        self.palette = ColorPalette()
        self.palette.color_selected.connect(self._on_color)
        layout.addWidget(self.palette)

        self.btn_select = QPushButton("Seleccionar audio...")
        self.btn_select.clicked.connect(self._on_select_audio)
        layout.addWidget(self.btn_select)

        self.label_file = QLabel("Sin audio")
        self.label_file.setWordWrap(True)
        layout.addWidget(self.label_file)

        layout.addStretch()

    def show_pad(self, pad_id: int, config: Optional[PadConfig]) -> None:
        self._pad_id = pad_id
        self.label_title.setText(f"Pad {pad_id}")
        if config:
            import os
            self.label_file.setText(os.path.basename(config.audio_file))
            self.palette.set_active_color(config.color)
        else:
            self.label_file.setText("Sin audio")

    def _on_color(self, color: int) -> None:
        if self._pad_id is not None:
            self.color_changed.emit(self._pad_id, color)

    def _on_select_audio(self) -> None:
        if self._pad_id is None:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar audio", "", AUDIO_FILTER)
        if path:
            import os
            self.label_file.setText(os.path.basename(path))
            self.audio_changed.emit(self._pad_id, path)
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_pad_config_panel.py -v
```

Esperado: 4 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add ui/pad_config_panel.py tests/test_pad_config_panel.py
git commit -S -m "feat: pad config panel (color + audio)"
```

---

## Tarea 11: Diálogo de configuración de pad (Modo Asignación)

**Archivos:**
- Crear: `ui/pad_config_dialog.py`
- Crear: `tests/test_pad_config_dialog.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_pad_config_dialog.py`:

```python
import pytest
from unittest.mock import patch
from models.project import PadConfig
from ui.pad_config_dialog import PadConfigDialog


@pytest.fixture
def empty_dialog(qapp):
    return PadConfigDialog(pad_id=11, current_config=None)


@pytest.fixture
def dialog_with_config(qapp):
    config = PadConfig(audio_file="/path/kick.wav", color=3)
    return PadConfigDialog(pad_id=11, current_config=config)


def test_empty_dialog_shows_no_audio(empty_dialog):
    assert empty_dialog.label_file.text() == "Sin audio"


def test_dialog_loads_existing_config(dialog_with_config):
    assert "kick.wav" in dialog_with_config.label_file.text()


def test_save_returns_pad_config(empty_dialog, qtbot):
    with patch("ui.pad_config_dialog.QFileDialog.getOpenFileName",
               return_value=("/path/snare.wav", "")):
        empty_dialog.btn_select.click()
    empty_dialog.palette.color_selected.emit(7)
    result = empty_dialog.get_config()
    assert result is not None
    assert result.audio_file == "/path/snare.wav"
    assert result.color == 7


def test_cancel_returns_none(empty_dialog):
    empty_dialog.reject()
    # get_config luego de reject debe retornar None
    assert empty_dialog.result() == 0
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_pad_config_dialog.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.pad_config_dialog'`

- [ ] **Paso 3: Implementar ui/pad_config_dialog.py**

```python
from __future__ import annotations
import os
from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QDialogButtonBox,
)
from models.project import PadConfig
from ui.color_palette import ColorPalette

AUDIO_FILTER = "Audio (*.wav *.mp3 *.ogg *.flac)"


class PadConfigDialog(QDialog):
    def __init__(
        self,
        pad_id: int,
        current_config: Optional[PadConfig],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._pad_id = pad_id
        self._audio_path: str = current_config.audio_file if current_config else ""
        self._color: int = current_config.color if current_config else 0
        self.setWindowTitle(f"Configurar Pad {pad_id}")
        self.setMinimumWidth(280)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"<b>Pad {pad_id}</b>"))

        # Audio
        layout.addWidget(QLabel("Archivo de audio:"))
        audio_row = QHBoxLayout()
        name = os.path.basename(self._audio_path) if self._audio_path else "Sin audio"
        self.label_file = QLabel(name)
        audio_row.addWidget(self.label_file, 1)
        self.btn_select = QPushButton("Seleccionar...")
        self.btn_select.clicked.connect(self._on_select)
        audio_row.addWidget(self.btn_select)
        layout.addLayout(audio_row)

        # Color
        layout.addWidget(QLabel("Color del pad:"))
        self.palette = ColorPalette()
        self.palette.color_selected.connect(self._on_color)
        if current_config:
            self.palette.set_active_color(current_config.color)
        layout.addWidget(self.palette)

        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("Guardar")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_select(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar audio", "", AUDIO_FILTER)
        if path:
            self._audio_path = path
            self.label_file.setText(os.path.basename(path))

    def _on_color(self, color: int) -> None:
        self._color = color

    def get_config(self) -> Optional[PadConfig]:
        if self.result() != QDialog.DialogCode.Accepted:
            return None
        if not self._audio_path:
            return None
        return PadConfig(audio_file=self._audio_path, color=self._color)
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_pad_config_dialog.py -v
```

Esperado: 4 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add ui/pad_config_dialog.py tests/test_pad_config_dialog.py
git commit -S -m "feat: pad config dialog for Assignment Mode"
```

---

## Tarea 12: Diálogo Acerca de

**Archivos:**
- Crear: `ui/about_dialog.py`
- Crear: `tests/test_about_dialog.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_about_dialog.py`:

```python
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
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_about_dialog.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.about_dialog'`

- [ ] **Paso 3: Implementar ui/about_dialog.py**

```python
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
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_about_dialog.py -v
```

Esperado: 3 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add ui/about_dialog.py tests/test_about_dialog.py
git commit -S -m "feat: About dialog with version, device and developer"
```

---

## Tarea 13: Panel de ajustes

**Archivos:**
- Crear: `ui/settings_panel.py`
- Crear: `tests/test_settings_panel.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_settings_panel.py`:

```python
import pytest
from models.project import Settings
from ui.settings_panel import SettingsPanel


@pytest.fixture
def settings():
    return Settings(
        midi_input="Launchpad Mini MK2",
        midi_output="Launchpad Mini MK2",
        audio_output="Built-in Audio",
        volume=0.8,
        play_mode="oneshot",
    )


def test_panel_loads_settings(qapp, settings):
    panel = SettingsPanel(
        settings=settings,
        midi_devices=["Launchpad Mini MK2", "Otro"],
        audio_devices=["Built-in Audio", "Externo"],
    )
    assert panel.combo_midi_in.currentText() == "Launchpad Mini MK2"
    assert panel.combo_audio.currentText() == "Built-in Audio"
    assert panel.combo_mode.currentText() == "Una vez"


def test_panel_emits_changes(qapp, settings, qtbot):
    panel = SettingsPanel(
        settings=settings,
        midi_devices=["Launchpad Mini MK2"],
        audio_devices=["Built-in Audio"],
    )
    signals = []
    panel.settings_changed.connect(signals.append)
    panel.volume_slider.setValue(60)
    assert len(signals) == 1
    assert signals[0].volume == pytest.approx(0.6)
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_settings_panel.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.settings_panel'`

- [ ] **Paso 3: Implementar ui/settings_panel.py**

```python
from __future__ import annotations
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QComboBox, QSlider, QLabel
)
from PyQt6.QtCore import Qt
from models.project import Settings

MODES = {"oneshot": "Una vez", "loop": "Bucle", "toggle": "Alternar"}
MODES_INV = {v: k for k, v in MODES.items()}


class SettingsPanel(QWidget):
    settings_changed = pyqtSignal(Settings)

    def __init__(
        self,
        settings: Settings,
        midi_devices: list[str],
        audio_devices: list[str],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._settings = settings
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.combo_midi_in = QComboBox()
        self.combo_midi_in.addItems(midi_devices)
        idx = self.combo_midi_in.findText(settings.midi_input)
        if idx >= 0:
            self.combo_midi_in.setCurrentIndex(idx)
        self.combo_midi_in.currentTextChanged.connect(self._on_change)
        form.addRow("MIDI Entrada:", self.combo_midi_in)

        self.combo_midi_out = QComboBox()
        self.combo_midi_out.addItems(midi_devices)
        idx = self.combo_midi_out.findText(settings.midi_output)
        if idx >= 0:
            self.combo_midi_out.setCurrentIndex(idx)
        self.combo_midi_out.currentTextChanged.connect(self._on_change)
        form.addRow("MIDI Salida:", self.combo_midi_out)

        self.combo_audio = QComboBox()
        self.combo_audio.addItems(audio_devices)
        idx = self.combo_audio.findText(settings.audio_output)
        if idx >= 0:
            self.combo_audio.setCurrentIndex(idx)
        self.combo_audio.currentTextChanged.connect(self._on_change)
        form.addRow("Audio Salida:", self.combo_audio)

        self.combo_mode = QComboBox()
        self.combo_mode.addItems(list(MODES.values()))
        self.combo_mode.setCurrentText(MODES.get(settings.play_mode, "Una vez"))
        self.combo_mode.currentTextChanged.connect(self._on_change)
        form.addRow("Modo reproducción:", self.combo_mode)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(settings.volume * 100))
        self.volume_slider.valueChanged.connect(self._on_change)
        form.addRow("Volumen:", self.volume_slider)

        layout.addLayout(form)
        layout.addStretch()

    def _on_change(self) -> None:
        settings = Settings(
            midi_input=self.combo_midi_in.currentText(),
            midi_output=self.combo_midi_out.currentText(),
            audio_output=self.combo_audio.currentText(),
            volume=self.volume_slider.value() / 100.0,
            play_mode=MODES_INV.get(self.combo_mode.currentText(), "oneshot"),
        )
        self._settings = settings
        self.settings_changed.emit(settings)
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_settings_panel.py -v
```

Esperado: 2 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add ui/settings_panel.py tests/test_settings_panel.py
git commit -S -m "feat: settings panel (MIDI, audio, volume, mode)"
```

---

## Tarea 14: Ventana principal

**Archivos:**
- Crear: `ui/main_window.py`
- Crear: `tests/test_main_window.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_main_window.py`:

```python
import pytest
from unittest.mock import MagicMock, patch
from models.project import Project
from ui.main_window import MainWindow


@pytest.fixture
def window(qapp):
    midi_engine = MagicMock()
    midi_engine.connected = False
    midi_engine.device_name = "Sin conexión"
    midi_engine.list_devices = MagicMock(return_value=[])
    audio_engine = MagicMock()
    project = Project.new()
    return MainWindow(project=project, midi_engine=midi_engine, audio_engine=audio_engine)


def test_window_has_title(window):
    assert "Launchpad" in window.windowTitle()


def test_status_bar_shows_disconnected(window):
    assert "Desconectado" in window.label_status.text() or \
           "Sin conexión" in window.label_status.text()


def test_assignment_mode_starts_disabled(window):
    assert window.assignment_mode_active is False


def test_toggle_assignment_mode(window):
    window.toggle_assignment_mode()
    assert window.assignment_mode_active is True
    window.toggle_assignment_mode()
    assert window.assignment_mode_active is False


def test_change_bank_updates_grid(window):
    window.project.banks.append(__import__('models.project', fromlist=['Bank']).Bank(name="B"))
    window.on_bank_changed(1)
    assert window.project.active_bank_index == 1
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_main_window.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.main_window'`

- [ ] **Paso 3: Implementar ui/main_window.py**

```python
from __future__ import annotations
import os
from typing import Optional
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QSlider, QToolButton, QFileDialog, QMessageBox,
    QStackedWidget, QStatusBar,
)
from models.project import PadConfig, Bank, Project
from engine.audio_engine import AudioEngine
from engine.midi_engine import MidiEngine, pad_to_note, note_to_pad, list_midi_devices
from ui.pad_grid import PadGrid
from ui.bank_selector import BankSelector
from ui.pad_config_panel import PadConfigPanel
from ui.settings_panel import SettingsPanel
from ui.pad_config_dialog import PadConfigDialog
from ui.about_dialog import AboutDialog
from ui.color_palette import LP_COLORS
import sounddevice as sd


PROJECT_FILTER = "Proyecto LP Sampler (*.lpsampler)"


class MainWindow(QMainWindow):
    def __init__(
        self,
        project: Project,
        midi_engine: MidiEngine,
        audio_engine: AudioEngine,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.project = project
        self.midi_engine = midi_engine
        self.audio_engine = audio_engine
        self.assignment_mode_active = False
        self._project_path: Optional[str] = None

        self.setWindowTitle("Launchpad Mini MK2 Sampler")
        self.resize(720, 520)
        self._build_ui()
        self._build_menu()
        self._connect_midi()
        self._update_grid_bank()

    # ── Construcción de UI ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(4)
        main_layout.setContentsMargins(8, 8, 8, 4)

        # Fila superior: bancos + botón modo asignación
        bank_row = QHBoxLayout()
        names = [b.name for b in self.project.banks]
        self.bank_selector = BankSelector(names=names)
        self.bank_selector.bank_changed.connect(self.on_bank_changed)
        bank_row.addWidget(self.bank_selector, 1)

        self.btn_assignment_mode = QToolButton()
        self.btn_assignment_mode.setText("⚡ Modo Asignación")
        self.btn_assignment_mode.setCheckable(True)
        self.btn_assignment_mode.clicked.connect(self.toggle_assignment_mode)
        bank_row.addWidget(self.btn_assignment_mode)
        main_layout.addLayout(bank_row)

        # Área central: grid + panel derecho
        center_area = QHBoxLayout()
        self.grid = PadGrid(color_palette=LP_COLORS)
        self.grid.pad_selected.connect(self.on_pad_click_ui)
        center_area.addWidget(self.grid, 1)

        # Panel derecho apilado: config pad / ajustes
        self.stack_panel = QStackedWidget()
        self.stack_panel.setMinimumWidth(200)
        self.stack_panel.setMaximumWidth(240)

        self.config_panel = PadConfigPanel()
        self.config_panel.color_changed.connect(self.on_color_changed)
        self.config_panel.audio_changed.connect(self.on_audio_changed)
        self.stack_panel.addWidget(self.config_panel)  # índice 0

        midi_devices = list_midi_devices()
        audio_devices = [d["name"] for d in sd.query_devices()
                         if d.get("max_output_channels", 0) > 0]
        self.settings_panel = SettingsPanel(
            settings=self.project.settings,
            midi_devices=midi_devices,
            audio_devices=audio_devices,
        )
        self.settings_panel.settings_changed.connect(self.on_settings_changed)
        self.stack_panel.addWidget(self.settings_panel)  # índice 1

        center_area.addWidget(self.stack_panel)
        main_layout.addLayout(center_area, 1)

        # Barra de estado
        self.label_status = QLabel("● Sin conexión")
        self.statusBar().addWidget(self.label_status, 1)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.project.settings.volume * 100))
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self._on_volume_slider)
        self.statusBar().addPermanentWidget(QLabel("Vol:"))
        self.statusBar().addPermanentWidget(self.volume_slider)

    def _build_menu(self) -> None:
        mb = self.menuBar()

        m_file = mb.addMenu("Archivo")
        m_file.addAction("Nuevo", self.new_project)
        m_file.addAction("Abrir...", self.open_project)
        m_file.addAction("Guardar", self.save_project)
        m_file.addAction("Guardar como...", self.save_project_as)
        m_file.addSeparator()
        m_file.addAction("Salir", self.close)

        m_config = mb.addMenu("Configuración")
        m_config.addAction("Ajustes", self.show_settings)

        m_help = mb.addMenu("Ayuda")
        m_help.addAction("Acerca de", self.show_about)

    # ── MIDI ────────────────────────────────────────────────────────────

    def _connect_midi(self) -> None:
        self.midi_engine.set_callback_pad(self.on_physical_pad)
        self.midi_engine.set_callback_scene(self.on_bank_changed)
        if self.midi_engine.connect():
            self.label_status.setText("● Launchpad conectado")
            self.midi_engine.update_bank_leds(
                self.project.active_bank,
                self.project.active_bank_index,
                self.project.banks,
            )
        else:
            self.label_status.setText("● Sin conexión — abrí Configuración > Ajustes")
            self.show_settings()

    def on_physical_pad(self, pad_id: int) -> None:
        """Llamado desde hilo MIDI cuando se presiona un pad físico."""
        if self.assignment_mode_active:
            current_config = self.project.active_bank.pads.get(pad_id)
            dialog = PadConfigDialog(pad_id=pad_id, current_config=current_config, parent=self)
            if dialog.exec():
                new_config = dialog.get_config()
                if new_config:
                    self.project.active_bank.pads[pad_id] = new_config
                    self.midi_engine.set_pad_color(pad_id, new_config.color)
                    row, col = note_to_pad(pad_id)
                    self.grid.set_pad_color(row, col, new_config.color)
        else:
            config = self.project.active_bank.pads.get(pad_id)
            if config and os.path.exists(config.audio_file):
                self.midi_engine.start_blink(pad_id, config.color)
                self.audio_engine.play(
                    config.audio_file,
                    volume=self.project.settings.volume,
                    mode=self.project.settings.play_mode,
                    pad_id=pad_id,
                    on_complete=lambda pid: self.midi_engine.stop_blink(
                        pid, self.project.active_bank.pads.get(pid, PadConfig("", 0)).color
                    ),
                )

    def on_pad_click_ui(self, row: int, col: int) -> None:
        """Selección desde la UI (click en grid)."""
        pad_id = pad_to_note(row, col)
        config = self.project.active_bank.pads.get(pad_id)
        self.config_panel.show_pad(pad_id, config)
        self.stack_panel.setCurrentIndex(0)

    def on_color_changed(self, pad_id: int, color: int) -> None:
        config = self.project.active_bank.pads.get(pad_id)
        if config:
            config.color = color
        else:
            self.project.active_bank.pads[pad_id] = PadConfig(audio_file="", color=color)
        row, col = note_to_pad(pad_id)
        self.grid.set_pad_color(row, col, color)
        self.midi_engine.set_pad_color(pad_id, color)

    def on_audio_changed(self, pad_id: int, path: str) -> None:
        config = self.project.active_bank.pads.get(pad_id)
        if config:
            config.audio_file = path
        else:
            self.project.active_bank.pads[pad_id] = PadConfig(audio_file=path, color=0)

    def on_bank_changed(self, index: int) -> None:
        if index < 0 or index >= len(self.project.banks):
            return
        self.project.active_bank_index = index
        self.bank_selector.setCurrentIndex(index)
        self._update_grid_bank()
        self.midi_engine.update_bank_leds(
            self.project.active_bank, index, self.project.banks
        )

    def on_settings_changed(self, settings) -> None:
        self.project.settings = settings
        self.volume_slider.setValue(int(settings.volume * 100))

    def toggle_assignment_mode(self) -> None:
        self.assignment_mode_active = not self.assignment_mode_active
        self.btn_assignment_mode.setChecked(self.assignment_mode_active)

    def show_settings(self) -> None:
        self.stack_panel.setCurrentIndex(1)

    def show_about(self) -> None:
        dialog = AboutDialog(
            connected_device=self.midi_engine.device_name,
            parent=self,
        )
        dialog.exec()

    # ── Archivo ─────────────────────────────────────────────────────────

    def new_project(self) -> None:
        self.project = Project.new()
        self._project_path = None
        self._update_grid_bank()

    def open_project(self) -> None:
        from config.project_file import load_project
        path, _ = QFileDialog.getOpenFileName(self, "Abrir proyecto", "", PROJECT_FILTER)
        if path:
            try:
                self.project = load_project(path)
                self._project_path = path
                self._update_grid_bank()
                self.midi_engine.update_bank_leds(
                    self.project.active_bank,
                    self.project.active_bank_index,
                    self.project.banks,
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el proyecto:\n{e}")

    def save_project(self) -> None:
        if self._project_path:
            self._save_to(self._project_path)
        else:
            self.save_project_as()

    def save_project_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Guardar proyecto", "", PROJECT_FILTER)
        if path:
            if not path.endswith(".lpsampler"):
                path += ".lpsampler"
            self._save_to(path)

    def _save_to(self, path: str) -> None:
        from config.project_file import save_project
        try:
            save_project(self.project, path)
            self._project_path = path
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")

    # ── Helpers ─────────────────────────────────────────────────────────

    def _update_grid_bank(self) -> None:
        bank = self.project.active_bank
        for row in range(8):
            for col in range(8):
                note = pad_to_note(row, col)
                config = bank.pads.get(note)
                color = config.color if config else 0
                self.grid.set_pad_color(row, col, color)

    def _on_volume_slider(self, value: int) -> None:
        self.project.settings.volume = value / 100.0

    def closeEvent(self, event) -> None:
        self.audio_engine.stop_all()
        self.midi_engine.disconnect()
        super().closeEvent(event)
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_main_window.py -v
```

Esperado: 5 tests PASSED

- [ ] **Paso 5: Ejecutar todos los tests**

```bash
pytest -v
```

Esperado: todos los tests PASSED

- [ ] **Paso 6: Commit**

```bash
git add ui/main_window.py tests/test_main_window.py
git commit -S -m "feat: main window — orchestrates grid, banks, MIDI and audio"
```

---

## Tarea 15: Punto de entrada y ejecución

**Archivos:**
- Crear: `main.py`

- [ ] **Paso 1: Crear main.py**

```python
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
```

- [ ] **Paso 2: Verificar que arranca (sin Launchpad conectado)**

```bash
python main.py
```

Esperado: ventana abre, muestra "Sin conexión" en barra de estado, panel de ajustes visible.

- [ ] **Paso 3: Commit**

```bash
git add main.py
git commit -S -m "feat: entry point — app ready to run"
```

---

## Tarea 16: Configuración de build con PyInstaller

**Archivos:**
- Crear: `launchpad-sampler.spec`

- [ ] **Paso 1: Generar spec base**

```bash
pyinstaller --name "Launchpad Sampler" --windowed --onefile main.py
```

Esto genera `Launchpad Sampler.spec`. Renombrarlo:

```bash
mv "Launchpad Sampler.spec" launchpad-sampler.spec
```

- [ ] **Paso 2: Ajustar el spec generado**

Abrir `launchpad-sampler.spec` y verificar que `hiddenimports` incluya los módulos de audio:

```python
# Buscar la línea `a = Analysis(` y asegurarse de que hiddenimports contenga:
hiddenimports=['sounddevice', 'soundfile', 'rtmidi'],
```

- [ ] **Paso 3: Construir el ejecutable**

```bash
pyinstaller launchpad-sampler.spec
```

Esperado: ejecutable en `dist/Launchpad Sampler` (macOS: `dist/Launchpad Sampler.app`, Windows: `dist/Launchpad Sampler.exe`)

- [ ] **Paso 4: Probar el ejecutable**

```bash
# macOS:
open "dist/Launchpad Sampler.app"
# Windows:
start "dist/Launchpad Sampler.exe"
```

Verificar que la ventana abre correctamente.

- [ ] **Paso 5: Commit**

```bash
git add launchpad-sampler.spec
git commit -S -m "build: PyInstaller config for .exe and .app"
```

---

## Tarea 17: Push al repositorio remoto

- [ ] **Paso 1: Verificar todos los tests**

```bash
pytest -v
```

Esperado: todos los tests PASSED, 0 errores.

- [ ] **Paso 2: Push**

```bash
git push -u origin main
```

---

## Resumen de cobertura del spec

| Requisito del spec | Tarea |
|---|---|
| Grid 8x8 con colores | Tarea 7 |
| Bancos A-H con tabs | Tarea 8 |
| Paleta 64 colores LP Mini MK2 | Tarea 9 |
| Panel config pad (color + audio) | Tarea 10 |
| Modo Asignación -> dialogo config | Tarea 11 |
| Acerca de (Martin Fernandez Funes) | Tarea 12 |
| Panel ajustes (MIDI, audio, modo, vol) | Tarea 13 |
| Ventana principal + orquestación | Tarea 14 |
| Botones de escena -> cambio de banco | Tarea 5 + 14 |
| Banco activo titila en LP | Tarea 5 |
| Pads titilan mientras reproducen | Tarea 5 + 14 |
| Audio standalone (sounddevice) | Tarea 4 |
| Modos oneshot / loop / toggle | Tarea 4 |
| Save/Load .lpsampler | Tarea 3 |
| Reconexión automática | Tarea 14 |
| README con imagen del dispositivo | Tarea 1 |
| Build .exe / .app | Tarea 16 |
| Commits firmados PGP | Todas |
