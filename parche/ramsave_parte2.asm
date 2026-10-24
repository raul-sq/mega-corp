; Parche RAMSAVE/RAMLOAD - Mega-Corp, segunda parte
; objetos: max n.16 -> 34 bytes + 256 bytes de variables
; codigo $6000-$611A (283 bytes), copia $611A-$623C (291 bytes)
; enganche: $7BEC  LD A,($5B00)  ->  CALL $6000

        ORG $6000
HOOK:     LD HL,$5B00                       ; $6000  21 00 5B
          LD DE,W_SAVE                      ; $6003  11 A5 60
          CALL MATCH                        ; $6006  CD 1A 60
          JR Z,DOSAVE                       ; $6009  28 32
          LD HL,$5B00                       ; $600B  21 00 5B
          LD DE,W_LOAD                      ; $600E  11 AD 60
          CALL MATCH                        ; $6011  CD 1A 60
          JR Z,DOLOAD                       ; $6014  28 4A
          LD A,($5B00)                      ; $6016  3A 00 5B
          RET                               ; $6019  C9
MATCH:    LD A,(HL)                         ; $601A  7E
          CP $20                            ; $601B  FE 20
          JR NZ,M1                          ; $601D  20 03
          INC HL                            ; $601F  23
          JR MATCH                          ; $6020  18 F8
M1:       LD A,(DE)                         ; $6022  1A
          AND A                             ; $6023  A7
          JR Z,MEND                         ; $6024  28 10
          LD C,A                            ; $6026  4F
          LD A,(HL)                         ; $6027  7E
          AND $7F                           ; $6028  E6 7F
          CP $61                            ; $602A  FE 61
          JR C,M2                           ; $602C  38 02
          AND $DF                           ; $602E  E6 DF
M2:       CP C                              ; $6030  B9
          RET NZ                            ; $6031  C0
          INC HL                            ; $6032  23
          INC DE                            ; $6033  13
          JR M1                             ; $6034  18 EC
MEND:     LD A,(HL)                         ; $6036  7E
          AND $7F                           ; $6037  E6 7F
          RET Z                             ; $6039  C8
          CP $20                            ; $603A  FE 20
          RET                               ; $603C  C9
DOSAVE:   LD HL,$A1FD                       ; $603D  21 FD A1
          LD DE,BUF+1                       ; $6040  11 1B 61
          LD BC,34                          ; $6043  01 22 00
          LDIR                              ; $6046  ED B0
          LD HL,$A3FD                       ; $6048  21 FD A3
          LD BC,$0100                       ; $604B  01 00 01
          LDIR                              ; $604E  ED B0
          LD A,$01                          ; $6050  3E 01
          LD (BUF),A                        ; $6052  32 1A 61
          LD HL,T_SAVED                     ; $6055  21 B5 60
PRTRET:   CALL $886C                        ; $6058  CD 6C 88
          XOR A                             ; $605B  AF
          LD ($5B00),A                      ; $605C  32 00 5B
          RET                               ; $605F  C9
DOLOAD:   LD A,(BUF)                        ; $6060  3A 1A 61
          AND A                             ; $6063  A7
          LD HL,T_NONE                      ; $6064  21 F5 60
          JR Z,PRTRET                       ; $6067  28 EF
          LD HL,($A4E8)                     ; $6069  2A E8 A4
          PUSH HL                           ; $606C  E5
          LD HL,($A4F4)                     ; $606D  2A F4 A4
          PUSH HL                           ; $6070  E5
          LD HL,BUF+1                       ; $6071  21 1B 61
          LD DE,$A1FD                       ; $6074  11 FD A1
          LD BC,34                          ; $6077  01 22 00
          LDIR                              ; $607A  ED B0
          LD DE,$A3FD                       ; $607C  11 FD A3
          LD BC,$0100                       ; $607F  01 00 01
          LDIR                              ; $6082  ED B0
          POP HL                            ; $6084  E1
          LD ($A4F4),HL                     ; $6085  22 F4 A4
          POP HL                            ; $6088  E1
          LD ($A4E8),HL                     ; $6089  22 E8 A4
          LD HL,T_LOADED                    ; $608C  21 D4 60
          CALL $886C                        ; $608F  CD 6C 88
          PUSH IX                           ; $6092  DD E5
          LD IX,$A51F                       ; $6094  DD 21 1F A5
          CALL $7334                        ; $6098  CD 34 73
          CALL $7660                        ; $609B  CD 60 76
          POP IX                            ; $609E  DD E1
          XOR A                             ; $60A0  AF
          LD ($5B00),A                      ; $60A1  32 00 5B
          RET                               ; $60A4  C9
W_SAVE:   DEFM "RAMSAVE"                    ; $60A5  52 41 4D 53 41 56 45
          DEFB $00                          ; $60AC  00
W_LOAD:   DEFM "RAMLOAD"                    ; $60AD  52 41 4D 4C 4F 41 44
          DEFB $00                          ; $60B4  00
T_SAVED:  DEFB $0D,$0A                      ; $60B5  0D 0A
          DEFM "Partida guardada en memoria."; $60B7  50 61 72 74 69 64 61 20 67 75 61 72 64 61 64 61 20 65 6E 20 6D 65 6D 6F 72 69 61 2E
          DEFB $FF                          ; $60D3  FF
T_LOADED: DEFB $0D,$0A                      ; $60D4  0D 0A
          DEFM "Partida recuperada de memoria."; $60D6  50 61 72 74 69 64 61 20 72 65 63 75 70 65 72 61 64 61 20 64 65 20 6D 65 6D 6F 72 69 61 2E
          DEFB $FF                          ; $60F4  FF
T_NONE:   DEFB $0D,$0A                      ; $60F5  0D 0A
          DEFM "No hay ninguna partida en memoria."; $60F7  4E 6F 20 68 61 79 20 6E 69 6E 67 75 6E 61 20 70 61 72 74 69 64 61 20 65 6E 20 6D 65 6D 6F 72 69 61 2E
          DEFB $FF                          ; $6119  FF
BUF:      DEFB $00                          ; $611A  00
BUFDATA:  DEFS 290                      ; $611B
