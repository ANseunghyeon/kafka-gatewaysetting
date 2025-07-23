#!/usr/bin/env bash
# Generates CA, server, and client certificates + JKS keystore/truststore
# Requires: openssl, keytool (from JDK) installed on host

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CERT_DIR="$SCRIPT_DIR/../security/certs"
PASSWORD="changeit"

mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

if [[ -f ca.crt ]]; then
  echo "[generate-certs] Certificates already exist in $CERT_DIR. Delete them to regenerate."
  exit 0
fi

echo "[generate-certs] Creating Certificate Authority (CA)..."
openssl req -new -x509 -days 3650 -nodes \
  -subj "/CN=kafka-ca" \
  -keyout ca.key -out ca.crt

echo "[generate-certs] Creating server certificate..."
openssl req -newkey rsa:4096 -days 365 -nodes \
  -subj "/CN=kafka-broker" \
  -keyout kafka.key -out kafka.csr
openssl x509 -req -in kafka.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out kafka.crt -days 365

# Convert server cert/key to PKCS12 for keystore import
openssl pkcs12 -export -in kafka.crt -inkey kafka.key -name kafka-broker \
  -out kafka.p12 -password pass:$PASSWORD -CAfile ca.crt -caname CARoot

# Convert RSA key to PKCS8 (unencrypted) for Envoy compatibility
echo "[generate-certs] Converting server key to PKCS8 for Envoy..."
mv kafka.key kafka_rsa.key
# Convert to PKCS8 PEM explicitly (-outform PEM) and verify
openssl pkcs8 -topk8 -nocrypt -in kafka_rsa.key -out kafka.key -outform PEM

# Quick sanity check to ensure key is valid PEM
openssl pkey -in kafka.key -noout >/dev/null 2>&1 || { echo "[generate-certs] ERROR: generated kafka.key is invalid"; exit 1; }

# Import CA into truststore
keytool -import -noprompt -alias CARoot -file ca.crt \
  -keystore kafka.truststore.jks -storepass $PASSWORD

# Import server cert into keystore
keytool -importkeystore -deststorepass $PASSWORD -destkeypass $PASSWORD \
  -destkeystore kafka.keystore.jks -srckeystore kafka.p12 -srcstoretype PKCS12 \
  -srcstorepass $PASSWORD -alias kafka-broker

echo "[generate-certs] Creating sample client certificate (CN=customerA)..."
openssl req -newkey rsa:4096 -days 365 -nodes \
  -subj "/CN=customerA" \
  -keyout client.key -out client.csr
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out client.crt -days 365

# Create credential helper files for Confluent image
printf "%s" "$PASSWORD" > keystore_creds
printf "%s" "$PASSWORD" > key_creds
printf "%s" "$PASSWORD" > truststore_creds

echo "[generate-certs] Done. Certificates available in $CERT_DIR" 