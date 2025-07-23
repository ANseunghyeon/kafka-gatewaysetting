#!/usr/bin/env python3
"""Simple Kafka producer using client certificate (should succeed).
Requirements: pip install confluent-kafka==2.3.0
Run: python3 producer_allowed.py
"""

from confluent_kafka import Producer
import sys, time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CERT_DIR = BASE_DIR / "security" / "certs"

conf = {
    "bootstrap.servers": "localhost:9093",  # adjust if broker runs on another host
    "security.protocol": "SSL",
    "ssl.ca.location": str(CERT_DIR / "ca.crt"),
    "ssl.certificate.location": str(CERT_DIR / "client.crt"),
    "ssl.key.location": str(CERT_DIR / "client.key"),
    "ssl.endpoint.identification.algorithm": "none",  # disable hostname verification for local SAN mismatch
}

topic = "custA.test"

p = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print("Delivery failed:", err)
    else:
        print(f"Produced to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")

msg_value = f"hello-secure-{int(time.time())}"
print("Producing message:", msg_value)

p.produce(topic, msg_value.encode(), callback=delivery_report)
p.flush(5)
print("Finished") 