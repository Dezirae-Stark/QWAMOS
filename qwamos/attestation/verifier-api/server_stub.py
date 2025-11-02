#!/usr/bin/env python3
"""
QWAMOS Attestation Verifier API
"""
from flask import Flask

app = Flask(__name__)

@app.route('/verify')
def verify():
    return {"status": "stub", "verified": False}

if __name__ == "__main__":
    print("QWAMOS Verifier API (stub)")
    app.run(port=8080)
