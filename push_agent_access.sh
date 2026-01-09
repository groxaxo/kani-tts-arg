#!/bin/bash

# Agent's public key
AGENT_KEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDsnYERxBRVUpQg2xhozu7g+wues9tXfo+f6RpfwL/+T op@op"
TARGET_HOST="100.85.200.52"
TARGET_USER="op"

echo "🔑 Preparing to push agent key to ${TARGET_USER}@${TARGET_HOST}..."

# Create temporary public key file
echo "$AGENT_KEY" > agent_temp_key.pub

# Use ssh-copy-id to push the key
# This will handle the permissions and authorized_keys file automatically
# It will prompt the user for the password interactively
echo "➡️  Running ssh-copy-id..."
echo "🔒 You will be asked for the password for ${TARGET_USER}@${TARGET_HOST}:"

ssh-copy-id -i agent_temp_key.pub -o StrictHostKeyChecking=no "${TARGET_USER}@${TARGET_HOST}"

EXIT_CODE=$?

# Cleanup
rm agent_temp_key.pub

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Success! Agent key added."
else
    echo "❌ Failed to add key. Please check your password and connectivity."
fi
