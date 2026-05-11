FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

COPY . .

# Gerar chaves RSA no build para uso em dev
# Em produção: montar via secrets ou variáveis de ambiente
RUN python -c "\
from cryptography.hazmat.primitives.asymmetric import rsa; \
from cryptography.hazmat.primitives import serialization; \
import os; \
os.makedirs('keys', exist_ok=True); \
private = rsa.generate_private_key(public_exponent=65537, key_size=2048); \
open('keys/private.pem', 'wb').write(private.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())); \
open('keys/public.pem', 'wb').write(private.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)); \
print('RSA keys generated for dev container.')"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
