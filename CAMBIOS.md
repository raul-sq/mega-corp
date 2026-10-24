# Cambios realizados para añadir RAMSAVE y RAMLOAD

Este documento explica exactamente qué se ha modificado en las cintas originales de Mega-Corp para añadir las órdenes RAMSAVE y RAMLOAD, por qué se ha hecho así y cómo se ha comprobado. Lo escribo a petición de Nick Lekuona, programador del juego.

## Resumen

En cada una de las dos partes solo cambian **dos zonas del bloque de código** de la cinta (además de su byte de checksum):

| Zona | Antes | Después |
|---|---|---|
| `$7BEC-$7BEE` (3 bytes) | `3A 00 5B` = `LD A,($5B00)` | `CD 00 60` = `CALL $6000` |
| `$6000-$6119` (282 bytes) | ceros | rutina nueva y sus textos |

Ningún otro byte cambia: la base de datos de la aventura (textos, gráficos, vocabulario, objetos y condiciones) y el resto del motor quedan exactamente como estaban. Las cintas modificadas tienen los mismos bloques, con las mismas longitudes, que las originales. El tamaño del fichero TZX tampoco cambia (49.382 bytes).

La copia de la partida que hace RAMSAVE va justo detrás, en `$611A`. En la cinta esa zona sigue a cero: solo se rellena mientras se juega.

## Punto de partida: cómo lee las órdenes el motor GAC

Mega-Corp está hecho con *Graphic Adventure Creator* (Incentive Software). El bucle principal de órdenes del motor está en `$7BD2`:

```
7BD2  LD C,$F0
7BD4  CALL $77B8          ; muestra el indicador ">>>"
7BD7  LD HL,$5B00
7BDA  LD ($A4F4),HL       ; puntero de análisis al principio de la línea
7BDD  LD (HL),$00
7BDF  CALL $85DC          ; lee la línea tecleada en $5B00 (mayúsculas, termina en 0)
7BE2  JR NC,$7BD2
7BE4  LD A,($A4E7)
7BE7  AND $EF
7BE9  LD ($A4E7),A
7BEC  LD A,($5B00)        ; <-- punto de enganche
7BEF  AND A
7BF0  JR Z,$7BD2          ; línea vacía: vuelve a pedir orden, sin gastar turno
7BF2  ...                 ; análisis de la orden y turno normal
```

La instrucción de `$7BEC` mira si la línea está vacía. Ocupa 3 bytes, lo mismo que un `CALL`, así que se puede sustituir por `CALL $6000` sin mover nada más. La rutina nueva decide qué hacer y devuelve en `A` lo mismo que habría leído la instrucción original:

- Si lo tecleado **no es** RAMSAVE ni RAMLOAD, ejecuta la instrucción original `LD A,($5B00)` y vuelve. El juego sigue exactamente igual que antes.
- Si **es** una de las dos órdenes, hace su trabajo, escribe un mensaje, deja la línea vacía (`($5B00)=0`) y devuelve `A=0`. El bucle la trata como una línea vacía y vuelve a mostrar el indicador. **No se analiza nada ni pasa un turno.**

## Qué se guarda

El SAVE a cinta del propio juego graba 768 bytes, de `$A1FD` a `$A4FC` (rutina `$788F`), y su LOAD los recupera en el mismo sitio (rutina `$78B3`). Ese bloque es el estado de la partida:

| Dirección | Contenido |
|---|---|
| `$A1FD + 2·n` | localidad del objeto n (palabra; `$7FFF` = lo llevas) |
| `$A403 + n` | contador n |
| `$A481` | contador de turnos (palabra) |
| `$A483...` | marcadores (bits) |
| `$A4A3-$A4E2` | pila de evaluación de las condiciones |
| `$A4E3-$A4FC` | variables del analizador y localidad actual (`$A4ED`) |

Las primeras 512 posiciones son la tabla de localidades de hasta 256 objetos, pero Mega-Corp usa muchos menos: la primera parte define objetos hasta el número 29 y la segunda hasta el 16. El resto de la tabla está siempre a cero. El motor nunca escribe en esas posiciones vacías: las órdenes de coger y dejar solo cambian un objeto si está en la localidad o lo llevas, y los objetos que no existen tienen la localidad 0. Por eso RAMSAVE copia:

- las localidades de los objetos usados: 60 bytes en la primera parte (objetos 0-29) y 34 en la segunda (0-16);
- el bloque completo de `$A3FD` a `$A4FC` (256 bytes): contadores, turnos, marcadores, pila y variables.

En total, 316 bytes en la primera parte y 290 en la segunda, en lugar de 768.

Al recuperar se conservan los dos punteros de análisis de la línea actual (`$A4E8` y `$A4F4`), igual que hace el LOAD original del motor.

## Dónde va la rutina

La rutina, sus textos y la copia ocupan `$6000-$6256` en la primera parte (599 bytes) y `$6000-$623C` en la segunda (573 bytes).

Esa zona pertenece al espacio de trabajo del **editor** de GAC, no al juego. Las aventuras hechas con GAC llevan dentro el programa completo, editor incluido, pero el juego solo usa de esa zona su búfer de texto, de `$5E18` a `$5F16` (256 bytes). El resto lo usan rutinas del editor (el menú y los listados de impresora, el compilador de condiciones) a las que el juego nunca llega. En la cinta original, `$6000-$6316` está entero a cero.

Se ha comprobado de tres formas:

1. Todas las instrucciones del motor que apuntan a `$5F17-$6317` pertenecen a rutinas que el juego no ejecuta nunca.
2. La única rutina que borra esa zona (`$7CBD`, que llena de espacios `$5E18-$6317`) solo se alcanza desde el menú de impresora del editor (`$7D93`), y no hay ningún puntero a ese menú en toda la memoria.
3. En partidas largas en el emulador, vigilando cada escritura en memoria, nada salvo la rutina nueva escribe en esa zona.

## La rutina, paso a paso

### Reconocer la orden

`MATCH` compara la línea con «RAMSAVE» o «RAMLOAD». Salta los espacios iniciales, admite mayúsculas y minúsculas, y exige que la palabra termine ahí, en fin de línea o en espacio. Así, por ejemplo, «RAMSAVEX» no se reconoce.

### RAMSAVE

1. Copia las localidades de los objetos y el bloque `$A3FD-$A4FC` a la copia.
2. Marca que hay una partida guardada (byte `BUF`, en `$611A`).
3. Escribe «Partida guardada en memoria.» con la propia rutina de textos del motor (`$886C`).
4. Vacía la línea para que no se analice.

Solo hay una ranura: cada RAMSAVE sustituye al anterior.

### RAMLOAD

1. Si no hay ninguna partida guardada, escribe «No hay ninguna partida en memoria.» y no hace nada más.
2. Si la hay, guarda los punteros `$A4E8` y `$A4F4` y copia de vuelta las localidades de los objetos y el bloque `$A3FD-$A4FC`.
3. Restaura esos dos punteros y escribe «Partida recuperada de memoria.».
4. **Vuelve a describir la localidad** sin pasar turno. Llama a las mismas rutinas que usa el motor:
   - `LD IX,$A51F`, la base de los punteros de la base de datos, como hace el intérprete de condiciones;
   - `CALL $7334`, que reinicia la pila de evaluación;
   - `CALL $7660`, que apila la localidad actual y salta a `$75B6`, la rutina que dibuja el gráfico y escribe la descripción y los objetos visibles.

   `IX` se guarda y se restaura alrededor de la llamada.
5. Vacía la línea para que no se analice.

Una primera versión volvía a describir la localidad tecleando internamente la orden `R`. Eso funcionaba, pero `R` es una orden normal que gasta un turno. La versión publicada llama directamente a la rutina de descripción, y el estado queda exactamente como estaba al guardar.

## Comportamiento resultante

- Ni RAMSAVE ni RAMLOAD gastan turno.
- Tras RAMLOAD, la partida queda en el mismo punto exacto que al hacer RAMSAVE: localidad, objetos, contadores, marcadores y turnos.
- Hay una sola ranura, y cada RAMSAVE sustituye al anterior.
- La copia se pierde al apagar o reiniciar el Spectrum (o el emulador). En cambio, sobrevive a FIN, porque al empezar de nuevo la aventura el motor solo pone a cero `$A1FD-$A4EF` (rutina `$7B3F`). Comprobado: tras FIN, RAMLOAD devuelve la partida guardada.
- SAVE y LOAD a cinta funcionan como siempre.
- Las dos órdenes también responden en la pantalla de la clave de la segunda parte, porque es el mismo bucle de órdenes. Sin una partida guardada en esa sesión, RAMLOAD no hace nada más que avisar.

## Cómo se ha comprobado

En un emulador de Spectrum 48K, con pruebas automáticas sobre las dos partes:

- **Recuperación exacta.** Hacer RAMSAVE, moverse, coger y dejar objetos, hacer RAMLOAD y comparar byte a byte el bloque de estado `$A1FD-$A4FC` antes y después. Solo difiere `$A4A3`, el primer byte de la pila de evaluación, que el motor sobrescribe en cada turno.
- **Redibujado.** Comprobar en capturas que, tras RAMLOAD, se ven el gráfico, la descripción y los objetos de la localidad guardada.
- **Memoria.** Vigilar todas las escrituras durante partidas largas: nada salvo la rutina nueva escribe en `$6000-$6256`.
- **Cintas.** Comprobar los checksums de las cintas y que el resto de cada bloque es idéntico al original.

## Versión en disco para Spectrum +3

Los ficheros DSK contienen el mismo bloque de 48 KB que la cinta modificada, byte a byte. Lo carga un pequeño cargador para +3DOS (`dsk/fuentes/loader.asm`):

1. Lee el fichero repartiéndolo por los bancos de memoria del +3.
2. Pasa el control a un trozo de código (`stub.asm`) que coloca cada parte en su sitio y bloquea la paginación en modo 48K.
3. Continúa el arranque igual que la cinta: vuelve al BASIC incluido en el volcado, que ejecuta `RANDOMIZE USR 34104`.

El juego no se modifica para la versión en disco.

## Listado de la rutina (primera parte)

En la segunda parte el listado es idéntico salvo `LD BC,34` en lugar de `LD BC,60` (en `$6043` y `$6077`) y el tamaño de la copia (290 bytes en lugar de 316). Los listados completos están en `parche/ramsave_parte1.asm` y `parche/ramsave_parte2.asm`.

```
        ORG $6000
HOOK:     LD HL,$5B00          ; ¿la línea es RAMSAVE?
          LD DE,W_SAVE
          CALL MATCH
          JR Z,DOSAVE
          LD HL,$5B00          ; ¿la línea es RAMLOAD?
          LD DE,W_LOAD
          CALL MATCH
          JR Z,DOLOAD
          LD A,($5B00)         ; instrucción original de $7BEC
          RET

MATCH:    LD A,(HL)            ; saltar espacios iniciales
          CP $20
          JR NZ,M1
          INC HL
          JR MATCH
M1:       LD A,(DE)            ; fin de la palabra buscada
          AND A
          JR Z,MEND
          LD C,A
          LD A,(HL)            ; carácter tecleado, en mayúsculas
          AND $7F
          CP $61
          JR C,M2
          AND $DF
M2:       CP C
          RET NZ               ; NZ: no coincide
          INC HL
          INC DE
          JR M1
MEND:     LD A,(HL)            ; la palabra debe terminar aquí
          AND $7F
          RET Z
          CP $20
          RET                  ; Z: coincide

DOSAVE:   LD HL,$A1FD          ; localidades de los objetos 0-29
          LD DE,BUF+1
          LD BC,60
          LDIR
          LD HL,$A3FD          ; contadores, marcadores y variables
          LD BC,$0100
          LDIR
          LD A,$01             ; hay partida guardada
          LD (BUF),A
          LD HL,T_SAVED
PRTRET:   CALL $886C           ; texto con la rutina del motor
          XOR A                ; línea vacía: no se analiza ni pasa turno
          LD ($5B00),A
          RET

DOLOAD:   LD A,(BUF)
          AND A
          LD HL,T_NONE
          JR Z,PRTRET          ; no hay partida guardada
          LD HL,($A4E8)        ; conservar los punteros de análisis
          PUSH HL
          LD HL,($A4F4)
          PUSH HL
          LD HL,BUF+1          ; recuperar el estado
          LD DE,$A1FD
          LD BC,60
          LDIR
          LD DE,$A3FD
          LD BC,$0100
          LDIR
          POP HL
          LD ($A4F4),HL
          POP HL
          LD ($A4E8),HL
          LD HL,T_LOADED
          CALL $886C
          PUSH IX              ; describir la localidad sin pasar turno
          LD IX,$A51F
          CALL $7334
          CALL $7660
          POP IX
          XOR A
          LD ($5B00),A
          RET

W_SAVE:   DEFM "RAMSAVE"
          DEFB $00
W_LOAD:   DEFM "RAMLOAD"
          DEFB $00
T_SAVED:  DEFB $0D,$0A
          DEFM "Partida guardada en memoria."
          DEFB $FF
T_LOADED: DEFB $0D,$0A
          DEFM "Partida recuperada de memoria."
          DEFB $FF
T_NONE:   DEFB $0D,$0A
          DEFM "No hay ninguna partida en memoria."
          DEFB $FF
BUF:      DEFB $00             ; $611A: 1 = hay partida guardada
                               ; $611B: copia (316 bytes)
```

## Reproducir el parche

`parche/ramsave_patch.py` genera las cintas modificadas a partir de las originales y escribe el listado:

```
python3 ramsave_patch.py "Megacorp - Part 1.tzx" Megacorp1_RAM.tzx ramsave_parte1.asm
python3 ramsave_patch.py "Megacorp - Part 2.tzx" Megacorp2_RAM.tzx ramsave_parte2.asm
```

Necesita Python 3 y SkoolKit (`pip install skoolkit`), cuyo ensamblador usa para el código Z80. Antes de modificar nada comprueba que en `$7BEC` está la instrucción esperada y que la zona de destino está a cero.
