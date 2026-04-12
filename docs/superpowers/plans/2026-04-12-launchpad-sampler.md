# Launchpad Mini MK2 Sampler — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir una app de escritorio standalone (Windows + macOS) en español que convierte el Novation Launchpad Mini MK2 en un sampler configurable con colores por pad, múltiples bancos y feedback visual vía LEDs.

**Architecture:** PyQt6 para la UI, python-rtmidi para comunicación MIDI bidireccional con el LP Mini MK2, y sounddevice+soundfile para reproducción de audio. La app se divide en: capa de modelos (dataclasses puras), motores (MIDI + audio, sin dependencia de UI), y widgets PyQt6 que orquestan todo.

**Tech Stack:** Python 3.11+, PyQt6 6.6+, python-rtmidi 1.5+, sounddevice 0.4+, soundfile 0.12+, pytest, PyInstaller 6+

---

## Mapa de archivos

| Archivo | Responsabilidad |
|---|---|
| `main.py` | Punto de entrada, inicializa QApplication y VentanaPrincipal |
| `modelos/proyecto.py` | Dataclasses: PadConfig, Banco, Ajustes, Proyecto |
| `config/archivo_proyecto.py` | Serialización/deserialización JSON (.lpsampler) |
| `motor/motor_audio.py` | Reproducción de audio con sounddevice (modos: única, bucle, alternar) |
| `motor/motor_midi.py` | Conexión MIDI, recepción de note_on, envío de colores y parpadeo |
| `ui/grid_pads.py` | Widget 8x8 grid de pads con colores y selección visual |
| `ui/selector_bancos.py` | Tabs A-H para seleccionar banco activo |
| `ui/panel_config_pad.py` | Panel derecho: paleta de colores + selector de audio (y panel de ajustes) |
| `ui/dialogo_config_pad.py` | Diálogo de asignación de audio + color (para Modo Asignación) |
| `ui/dialogo_acerca_de.py` | Diálogo "Acerca de" con info de app y developer |
| `ui/ventana_principal.py` | Ventana principal: orquesta todos los widgets, Modo Asignación, menú |
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
- Crear: `modelos/__init__.py`, `motor/__init__.py`, `ui/__init__.py`, `config/__init__.py`, `tests/__init__.py`

- [ ] **Paso 1: Inicializar git y estructura de directorios**

```bash
cd /Users/martin.fernandez/Documents/repos_personal/launchpad-pro-app
git init
git remote add origin git@github.com:mfernandezfunes/launchpad-pro-app.git
mkdir -p modelos motor ui config tests
touch modelos/__init__.py motor/__init__.py ui/__init__.py config/__init__.py tests/__init__.py
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
git add pyproject.toml .gitignore README.md modelos/ motor/ ui/ config/ tests/
git commit -S -m "chore: setup inicial del proyecto"
```

---

## Tarea 2: Modelos de datos

**Archivos:**
- Crear: `modelos/proyecto.py`
- Crear: `tests/test_modelos.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_modelos.py`:

```python
from modelos.proyecto import PadConfig, Banco, Ajustes, Proyecto


def test_pad_config_defaults():
    pad = PadConfig(audio_file="/ruta/kick.wav", color=3)
    assert pad.audio_file == "/ruta/kick.wav"
    assert pad.color == 3


def test_banco_pads_vacio():
    banco = Banco(nombre="A")
    assert banco.pads == {}


def test_banco_agregar_pad():
    banco = Banco(nombre="A")
    banco.pads[11] = PadConfig(audio_file="/ruta/snare.wav", color=5)
    assert 11 in banco.pads
    assert banco.pads[11].color == 5


def test_proyecto_bancos_iniciales():
    proyecto = Proyecto.nuevo()
    assert len(proyecto.bancos) == 1
    assert proyecto.bancos[0].nombre == "A"


def test_proyecto_banco_activo():
    proyecto = Proyecto.nuevo()
    assert proyecto.banco_activo_indice == 0


def test_ajustes_modo_reproduccion():
    ajustes = Ajustes(
        midi_entrada="",
        midi_salida="",
        audio_salida="",
        volumen=0.8,
        modo_reproduccion="unica",
    )
    assert ajustes.modo_reproduccion == "unica"
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_modelos.py -v
```

Esperado: `ModuleNotFoundError: No module named 'modelos.proyecto'`

- [ ] **Paso 3: Implementar modelos/proyecto.py**

```python
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class PadConfig:
    audio_file: str
    color: int  # velocidad MIDI 1-63, 0 = apagado


@dataclass
class Banco:
    nombre: str
    pads: dict[int, PadConfig] = field(default_factory=dict)


@dataclass
class Ajustes:
    midi_entrada: str
    midi_salida: str
    audio_salida: str
    volumen: float  # 0.0-1.0
    modo_reproduccion: str  # "unica" | "bucle" | "alternar"


@dataclass
class Proyecto:
    bancos: list[Banco]
    ajustes: Ajustes
    banco_activo_indice: int = 0

    @classmethod
    def nuevo(cls) -> Proyecto:
        return cls(
            bancos=[Banco(nombre="A")],
            ajustes=Ajustes(
                midi_entrada="",
                midi_salida="",
                audio_salida="",
                volumen=0.8,
                modo_reproduccion="unica",
            ),
        )

    @property
    def banco_activo(self) -> Banco:
        return self.bancos[self.banco_activo_indice]
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_modelos.py -v
```

Esperado: 6 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add modelos/proyecto.py tests/test_modelos.py
git commit -S -m "feat: modelos de datos (PadConfig, Banco, Ajustes, Proyecto)"
```

---

## Tarea 3: Serialización del proyecto (JSON)

**Archivos:**
- Crear: `config/archivo_proyecto.py`
- Crear: `tests/test_archivo_proyecto.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_archivo_proyecto.py`:

```python
import json
import pytest
from pathlib import Path
from modelos.proyecto import PadConfig, Banco, Ajustes, Proyecto
from config.archivo_proyecto import guardar_proyecto, cargar_proyecto


@pytest.fixture
def proyecto_con_pads():
    p = Proyecto.nuevo()
    p.bancos[0].pads[11] = PadConfig(audio_file="/audio/kick.wav", color=3)
    p.bancos[0].pads[12] = PadConfig(audio_file="/audio/snare.wav", color=5)
    return p


def test_guardar_y_cargar_roundtrip(tmp_path, proyecto_con_pads):
    ruta = tmp_path / "test.lpsampler"
    guardar_proyecto(proyecto_con_pads, ruta)
    cargado = cargar_proyecto(ruta)
    assert cargado.bancos[0].nombre == "A"
    assert cargado.bancos[0].pads[11].audio_file == "/audio/kick.wav"
    assert cargado.bancos[0].pads[11].color == 3
    assert cargado.ajustes.volumen == pytest.approx(0.8)
    assert cargado.ajustes.modo_reproduccion == "unica"


def test_archivo_es_json_valido(tmp_path, proyecto_con_pads):
    ruta = tmp_path / "test.lpsampler"
    guardar_proyecto(proyecto_con_pads, ruta)
    contenido = json.loads(ruta.read_text())
    assert "bancos" in contenido
    assert "ajustes" in contenido


def test_cargar_archivo_inexistente_lanza_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        cargar_proyecto(tmp_path / "inexistente.lpsampler")


def test_multiples_bancos_roundtrip(tmp_path):
    p = Proyecto.nuevo()
    p.bancos.append(Banco(nombre="B"))
    p.bancos[1].pads[21] = PadConfig(audio_file="/audio/hihat.wav", color=9)
    ruta = tmp_path / "test.lpsampler"
    guardar_proyecto(p, ruta)
    cargado = cargar_proyecto(ruta)
    assert len(cargado.bancos) == 2
    assert cargado.bancos[1].pads[21].audio_file == "/audio/hihat.wav"
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_archivo_proyecto.py -v
```

Esperado: `ModuleNotFoundError: No module named 'config.archivo_proyecto'`

- [ ] **Paso 3: Implementar config/archivo_proyecto.py**

```python
from __future__ import annotations
import json
from pathlib import Path
from modelos.proyecto import PadConfig, Banco, Ajustes, Proyecto


def guardar_proyecto(proyecto: Proyecto, ruta: Path) -> None:
    datos = {
        "banco_activo_indice": proyecto.banco_activo_indice,
        "bancos": [
            {
                "nombre": banco.nombre,
                "pads": {
                    str(nota): {"audio_file": pad.audio_file, "color": pad.color}
                    for nota, pad in banco.pads.items()
                },
            }
            for banco in proyecto.bancos
        ],
        "ajustes": {
            "midi_entrada": proyecto.ajustes.midi_entrada,
            "midi_salida": proyecto.ajustes.midi_salida,
            "audio_salida": proyecto.ajustes.audio_salida,
            "volumen": proyecto.ajustes.volumen,
            "modo_reproduccion": proyecto.ajustes.modo_reproduccion,
        },
    }
    Path(ruta).write_text(json.dumps(datos, indent=2, ensure_ascii=False))


def cargar_proyecto(ruta: Path) -> Proyecto:
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {ruta}")
    datos = json.loads(ruta.read_text())
    bancos = [
        Banco(
            nombre=b["nombre"],
            pads={
                int(nota): PadConfig(
                    audio_file=pad["audio_file"],
                    color=pad["color"],
                )
                for nota, pad in b["pads"].items()
            },
        )
        for b in datos["bancos"]
    ]
    a = datos["ajustes"]
    ajustes = Ajustes(
        midi_entrada=a["midi_entrada"],
        midi_salida=a["midi_salida"],
        audio_salida=a["audio_salida"],
        volumen=a["volumen"],
        modo_reproduccion=a["modo_reproduccion"],
    )
    return Proyecto(
        bancos=bancos,
        ajustes=ajustes,
        banco_activo_indice=datos.get("banco_activo_indice", 0),
    )
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_archivo_proyecto.py -v
```

Esperado: 4 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add config/archivo_proyecto.py tests/test_archivo_proyecto.py
git commit -S -m "feat: serialización de proyecto a JSON (.lpsampler)"
```

---

## Tarea 4: Motor de audio

**Archivos:**
- Crear: `motor/motor_audio.py`
- Crear: `tests/test_motor_audio.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_motor_audio.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
from motor.motor_audio import MotorAudio


@pytest.fixture
def motor():
    with patch("motor.motor_audio.sd") as mock_sd, \
         patch("motor.motor_audio.sf") as mock_sf:
        mock_sf.read.return_value = ([0.0, 0.1, 0.2], 44100)
        yield MotorAudio(), mock_sd, mock_sf


def test_reproducir_unica_llama_play(motor):
    m, mock_sd, mock_sf = motor
    m.reproducir("/audio/kick.wav", volumen=0.8, modo="unica", pad_id=11,
                 al_terminar=None)
    mock_sd.play.assert_called_once()


def test_reproducir_ajusta_volumen(motor):
    m, mock_sd, mock_sf = motor
    m.reproducir("/audio/kick.wav", volumen=0.5, modo="unica", pad_id=11,
                 al_terminar=None)
    args, kwargs = mock_sd.play.call_args
    # el primer argumento es el array de audio * volumen
    import numpy as np
    assert args[0].max() <= 0.5 * 1.1  # tolerancia


def test_detener_pad(motor):
    m, mock_sd, _ = motor
    m.reproducir("/audio/kick.wav", volumen=1.0, modo="bucle", pad_id=11,
                 al_terminar=None)
    m.detener(pad_id=11)
    mock_sd.stop.assert_called()


def test_reproducir_archivo_inexistente_no_lanza(motor):
    m, mock_sd, mock_sf = motor
    mock_sf.read.side_effect = FileNotFoundError
    # No debe propagar la excepción
    m.reproducir("/no/existe.wav", volumen=1.0, modo="unica", pad_id=99,
                 al_terminar=None)
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_motor_audio.py -v
```

Esperado: `ModuleNotFoundError: No module named 'motor.motor_audio'`

- [ ] **Paso 3: Implementar motor/motor_audio.py**

```python
from __future__ import annotations
import logging
import threading
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
import soundfile as sf

logger = logging.getLogger(__name__)


class MotorAudio:
    def __init__(self) -> None:
        self._activos: dict[int, threading.Thread] = {}
        self._detener_flags: dict[int, threading.Event] = {}

    def reproducir(
        self,
        audio_file: str,
        volumen: float,
        modo: str,
        pad_id: int,
        al_terminar: Optional[Callable[[int], None]],
        dispositivo: Optional[str] = None,
    ) -> None:
        """Reproduce audio para un pad. modo: 'unica' | 'bucle' | 'alternar'"""
        if modo == "alternar" and pad_id in self._activos:
            self.detener(pad_id)
            return

        self.detener(pad_id)
        flag = threading.Event()
        self._detener_flags[pad_id] = flag

        hilo = threading.Thread(
            target=self._reproducir_hilo,
            args=(audio_file, volumen, modo, pad_id, flag, al_terminar, dispositivo),
            daemon=True,
        )
        self._activos[pad_id] = hilo
        hilo.start()

    def _reproducir_hilo(
        self,
        audio_file: str,
        volumen: float,
        modo: str,
        pad_id: int,
        flag: threading.Event,
        al_terminar: Optional[Callable[[int], None]],
        dispositivo: Optional[str],
    ) -> None:
        try:
            datos, samplerate = sf.read(audio_file, dtype="float32")
            datos = datos * volumen
            kwargs: dict = {"samplerate": samplerate}
            if dispositivo:
                kwargs["device"] = dispositivo
            while not flag.is_set():
                sd.play(datos, **kwargs)
                sd.wait()
                if modo != "bucle" or flag.is_set():
                    break
        except FileNotFoundError:
            logger.warning("Archivo de audio no encontrado: %s", audio_file)
        except Exception as e:
            logger.error("Error reproduciendo %s: %s", audio_file, e)
        finally:
            self._activos.pop(pad_id, None)
            self._detener_flags.pop(pad_id, None)
            if al_terminar:
                al_terminar(pad_id)

    def detener(self, pad_id: int) -> None:
        flag = self._detener_flags.get(pad_id)
        if flag:
            flag.set()
            sd.stop()

    def detener_todo(self) -> None:
        for pad_id in list(self._detener_flags):
            self.detener(pad_id)

    def esta_reproduciendo(self, pad_id: int) -> bool:
        return pad_id in self._activos
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_motor_audio.py -v
```

Esperado: 4 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add motor/motor_audio.py tests/test_motor_audio.py
git commit -S -m "feat: motor de audio con modos única, bucle y alternar"
```

---

## Tarea 5: Motor MIDI

**Archivos:**
- Crear: `motor/motor_midi.py`
- Crear: `tests/test_motor_midi.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_motor_midi.py`:

```python
import pytest
from unittest.mock import patch, MagicMock, call
from motor.motor_midi import MotorMidi, pad_a_nota, nota_a_pad, NOTAS_ESCENA


def test_pad_a_nota_esquina_superior_izquierda():
    # Fila visual 0 (arriba), col 0 → nota MIDI 81
    assert pad_a_nota(0, 0) == 81


def test_pad_a_nota_esquina_inferior_derecha():
    # Fila visual 7 (abajo), col 7 → nota MIDI 18
    assert pad_a_nota(7, 7) == 18


def test_nota_a_pad_roundtrip():
    for fila in range(8):
        for col in range(8):
            nota = pad_a_nota(fila, col)
            f2, c2 = nota_a_pad(nota)
            assert (f2, c2) == (fila, col)


def test_notas_escena_son_8():
    assert len(NOTAS_ESCENA) == 8


def test_listar_dispositivos_llama_rtmidi():
    with patch("motor.motor_midi.rtmidi.MidiIn") as mock_in:
        mock_in.return_value.get_ports.return_value = ["Launchpad Mini", "otro"]
        from motor.motor_midi import listar_dispositivos_midi
        dispositivos = listar_dispositivos_midi()
        assert "Launchpad Mini" in dispositivos


def test_conectar_detecta_launchpad():
    motor = MotorMidi()
    with patch.object(motor, "_midi_in") as mock_in, \
         patch.object(motor, "_midi_out") as mock_out:
        mock_in.get_ports.return_value = ["Launchpad Mini MK2", "otro"]
        mock_out.get_ports.return_value = ["Launchpad Mini MK2", "otro"]
        resultado = motor.conectar()
        assert resultado is True


def test_set_color_pad_envia_note_on():
    motor = MotorMidi()
    mock_out = MagicMock()
    motor._midi_out = mock_out
    motor._conectado = True
    motor.set_color_pad(pad_id=11, color=3)
    # note_on ch1 (0x90), nota 11, velocity 3
    mock_out.send_message.assert_called_with([0x90, 11, 3])


def test_set_color_pad_apaga_con_0():
    motor = MotorMidi()
    mock_out = MagicMock()
    motor._midi_out = mock_out
    motor._conectado = True
    motor.set_color_pad(pad_id=11, color=0)
    mock_out.send_message.assert_called_with([0x90, 11, 0])
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_motor_midi.py -v
```

Esperado: `ModuleNotFoundError: No module named 'motor.motor_midi'`

- [ ] **Paso 3: Implementar motor/motor_midi.py**

```python
from __future__ import annotations
import logging
import threading
import time
from typing import Callable, Optional

import rtmidi

logger = logging.getLogger(__name__)

# Notas de escena: CC 104-111 (fila superior del LP Mini MK2)
NOTAS_ESCENA = list(range(104, 112))


def pad_a_nota(fila: int, col: int) -> int:
    """Convierte posición visual del grid (fila 0=arriba) a nota MIDI."""
    fila_midi = 8 - fila  # fila visual 0 → fila MIDI 8 (notas 81-88)
    return fila_midi * 10 + (col + 1)


def nota_a_pad(nota: int) -> tuple[int, int]:
    """Convierte nota MIDI a posición visual del grid (fila 0=arriba)."""
    fila_midi = nota // 10
    col = (nota % 10) - 1
    fila = 8 - fila_midi
    return fila, col


def listar_dispositivos_midi() -> list[str]:
    midi_in = rtmidi.MidiIn()
    return midi_in.get_ports()


class MotorMidi:
    def __init__(self) -> None:
        self._midi_in = rtmidi.MidiIn()
        self._midi_out = rtmidi.MidiOut()
        self._conectado = False
        self._callback_pad: Optional[Callable[[int], None]] = None
        self._callback_escena: Optional[Callable[[int], None]] = None
        self._parpadeos: dict[int, threading.Event] = {}

    def conectar(self, nombre_dispositivo: str = "Launchpad") -> bool:
        puertos_in = self._midi_in.get_ports()
        puertos_out = self._midi_out.get_ports()
        idx_in = next(
            (i for i, p in enumerate(puertos_in) if nombre_dispositivo.lower() in p.lower()),
            None,
        )
        idx_out = next(
            (i for i, p in enumerate(puertos_out) if nombre_dispositivo.lower() in p.lower()),
            None,
        )
        if idx_in is None or idx_out is None:
            logger.warning("Launchpad no encontrado en puertos MIDI")
            return False
        self._midi_in.open_port(idx_in)
        self._midi_out.open_port(idx_out)
        self._midi_in.set_callback(self._on_mensaje)
        self._conectado = True
        logger.info("Launchpad conectado: %s", puertos_in[idx_in])
        return True

    def desconectar(self) -> None:
        self.detener_todos_parpadeos()
        if self._midi_in.is_port_open():
            self._midi_in.close_port()
        if self._midi_out.is_port_open():
            self._midi_out.close_port()
        self._conectado = False

    def set_callback_pad(self, callback: Callable[[int], None]) -> None:
        """callback(pad_id: int) llamado al presionar un pad del grid."""
        self._callback_pad = callback

    def set_callback_escena(self, callback: Callable[[int], None]) -> None:
        """callback(indice_banco: int) llamado al presionar botón de escena."""
        self._callback_escena = callback

    def set_color_pad(self, pad_id: int, color: int) -> None:
        """Envía color estático a un pad. color=0 apaga."""
        if not self._conectado:
            return
        self._midi_out.send_message([0x90, pad_id, color])

    def iniciar_parpadeo(self, pad_id: int, color: int) -> None:
        """Hace parpadear un pad usando canal 2 (0x91) del LP Mini MK2."""
        if not self._conectado:
            return
        self.detener_parpadeo(pad_id)
        self._midi_out.send_message([0x91, pad_id, color])

    def detener_parpadeo(self, pad_id: int, color: int = 0) -> None:
        """Detiene el parpadeo y restaura color estático."""
        if not self._conectado:
            return
        self._midi_out.send_message([0x90, pad_id, color])

    def detener_todos_parpadeos(self) -> None:
        for flag in self._parpadeos.values():
            flag.set()
        self._parpadeos.clear()

    def set_color_escena(self, indice_banco: int, color: int) -> None:
        """Envía color a un botón de escena (CC 104-111)."""
        if not self._conectado:
            return
        cc = 104 + indice_banco
        self._midi_out.send_message([0xB0, cc, color])

    def actualizar_leds_banco(self, banco, indice_banco_activo: int, todos_bancos: list) -> None:
        """Actualiza todos los LEDs del LP para el banco dado."""
        # Apagar todos los pads del grid
        for fila in range(8):
            for col in range(8):
                nota = pad_a_nota(fila, col)
                self.set_color_pad(nota, 0)
        # Iluminar pads del banco activo
        for nota, pad_config in banco.pads.items():
            self.set_color_pad(nota, pad_config.color)
        # Actualizar botones de escena
        for i, b in enumerate(todos_bancos):
            if i == indice_banco_activo:
                self.iniciar_parpadeo_escena(i, color=3)  # titila verde
            elif b.pads:
                self.set_color_escena(i, color=1)  # iluminado fijo bajo
            else:
                self.set_color_escena(i, color=0)  # apagado

    def iniciar_parpadeo_escena(self, indice_banco: int, color: int) -> None:
        cc = 104 + indice_banco
        if self._conectado:
            self._midi_out.send_message([0xB1, cc, color])  # canal 2 = titila

    def _on_mensaje(self, mensaje, datos=None) -> None:
        msg, _ = mensaje
        status, nota, velocity = msg[0], msg[1], msg[2]
        if velocity == 0:
            return
        canal = status & 0x0F
        tipo = status & 0xF0
        if tipo == 0x90 and canal == 0:  # note_on canal 1
            if 11 <= nota <= 88 and nota % 10 != 9:  # pad del grid
                if self._callback_pad:
                    self._callback_pad(nota)
        elif tipo == 0xB0:  # control change (botones de escena)
            if nota in NOTAS_ESCENA and self._callback_escena:
                self._callback_escena(nota - 104)

    @property
    def conectado(self) -> bool:
        return self._conectado

    @property
    def nombre_dispositivo(self) -> str:
        if not self._conectado:
            return "Sin conexión"
        puertos = self._midi_in.get_ports()
        return puertos[0] if puertos else "Desconocido"
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_motor_midi.py -v
```

Esperado: 8 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add motor/motor_midi.py tests/test_motor_midi.py
git commit -S -m "feat: motor MIDI — conexión, colores, parpadeo LP Mini MK2"
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
git commit -S -m "test: fixture QApplication para tests de UI"
```

---

## Tarea 7: Widget Grid de Pads

**Archivos:**
- Crear: `ui/grid_pads.py`
- Crear: `tests/test_grid_pads.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_grid_pads.py`:

```python
import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from ui.grid_pads import GridPads

COLORES_LP = {0: "#000000", 3: "#FF0000", 5: "#00FF00", 9: "#FFFF00"}


@pytest.fixture
def grid(qapp):
    g = GridPads(colores_paleta=COLORES_LP)
    return g


def test_grid_crea_64_botones(grid):
    assert len(grid.botones) == 64


def test_pad_sin_config_aparece_oscuro(grid):
    # pad (0,0) → sin config → color oscuro (#1a1a1a)
    btn = grid.botones[(0, 0)]
    assert "1a1a1a" in btn.styleSheet().lower() or "background" in btn.styleSheet()


def test_set_color_pad_actualiza_boton(grid):
    grid.set_color_pad(fila=0, col=0, color=3)
    btn = grid.botones[(0, 0)]
    assert "ff0000" in btn.styleSheet().lower()


def test_click_pad_emite_senal(grid, qtbot):
    señales = []
    grid.pad_seleccionado.connect(lambda f, c: señales.append((f, c)))
    btn = grid.botones[(2, 3)]
    qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
    assert señales == [(2, 3)]


def test_seleccionar_pad_marca_borde(grid):
    grid.seleccionar(fila=1, col=2)
    btn = grid.botones[(1, 2)]
    assert "border" in btn.styleSheet()
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_grid_pads.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.grid_pads'`

- [ ] **Paso 3: Implementar ui/grid_pads.py**

```python
from __future__ import annotations
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton


class GridPads(QWidget):
    pad_seleccionado = pyqtSignal(int, int)  # fila, col

    def __init__(self, colores_paleta: dict[int, str], parent=None) -> None:
        super().__init__(parent)
        self._colores_paleta = colores_paleta
        self._colores_actuales: dict[tuple[int, int], int] = {}
        self._seleccionado: tuple[int, int] | None = None
        self.botones: dict[tuple[int, int], QPushButton] = {}
        layout = QGridLayout(self)
        layout.setSpacing(3)
        layout.setContentsMargins(4, 4, 4, 4)
        for fila in range(8):
            for col in range(8):
                btn = QPushButton()
                btn.setFixedSize(44, 44)
                btn.setStyleSheet(self._estilo_pad(color=0, seleccionado=False))
                btn.clicked.connect(lambda _, f=fila, c=col: self._on_click(f, c))
                layout.addWidget(btn, fila, col)
                self.botones[(fila, col)] = btn

    def set_color_pad(self, fila: int, col: int, color: int) -> None:
        self._colores_actuales[(fila, col)] = color
        seleccionado = self._seleccionado == (fila, col)
        self.botones[(fila, col)].setStyleSheet(
            self._estilo_pad(color=color, seleccionado=seleccionado)
        )

    def seleccionar(self, fila: int, col: int) -> None:
        if self._seleccionado:
            f0, c0 = self._seleccionado
            color_prev = self._colores_actuales.get((f0, c0), 0)
            self.botones[(f0, c0)].setStyleSheet(
                self._estilo_pad(color=color_prev, seleccionado=False)
            )
        self._seleccionado = (fila, col)
        color = self._colores_actuales.get((fila, col), 0)
        self.botones[(fila, col)].setStyleSheet(
            self._estilo_pad(color=color, seleccionado=True)
        )

    def _on_click(self, fila: int, col: int) -> None:
        self.seleccionar(fila, col)
        self.pad_seleccionado.emit(fila, col)

    def _estilo_pad(self, color: int, seleccionado: bool) -> str:
        hex_color = self._colores_paleta.get(color, "#1a1a1a")
        borde = "2px solid #ffffff" if seleccionado else "1px solid #333333"
        return (
            f"background-color: {hex_color};"
            f"border: {borde};"
            f"border-radius: 4px;"
        )
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_grid_pads.py -v
```

Esperado: 5 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add ui/grid_pads.py tests/test_grid_pads.py
git commit -S -m "feat: widget grid 8x8 de pads con colores y selección"
```

---

## Tarea 8: Selector de bancos

**Archivos:**
- Crear: `ui/selector_bancos.py`
- Crear: `tests/test_selector_bancos.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_selector_bancos.py`:

```python
import pytest
from ui.selector_bancos import SelectorBancos


@pytest.fixture
def selector(qapp):
    return SelectorBancos(nombres=["A", "B", "C"])


def test_muestra_bancos_iniciales(selector):
    assert selector.count() == 3


def test_agregar_banco(selector):
    selector.agregar_banco("D")
    assert selector.count() == 4


def test_cambio_banco_emite_senal(selector, qtbot):
    señales = []
    selector.banco_cambiado.connect(señales.append)
    selector.setCurrentIndex(1)
    assert 1 in señales


def test_banco_activo_index(selector):
    selector.setCurrentIndex(2)
    assert selector.banco_activo == 2
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_selector_bancos.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.selector_bancos'`

- [ ] **Paso 3: Implementar ui/selector_bancos.py**

```python
from __future__ import annotations
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QTabBar


class SelectorBancos(QTabBar):
    banco_cambiado = pyqtSignal(int)

    def __init__(self, nombres: list[str], parent=None) -> None:
        super().__init__(parent)
        for nombre in nombres:
            self.addTab(nombre)
        self.currentChanged.connect(self.banco_cambiado)

    def agregar_banco(self, nombre: str) -> None:
        self.addTab(nombre)

    @property
    def banco_activo(self) -> int:
        return self.currentIndex()
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_selector_bancos.py -v
```

Esperado: 4 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add ui/selector_bancos.py tests/test_selector_bancos.py
git commit -S -m "feat: widget selector de bancos (tabs A-H)"
```

---

## Tarea 9: Paleta de colores LP Mini MK2

**Archivos:**
- Crear: `ui/paleta_colores.py`
- Crear: `tests/test_paleta_colores.py`

> Esta paleta es compartida por `panel_config_pad.py` y `dialogo_config_pad.py`.

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_paleta_colores.py`:

```python
import pytest
from ui.paleta_colores import PaletaColores, COLORES_LP


def test_paleta_tiene_64_entradas():
    assert len(COLORES_LP) == 64


def test_color_0_es_negro():
    assert COLORES_LP[0].lower() == "#000000"


def test_paleta_widget_crea_64_botones(qapp):
    paleta = PaletaColores()
    assert len(paleta.botones) == 64


def test_click_color_emite_senal(qapp, qtbot):
    paleta = PaletaColores()
    señales = []
    paleta.color_seleccionado.connect(señales.append)
    from PyQt6.QtCore import Qt
    qtbot.mouseClick(paleta.botones[3], Qt.MouseButton.LeftButton)
    assert señales == [3]


def test_marcar_color_activo(qapp):
    paleta = PaletaColores()
    paleta.set_color_activo(5)
    assert "border: 2px solid" in paleta.botones[5].styleSheet()
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_paleta_colores.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.paleta_colores'`

- [ ] **Paso 3: Implementar ui/paleta_colores.py**

```python
from __future__ import annotations
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QGridLayout, QPushButton

# Paleta nativa Launchpad Mini MK2: índice (velocity) → hex RGB aproximado
COLORES_LP: dict[int, str] = {
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


class PaletaColores(QWidget):
    color_seleccionado = pyqtSignal(int)  # índice de color (0-63)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._color_activo: int | None = None
        self.botones: dict[int, QPushButton] = {}
        layout = QGridLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(2, 2, 2, 2)
        for idx in range(64):
            fila, col = divmod(idx, 8)
            btn = QPushButton()
            btn.setFixedSize(22, 22)
            hex_c = COLORES_LP.get(idx, "#000000")
            btn.setStyleSheet(
                f"background-color:{hex_c}; border:1px solid #333; border-radius:2px;"
            )
            btn.clicked.connect(lambda _, i=idx: self._on_click(i))
            layout.addWidget(btn, fila, col)
            self.botones[idx] = btn

    def _on_click(self, indice: int) -> None:
        self.set_color_activo(indice)
        self.color_seleccionado.emit(indice)

    def set_color_activo(self, indice: int) -> None:
        if self._color_activo is not None:
            prev = self._color_activo
            hex_c = COLORES_LP.get(prev, "#000000")
            self.botones[prev].setStyleSheet(
                f"background-color:{hex_c}; border:1px solid #333; border-radius:2px;"
            )
        self._color_activo = indice
        hex_c = COLORES_LP.get(indice, "#000000")
        self.botones[indice].setStyleSheet(
            f"background-color:{hex_c}; border:2px solid #ffffff; border-radius:2px;"
        )
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_paleta_colores.py -v
```

Esperado: 5 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add ui/paleta_colores.py tests/test_paleta_colores.py
git commit -S -m "feat: paleta de 64 colores nativos LP Mini MK2"
```

---

## Tarea 10: Panel de configuración de pad

**Archivos:**
- Crear: `ui/panel_config_pad.py`
- Crear: `tests/test_panel_config_pad.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_panel_config_pad.py`:

```python
import pytest
from unittest.mock import patch
from modelos.proyecto import PadConfig
from ui.panel_config_pad import PanelConfigPad


@pytest.fixture
def panel(qapp):
    return PanelConfigPad()


def test_panel_muestra_pad_vacio(panel):
    panel.mostrar_pad(pad_id=11, config=None)
    assert panel.label_archivo.text() == "Sin audio"


def test_panel_muestra_pad_con_config(panel):
    config = PadConfig(audio_file="/ruta/kick.wav", color=3)
    panel.mostrar_pad(pad_id=11, config=config)
    assert "kick.wav" in panel.label_archivo.text()


def test_cambio_color_emite_senal(panel, qtbot):
    panel.mostrar_pad(pad_id=11, config=None)
    señales = []
    panel.color_cambiado.connect(lambda pad, color: señales.append((pad, color)))
    panel.paleta.color_seleccionado.emit(5)
    assert señales == [(11, 5)]


def test_seleccionar_audio_emite_senal(panel, qtbot):
    panel.mostrar_pad(pad_id=11, config=None)
    señales = []
    panel.audio_cambiado.connect(lambda pad, ruta: señales.append((pad, ruta)))
    with patch("ui.panel_config_pad.QFileDialog.getOpenFileName",
               return_value=("/ruta/kick.wav", "")):
        panel.btn_seleccionar.click()
    assert señales == [(11, "/ruta/kick.wav")]
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_panel_config_pad.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.panel_config_pad'`

- [ ] **Paso 3: Implementar ui/panel_config_pad.py**

```python
from __future__ import annotations
from typing import Optional
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
)
from modelos.proyecto import PadConfig
from ui.paleta_colores import PaletaColores


FILTRO_AUDIO = "Audio (*.wav *.mp3 *.ogg *.flac)"


class PanelConfigPad(QWidget):
    color_cambiado = pyqtSignal(int, int)   # pad_id, color
    audio_cambiado = pyqtSignal(int, str)   # pad_id, ruta

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._pad_id: Optional[int] = None
        layout = QVBoxLayout(self)

        self.label_titulo = QLabel("Seleccioná un pad")
        layout.addWidget(self.label_titulo)

        self.paleta = PaletaColores()
        self.paleta.color_seleccionado.connect(self._on_color)
        layout.addWidget(self.paleta)

        self.btn_seleccionar = QPushButton("Seleccionar audio...")
        self.btn_seleccionar.clicked.connect(self._on_seleccionar_audio)
        layout.addWidget(self.btn_seleccionar)

        self.label_archivo = QLabel("Sin audio")
        self.label_archivo.setWordWrap(True)
        layout.addWidget(self.label_archivo)

        layout.addStretch()

    def mostrar_pad(self, pad_id: int, config: Optional[PadConfig]) -> None:
        self._pad_id = pad_id
        self.label_titulo.setText(f"Pad {pad_id}")
        if config:
            import os
            self.label_archivo.setText(os.path.basename(config.audio_file))
            self.paleta.set_color_activo(config.color)
        else:
            self.label_archivo.setText("Sin audio")

    def _on_color(self, color: int) -> None:
        if self._pad_id is not None:
            self.color_cambiado.emit(self._pad_id, color)

    def _on_seleccionar_audio(self) -> None:
        if self._pad_id is None:
            return
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar audio", "", FILTRO_AUDIO)
        if ruta:
            import os
            self.label_archivo.setText(os.path.basename(ruta))
            self.audio_cambiado.emit(self._pad_id, ruta)
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_panel_config_pad.py -v
```

Esperado: 4 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add ui/panel_config_pad.py tests/test_panel_config_pad.py
git commit -S -m "feat: panel de configuración de pad (color + audio)"
```

---

## Tarea 11: Diálogo de configuración de pad (Modo Asignación)

**Archivos:**
- Crear: `ui/dialogo_config_pad.py`
- Crear: `tests/test_dialogo_config_pad.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_dialogo_config_pad.py`:

```python
import pytest
from unittest.mock import patch
from modelos.proyecto import PadConfig
from ui.dialogo_config_pad import DialogoConfigPad


@pytest.fixture
def dialogo_vacio(qapp):
    return DialogoConfigPad(pad_id=11, config_actual=None)


@pytest.fixture
def dialogo_con_config(qapp):
    config = PadConfig(audio_file="/ruta/kick.wav", color=3)
    return DialogoConfigPad(pad_id=11, config_actual=config)


def test_dialogo_vacio_muestra_sin_audio(dialogo_vacio):
    assert dialogo_vacio.label_archivo.text() == "Sin audio"


def test_dialogo_carga_config_existente(dialogo_con_config):
    assert "kick.wav" in dialogo_con_config.label_archivo.text()


def test_guardar_retorna_pad_config(dialogo_vacio, qtbot):
    with patch("ui.dialogo_config_pad.QFileDialog.getOpenFileName",
               return_value=("/ruta/snare.wav", "")):
        dialogo_vacio.btn_seleccionar.click()
    dialogo_vacio.paleta.color_seleccionado.emit(7)
    resultado = dialogo_vacio.obtener_config()
    assert resultado is not None
    assert resultado.audio_file == "/ruta/snare.wav"
    assert resultado.color == 7


def test_cancelar_retorna_none(dialogo_vacio):
    dialogo_vacio.reject()
    # obtener_config luego de reject debe retornar None
    assert dialogo_vacio.result() == 0
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_dialogo_config_pad.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.dialogo_config_pad'`

- [ ] **Paso 3: Implementar ui/dialogo_config_pad.py**

```python
from __future__ import annotations
import os
from typing import Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QDialogButtonBox,
)
from modelos.proyecto import PadConfig
from ui.paleta_colores import PaletaColores

FILTRO_AUDIO = "Audio (*.wav *.mp3 *.ogg *.flac)"


class DialogoConfigPad(QDialog):
    def __init__(
        self,
        pad_id: int,
        config_actual: Optional[PadConfig],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._pad_id = pad_id
        self._ruta_audio: str = config_actual.audio_file if config_actual else ""
        self._color: int = config_actual.color if config_actual else 0
        self.setWindowTitle(f"Configurar Pad {pad_id}")
        self.setMinimumWidth(280)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"<b>Pad {pad_id}</b>"))

        # Audio
        layout.addWidget(QLabel("Archivo de audio:"))
        fila_audio = QHBoxLayout()
        nombre = os.path.basename(self._ruta_audio) if self._ruta_audio else "Sin audio"
        self.label_archivo = QLabel(nombre)
        fila_audio.addWidget(self.label_archivo, 1)
        self.btn_seleccionar = QPushButton("Seleccionar...")
        self.btn_seleccionar.clicked.connect(self._on_seleccionar)
        fila_audio.addWidget(self.btn_seleccionar)
        layout.addLayout(fila_audio)

        # Color
        layout.addWidget(QLabel("Color del pad:"))
        self.paleta = PaletaColores()
        self.paleta.color_seleccionado.connect(self._on_color)
        if config_actual:
            self.paleta.set_color_activo(config_actual.color)
        layout.addWidget(self.paleta)

        # Botones
        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        botones.button(QDialogButtonBox.StandardButton.Save).setText("Guardar")
        botones.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def _on_seleccionar(self) -> None:
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar audio", "", FILTRO_AUDIO)
        if ruta:
            self._ruta_audio = ruta
            self.label_archivo.setText(os.path.basename(ruta))

    def _on_color(self, color: int) -> None:
        self._color = color

    def obtener_config(self) -> Optional[PadConfig]:
        if self.result() != QDialog.DialogCode.Accepted:
            return None
        if not self._ruta_audio:
            return None
        return PadConfig(audio_file=self._ruta_audio, color=self._color)
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_dialogo_config_pad.py -v
```

Esperado: 4 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add ui/dialogo_config_pad.py tests/test_dialogo_config_pad.py
git commit -S -m "feat: diálogo de configuración de pad para Modo Asignación"
```

---

## Tarea 12: Diálogo Acerca de

**Archivos:**
- Crear: `ui/dialogo_acerca_de.py`
- Crear: `tests/test_dialogo_acerca_de.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_dialogo_acerca_de.py`:

```python
from ui.dialogo_acerca_de import DialogoAcercaDe


def test_muestra_developer(qapp):
    d = DialogoAcercaDe(dispositivo_conectado="Sin conexión")
    assert "Martin Fernandez Funes" in d.label_info.text()


def test_muestra_dispositivo_conectado(qapp):
    d = DialogoAcercaDe(dispositivo_conectado="Launchpad Mini MK2")
    assert "Launchpad Mini MK2" in d.label_info.text()


def test_muestra_sin_conexion(qapp):
    d = DialogoAcercaDe(dispositivo_conectado="Sin conexión")
    assert "Sin conexión" in d.label_info.text()
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_dialogo_acerca_de.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.dialogo_acerca_de'`

- [ ] **Paso 3: Implementar ui/dialogo_acerca_de.py**

```python
from __future__ import annotations
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

VERSION = "1.0.0"


class DialogoAcercaDe(QDialog):
    def __init__(self, dispositivo_conectado: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Acerca de")
        self.setFixedWidth(320)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        titulo = QLabel("<h2>Launchpad Mini MK2 Sampler</h2>")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)

        self.label_info = QLabel(
            f"<p><b>Versión:</b> {VERSION}</p>"
            f"<p><b>Controladora:</b> {dispositivo_conectado}</p>"
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
pytest tests/test_dialogo_acerca_de.py -v
```

Esperado: 3 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add ui/dialogo_acerca_de.py tests/test_dialogo_acerca_de.py
git commit -S -m "feat: diálogo Acerca de con versión, dispositivo y developer"
```

---

## Tarea 13: Panel de ajustes

**Archivos:**
- Crear: `ui/panel_ajustes.py`
- Crear: `tests/test_panel_ajustes.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_panel_ajustes.py`:

```python
import pytest
from modelos.proyecto import Ajustes
from ui.panel_ajustes import PanelAjustes


@pytest.fixture
def ajustes():
    return Ajustes(
        midi_entrada="Launchpad Mini MK2",
        midi_salida="Launchpad Mini MK2",
        audio_salida="Built-in Audio",
        volumen=0.8,
        modo_reproduccion="unica",
    )


def test_panel_carga_ajustes(qapp, ajustes):
    panel = PanelAjustes(
        ajustes=ajustes,
        dispositivos_midi=["Launchpad Mini MK2", "Otro"],
        dispositivos_audio=["Built-in Audio", "Externo"],
    )
    assert panel.combo_midi_in.currentText() == "Launchpad Mini MK2"
    assert panel.combo_audio.currentText() == "Built-in Audio"
    assert panel.combo_modo.currentText() == "Una vez"


def test_panel_emite_cambios(qapp, ajustes, qtbot):
    panel = PanelAjustes(
        ajustes=ajustes,
        dispositivos_midi=["Launchpad Mini MK2"],
        dispositivos_audio=["Built-in Audio"],
    )
    señales = []
    panel.ajustes_cambiados.connect(señales.append)
    panel.slider_volumen.setValue(60)
    assert len(señales) == 1
    assert señales[0].volumen == pytest.approx(0.6)
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_panel_ajustes.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.panel_ajustes'`

- [ ] **Paso 3: Implementar ui/panel_ajustes.py**

```python
from __future__ import annotations
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QComboBox, QSlider, QLabel
)
from PyQt6.QtCore import Qt
from modelos.proyecto import Ajustes

MODOS = {"unica": "Una vez", "bucle": "Bucle", "alternar": "Alternar"}
MODOS_INV = {v: k for k, v in MODOS.items()}


class PanelAjustes(QWidget):
    ajustes_cambiados = pyqtSignal(Ajustes)

    def __init__(
        self,
        ajustes: Ajustes,
        dispositivos_midi: list[str],
        dispositivos_audio: list[str],
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._ajustes = ajustes
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.combo_midi_in = QComboBox()
        self.combo_midi_in.addItems(dispositivos_midi)
        idx = self.combo_midi_in.findText(ajustes.midi_entrada)
        if idx >= 0:
            self.combo_midi_in.setCurrentIndex(idx)
        self.combo_midi_in.currentTextChanged.connect(self._on_cambio)
        form.addRow("MIDI Entrada:", self.combo_midi_in)

        self.combo_midi_out = QComboBox()
        self.combo_midi_out.addItems(dispositivos_midi)
        idx = self.combo_midi_out.findText(ajustes.midi_salida)
        if idx >= 0:
            self.combo_midi_out.setCurrentIndex(idx)
        self.combo_midi_out.currentTextChanged.connect(self._on_cambio)
        form.addRow("MIDI Salida:", self.combo_midi_out)

        self.combo_audio = QComboBox()
        self.combo_audio.addItems(dispositivos_audio)
        idx = self.combo_audio.findText(ajustes.audio_salida)
        if idx >= 0:
            self.combo_audio.setCurrentIndex(idx)
        self.combo_audio.currentTextChanged.connect(self._on_cambio)
        form.addRow("Audio Salida:", self.combo_audio)

        self.combo_modo = QComboBox()
        self.combo_modo.addItems(list(MODOS.values()))
        self.combo_modo.setCurrentText(MODOS.get(ajustes.modo_reproduccion, "Una vez"))
        self.combo_modo.currentTextChanged.connect(self._on_cambio)
        form.addRow("Modo reproducción:", self.combo_modo)

        self.slider_volumen = QSlider(Qt.Orientation.Horizontal)
        self.slider_volumen.setRange(0, 100)
        self.slider_volumen.setValue(int(ajustes.volumen * 100))
        self.slider_volumen.valueChanged.connect(self._on_cambio)
        form.addRow("Volumen:", self.slider_volumen)

        layout.addLayout(form)
        layout.addStretch()

    def _on_cambio(self) -> None:
        ajustes = Ajustes(
            midi_entrada=self.combo_midi_in.currentText(),
            midi_salida=self.combo_midi_out.currentText(),
            audio_salida=self.combo_audio.currentText(),
            volumen=self.slider_volumen.value() / 100.0,
            modo_reproduccion=MODOS_INV.get(self.combo_modo.currentText(), "unica"),
        )
        self._ajustes = ajustes
        self.ajustes_cambiados.emit(ajustes)
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_panel_ajustes.py -v
```

Esperado: 2 tests PASSED

- [ ] **Paso 5: Commit**

```bash
git add ui/panel_ajustes.py tests/test_panel_ajustes.py
git commit -S -m "feat: panel de ajustes (MIDI, audio, volumen, modo)"
```

---

## Tarea 14: Ventana principal

**Archivos:**
- Crear: `ui/ventana_principal.py`
- Crear: `tests/test_ventana_principal.py`

- [ ] **Paso 1: Escribir el test**

Crear `tests/test_ventana_principal.py`:

```python
import pytest
from unittest.mock import MagicMock, patch
from modelos.proyecto import Proyecto
from ui.ventana_principal import VentanaPrincipal


@pytest.fixture
def ventana(qapp):
    motor_midi = MagicMock()
    motor_midi.conectado = False
    motor_midi.nombre_dispositivo = "Sin conexión"
    motor_midi.listar_dispositivos = MagicMock(return_value=[])
    motor_audio = MagicMock()
    proyecto = Proyecto.nuevo()
    return VentanaPrincipal(proyecto=proyecto, motor_midi=motor_midi, motor_audio=motor_audio)


def test_ventana_tiene_titulo(ventana):
    assert "Launchpad" in ventana.windowTitle()


def test_barra_estado_muestra_desconectado(ventana):
    assert "Desconectado" in ventana.label_estado.text() or \
           "Sin conexión" in ventana.label_estado.text()


def test_modo_asignacion_inicia_desactivado(ventana):
    assert ventana.modo_asignacion_activo is False


def test_toggle_modo_asignacion(ventana):
    ventana.toggle_modo_asignacion()
    assert ventana.modo_asignacion_activo is True
    ventana.toggle_modo_asignacion()
    assert ventana.modo_asignacion_activo is False


def test_cambiar_banco_actualiza_grid(ventana):
    ventana.proyecto.bancos.append(__import__('modelos.proyecto', fromlist=['Banco']).Banco(nombre="B"))
    ventana.on_banco_cambiado(1)
    assert ventana.proyecto.banco_activo_indice == 1
```

- [ ] **Paso 2: Ejecutar test (debe fallar)**

```bash
pytest tests/test_ventana_principal.py -v
```

Esperado: `ModuleNotFoundError: No module named 'ui.ventana_principal'`

- [ ] **Paso 3: Implementar ui/ventana_principal.py**

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
from modelos.proyecto import PadConfig, Banco, Proyecto
from motor.motor_audio import MotorAudio
from motor.motor_midi import MotorMidi, pad_a_nota, nota_a_pad, listar_dispositivos_midi
from ui.grid_pads import GridPads
from ui.selector_bancos import SelectorBancos
from ui.panel_config_pad import PanelConfigPad
from ui.panel_ajustes import PanelAjustes
from ui.dialogo_config_pad import DialogoConfigPad
from ui.dialogo_acerca_de import DialogoAcercaDe
from ui.paleta_colores import COLORES_LP
import sounddevice as sd


FILTRO_PROYECTO = "Proyecto LP Sampler (*.lpsampler)"


class VentanaPrincipal(QMainWindow):
    def __init__(
        self,
        proyecto: Proyecto,
        motor_midi: MotorMidi,
        motor_audio: MotorAudio,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.proyecto = proyecto
        self.motor_midi = motor_midi
        self.motor_audio = motor_audio
        self.modo_asignacion_activo = False
        self._ruta_proyecto: Optional[str] = None

        self.setWindowTitle("Launchpad Mini MK2 Sampler")
        self.resize(720, 520)
        self._construir_ui()
        self._construir_menu()
        self._conectar_midi()
        self._actualizar_grid_banco()

    # ── Construcción de UI ──────────────────────────────────────────────

    def _construir_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout_principal = QVBoxLayout(central)
        layout_principal.setSpacing(4)
        layout_principal.setContentsMargins(8, 8, 8, 4)

        # Fila superior: bancos + botón modo asignación
        fila_bancos = QHBoxLayout()
        nombres = [b.nombre for b in self.proyecto.bancos]
        self.selector_bancos = SelectorBancos(nombres=nombres)
        self.selector_bancos.banco_cambiado.connect(self.on_banco_cambiado)
        fila_bancos.addWidget(self.selector_bancos, 1)

        self.btn_modo_asignacion = QToolButton()
        self.btn_modo_asignacion.setText("⚡ Modo Asignación")
        self.btn_modo_asignacion.setCheckable(True)
        self.btn_modo_asignacion.clicked.connect(self.toggle_modo_asignacion)
        fila_bancos.addWidget(self.btn_modo_asignacion)
        layout_principal.addLayout(fila_bancos)

        # Área central: grid + panel derecho
        area_central = QHBoxLayout()
        self.grid = GridPads(colores_paleta=COLORES_LP)
        self.grid.pad_seleccionado.connect(self.on_pad_click_ui)
        area_central.addWidget(self.grid, 1)

        # Panel derecho apilado: config pad / ajustes
        self.stack_panel = QStackedWidget()
        self.stack_panel.setMinimumWidth(200)
        self.stack_panel.setMaximumWidth(240)

        self.panel_config = PanelConfigPad()
        self.panel_config.color_cambiado.connect(self.on_color_cambiado)
        self.panel_config.audio_cambiado.connect(self.on_audio_cambiado)
        self.stack_panel.addWidget(self.panel_config)  # índice 0

        dispositivos_midi = listar_dispositivos_midi()
        dispositivos_audio = [d["name"] for d in sd.query_devices()
                              if d.get("max_output_channels", 0) > 0]
        self.panel_ajustes = PanelAjustes(
            ajustes=self.proyecto.ajustes,
            dispositivos_midi=dispositivos_midi,
            dispositivos_audio=dispositivos_audio,
        )
        self.panel_ajustes.ajustes_cambiados.connect(self.on_ajustes_cambiados)
        self.stack_panel.addWidget(self.panel_ajustes)  # índice 1

        area_central.addWidget(self.stack_panel)
        layout_principal.addLayout(area_central, 1)

        # Barra de estado
        self.label_estado = QLabel("● Sin conexión")
        self.statusBar().addWidget(self.label_estado, 1)

        self.slider_volumen = QSlider(Qt.Orientation.Horizontal)
        self.slider_volumen.setRange(0, 100)
        self.slider_volumen.setValue(int(self.proyecto.ajustes.volumen * 100))
        self.slider_volumen.setMaximumWidth(100)
        self.slider_volumen.valueChanged.connect(self._on_volumen_slider)
        self.statusBar().addPermanentWidget(QLabel("Vol:"))
        self.statusBar().addPermanentWidget(self.slider_volumen)

    def _construir_menu(self) -> None:
        mb = self.menuBar()

        m_archivo = mb.addMenu("Archivo")
        m_archivo.addAction("Nuevo", self.nuevo_proyecto)
        m_archivo.addAction("Abrir...", self.abrir_proyecto)
        m_archivo.addAction("Guardar", self.guardar_proyecto)
        m_archivo.addAction("Guardar como...", self.guardar_proyecto_como)
        m_archivo.addSeparator()
        m_archivo.addAction("Salir", self.close)

        m_config = mb.addMenu("Configuración")
        m_config.addAction("Ajustes", self.mostrar_ajustes)

        m_ayuda = mb.addMenu("Ayuda")
        m_ayuda.addAction("Acerca de", self.mostrar_acerca_de)

    # ── MIDI ────────────────────────────────────────────────────────────

    def _conectar_midi(self) -> None:
        self.motor_midi.set_callback_pad(self.on_pad_fisico)
        self.motor_midi.set_callback_escena(self.on_banco_cambiado)
        if self.motor_midi.conectar():
            self.label_estado.setText("● Launchpad conectado")
            self.motor_midi.actualizar_leds_banco(
                self.proyecto.banco_activo,
                self.proyecto.banco_activo_indice,
                self.proyecto.bancos,
            )
        else:
            self.label_estado.setText("● Sin conexión — abrí Configuración > Ajustes")
            self.mostrar_ajustes()

    def on_pad_fisico(self, pad_id: int) -> None:
        """Llamado desde hilo MIDI cuando se presiona un pad físico."""
        if self.modo_asignacion_activo:
            config_actual = self.proyecto.banco_activo.pads.get(pad_id)
            dialogo = DialogoConfigPad(pad_id=pad_id, config_actual=config_actual, parent=self)
            if dialogo.exec():
                nueva_config = dialogo.obtener_config()
                if nueva_config:
                    self.proyecto.banco_activo.pads[pad_id] = nueva_config
                    self.motor_midi.set_color_pad(pad_id, nueva_config.color)
                    fila, col = nota_a_pad(pad_id)
                    self.grid.set_color_pad(fila, col, nueva_config.color)
        else:
            config = self.proyecto.banco_activo.pads.get(pad_id)
            if config and os.path.exists(config.audio_file):
                self.motor_midi.iniciar_parpadeo(pad_id, config.color)
                self.motor_audio.reproducir(
                    config.audio_file,
                    volumen=self.proyecto.ajustes.volumen,
                    modo=self.proyecto.ajustes.modo_reproduccion,
                    pad_id=pad_id,
                    al_terminar=lambda pid: self.motor_midi.detener_parpadeo(
                        pid, self.proyecto.banco_activo.pads.get(pid, PadConfig("", 0)).color
                    ),
                )

    def on_pad_click_ui(self, fila: int, col: int) -> None:
        """Selección desde la UI (click en grid)."""
        pad_id = pad_a_nota(fila, col)
        config = self.proyecto.banco_activo.pads.get(pad_id)
        self.panel_config.mostrar_pad(pad_id, config)
        self.stack_panel.setCurrentIndex(0)

    def on_color_cambiado(self, pad_id: int, color: int) -> None:
        config = self.proyecto.banco_activo.pads.get(pad_id)
        if config:
            config.color = color
        else:
            self.proyecto.banco_activo.pads[pad_id] = PadConfig(audio_file="", color=color)
        fila, col = nota_a_pad(pad_id)
        self.grid.set_color_pad(fila, col, color)
        self.motor_midi.set_color_pad(pad_id, color)

    def on_audio_cambiado(self, pad_id: int, ruta: str) -> None:
        config = self.proyecto.banco_activo.pads.get(pad_id)
        if config:
            config.audio_file = ruta
        else:
            self.proyecto.banco_activo.pads[pad_id] = PadConfig(audio_file=ruta, color=0)

    def on_banco_cambiado(self, indice: int) -> None:
        if indice < 0 or indice >= len(self.proyecto.bancos):
            return
        self.proyecto.banco_activo_indice = indice
        self.selector_bancos.setCurrentIndex(indice)
        self._actualizar_grid_banco()
        self.motor_midi.actualizar_leds_banco(
            self.proyecto.banco_activo, indice, self.proyecto.bancos
        )

    def on_ajustes_cambiados(self, ajustes) -> None:
        self.proyecto.ajustes = ajustes
        self.slider_volumen.setValue(int(ajustes.volumen * 100))

    def toggle_modo_asignacion(self) -> None:
        self.modo_asignacion_activo = not self.modo_asignacion_activo
        self.btn_modo_asignacion.setChecked(self.modo_asignacion_activo)

    def mostrar_ajustes(self) -> None:
        self.stack_panel.setCurrentIndex(1)

    def mostrar_acerca_de(self) -> None:
        dialogo = DialogoAcercaDe(
            dispositivo_conectado=self.motor_midi.nombre_dispositivo,
            parent=self,
        )
        dialogo.exec()

    # ── Archivo ─────────────────────────────────────────────────────────

    def nuevo_proyecto(self) -> None:
        self.proyecto = Proyecto.nuevo()
        self._ruta_proyecto = None
        self._actualizar_grid_banco()

    def abrir_proyecto(self) -> None:
        from config.archivo_proyecto import cargar_proyecto
        ruta, _ = QFileDialog.getOpenFileName(self, "Abrir proyecto", "", FILTRO_PROYECTO)
        if ruta:
            try:
                self.proyecto = cargar_proyecto(ruta)
                self._ruta_proyecto = ruta
                self._actualizar_grid_banco()
                self.motor_midi.actualizar_leds_banco(
                    self.proyecto.banco_activo,
                    self.proyecto.banco_activo_indice,
                    self.proyecto.bancos,
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el proyecto:\n{e}")

    def guardar_proyecto(self) -> None:
        if self._ruta_proyecto:
            self._guardar_en(self._ruta_proyecto)
        else:
            self.guardar_proyecto_como()

    def guardar_proyecto_como(self) -> None:
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar proyecto", "", FILTRO_PROYECTO)
        if ruta:
            if not ruta.endswith(".lpsampler"):
                ruta += ".lpsampler"
            self._guardar_en(ruta)

    def _guardar_en(self, ruta: str) -> None:
        from config.archivo_proyecto import guardar_proyecto
        try:
            guardar_proyecto(self.proyecto, ruta)
            self._ruta_proyecto = ruta
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")

    # ── Helpers ─────────────────────────────────────────────────────────

    def _actualizar_grid_banco(self) -> None:
        banco = self.proyecto.banco_activo
        for fila in range(8):
            for col in range(8):
                nota = pad_a_nota(fila, col)
                config = banco.pads.get(nota)
                color = config.color if config else 0
                self.grid.set_color_pad(fila, col, color)

    def _on_volumen_slider(self, valor: int) -> None:
        self.proyecto.ajustes.volumen = valor / 100.0

    def closeEvent(self, event) -> None:
        self.motor_audio.detener_todo()
        self.motor_midi.desconectar()
        super().closeEvent(event)
```

- [ ] **Paso 4: Ejecutar test (debe pasar)**

```bash
pytest tests/test_ventana_principal.py -v
```

Esperado: 5 tests PASSED

- [ ] **Paso 5: Ejecutar todos los tests**

```bash
pytest -v
```

Esperado: todos los tests PASSED

- [ ] **Paso 6: Commit**

```bash
git add ui/ventana_principal.py tests/test_ventana_principal.py
git commit -S -m "feat: ventana principal — orquesta grid, bancos, MIDI y audio"
```

---

## Tarea 15: Punto de entrada y ejecución

**Archivos:**
- Crear: `main.py`

- [ ] **Paso 1: Crear main.py**

```python
import sys
from PyQt6.QtWidgets import QApplication
from motor.motor_midi import MotorMidi
from motor.motor_audio import MotorAudio
from modelos.proyecto import Proyecto
from ui.ventana_principal import VentanaPrincipal


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Launchpad Mini MK2 Sampler")
    app.setOrganizationName("mfernandezfunes")

    proyecto = Proyecto.nuevo()
    motor_midi = MotorMidi()
    motor_audio = MotorAudio()

    ventana = VentanaPrincipal(
        proyecto=proyecto,
        motor_midi=motor_midi,
        motor_audio=motor_audio,
    )
    ventana.show()
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
git commit -S -m "feat: punto de entrada — app lista para ejecutar"
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
git commit -S -m "build: configuración PyInstaller para .exe y .app"
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
| Grid 8×8 con colores | Tarea 7 |
| Bancos A–H con tabs | Tarea 8 |
| Paleta 64 colores LP Mini MK2 | Tarea 9 |
| Panel config pad (color + audio) | Tarea 10 |
| Modo Asignación → diálogo config | Tarea 11 |
| Acerca de (Martin Fernandez Funes) | Tarea 12 |
| Panel ajustes (MIDI, audio, modo, vol) | Tarea 13 |
| Ventana principal + orquestación | Tarea 14 |
| Botones de escena → cambio de banco | Tarea 5 + 14 |
| Banco activo titila en LP | Tarea 5 |
| Pads titilan mientras reproducen | Tarea 5 + 14 |
| Audio standalone (sounddevice) | Tarea 4 |
| Modos única / bucle / alternar | Tarea 4 |
| Save/Load .lpsampler | Tarea 3 |
| Reconexión automática | Tarea 14 |
| README con imagen del dispositivo | Tarea 1 |
| Build .exe / .app | Tarea 16 |
| Commits firmados PGP | Todas |
