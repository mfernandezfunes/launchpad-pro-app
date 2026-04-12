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
        raise FileNotFoundError(f"File not found: {path}")
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
    s = data["settings"]
    settings = Settings(
        midi_input=s["midi_input"],
        midi_output=s["midi_output"],
        audio_output=s["audio_output"],
        volume=s["volume"],
        play_mode=s["play_mode"],
    )
    return Project(
        banks=banks,
        settings=settings,
        active_bank_index=data.get("active_bank_index", 0),
    )
