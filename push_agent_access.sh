#!/bin/bash

# Agent's public key
AGENT_KEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDsnYERxBRVUpQg2xhozu7g+wues9tXfo+f6RpfwL/+T op@op"
TARGET_HOST="100.85.200.52"
TARGET_USER="op"

echo "🔑 Preparing to push agent key to ${TARGET_USER}@${TARGET_HOST}..."

# Create temporary public key file
echo "$AGENT_KEY" > agent_temp_key.pub

# Use direct ssh to append the key
# This works without requiring the private key file locally
echo "➡️  Connecting to server to add key..."
echo "🔒 You will be asked for the password for ${TARGET_USER}@${TARGET_HOST}:"

cat agent_temp_key.pub | ssh -o StrictHostKeyChecking=no "${TARGET_USER}@${TARGET_HOST}" "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

EXIT_CODE=$?

# Cleanup
rm agent_temp_key.pub

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Success! Agent key added."
else
    echo "❌ Failed to add key. Please check your password and connectivity."
fi
