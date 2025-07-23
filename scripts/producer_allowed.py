#!/usr/bin/env python3
"""Simple Kafka producer using client certificate (should succeed).
Requirements: pip install confluent-kafka==2.3.0
Run: python3 producer_allowed.py
"""

from confluent_kafka import Producer
import sys, time

conf = {
    "bootstrap.servers": "localhost:9093",  # adjust if broker runs on another host
    "security.protocol": "SSL",
    "ssl.ca.location": "../security/certs/ca.crt",
    "ssl.certificate.location": "../security/certs/client.crt",
    "ssl.key.location": "../security/certs/client.key",
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