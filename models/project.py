from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class PadConfig:
    audio_file: str
    color: int  # MIDI velocity 1-63, 0 = off


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
