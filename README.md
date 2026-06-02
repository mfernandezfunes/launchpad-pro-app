# Launchpad Mini MK2 Sampler

App de escritorio standalone para configurar el Novation Launchpad Mini MK2 como sampler de audio.

![Novation Launchpad Mini MK2](https://http2.mlstatic.com/D_NQ_NP_2X_674503-MLU72636681781_112023-F.webp)

## Funcionalidades

- Grid 8x8 con mapeo MIDI correcto al hardware (layout Session, notas 11-88)
- Paleta de 128 colores oficial Novation con selector curado de 37 colores distinguibles
- 8 bancos configurables con cambio desde botones de escena del LP
- Modo asignación para configurar audio y color por pad
- Indicador de nota MIDI y posición (fila/columna) en barra de estado
- Modos de reproducción: oneshot, loop, toggle
- Inicialización/reset automático del Launchpad al conectar/desconectar
- Exportación como .app (macOS) y .exe (Windows) via PyInstaller

## Instalación

```bash
pip install -e ".[dev]"
```

## Uso

```bash
python main.py
```

## Tests

```bash
pytest
```

## Build

El workflow de GitHub Actions genera builds para macOS y Windows automáticamente al pushear un tag `v*`:

```bash
git tag v1.1.0
git push origin v1.1.0
```

## Changelog

### v1.1.0

- Fix: mapeo MIDI corregido — inicialización SysEx layout Session al conectar
- Fix: filtro de notas válidas (descartaba/aceptaba notas incorrectas)
- Fix: paleta de colores reemplazada por la oficial de 128 colores Novation
- Nuevo: selector UI curado con 37 colores distinguibles
- Nuevo: indicador de nota MIDI y posición en barra de estado
- Nuevo: reset de LEDs al desconectar la app
- Nuevo: flush de buffer MIDI al conectar

### v1.0.0

- Release inicial con grid, bancos, audio engine y build CI

## Desarrollado por

Martin Fernandez Funes
