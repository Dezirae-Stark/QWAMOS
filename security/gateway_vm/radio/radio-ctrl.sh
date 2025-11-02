#!/bin/bash
# QWAMOS Radio Controller
# Controls cellular radio power and idle timeout

IDLE_TIMEOUT_MIN=${RADIO_IDLE_TIMEOUT_MIN:-10}
STATE_FILE="/var/run/qwamos/radio-state"

radio_on() {
    echo "📡 Enabling cellular radio..."

    # Enable data via Android service control
    svc data enable

    # Record state
    echo "on" > "$STATE_FILE"
    echo "$(date +%s)" >> "$STATE_FILE"

    echo "✅ Radio enabled"
}

radio_off() {
    echo "📴 Disabling cellular radio..."

    # Disable data
    svc data disable

    # Record state
    echo "off" > "$STATE_FILE"

    echo "✅ Radio disabled"
}

radio_status() {
    if [ -f "$STATE_FILE" ]; then
        state=$(head -n1 "$STATE_FILE")

        if [ "$state" = "on" ]; then
            timestamp=$(tail -n1 "$STATE_FILE")
            current=$(date +%s)
            idle_sec=$((current - timestamp))
            idle_min=$((idle_sec / 60))

            echo "Radio: ON (idle: ${idle_min} min)"
        else
            echo "Radio: OFF"
        fi
    else
        echo "Radio: UNKNOWN"
    fi
}

monitor_idle() {
    echo "🔍 Starting idle monitor (timeout: $IDLE_TIMEOUT_MIN min)"

    mkdir -p "$(dirname "$STATE_FILE")"

    while true; do
        sleep 60  # Check every minute

        if [ ! -f "$STATE_FILE" ]; then
            continue
        fi

        state=$(head -n1 "$STATE_FILE")

        if [ "$state" = "on" ]; then
            # Check network activity
            current_rx=$(cat /sys/class/net/rmnet_data0/statistics/rx_bytes 2>/dev/null || echo 0)

            # Read last activity
            if [ -f "/var/run/qwamos/radio-last-rx" ]; then
                last_rx=$(cat /var/run/qwamos/radio-last-rx)
            else
                last_rx=0
            fi

            # Update last activity
            echo "$current_rx" > /var/run/qwamos/radio-last-rx

            # If activity detected, update timestamp
            if [ "$current_rx" != "$last_rx" ]; then
                echo "on" > "$STATE_FILE"
                echo "$(date +%s)" >> "$STATE_FILE"
                continue
            fi

            # No activity - check idle time
            timestamp=$(tail -n1 "$STATE_FILE")
            current=$(date +%s)
            idle_min=$(( (current - timestamp) / 60 ))

            echo "ℹ️  Radio idle: ${idle_min}/${IDLE_TIMEOUT_MIN} min"

            if [ $idle_min -ge $IDLE_TIMEOUT_MIN ]; then
                echo "⏱️  Idle timeout reached"
                radio_off
            fi
        fi
    done
}

reset_idle_timer() {
    if [ -f "$STATE_FILE" ]; then
        state=$(head -n1 "$STATE_FILE")
        if [ "$state" = "on" ]; then
            echo "on" > "$STATE_FILE"
            echo "$(date +%s)" >> "$STATE_FILE"
            echo "✅ Idle timer reset"
        fi
    fi
}

case "$1" in
    on)
        radio_on
        ;;
    off)
        radio_off
        ;;
    status)
        radio_status
        ;;
    monitor)
        monitor_idle
        ;;
    reset-idle)
        reset_idle_timer
        ;;
    *)
        echo "Usage: $0 {on|off|status|monitor|reset-idle}"
        exit 1
        ;;
esac
