#!/bin/bash
# Quick Token Getter - Get access token for any user

USERNAME="${1:-}"
PASSWORD="${2:-}"

if [ -z "$USERNAME" ]; then
    read -p "Username: " USERNAME
fi

if [ -z "$PASSWORD" ]; then
    read -sp "Password: " PASSWORD
    echo ""
fi

# Get token
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$USERNAME&password=$PASSWORD")

TOKEN=$(echo $RESPONSE | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Login failed" >&2
    echo "$RESPONSE" >&2
    exit 1
fi

# Output just the token (so it can be captured)
echo "$TOKEN"

# Also save to file and env
echo "$TOKEN" > /tmp/lifevault_token.txt
export LIFEVAULT_TOKEN="$TOKEN"

# If running interactively, show helpful info
if [ -t 1 ]; then
    echo "" >&2
    echo "✅ Token saved to: /tmp/lifevault_token.txt" >&2
    echo "" >&2
    echo "Usage:" >&2
    echo '  TOKEN=$(cat /tmp/lifevault_token.txt)' >&2
    echo '  curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/analytics/sleep' >&2
fi
