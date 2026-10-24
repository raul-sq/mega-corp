"""Parche RAMSAVE / RAMLOAD para Mega-Corp (Dinamic, 1987; motor GAC, ZX Spectrum 48K).

Uso: python3 ramsave_patch.py original.tzx parcheado.tzx listado.asm
Requiere: Python 3 y SkoolKit (pip install skoolkit), cuyo ensamblador Z80 usa.

- Engancha el bucle de ordenes en $7BEC (LD A,($5B00) -> CALL HOOK).
- Guarda solo el estado de partida que usa el juego:
    posiciones de objetos   $A1FD .. $A1FD+2*(max_obj+1)-1
    contadores/marcadores   $A3FD .. $A4FC (256 bytes)
  (el SAVE de cinta original guarda $A1FD-$A4FC, 768 bytes; la parte de la
  tabla de objetos sin objetos es siempre cero y no hace falta copiarla).
- Codigo y copia van en $6000-$6316, espacio de trabajo del editor GAC
  que el juego no usa.
- RAMLOAD vuelve a describir la localidad llamando a $7334 y $7660 del motor,
  sin pasar turno.
- Explicacion completa: CAMBIOS.md
"""
import struct, sys, re
from skoolkit.z80 import Assembler

BASE = 0x6000
PATCH_AT = 0x7BEC
PRINT = 0x886C          # imprime texto terminado en $FF
INBUF = 0x5B00          # linea de ordenes (mayusculas, termina en 0)
OBJTAB = 0xA1FD
VARS = 0xA3FD


TAIL_LOOK = """        PUSH IX
        LD IX,$A51F
        CALL $7334
        CALL $7660
        POP IX
        XOR A
        LD ($5B00),A
        RET
"""


def program(nobj_bytes):
    return f"""
HOOK:   LD HL,$5B00
        LD DE,W_SAVE
        CALL MATCH
        JR Z,DOSAVE
        LD HL,$5B00
        LD DE,W_LOAD
        CALL MATCH
        JR Z,DOLOAD
        LD A,($5B00)
        RET
MATCH:  LD A,(HL)
        CP $20
        JR NZ,M1
        INC HL
        JR MATCH
M1:     LD A,(DE)
        AND A
        JR Z,MEND
        LD C,A
        LD A,(HL)
        AND $7F
        CP $61
        JR C,M2
        AND $DF
M2:     CP C
        RET NZ
        INC HL
        INC DE
        JR M1
MEND:   LD A,(HL)
        AND $7F
        RET Z
        CP $20
        RET
DOSAVE: LD HL,$A1FD
        LD DE,BUF+1
        LD BC,{nobj_bytes}
        LDIR
        LD HL,$A3FD
        LD BC,$0100
        LDIR
        LD A,$01
        LD (BUF),A
        LD HL,T_SAVED
PRTRET: CALL $886C
        XOR A
        LD ($5B00),A
        RET
DOLOAD: LD A,(BUF)
        AND A
        LD HL,T_NONE
        JR Z,PRTRET
        LD HL,($A4E8)
        PUSH HL
        LD HL,($A4F4)
        PUSH HL
        LD HL,BUF+1
        LD DE,$A1FD
        LD BC,{nobj_bytes}
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
{TAIL_LOOK}W_SAVE: DEFM "RAMSAVE"
        DEFB $00
W_LOAD: DEFM "RAMLOAD"
        DEFB $00
T_SAVED: DEFB $0D,$0A
        DEFM "Partida guardada en memoria."
        DEFB $FF
T_LOADED: DEFB $0D,$0A
        DEFM "Partida recuperada de memoria."
        DEFB $FF
T_NONE: DEFB $0D,$0A
        DEFM "No hay ninguna partida en memoria."
        DEFB $FF
BUF:    DEFB $00
"""


def assemble(src, org):
    asm = Assembler()
    lines = []
    for raw in src.strip("\n").split("\n"):
        m = re.match(r"^(\w+):\s*(.*)$", raw.strip())
        label, ins = (m.group(1), m.group(2).strip()) if m else (None, raw.strip())
        lines.append((label, ins))
    labels = {}
    for pass_no in (1, 2):
        addr, out, listing = org, bytearray(), []
        for label, ins in lines:
            if label:
                labels[label] = addr
            if not ins:
                continue
            def sub(mo):
                name = mo.group(0)
                if name in labels:
                    return "${:04X}".format(labels[name])
                return "${:04X}".format(addr) if pass_no == 1 else name
            ins2 = re.sub(r"\b[A-Z_][A-Z_0-9]*\+?\d*\b", lambda mo: mo.group(0), ins)
            ins2 = re.sub(r"\b(?:HOOK|MATCH|M1|M2|MEND|DOSAVE|DOLOAD|PRTRET|W_SAVE|W_LOAD|T_SAVED|T_LOADED|T_NONE|BUF)\b", sub, ins)
            ins2 = re.sub(r"\$([0-9A-F]{4})\+(\d+)", lambda mo: "${:04X}".format(int(mo.group(1), 16) + int(mo.group(2))), ins2)
            code = asm.assemble(ins2, addr)
            if not code:
                raise SystemExit(f"no se pudo ensamblar: {ins2!r} en ${addr:04X}")
            listing.append((addr, bytes(code), (label + ":") if label else "", ins))
            out += bytes(code)
            addr += len(code)
    return bytes(out), labels, listing


def tzx_blocks(data):
    p, blocks = 10, []
    while p < len(data):
        bid = data[p]
        if bid == 0x10:
            ln = struct.unpack_from("<H", data, p + 3)[0]
            blocks.append((p, p + 5, ln))
            p += 5 + ln
        elif bid == 0x30:
            p += 2 + data[p + 1]
        elif bid == 0x32:
            p += 3 + struct.unpack_from("<H", data, p + 1)[0]
        else:
            raise SystemExit(f"bloque TZX no previsto {bid:#x}")
    return blocks


def main(src_tzx, dst_tzx, lst_path):
    tzx = bytearray(open(src_tzx, "rb").read())
    blocks = tzx_blocks(tzx)
    # bloque de codigo principal: el que, segun su cabecera, cubre el motor GAC
    # (en Mega-Corp: bloque de 48K cargado en $4000)
    org = None
    for i, (_, st, ln) in enumerate(blocks[:-1]):
        if ln == 19 and tzx[st] == 0x00 and tzx[st + 1] == 3:          # cabecera CODE
            length, addr = struct.unpack_from("<HH", tzx, st + 12)
            if addr <= BASE and addr + length >= 0xA540 and blocks[i + 1][2] == length + 2:
                start, org, dlen = blocks[i + 1][1], addr, length
    assert org is not None, "no encuentro el bloque de codigo del motor"
    mem = bytearray(65536)
    mem[org:org + dlen] = tzx[start + 1:start + 1 + dlen]

    # numero de objetos usados: tabla de objetos en ($A523)
    p = struct.unpack_from("<H", mem, 0xA523)[0]
    maxobj = 0
    while mem[p]:
        maxobj = max(maxobj, mem[p])
        p += 2 + mem[p + 1]
    nobj_bytes = 2 * (maxobj + 1)

    assert mem[PATCH_AT:PATCH_AT + 3] == bytes([0x3A, 0x00, 0x5B]), "punto de enganche distinto"
    code, labels, listing = assemble(program(nobj_bytes), BASE)
    buf_end = labels["BUF"] + 1 + nobj_bytes + 256
    assert buf_end <= 0x6317, f"no cabe: termina en {buf_end:#x}"
    assert not any(mem[BASE:buf_end]), "zona de destino no esta a cero"

    mem[BASE:BASE + len(code)] = code
    hook = labels["HOOK"]
    mem[PATCH_AT:PATCH_AT + 3] = bytes([0xCD, hook & 0xFF, hook >> 8])

    payload = bytes([0xFF]) + bytes(mem[org:org + dlen])
    chk = 0
    for b in payload:
        chk ^= b
    tzx[start:start + dlen + 2] = payload + bytes([chk])
    open(dst_tzx, "wb").write(tzx)

    with open(lst_path, "w") as f:
        f.write(f"; Parche RAMSAVE/RAMLOAD - {src_tzx}\n")
        f.write(f"; objetos: max n.{maxobj} -> {nobj_bytes} bytes + 256 bytes de variables\n")
        f.write(f"; codigo ${BASE:04X}-${BASE + len(code) - 1:04X} ({len(code)} bytes), "
                f"copia ${labels['BUF']:04X}-${buf_end - 1:04X} ({buf_end - labels['BUF']} bytes)\n")
        f.write(f"; enganche: ${PATCH_AT:04X}  LD A,($5B00)  ->  CALL ${hook:04X}\n\n")
        f.write(f"        ORG ${BASE:04X}\n")
        for addr, b, label, ins in listing:
            f.write(f"{label:<10}{ins:<34}; ${addr:04X}  {b.hex(' ').upper()}\n")
        f.write(f"BUFDATA:  DEFS {nobj_bytes + 256}                      ; ${labels['BUF'] + 1:04X}\n")
    print(f"{src_tzx}: max obj {maxobj}, codigo {len(code)} B, copia {1 + nobj_bytes + 256} B, "
          f"total ${BASE:04X}-${buf_end - 1:04X} ({buf_end - BASE} B), HOOK=${hook:04X}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
