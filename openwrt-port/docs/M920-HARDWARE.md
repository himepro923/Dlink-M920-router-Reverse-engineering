# D-Link DWR-M920 (Zain, hw A1, fw DWR-M920B_ZAIN_V1.0.30) - hardware map

Sources: full SPI dump (rom.bin) and the stock serial boot log. Nothing here was run on OpenWrt.

## SoC / memory / flash
- Realtek RTL8197F-VG (kernel reports "8197FH-VG"), MIPS 24Kc, bootloader "v3.4.14, 999MHz", built 2023.04.11
- 128 MB DDR2 @ 533 MHz
- SPI NOR: EON EN25QH128A, JEDEC 1C7018, 16 MB, 64 KB erase, bootloader runs it at 75 MHz
- Console: ttyS0, 38400 8N1 (UART at 0x18147000)
- Stock kernel 3.10.90 (Realtek SDK 3.4.14), cmdline `console=ttyS0,38400 root=/dev/mtdblock1`

## Flash map (stock; bank 2 is a complete copy of bank 1 at +0x800000)
| offset | size | content |
|---|---|---|
| 0x000000 | 0x20000 | two-stage bootloader |
| 0x020000 | | 'H601' hardware settings (MAC, RF calibration) - read-only for us |
| 0x02A000 | | 'COMPCS' compressed current settings |
| 0x030000 | 0x2D0000 | kernel image: 'cr6c' header (start 0x80A00000, burn 0x30000), LZMA payload, 2-byte checksum |
| 0x300000 | 0x500000 | SquashFS 4.0 (xz) padded to 64 KB + 2-byte checksum |
| 0x800000-0xFFFFFF | | bank 2 (same layout) |
Kernel mtd names: boot+cfg+linux, rootfs, boot+cfg+linux2, rootfs2 ("rtkxxpart" parser).
Checksum rule (verified on all four regions): sum of big-endian 16-bit words, checksum included, == 0.
A bad bank-1 checksum hangs the loader (no automatic fallback to bank 2 observed).

## Ports (internal switch, no external switch chip)
eth1 = WAN, switch port mask 0x01 (vid 8); eth0/eth2/eth3/eth4 = LAN, masks 0x02/0x04/0x08/0x10 (vid 9).
Stock log: "INIT swCore descriptor count Failed : (0 [0])" appears at NIC probe (harmless in stock).
Bootloader banner: "M920_ZAIN disable switch/ETH during boot".

## Wi-Fi
2.4 GHz only (wlan0), vendor driver "Realtek WLAN driver 3.8.0 (2017-12-26)". PCIe: "Cannot LinkUP" (nothing attached).

## USB / modem
- On-chip EHCI @0x18021000 and OHCI @0x18020000, IRQ 21, ONE root port, modem attached directly.
- Modem: Quectel 2c7c:6005 ("Android"). Interfaces: 1.0 cdc_ether -> usb0 (ECM, gets IP by DHCP);
  1.2 and 1.3 -> `option` serial, ttyUSB0 / ttyUSB1 (AT commands).
- Stock AT sequence: AT+CFUN=1, AT+QCFG="band",FFFF,FFFFFFFF, AT+COPS=3,2, AT+CGREG=1,
  AT+QCFG="nwscanmode",0, AT+QCUSDCVT=1, AT+QNETDEVCTL=0 then =3,1 (module dials itself, DHCP on usb0).
- USB PHY bring-up values printed by the stock kernel (40 MHz OSC patch), port 0 PHY regs:
  e0=e2 e1=31 e2=39 e3=8d e4=91 e5=19 e6=c0 e7=91 f0=fc f1=8c f2=00 f3=11 f4=9b f5=15 f6=00
  system regs: b8000010=80043000 b8000014=118 b8000160=1 b8000164=0 b8000168=0 b800016c=10280500
  b8000180=60000 b8021094=200020 b8140200=f902cc11 b8140204=0 b8140208=2010000 b814020c=1b91 b8140210=ca00ca
  EHCI b8021050=0 b8021054=2000 b8021058=0; OHCI b8020000=110 b8020004=0
  Reference code: Realtek SDK mirror, target/linux/rtkmipsel/files/arch/mips/rtl8197f/dev_usb.c

## Not known yet
LED / button / modem reset+power GPIOs; internal switch PHY init for the DIR-842 driver; the loader's
exact rootfs length rule (the build step pads to 64 KB then appends the checksum, which reproduces
the stock bytes exactly); whether the loader can RAM-boot an image.
