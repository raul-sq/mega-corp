"""Genera un DSK de Spectrum +3 (Extended CPCEMU) con ficheros +3DOS."""
import struct, sys, subprocess, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tzxdump import blocks

TRACKS, SECS, SECSZ = 40, 9, 512

def plus3hdr(ftype, data, p1, p2):
    total = 128 + len(data)
    h = bytearray(128)
    h[0:8] = b'PLUS3DOS'; h[8] = 0x1A; h[9] = 1; h[10] = 0
    h[11:15] = struct.pack('<I', total)
    h[15] = ftype
    h[16:22] = struct.pack('<HHH', len(data), p1, p2)
    h[127] = sum(h[:127]) & 0xFF
    return bytes(h) + data

def num(n):  # literal BASIC con forma de 5 bytes
    return str(n).encode() + b'\x0e\x00\x00' + struct.pack('<H', n) + b'\x00'

def line(no, body):
    body += b'\x0d'
    return struct.pack('>H', no) + struct.pack('<H', len(body)) + body

def basic_disk(ldrname):
    B, P, I, CL, LD, CO, RA, US, CLS, PR = 0xE7,0xDA,0xD9,0xFD,0xEF,0xAF,0xF9,0xC0,0xFB,0xF5
    t = lambda x: bytes([x])
    l10 = (t(B)+num(0)+b':'+t(P)+num(0)+b':'+t(I)+num(0)+b':'+t(CL)+num(32767)+b':'
           +t(LD)+b'"'+ldrname.encode()+b'"'+t(CO)+num(32768)+b':'+t(RA)+t(US)+num(32768))
    l20 = (t(B)+num(7)+b':'+t(P)+num(7)+b':'+t(I)+num(0)+b':'+t(CLS)+b':'+t(PR)+b'"Error de disco"')
    return line(10, l10) + line(20, l20)

def cpm_name(n):
    base, _, ext = n.partition('.')
    return base.upper().ljust(8).encode() + ext.upper().ljust(3).encode()

def build(files, out):
    nblocks = (TRACKS-1)*SECS*SECSZ//1024          # 175
    data = bytearray(b'\xe5'*(TRACKS*SECS*SECSZ))
    spec = bytes([0,0,TRACKS,SECS,2,1,3,2,0x2A,0x52]) + bytes(6)
    data[0:16] = spec
    dirent = []
    nextblk = 2                                      # bloques 0-1 = directorio
    def blkoff(b):  # offset lineal (pista 1 en adelante)
        return SECS*SECSZ + b*1024
    for name, content in files:
        recs = (len(content)+127)//128
        nb = (len(content)+1023)//1024
        blks = list(range(nextblk, nextblk+nb)); nextblk += nb
        assert nextblk <= nblocks
        for i, b in enumerate(blks):
            chunk = content[i*1024:(i+1)*1024]
            data[blkoff(b):blkoff(b)+len(chunk)] = chunk
        ext = 0
        while recs > 0 or ext == 0:
            r = min(recs, 128); eb = blks[ext*16:(ext+1)*16]
            e = bytes([0]) + cpm_name(name) + bytes([ext, 0, 0, r]) + bytes(eb) + bytes(16-len(eb))
            dirent.append(e); recs -= r; ext += 1
    d = b''.join(dirent)
    assert len(d) <= 2048
    data[blkoff(0):blkoff(0)+len(d)] = d
    # contenedor Extended DSK
    tsize = 256 + SECS*SECSZ
    hdr = bytearray(256)
    hdr[0:34] = b'EXTENDED CPC DSK File\r\nDisk-Info\r\n'
    hdr[34:48] = b'mkdsk.py'.ljust(14)
    hdr[48] = TRACKS; hdr[49] = 1
    for t in range(TRACKS): hdr[52+t] = tsize >> 8
    outb = bytearray(hdr)
    for t in range(TRACKS):
        th = bytearray(256)
        th[0:12] = b'Track-Info\r\n'; th[16] = t; th[17] = 0
        th[20] = 2; th[21] = SECS; th[22] = 0x2A; th[23] = 0xE5
        for s in range(SECS):
            th[24+8*s:32+8*s] = bytes([t, 0, s+1, 2, 0, 0]) + struct.pack('<H', SECSZ)
        outb += th + data[t*SECS*SECSZ:(t+1)*SECS*SECSZ]
    open(out, 'wb').write(outb)

if __name__ == '__main__':
    tzx, datname, out = sys.argv[1:4]
    here = os.path.dirname(os.path.abspath(__file__))
    b = [x for x in blocks(tzx) if x[0] == 0x10]
    code = b[3][2][1:-1]
    assert len(code) == 49152
    open(os.path.join(here, 'fname.inc'), 'w').write('        db "%s",0FFh\n' % datname)
    subprocess.run(['pasmo', 'loader.asm', 'loader.bin', 'loader.sym'], cwd=here, check=True)
    ldr = open(os.path.join(here, 'loader.bin'), 'rb').read()
    bas = basic_disk('MEGALDR')
    files = [('DISK', plus3hdr(0, bas, 10, len(bas))),
             ('MEGALDR', plus3hdr(3, ldr, 32768, 32768)),
             (datname, plus3hdr(3, code, 16384, 32768))]
    build(files, out)
    print(out, os.path.getsize(out), 'loader', len(ldr))
