#!/bin/bash
# OMEGA-CODE TLS Certificate Generator
mkdir -p certs
CERT_DIR="./certs"
DOMAIN="omega-tls-proxy"

echo "🔐 Generating Self-Signed TLS Certificates..."

# 1. Create Root CA
openssl genrsa -out $CERT_DIR/ca.key 4096
openssl req -x509 -new -nodes -key $CERT_DIR/ca.key -sha256 -days 3650 -out $CERT_DIR/ca.crt -subj "/CN=Omega-CA"

# 2. Create Proxy Certificate
openssl genrsa -out $CERT_DIR/proxy.key 2048
openssl req -new -key $CERT_DIR/proxy.key -out $CERT_DIR/proxy.csr -subj "/CN=$DOMAIN"
openssl x509 -req -in $CERT_DIR/proxy.csr -CA $CERT_DIR/ca.crt -CAkey $CERT_DIR/ca.key -CAcreateserial -out $CERT_DIR/proxy.crt -days 365 -sha256

# 3. Lockdown Permissions
chmod 600 $CERT_DIR/*.key
chmod 644 $CERT_DIR/*.crt
echo "✅ Carrier Encryption Certificates Ready."
