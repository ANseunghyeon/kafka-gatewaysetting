#!/usr/bin/env python3
"""Producer WITHOUT client certificate – expected to fail due to ssl client auth.
Run: python3 producer_denied.py
"""

from confluent_kafka import Producer
import time

conf = {
    "bootstrap.servers": "localhost:9093",
    "security.protocol": "SSL",
    "ssl.ca.location": "../security/certs/ca.crt",
    # Intentionally omitting ssl.certificate.location and ssl.key.location
}

topic = "custA.test"

p = Producer(conf)

try:
    p.produce(topic, b"unauthorized-message")
    p.flush(5)
    print("Unexpectedly succeeded – check broker config")
except Exception as e:
    print("Expected failure:", e) 