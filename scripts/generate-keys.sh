#!/usr/bin/env sh
set -e

KEYS_DIR="$(dirname "$0")/../backend/keys"
mkdir -p "$KEYS_DIR"

if [ -f "$KEYS_DIR/private.pem" ]; then
  echo "Chaves já existem em backend/keys/. Use --force para regenerar."
  if [ "$1" != "--force" ]; then
    exit 0
  fi
fi

openssl genrsa -out "$KEYS_DIR/private.pem" 2048
openssl rsa -in "$KEYS_DIR/private.pem" -pubout -out "$KEYS_DIR/public.pem"

echo "Chaves RSA geradas em backend/keys/"
