BANKM    equ 5B5Ch
BANK678  equ 5B67h
DOS_OPEN equ 0106h
DOS_CLOSE equ 0109h
DOS_READ equ 0112h
DOS_MOTOR_OFF equ 019Ch
STUB     equ 5D2Dh

        org 8000h
start:  di
        ld a,(BANKM)
        and 0E8h
        or 07h              ; pag.7, bit ROM bajo = 0
        ld bc,7FFDh
        ld (BANKM),a
        out (c),a
        ld a,(BANK678)
        or 04h              ; bit ROM alto = 1 -> ROM2 (+3DOS)
        ld b,1Fh
        ld (BANK678),a
        out (c),a
        ei
        ld bc,0001h         ; fichero 0, lectura exclusiva
        ld de,0001h         ; abrir existente saltando cabecera +3DOS
        ld hl,fname
        call DOS_OPEN
        jr nc,error
        ld c,0
        ld de,6912
        ld hl,4000h         ; pantalla directamente
        call rd
        ld c,1
        ld de,9472
        ld hl,0DB00h        ; 5B00h-7FFFh -> pag.1
        call rd
        ld c,3
        ld de,16384
        ld hl,0C000h        ; 8000h-BFFFh -> pag.3
        call rd
        ld c,0
        ld de,16384
        ld hl,0C000h        ; C000h-FFFFh -> pag.0 (destino final)
        call rd
        ld b,0
        call DOS_CLOSE
        call DOS_MOTOR_OFF
        di
        ld hl,stubsrc
        ld de,STUB
        ld bc,stubsrc_end-stubsrc
        ldir
        jp STUB

rd:     ld b,0
        call DOS_READ
        ret c
        pop hl              ; descartar retorno
error:  di
        ld a,(BANKM)
        and 0E8h
        or 10h              ; pag.0, ROM3
        ld bc,7FFDh
        ld (BANKM),a
        out (c),a
        ei
        ret                 ; vuelve al BASIC (linea 20: mensaje de error)

fname:
        include "fname.inc"
stubsrc:
        incbin "stub.bin"
stubsrc_end:
