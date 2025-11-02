#!/usr/bin/env python3
"""
QWAMOS Control CLI — signed control bus client for sending policy updates.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path
from base64 import b64encode
from nacl.signing import SigningKey

SOCKET_PATH = "/tmp/qwamos_bus.sock"
KEY_PATH = Path.home() / ".qwamos" / "dom0.key"

def sign_message(payload):
    key = SigningKey.generate() if not KEY_PATH.exists() else SigningKey(KEY_PATH.read_bytes())
    signed = key.sign(json.dumps(payload).encode())
    return b64encode(signed).decode()

def send_command(target, command, payload):
    msg = {"target": target, "command": command, "payload": payload, "timestamp": time.time()}
    msg["sig"] = sign_message(msg)
    with open(SOCKET_PATH, "a") as f:
        f.write(json.dumps(msg) + "\n")
    print(f"Sent command to {target}: {command}")

def main():
    parser = argparse.ArgumentParser(description="QWAMOS Control CLI")
    parser.add_argument("target", help="Target VM (gateway_vm/ui_vm/attestation)")
    parser.add_argument("command", help="Command (reload, shutdown, reboot, policy-update)")
    parser.add_argument("--payload", help="Optional JSON payload string", default="{}")
    args = parser.parse_args()
    payload = json.loads(args.payload)
    send_command(args.target, args.command, payload)

if __name__ == "__main__":
    main()
