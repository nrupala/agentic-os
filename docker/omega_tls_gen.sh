#!/bin/bash
# =============================================================================
# OMEGA-CODE TLS Certificate Generator
# =============================================================================
# Purpose: Generate self-signed certificates and Root CA for mTLS
# Features:
#   - Root CA creation
#   - Proxy certificate generation
#   - Proper permissions (chmod 600 for keys)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERT_DIR="${SCRIPT_DIR}/certs"
DOMAIN="${DOMAIN:-omega-tls-proxy}"
DAYS="${DAYS:-365}"
CA_DAYS="${CA_DAYS:-3650}"

echo "============================================================================"
echo "🔐 OMEGA-CODE TLS Certificate Generator"
echo "============================================================================"

# Create certificate directory
mkdir -p "${CERT_DIR}"

# =============================================================================
# 1. CREATE ROOT CA
# =============================================================================

echo ""
echo "[1/3] Creating Root CA..."

if [ -f "${CERT_DIR}/ca.key" ]; then
    echo "  CA key exists, skipping..."
else
    openssl genrsa -out "${CERT_DIR}/ca.key" 4096 2>/dev/null
    echo "  Generated: ca.key (4098-bit RSA)"
fi

openssl req -x509 -new -nodes \
    -key "${CERT_DIR}/ca.key" \
    -sha256 \
    -days "${CA_DAYS}" \
    -out "${CERT_DIR}/ca.crt" \
    -subj "/CN=Omega-CA/O=Paradise-Stack/C=US" \
    2>/dev/null

echo "  Generated: ca.crt (valid ${CA_DAYS} days)"

# =============================================================================
# 2. CREATE PROXY CERTIFICATE
# =============================================================================

echo ""
echo "[2/3] Creating Proxy Certificate..."

openssl genrsa -out "${CERT_DIR}/proxy.key" 2048 2>/dev/null
echo "  Generated: proxy.key (2048-bit RSA)"

openssl req -new -key "${CERT_DIR}/proxy.key" \
    -out "${CERT_DIR}/proxy.csr" \
    -subj "/CN=${DOMAIN}/O=Paradise-Stack/C=US" \
    2>/dev/null

openssl x509 -req -in "${CERT_DIR}/proxy.csr" \
    -CA "${CERT_DIR}/ca.crt" \
    -CAkey "${CERT_DIR}/ca.key" \
    -CAcreateserial \
    -out "${CERT_DIR}/proxy.crt" \
    -days "${DAYS}" \
    -sha256 \
    2>/dev/null

echo "  Generated: proxy.crt (valid ${DAYS} days)"
echo "  Generated: proxy.csr (Certificate Signing Request)"

# =============================================================================
# 3. CREATE DIFFIE-HELLMAN PARAMETERS (Optional)
# =============================================================================

echo ""
echo "[3/3] Setting permissions..."

# Set restrictive permissions
chmod 600 "${CERT_DIR}"/*.key
chmod 644 "${CERT_DIR}"/*.crt
chmod 644 "${CERT_DIR}"/*.csr
chmod 644 "${CERT_DIR}"/*.srl 2>/dev/null || true

echo "  Set: chmod 600 *.key (owner read/write only)"
echo "  Set: chmod 644 *.crt (owner read/write, others read)"

# =============================================================================
# SUMMARY
# =============================================================================

echo ""
echo "============================================================================"
echo "✅ CARRIER ENCRYPTION CERTIFICATES READY"
echo "============================================================================"
echo ""
echo "Certificate Files:"
ls -la "${CERT_DIR}"/*.crt "${CERT_DIR}"/*.key 2>/dev/null || true
echo ""
echo "Usage:"
echo "  1. Configure Nginx with these certificates"
echo "  2. Set environment: CA_CERT=${CERT_DIR}/ca.crt"
echo "  3. Client must trust ca.crt for mTLS"
echo ""
echo "Security Notes:"
echo "  - ca.key: KEEP SECRET (signs all certificates)"
echo "  - proxy.key: Server private key (keep secret)"
echo "  - ca.crt: Add to client trust stores for mTLS"
echo ""
echo "============================================================================"
