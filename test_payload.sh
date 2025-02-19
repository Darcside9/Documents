#!/bin/bash

# Define the logrotate configuration file
LOGROTATE_CONF="payload_logrotate.conf"

# Define a local state file to avoid permission issues
STATE_FILE="/home/$USER/logrotate.status"

# Ensure jq is installed
if ! command -v jq &> /dev/null; then
  echo "Error: jq is not installed. Install it with 'sudo apt install jq' and try again."
  exit 1
fi

# Get Ngrok URL
NGROK_URL=$(curl -s localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

# Check if NGROK_URL is retrieved correctly
if [[ -z "$NGROK_URL" || "$NGROK_URL" == "null" ]]; then
  echo "Error: Could not retrieve Ngrok URL. Make sure Ngrok is running."
  exit 1
fi

# Define payload
PAYLOAD='{"device_id": "test123", "os_version": "Android13"}'

# Send request
curl -X POST \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  "${NGROK_URL}/your-api-endpoint"

# Run logrotate with the local state file (avoiding permission issues)
if [[ -f "$LOGROTATE_CONF" ]]; then
  /usr/sbin/logrotate -f "$LOGROTATE_CONF" --state "$STATE_FILE"
else
  echo "Error: Logrotate config file '$LOGROTATE_CONF' not found!"
  exit 1
fi
