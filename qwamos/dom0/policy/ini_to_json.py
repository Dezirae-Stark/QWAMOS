#!/usr/bin/env python3
"""
QWAMOS Policy Converter: INI to JSON

Converts legacy policy.conf (INI format) to policy.json for use with qwamosctl.

Usage:
  ./ini_to_json.py policy.conf.example > policy.json
"""
import sys
import json
import configparser
from pathlib import Path

def convert_ini_to_json(ini_path):
    """Convert INI policy file to JSON format"""
    config = configparser.ConfigParser()
    config.read(ini_path)

    policy = {}

    # Read all sections and keys
    for section in config.sections():
        for key, value in config.items(section):
            # Build dotted key for nested config (e.g., RADIO_HARDENING.level)
            if section.upper() != "DEFAULT":
                full_key = f"{section.upper()}.{key}"
            else:
                full_key = key.upper()

            # Convert value type
            if value.lower() in ("true", "false"):
                policy[full_key] = value.lower() == "true"
            elif value.isdigit():
                policy[full_key] = int(value)
            else:
                policy[full_key] = value

    return policy

def main():
    if len(sys.argv) < 2:
        print("Usage: ini_to_json.py <policy.conf>", file=sys.stderr)
        print("Example: ./ini_to_json.py policy.conf.example > policy.json", file=sys.stderr)
        sys.exit(1)

    ini_path = Path(sys.argv[1])
    if not ini_path.exists():
        print(f"ERROR: File not found: {ini_path}", file=sys.stderr)
        sys.exit(1)

    policy = convert_ini_to_json(ini_path)
    print(json.dumps(policy, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
