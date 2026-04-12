# Launchpad Mini MK2 Sampler — Diseño del Sistema

**Fecha:** 2026-04-12
**Estado:** Aprobado

---

## Descripción general

App de escritorio standalone (Windows + macOS) en español que permite configurar un Novation Launchpad Mini MK2 como sampler: cada pad tiene un archivo de audio asignado y un color, y al presionarlo dispara el audio a través de la placa de sonido del equipo. Los pads titilan mientras el audio está reproduciéndose.

---

## Stack

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| UI | PyQt6 (idioma: español) |
| MIDI I/O | python-rtmidi |
| Audio | sounddevice + soundfile |
| Distribución | PyInstaller (`.exe` Windows, `.app` macOS) |
| Dependencias | pyproject.toml (compatible con uv/pip) |

---

## Repositorio

- **Remote:** `git@github.com:mfernandezfunes/launchpad-pro-app.git`
- **Commits:** firmados con PGP (`git commit -S`), autor `mfernandezfunes`

---

## Dispositivo: Novation Launchpad Mini MK2

- Grid principal: 8×8 pads (64 pads configurables)
- Fila superior: 8 botones redondos de escena → cambian entre bancos A–H
  - Banco activo: titila (parpadeo via MIDI)
  - Bancos con audio asignado: iluminados fijo
  - Bancos vacíos: apagados
- Columna derecha: 8 botones redondos de pista → reservados para versiones futuras, ignorados por ahora
- Paleta de colores: **64 colores** vía velocidad MIDI (0 = apagado, 1–63 = colores)
- Protocolo: MIDI estándar + SysEx para modo de programación de colores

---

## Comportamiento visual de los pads

### Modo normal

| Estado del pad | LED en el dispositivo |
|---|---|
| Sin audio asignado | Apagado |
| Con audio asignado | Color configurado, fijo |
| Reproduciéndose | Titila hasta que el audio termina |
| Seleccionado en la UI | Borde blanco en la app (no afecta el LED) |

### Modo Asignación (activo)

| Estado del pad | LED en el dispositivo |
|---|---|
| Sin audio asignado | Apagado |
| Con audio asignado | Color configurado, fijo |
| Presionado (cualquiera) | Abre diálogo de configuración en la app |

---

## Layout de la interfaz

Ventana única con tres zonas, UI completamente en español:

```
┌──────────────────────────────────────────────────────────┐
│  Menú: Archivo | Editar | Configuración | Ayuda          │
├────────────────────────────────────┬─────────────────────┤
│  Bancos: [A] [B] [C] [D]...        │                     │
│  [⚡ Modo Asignación: OFF]          │  Panel derecho      │
│                                    │  (config pad        │
│  Grid 8x8 (pads del LP Mini MK2)   │   o ajustes)        │
│  · Click = seleccionar pad         │                     │
│  · Presión física = disparar       │                     │
│                                    │                     │
├────────────────────────────────────┴─────────────────────┤
│  Estado: [● Launchpad conectado]           Vol: [====]  │
└──────────────────────────────────────────────────────────┘
```

### Panel derecho — dos modos

**Modo config de pad** (por defecto, al seleccionar un pad):
- Color del pad: paleta nativa LP Mini MK2 (64 colores, grid de velocidades MIDI 1–63)
- Archivo de audio: botón "Seleccionar..." abre selector de archivo (`.wav`, `.mp3`, `.ogg`, `.flac`)
- Nombre del archivo seleccionado

**Modo ajustes** (menú Configuración o ícono ⚙):
- Panel deslizable desde la derecha, reemplaza el panel de config del pad
- Dispositivo MIDI entrada: desplegable con todos los dispositivos MIDI del sistema
- Dispositivo MIDI salida: desplegable con todos los dispositivos MIDI del sistema
- Dispositivo de audio salida: desplegable con todos los dispositivos de audio del sistema
- Modo de reproducción: selector Una vez / Bucle / Alternar (global, aplica a todos los pads)
- Volumen maestro: control deslizante 0–100%

### Diálogo de configuración de pad

Se abre al presionar un pad en Modo Asignación. Contiene:
- Selector de archivo de audio (`.wav`, `.mp3`, `.ogg`, `.flac`)
- Paleta de colores (64 colores nativos LP Mini MK2)
- Botones: "Guardar" y "Cancelar"
- Si el pad ya tenía config, muestra los valores actuales para editar

### Diálogo Acerca de

Accesible desde `Ayuda > Acerca de`. Contiene:
- Nombre de la app y versión
- Controladora conectada (nombre del dispositivo MIDI, o "Sin conexión")
- Desarrollado por **Martin Fernandez Funes**

---

## Modelo de datos

```python
@dataclass
class PadConfig:
    audio_file: str        # ruta absoluta al archivo de audio
    color: int             # velocidad MIDI 1-63 (paleta nativa LP Mini MK2)

@dataclass
class Banco:
    nombre: str
    pads: dict[int, PadConfig]   # key = nota MIDI del pad

@dataclass
class Ajustes:
    midi_entrada: str      # nombre del dispositivo MIDI in
    midi_salida: str       # nombre del dispositivo MIDI out
    audio_salida: str      # nombre del dispositivo de audio out
    volumen: float         # 0.0–1.0
    modo_reproduccion: str # "unica" | "bucle" | "alternar"

@dataclass
class Proyecto:
    bancos: list[Banco]    # máximo 8 bancos (A–H)
    ajustes: Ajustes
```

**Persistencia:** archivo `.lpsampler` (JSON). Las rutas de audio son absolutas. Si un archivo de audio no se encuentra, el pad muestra ícono de advertencia pero la app no falla.

---

## Arquitectura de módulos

```
launchpad-pro-app/
├── main.py
├── ui/
│   ├── ventana_principal.py    # Ventana principal, orquesta todos los widgets
│   ├── grid_pads.py            # Widget QWidget con grid 8x8 de pads coloreados
│   ├── panel_config_pad.py     # Panel derecho: paleta de colores + selector de archivo
│   ├── selector_bancos.py      # Tabs de bancos (QTabBar)
│   ├── dialogo_config_pad.py   # Diálogo de asignación de audio y color
│   └── dialogo_acerca_de.py    # Diálogo Acerca de
├── motor/
│   ├── motor_midi.py           # Recibe note_on del LP, envía colores y parpadeo al LP
│   └── motor_audio.py          # Reproduce audio con sounddevice
├── modelos/
│   └── proyecto.py             # Dataclasses: PadConfig, Banco, Ajustes, Proyecto
└── config/
    └── archivo_proyecto.py     # Guardar/cargar JSON (.lpsampler)
```

---

## Flujos principales

### Configurar un pad (desde la UI)

1. Click en pad del grid → pad se marca como seleccionado (borde blanco en UI)
2. Panel derecho muestra la config actual del pad
3. Click en color de la paleta → `MotorMidi.set_color_pad(pad_id, velocidad)` actualiza el LP en tiempo real
4. Click en "Seleccionar audio..." → selector de archivo → ruta se guarda en `PadConfig.audio_file`
5. Cambios se aplican al modelo en memoria inmediatamente

### Modo Asignación

1. Usuario activa "Modo Asignación" desde la barra de herramientas de la app
2. Usuario presiona cualquier pad en el LP físico (asignado o vacío)
3. App abre `DialogoConfigPad` con los valores actuales del pad (vacíos si no tenía config)
4. Usuario selecciona archivo de audio y color → confirma con "Guardar"
5. Config se aplica al modelo, LED del pad se actualiza en el LP
6. El diálogo se cierra; el usuario puede presionar otro pad sin desactivar el modo
7. Para salir: click en "Modo Asignación" en la barra de herramientas

### Disparar audio (modo normal)

1. Usuario presiona pad físico → LP Mini MK2 envía `note_on` MIDI
2. `MotorMidi` recibe evento, obtiene `pad_id`
3. Busca `PadConfig` en el banco activo
4. `MotorMidi` inicia parpadeo del pad (note_on/off alternados a ~8 Hz)
5. Llama a `MotorAudio.reproducir(audio_file, volumen, modo)`:
   - `unica`: reproduce hasta el final, puede sonar simultáneo con otros pads
   - `bucle`: repite en bucle hasta nueva presión del mismo pad
   - `alternar`: primera presión inicia, segunda presión detiene
6. Cuando el audio termina → `MotorMidi` detiene el parpadeo, restaura color fijo del pad
7. Audio sale por el dispositivo configurado en ajustes

### Cambiar de banco

1. Usuario presiona botón de escena en el LP (fila superior) O hace click en tab de banco en la UI
2. Banco activo cambia
3. Grid se re-renderiza con los colores del nuevo banco
4. `MotorMidi` actualiza todos los LEDs: botón del banco activo titila, pads con sus colores

### Inicio de la app

1. App intenta conectar MIDI buscando "Launchpad" en nombre del dispositivo
2. Si lo encuentra: conecta automáticamente, envía colores del banco activo al LP
3. Si no lo encuentra: abre panel de ajustes con aviso "Launchpad no detectado"
4. Barra de estado muestra estado de conexión en tiempo real

---

## Manejo de errores

| Situación | Comportamiento |
|---|---|
| LP no conectado al iniciar | Aviso en panel de ajustes, app funcional en modo offline |
| Dispositivo MIDI desconectado en uso | Barra de estado muestra "● Desconectado", intento de reconexión automática |
| Archivo de audio no encontrado | Pad muestra ícono ⚠, no bloquea otros pads |
| Error al reproducir audio | Log en consola, no interrumpe otros pads |
| Proyecto con rutas de audio inválidas | Carga igual, marca pads con advertencia |

---

## Distribución

- `pyproject.toml` con dependencias
- `build.spec` para PyInstaller
- Genera `.exe` en Windows y `.app` en macOS
- Sin dependencia de Python instalado en el sistema del usuario

---

## Dependencias

```toml
[project]
name = "launchpad-sampler"
dependencies = [
    "PyQt6>=6.6",
    "python-rtmidi>=1.5",
    "sounddevice>=0.4",
    "soundfile>=0.12",
]

[build-system]
requires = ["pyinstaller>=6.0"]
```
