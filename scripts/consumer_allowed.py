#!/usr/bin/env python3
"""Simple Kafka consumer using client certificate (should succeed).
Requirements: pip install confluent-kafka==2.3.0
Run: python3 consumer_allowed.py
"""
from confluent_kafka import Consumer
import sys, time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CERT_DIR = BASE_DIR / "security" / "certs"

conf = {
    "bootstrap.servers": "localhost:9093",
    "group.id": "demo-consumer-group",
    "auto.offset.reset": "earliest",
    "security.protocol": "SSL",
    "ssl.ca.location": str(CERT_DIR / "ca.crt"),
    "ssl.certificate.location": str(CERT_DIR / "client.crt"),
    "ssl.key.location": str(CERT_DIR / "client.key"),
    "ssl.endpoint.identification.algorithm": "none",
}

topic = "custA.test"

c = Consumer(conf)
c.subscribe([topic])
print("Consuming messages from", topic)
try:
    while True:
        msg = c.poll(5)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error:", msg.error())
            continue
        print(f"Consumed: {msg.value().decode()} @ offset {msg.offset()}")
except KeyboardInterrupt:
    pass
finally:
    c.close() 