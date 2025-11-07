#!/system/bin/sh
# QWAMOS Late Start Service
# Runs after boot is complete

MODDIR=${0%/*}

# Wait for boot to complete
while [ "$(getprop sys.boot_completed)" != "1" ]; do
  sleep 1
done

# Wait for Magisk to be ready
sleep 5

# Log startup
LOG_FILE="/data/qwamos/logs/magisk_service.log"
echo "$(date): QWAMOS Magisk service starting..." >> $LOG_FILE

# Load kernel modules (if available)
if [ -f "/system/lib/modules/kvm.ko" ]; then
  insmod /system/lib/modules/kvm.ko 2>> $LOG_FILE
  echo "$(date): KVM module loaded" >> $LOG_FILE
fi

if [ -f "/system/lib/modules/usb_killswitch.ko" ]; then
  insmod /system/lib/modules/usb_killswitch.ko 2>> $LOG_FILE
  echo "$(date): USB kill switch module loaded" >> $LOG_FILE
fi

# Set permissions on /dev/kvm
if [ -e "/dev/kvm" ]; then
  chmod 666 /dev/kvm
  echo "$(date): /dev/kvm permissions set" >> $LOG_FILE
fi

# Start Dom0 policy manager (if configured)
if [ -f "/data/qwamos/dom0/qwamosd/qwamosd.py" ]; then
  if [ -x "/data/data/com.termux/files/usr/bin/python3" ]; then
    /data/data/com.termux/files/usr/bin/python3 /data/qwamos/dom0/qwamosd/qwamosd.py &
    echo "$(date): Dom0 policy manager started" >> $LOG_FILE
  fi
fi

# Start network manager (if configured)
if [ -f "/data/qwamos/network/network_manager.py" ]; then
  if [ -x "/data/data/com.termux/files/usr/bin/python3" ]; then
    /data/data/com.termux/files/usr/bin/python3 /data/qwamos/network/network_manager.py --daemon &
    echo "$(date): Network manager started" >> $LOG_FILE
  fi
fi

# Start ML threat detection (if configured)
if [ -f "/data/qwamos/ml/threat_detection_daemon.py" ]; then
  if [ -x "/data/data/com.termux/files/usr/bin/python3" ]; then
    /data/data/com.termux/files/usr/bin/python3 /data/qwamos/ml/threat_detection_daemon.py &
    echo "$(date): ML threat detection started" >> $LOG_FILE
  fi
fi

echo "$(date): QWAMOS Magisk service startup complete" >> $LOG_FILE
