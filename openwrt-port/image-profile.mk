# Insert inside "ifeq ($(SUBTARGET),rtl8197f)" in target/linux/realtek/image/Makefile.
# STAGE 1 SKETCH - not built. Stock facts: kernel header 'cr6c', start 0x80A00000,
# burn 0x30000; rootfs squashfs at 0x300000 padded to 64 KB, then a 2-byte checksum
# (two's-complement sum of big-endian 16-bit words, the same as cvimg's calculate_checksum).

# The stock loader reads the rootfs length from the SquashFS superblock "mkfs_time" field:
#   len = big-endian word at offset 8 + 0x282, checksummed region = [rootfs, rootfs+len),
#   sum of big-endian 16-bit words must be 0. Pad to 64 KB, set the field, append the checksum.
# (Verified: reproduces the stock rootfs bytes exactly; a build without this field failed with
#  "rootfs checksum error at 00300000!" on the real router.)
# Pad so that data + 2-byte checksum is an exact multiple of 64 KB: the checksum then sits in the
# last two bytes of the last rootfs erase block and the auto-split "rootfs_data" (jffs2 overlay) that
# starts at the next block never contains it, so formatting the overlay cannot destroy the checksum.
define Build/m920-rootfs-sum
	perl -e 'local $$/; open F,"<$@" or die; $$d=<F>; close F; \
	  $$d.="\0" x ((65534-length($$d)%65536+65536)%65536); \
	  substr($$d,8,4)=pack("N",length($$d)+2-0x282); \
	  $$s=0; $$s+=$$_ for unpack("n*",$$d); $$c=(-$$s)&0xffff; \
	  open O,">$@" or die; binmode O; print O $$d, pack("n",$$c); close O'
endef

DEVICE_VARS += LOADER_TEXT_START

define Device/DWRM920
  $(Device/RealtekDTS)
  BLOCKSIZE := 64k
  DEVICE_DTS := DWRM920
  DEVICE_TITLE := D-Link DWR-M920
  SUPPORTED_DEVICES := dlink,dwr-m920
  DEV_PROFILE := DWRM920
  IMAGE_SIZE := 5120k
  CMDLINE := console=ttyS0,38400
  KERNEL := kernel-bin | append-dtb | lzma | loader-cmdline-compile
  CVIMG_KERNEL_BURN_ADDR := 0x30000
  CVIMG_LOADER_START_ADDR := 0x80A00000
  CVIMG_CUSTOM_SIGNATURE := cr6c
  # The Realtek loader copies the image to the header start address and jumps there, so the
  # lzma stub must be LINKED at that address (stock: 0x80A00000). Default 0x81000000 would crash.
  LOADER_TEXT_START := 0x80A00000
  IMAGES := kernel.bin rootfs.bin
  IMAGE/kernel.bin = append-kernel | cvimg-custom | pad-to 2880k
  IMAGE/rootfs.bin = append-rootfs | m920-rootfs-sum
  DEVICE_PACKAGES := kmod-usb-core kmod-usb-ohci kmod-usb2 kmod-usb-net-cdc-ether \
	kmod-usb-serial-option swconfig ppp
endef
TARGET_DEVICES += DWRM920
