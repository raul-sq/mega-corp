; Stub de arranque: se copia a 5D2Dh (workspace libre de la imagen, entre STKEND y la pila)
; Entrada: DI, ROM2/pag.7 aun paginadas, motor apagado.
; Pag.1 @C000 = imagen 5B00h-7FFFh (desde C000h+1B00h); pag.3 = imagen 8000h-BFFFh;
; pag.0 = imagen C000h-FFFFh (ya en su sitio); pantalla ya en 4000h.
        org 5D2Dh
stub:   ld bc,7FFDh
        ld a,11h            ; pag.1 en C000h; ROM3 (1FFDh ya vale 04h tras DOS_MOTOR_OFF)
        out (c),a
        ld hl,0DB00h        ; 5B00h..stub-1
        ld de,5B00h
        ld bc,stub-5B00h
        ldir
        ld hl,0DB00h+(stubend-5B00h)   ; stubend..7FFFh
        ld de,stubend
        ld bc,8000h-stubend
        ldir
        ld bc,7FFDh
        ld a,13h            ; pag.3 en C000h
        out (c),a
        ld hl,0C000h
        ld de,8000h
        ld bc,4000h
        ldir
        ld bc,7FFDh
        ld a,30h            ; pag.0, ROM3, paginacion bloqueada (modo 48K)
        out (c),a
        ld iy,5C3Ah
        exx
        ld hl,2758h
        exx
        ld sp,5DBAh         ; pila de la imagen: RET -> 1B76h STMT-RET
        ei                  ; el BASIC de la imagen sigue con ': RANDOMIZE USR 34104'
        ret
stubend:
