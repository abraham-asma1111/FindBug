#!/bin/bash

echo "=== Testing Admin Users Endpoint ==="
echo ""

# Step 1: Login
echo "1. Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8002/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"remainsecure@findbug.com","password":"admin123"}')

echo "Login response: $LOGIN_RESPONSE"
echo ""

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "✗ Failed to get token"
  exit 1
fi

echo "✓ Got token: ${TOKEN:0:50}..."
echo ""

# Step 2: Get users
echo "2. Fetching users..."
USERS_RESPONSE=$(curl -s -X GET "http://127.0.0.1:8002/api/v1/admin/users" \
  -H "Authorization: Bearer $TOKEN")

echo "$USERS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$USERS_RESPONSE"
