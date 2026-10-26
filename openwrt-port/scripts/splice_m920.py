#!/usr/bin/env python3
"""Insert the DWR-M920 device profile into target/linux/realtek/image/Makefile (inside the rtl8197f block)."""
import sys
mk, prof = sys.argv[1], sys.argv[2]
lines = open(mk).read().split('\n')
snippet = open(prof).read().rstrip('\n').split('\n')
if any('Device/DWRM920' in l for l in lines):
    sys.exit('already spliced')
i = next(n for n, l in enumerate(lines) if l.strip() == 'ifeq ($(SUBTARGET),rtl8196e)')
j = max(n for n in range(i) if lines[n].strip() == 'endif')   # endif closing the rtl8197f block
lines[j:j] = [''] + snippet + ['']
text = '\n'.join(lines)
old = 'LZMA_TEXT_START=0x81000000'
assert text.count(old) == 1, 'loader-common not found'
text = text.replace(old, 'LZMA_TEXT_START=$(if $(LOADER_TEXT_START),$(LOADER_TEXT_START),0x81000000)')
open(mk, 'w').write(text)
print('spliced DWRM920 profile before line', j + 1)
