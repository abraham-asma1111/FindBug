#!/bin/bash

# ============================================================================
# Secret Generation Script
# ============================================================================
# This script generates secure random secrets for the application
# Run this once during initial setup
# ============================================================================

echo "🔐 Generating secure secrets for Bug Bounty Platform..."
echo ""

# Generate JWT Secret
echo "JWT_SECRET_KEY:"
openssl rand -hex 32
echo ""

# Generate Database Password
echo "POSTGRES_PASSWORD:"
openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
echo ""

# Generate Redis Password
echo "REDIS_PASSWORD:"
openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
echo ""

# Generate MinIO Access Key
echo "MINIO_ACCESS_KEY:"
openssl rand -base64 16 | tr -d "=+/" | cut -c1-20
echo ""

# Generate MinIO Secret Key
echo "MINIO_SECRET_KEY:"
openssl rand -base64 32 | tr -d "=+/" | cut -c1-40
echo ""

echo "✅ Secrets generated!"
echo ""
echo "⚠️  IMPORTANT:"
echo "1. Copy these values to your .env file"
echo "2. Never commit .env to Git"
echo "3. Store production secrets in a secure vault (AWS Secrets Manager, HashiCorp Vault, etc.)"
echo "4. Rotate secrets regularly"
echo ""
