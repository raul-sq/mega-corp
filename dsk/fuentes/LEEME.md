# Fuentes de la versión en disco para Spectrum +3

- `mkdsk.py`: crea un disco `.dsk` (formato Extended CPCEMU, 40 pistas, una cara) con tres ficheros +3DOS:
  - `DISK`: BASIC de arranque automático (línea 10);
  - `MEGALDR`: el cargador;
  - `MEGA1.BIN` o `MEGA2.BIN`: el bloque de 48 KB de la cinta modificada.
- `loader.asm`: cargador para +3DOS. Pagina la ROM de +3DOS y lee el fichero repartiéndolo por los bancos de memoria (pantalla en `$4000`, `$5B00-$7FFF` en el banco 1, `$8000-$BFFF` en el banco 3, `$C000-$FFFF` en el banco 0).
- `stub.asm`: código que se copia a `$5D2D`. Mueve cada parte a su sitio, deja la paginación bloqueada en modo 48K y retoma el BASIC del volcado, que ejecuta `RANDOMIZE USR 34104` como en la cinta.
- `tzxdump.py`: lee los bloques de un fichero TZX.

Necesita el ensamblador `pasmo`. Primero hay que ensamblar `stub.asm` a `stub.bin`, que `loader.asm` incluye con `incbin`. `mkdsk.py` crea `fname.inc` y ensambla `loader.asm`:

```
pasmo stub.asm stub.bin
python3 mkdsk.py ../../tzx/Megacorp1_RAM.tzx MEGA1.BIN Megacorp1_RAM.dsk
python3 mkdsk.py ../../tzx/Megacorp2_RAM.tzx MEGA2.BIN Megacorp2_RAM.dsk
```
