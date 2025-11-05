# QWAMOS Phase 10: USB Kill Switch Kernel Module Makefile
# =========================================================

obj-m += usb_killswitch.o

# Kernel source directory (adjust for your device)
KDIR ?= /lib/modules/$(shell uname -r)/build

# Cross-compile toolchain (for Android ARM64)
ARCH ?= arm64
CROSS_COMPILE ?= aarch64-linux-android-

all:
	$(MAKE) -C $(KDIR) M=$(PWD) ARCH=$(ARCH) CROSS_COMPILE=$(CROSS_COMPILE) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

install:
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install

.PHONY: all clean install
