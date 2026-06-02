from __future__ import annotations
import logging
import threading
import time
from typing import Callable, Optional

import rtmidi

logger = logging.getLogger(__name__)

# Notas de escena: CC 104-111 (fila superior del LP Mini MK2)
SCENE_NOTES = list(range(104, 112))

# SysEx para Launchpad Mini MK2 (device ID 0x18)
SYSEX_HEADER_MK2 = [0x00, 0x20, 0x29, 0x02, 0x18]
LAYOUT_SESSION = 0x00
LAYOUT_DRUM_RACK = 0x01
LAYOUT_USER = 0x03


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
        self._init_device()
        logger.info("Launchpad conectado: %s", ports_in[idx_in])
        return True

    def _init_device(self) -> None:
        """Inicializa el Launchpad: layout Session y flush de buffer."""
        self._midi_out.send_message(
            [0xF0] + SYSEX_HEADER_MK2 + [0x22, LAYOUT_SESSION, 0xF7]
        )
        self._flush_buttons()

    def _flush_buttons(self) -> None:
        """Limpia el buffer de eventos pendientes del Launchpad."""
        for _ in range(64):
            msg = self._midi_in.get_message()
            if msg is None:
                break

    def disconnect(self) -> None:
        self.stop_all_blinks()
        if self._connected:
            self._reset_device()
        if self._midi_in.is_port_open():
            self._midi_in.close_port()
        if self._midi_out.is_port_open():
            self._midi_out.close_port()
        self._connected = False

    def _reset_device(self) -> None:
        """Apaga todos los LEDs al desconectar."""
        self._midi_out.send_message(
            [0xF0] + SYSEX_HEADER_MK2 + [0x0E, 0x00, 0xF7]
        )

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
            if 11 <= note <= 88 and 1 <= (note % 10) <= 8:  # pad del grid
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
