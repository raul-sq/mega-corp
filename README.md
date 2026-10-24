# Mega-Corp con RAMSAVE y RAMLOAD

*Mega-Corp* es una aventura conversacional para ZX Spectrum, Amstrad CPC, C64, MSX y PC DOS publicada por Dinamic en 1987, en dos partes. Este repositorio contiene una versión modificada del juego original a la que se han añadido dos órdenes que no tenía:

- **RAMSAVE**: guarda la partida en la memoria, al instante y sin cinta.
- **RAMLOAD**: recupera la partida guardada y vuelve a describir la localidad.

Ninguna de las dos gasta turno. Es el sistema que popularizaron más tarde las aventuras de Aventuras AD.

El juego se publica aquí **con el permiso de Nick (Nicolás) Lekuona**, programador de Mega-Corp.

## Créditos del juego original

- Programa: Nicolás Lecuona
- Gráficos: Luis Franco
- Pantalla de presentación: Javier Cubedo
- Ilustración: Alfonso Azpiri
- Editado por Dinamic Software, 1987
- Creado con *Graphic Adventure Creator*, de Incentive Software

## Contenido

| Carpeta | Contenido |
|---|---|
| `tzx/` | Las dos partes en cinta (`Megacorp1_RAM.tzx`, `Megacorp2_RAM.tzx`) para cualquier emulador o un Spectrum real |
| `dsk/` | Las dos partes en disco para Spectrum +3 (`Megacorp1_RAM.dsk`, `Megacorp2_RAM.dsk`) |
| `dsk/fuentes/` | Cargador para +3DOS y script que crea los discos a partir de las cintas |
| `windows/` | Ejecutables para Windows (`Megacorp1.exe`, `Megacorp2.exe`) y paquetes completos con su código fuente |
| `parche/` | Script que aplica el parche a las cintas originales y listados de la rutina añadida |
| [`CAMBIOS.md`](CAMBIOS.md) | Explicación detallada de los cambios realizados en el juego |
| [`INSTRUCCIONES.txt`](INSTRUCCIONES.txt) | Instrucciones originales del juego, con RAMSAVE, RAMLOAD y la carga en Spectrum +3 añadidas |

## Cómo jugar

### En cinta (TZX)

Abre `tzx/Megacorp1_RAM.tzx` en cualquier emulador de Spectrum 48K o superior y carga con `LOAD ""`, como el original. La segunda parte es `tzx/Megacorp2_RAM.tzx`. Al empezarla, el juego pide la clave que se obtiene al terminar la primera.

### En disco para Spectrum +3 (DSK)

Cada parte del juego ocupa un disco: `Megacorp1_RAM.dsk` contiene la primera y `Megacorp2_RAM.dsk` la segunda. Los ficheros DSK pueden usarse en un emulador o grabarse en un disquete para jugar en un Spectrum +3 real, tanto de 3 pulgadas (la unidad original del +3) como de 3,5 pulgadas (en un +3 con unidad de 3,5).

Inserta el disco de la primera parte (`dsk/Megacorp1_RAM.dsk`) en la unidad A y elige **Cargador** en el menú del +3. El disco arranca solo: lee el juego y lo pone en marcha en modo 48K. La segunda parte está en `dsk/Megacorp2_RAM.dsk`.

En el +3 también se pueden cargar las cintas: elige **48 BASIC** en el menú y escribe `LOAD ""`.

### En Windows

`windows/Megacorp1.exe` y `windows/Megacorp2.exe` funcionan sin instalar nada (Windows 10/11 de 64 bits). Llevan dentro un emulador de Spectrum 48K, su ROM y la cinta modificada:

- La carga es casi instantánea. La pantalla de presentación se queda en pantalla hasta que pulsas una tecla o haces clic.
- Menú **Juego**: Reiniciar (Ctrl+R), Sonido (Ctrl+M) y Salir.
- La ventana se puede redimensionar.

Al no estar firmados, Windows SmartScreen puede mostrar un aviso. Pulsa «Más información» y luego «Ejecutar de todas formas».

Los paquetes `windows/Megacorp1_Windows.zip` y `Megacorp2_Windows.zip` incluyen además el código fuente de los ejecutables y un desensamblado del juego.

## Las órdenes nuevas

| Orden | Efecto |
|---|---|
| `RAMSAVE` | Guarda la partida en memoria: «Partida guardada en memoria.» |
| `RAMLOAD` | Recupera la partida guardada y vuelve a describir la localidad: «Partida recuperada de memoria.» Si no hay ninguna: «No hay ninguna partida en memoria.» |

- Solo hay una partida guardada. Cada RAMSAVE sustituye a la anterior.
- Ninguna de las dos órdenes gasta turno. Tras RAMLOAD, la partida queda exactamente igual que al hacer RAMSAVE.
- La partida guardada sobrevive a FIN, pero se pierde al apagar o reiniciar el ordenador.
- SAVE y LOAD a cinta siguen funcionando como en el original.

## Qué se ha cambiado

En cada parte solo se han modificado dos zonas del código: tres bytes del bucle que lee las órdenes, convertidos en una llamada a la rutina nueva, y 282 bytes que estaban a cero, donde va esa rutina. Los textos, los gráficos, el vocabulario y la lógica de la aventura no se han tocado. Todos los detalles, con el listado de la rutina y cómo se ha comprobado, están en [CAMBIOS.md](CAMBIOS.md).

Para aplicar el parche a las cintas originales:

```
python3 parche/ramsave_patch.py "Megacorp - Part 1.tzx" Megacorp1_RAM.tzx ramsave_parte1.asm
python3 parche/ramsave_patch.py "Megacorp - Part 2.tzx" Megacorp2_RAM.tzx ramsave_parte2.asm
```

Necesita Python 3 y SkoolKit (`pip install skoolkit`).

## Derechos

- *Mega-Corp* es una obra de sus autores y de Dinamic Software. Aunque esta versión esté modificada, el juego sigue perteneciendo a sus propietarios. Se publica con el permiso de Nick Lekuona, sin ánimo de lucro, y se retirará si los titulares de los derechos lo piden.
- *Graphic Adventure Creator* pertenece a Incentive Software.
- La ROM del ZX Spectrum 48K incluida en los ejecutables es propiedad de Amstrad, que permite su distribución junto a emuladores.
- El núcleo de emulación de los ejecutables es [floooh/chips](https://github.com/floooh/chips), de Andre Weissflog, con licencia zlib (copia en los paquetes de `windows/`).
- El código propio de este repositorio (el parche, los scripts y el cargador para +3) no tiene todavía una licencia asignada.

## Agradecimientos

A Nick Lekuona, por su permiso y su interés en conocer cómo se ha modificado su juego.
