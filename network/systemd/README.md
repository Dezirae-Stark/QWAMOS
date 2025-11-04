# QWAMOS Network Systemd Services

This directory contains systemd service files for QWAMOS network isolation components.

## Services

- `qwamos-tor.service` - Tor anonymity network
- `qwamos-i2p.service` - I2P anonymous network
- `qwamos-dnscrypt.service` - DNSCrypt DNS privacy
- `qwamos-vpn.service` - VPN connection manager
- `qwamos-network-monitor.service` - Network isolation monitor

## Installation

```bash
# Copy service files to system location
sudo cp *.service /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable qwamos-tor qwamos-dnscrypt
```

## Status

**Phase 5**: Service files will be created during device integration testing.

This directory structure is ready for systemd service implementation.
