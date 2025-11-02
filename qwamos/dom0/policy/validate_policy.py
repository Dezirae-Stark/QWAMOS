#!/usr/bin/env python3
import json
import sys
import jsonschema
from jsonschema import validate

SCHEMA_FILE = "policy.schema.json"

def main():
    if len(sys.argv) < 2:
        print("Usage: validate_policy.py <policy.json>")
        sys.exit(1)
    with open(SCHEMA_FILE) as s:
        schema = json.load(s)
    with open(sys.argv[1]) as p:
        policy = json.load(p)
    try:
        validate(instance=policy, schema=schema)
        print("Policy valid ✔️")
    except jsonschema.exceptions.ValidationError as e:
        print("Policy invalid ❌")
        print(e)
        sys.exit(2)

if __name__ == "__main__":
    main()
