# Insert inside "ifeq ($(SUBTARGET),rtl8197f)" in target/linux/realtek/image/Makefile.
# STAGE 1 SKETCH - not built. Stock facts: kernel header 'cr6c', start 0x80A00000,
# burn 0x30000; rootfs squashfs at 0x300000 padded to 64 KB, then a 2-byte checksum
# (two's-complement sum of big-endian 16-bit words, the same as cvimg's calculate_checksum).

# pad squashfs to 64 KB, append the 16-bit checksum (checked against the stock image)
define Build/m920-rootfs-sum
	perl -e 'local $$/; open F,"<$@" or die; $$d=<F>; close F; \
	  $$d.="\0" x ((65536-length($$d)%65536)%65536); \
	  $$s=0; $$s+=$$_ for unpack("n*",$$d); $$c=(-$$s)&0xffff; \
	  open O,">$@" or die; binmode O; print O $$d, pack("n",$$c); close O'
endef

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
  IMAGES := kernel.bin rootfs.bin
  IMAGE/kernel.bin = append-kernel | cvimg-custom | pad-to 2816k
  IMAGE/rootfs.bin = append-rootfs | m920-rootfs-sum
  DEVICE_PACKAGES := kmod-usb-core kmod-usb-ohci kmod-usb2 kmod-usb-net-cdc-ether \
	kmod-usb-serial-option swconfig ppp
endef
TARGET_DEVICES += DWRM920
