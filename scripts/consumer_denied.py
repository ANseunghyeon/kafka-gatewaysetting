#!/usr/bin/env python3
"""Consumer WITHOUT client certificate – expected to fail due to mTLS.
Run: python3 consumer_denied.py
"""
from confluent_kafka import Consumer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CERT_DIR = BASE_DIR / "security" / "certs"

conf = {
    "bootstrap.servers": "localhost:9093",
    "group.id": "demo-consumer-group",
    "auto.offset.reset": "earliest",
    "security.protocol": "SSL",
    "ssl.ca.location": str(CERT_DIR / "ca.crt"),
    "ssl.endpoint.identification.algorithm": "none",
}

c = Consumer(conf)
try:
    c.subscribe(["custA.test"])
    msg = c.poll(5)
    print("Unexpectedly received message:", msg)
except Exception as e:
    print("Expected failure:", e)
finally:
    c.close() 