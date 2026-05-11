param([switch]$Force)

$keysDir = Join-Path $PSScriptRoot "..\backend\keys"
New-Item -ItemType Directory -Force -Path $keysDir | Out-Null

if ((Test-Path "$keysDir\private.pem") -and -not $Force) {
    Write-Host "Chaves ja existem em backend/keys/. Use -Force para regenerar."
    exit 0
}

docker run --rm -v "${keysDir}:/keys" alpine/openssl sh -c `
    "openssl genrsa -out /keys/private.pem 2048 && openssl rsa -in /keys/private.pem -pubout -out /keys/public.pem"

Write-Host "Chaves RSA geradas em backend/keys/"
