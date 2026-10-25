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
open(mk, 'w').write('\n'.join(lines))
print('spliced DWRM920 profile before line', j + 1)
