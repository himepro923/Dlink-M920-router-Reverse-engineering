#!/usr/bin/env python3
"""Build a full 16 MB flash image: the stock dump with only the OpenWrt kernel + rootfs swapped in.
Usage: make_full_image.py stock_dump.bin kernel.bin rootfs.bin out.bin
Bootloader/settings (0x0-0x30000) and bank-2 boot area (0x800000-0xb00000) are kept byte-identical.
Refuses to write the file unless the stock loader's own checks (replicated from the disassembled
bootloader) pass for the kernel and the rootfs."""
import struct, sys
stock = open(sys.argv[1], 'rb').read(); k = open(sys.argv[2], 'rb').read(); r = open(sys.argv[3], 'rb').read()
wsum = lambda b: sum(struct.unpack('>%dH' % (len(b) // 2), b)) & 0xFFFF
assert len(stock) == 0x1000000, 'dump must be 16 MB'
assert k[:4] == b'cr6c' and len(k) == 0x2D0000, 'kernel image: cr6c header, 0x2d0000 bytes'
st, burn, ln = struct.unpack('>III', k[4:16])
assert (st, burn) == (0x80A00000, 0x30000), 'kernel header start/burn address'
assert wsum(k[16:16 + ln]) == 0, 'kernel checksum'
assert r[:4] == b'hsqs', 'rootfs is not squashfs'
rl = struct.unpack('>I', r[8:12])[0] + 0x282          # bootloader: length = bswap(word@8) + 0x282
assert rl <= len(r) and rl % 2 == 0 and wsum(r[:rl]) == 0, 'rootfs length field / checksum (loader would say "rootfs checksum error")'
assert len(r) <= 0x500000
o = bytearray(stock)
o[0x30000:0x300000] = k
o[0x300000:0x800000] = r + b'\xff' * (0x500000 - len(r))
o[0xB00000:0x1000000] = b'\xff' * 0x500000
open(sys.argv[4], 'wb').write(o)
print('ok: kernel len %#x, rootfs len %#x, wrote %s' % (ln, rl, sys.argv[4]))
