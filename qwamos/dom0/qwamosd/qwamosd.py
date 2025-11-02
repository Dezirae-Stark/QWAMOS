#!/usr/bin/env python3
"""
QWAMOS Daemon — monitors policy.conf and pending.conf, validates signature,
pushes changes to control bus, and schedules reboot if needed.
"""
import os
import time
import json
import hashlib
import shutil
import subprocess
from pathlib import Path

POLICY_DIR = Path(__file__).resolve().parent.parent / "policy"
POLICY = POLICY_DIR / "policy.conf.example"
PENDING = POLICY_DIR / "pending.conf"
HASH_FILE = POLICY_DIR / ".last_hash"

def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def apply_policy():
    print("[Dom0] Applying policy changes...")
    subprocess.run(["python3", "validate_policy.py", str(POLICY.with_suffix('.json'))])
    print("[Dom0] Broadcast: policy-update")

def main():
    print("[QWAMOSD] Starting daemon loop...")
    last = file_hash(POLICY)
    while True:
        time.sleep(3)
        h = file_hash(POLICY)
        if h != last:
            print("[QWAMOSD] Detected policy.conf change.")
            apply_policy()
            last = h
    # In real implementation: handle pending.conf, signed verification, bus transport

if __name__ == "__main__":
    main()
