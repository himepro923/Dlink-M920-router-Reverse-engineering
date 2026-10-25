#!/usr/bin/env python3
"""m920_fixsum.py - fix the Realtek 16-bit checksums in a D-Link M920 (RTL8197F) 16MB SPI dump.

Layout (derived from the dump; bank A shown, bank B is +0x800000):
  kernel : header 'cr6c' at 0x30000 (16 bytes), payload 0x30010, length = header[12:16]
           (includes a 2-byte checksum at its end)
  rootfs : SquashFS at 0x300000, region 0x450002 bytes: 0x450000 data (zero padded)
           + 2-byte checksum at 0x750000
Rule: the sum of all big-endian 16-bit words in a region, checksum included, == 0 (mod 65536).

Usage:
  m920_fixsum.py check  rom.bin
  m920_fixsum.py fix    rom.bin out.bin [--bank A|B|both]            # after you hex-edited rom.bin
  m920_fixsum.py fix    rom.bin out.bin --rootfs new.squashfs [--bank A|B|both]
Default bank is A only; bank B stays as an untouched fallback.
"""
import sys, struct, argparse
BANKS = {'A': (0x30000, 0x300000), 'B': (0x830000, 0xB00000)}
ROOT_DATA = 0x450000          # padded squashfs size inside the region
def wsum(b):
    assert len(b) % 2 == 0
    return sum(struct.unpack('>%dH' % (len(b)//2), b)) & 0xFFFF
def regions(d, bank):
    k, r = BANKS[bank]
    if d[k:k+4] != b'cr6c': raise SystemExit(f'bank {bank}: no cr6c header at {k:#x}')
    klen = struct.unpack('>I', d[k+12:k+16])[0]
    if d[r:r+4] != b'hsqs': raise SystemExit(f'bank {bank}: no squashfs at {r:#x}')
    return (k+16, klen), (r, ROOT_DATA+2)
def fix_region(d, off, ln):
    s = wsum(bytes(d[off:off+ln-2]))
    d[off+ln-2:off+ln] = struct.pack('>H', (-s) & 0xFFFF)
def check(d):
    ok = True
    for bank in BANKS:
        for name, (off, ln) in zip(('kernel', 'rootfs'), regions(d, bank)):
            s = wsum(bytes(d[off:off+ln]))
            print(f'bank {bank} {name}: {off:#x}+{ln:#x} sum={s:#06x} {"OK" if s == 0 else "BAD"} (stored {d[off+ln-2:off+ln].hex()})')
            ok &= (s == 0)
    return ok
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['check', 'fix']); ap.add_argument('inp'); ap.add_argument('out', nargs='?')
    ap.add_argument('--bank', default='A', choices=['A', 'B', 'both']); ap.add_argument('--rootfs')
    a = ap.parse_args()
    d = bytearray(open(a.inp, 'rb').read())
    if len(d) != 0x1000000: raise SystemExit('expected a 16 MB (0x1000000) full-flash dump')
    if a.cmd == 'check': sys.exit(0 if check(d) else 1)
    if not a.out: raise SystemExit('need an output file')
    for bank in (BANKS if a.bank == 'both' else [a.bank]):
        (ko, kl), (ro, rl) = regions(d, bank)
        if a.rootfs:
            fs = open(a.rootfs, 'rb').read()
            if fs[:4] != b'hsqs': raise SystemExit('--rootfs is not a SquashFS image')
            if len(fs) > ROOT_DATA: raise SystemExit(f'squashfs too big: {len(fs):#x} > {ROOT_DATA:#x}')
            d[ro:ro+ROOT_DATA] = fs + b'\0' * (ROOT_DATA - len(fs))
        fix_region(d, ko, kl); fix_region(d, ro, rl)
    open(a.out, 'wb').write(d)
    print('written', a.out); check(bytearray(d))
main()
