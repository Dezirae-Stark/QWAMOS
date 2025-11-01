# ARM64 Compilation Environment
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-android-
export CC=clang
export CXX=clang++
export AR=llvm-ar
export NM=llvm-nm
export OBJCOPY=llvm-objcopy
export OBJDUMP=llvm-objdump
export READELF=llvm-readelf
export STRIP=llvm-strip
export CFLAGS="-march=armv8-a -O2"
export CXXFLAGS="-march=armv8-a -O2"
