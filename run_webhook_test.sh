#!/usr/bin/env bash

set -euo pipefail

WEBHOOK_URL="https://api.v2.gather.town/api/v2/hooks/spaces/92356cd8-985d-4ad6-b8bf-fc59b10221b9/objects/22979152-f25d-4a92-b7c7-03c034b0496b"

# Preencha antes de executar:
WEBHOOK_SECRET="${GATHER_WEBHOOK_SECRET:-}"

if [[ -z "$WEBHOOK_SECRET" ]]; then
    echo "Erro: defina GATHER_WEBHOOK_SECRET"
    echo 'Exemplo: export GATHER_WEBHOOK_SECRET="whsec_..."'
    exit 1
fi

if [[ "$WEBHOOK_SECRET" != whsec_* ]]; then
    echo "Erro: o secret precisa começar com whsec_"
    exit 1
fi

WEBHOOK_ID="$(cat /proc/sys/kernel/random/uuid)"
WEBHOOK_TIMESTAMP="$(date +%s)"

# IMPORTANTE:
# Não altere esse JSON depois de gerar a assinatura.
BODY='{"type":"webhook.ping"}'

# Standard Webhooks:
# HMAC-SHA256 de:
# webhook-id.webhook-timestamp.rawBody
SIGNED_CONTENT="${WEBHOOK_ID}.${WEBHOOK_TIMESTAMP}.${BODY}"

# Remove o prefixo whsec_ e decodifica o secret em base64
SECRET_BASE64="${WEBHOOK_SECRET#whsec_}"

SIGNATURE="$(
    printf '%s' "$SIGNED_CONTENT" |
    openssl dgst -sha256 \
        -mac HMAC \
        -macopt "key:$(printf '%s' "$SECRET_BASE64" | base64 -d)" \
        -binary |
    base64 -w 0
)"

WEBHOOK_SIGNATURE="v1,${SIGNATURE}"

echo "Sending webhook.ping..."
echo "webhook-id:        $WEBHOOK_ID"
echo "webhook-timestamp: $WEBHOOK_TIMESTAMP"

curl --fail-with-body -i \
    -X POST "$WEBHOOK_URL" \
    -H "Content-Type: application/json" \
    -H "webhook-id: $WEBHOOK_ID" \
    -H "webhook-timestamp: $WEBHOOK_TIMESTAMP" \
    -H "webhook-signature: $WEBHOOK_SIGNATURE" \
    --data-binary "$BODY"