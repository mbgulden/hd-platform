#!/bin/bash
set -e

# Config paths
BOT_DIR="/home/ubuntu/guest_hermes_bot"
WORKSPACE_DIR="/home/ubuntu/users/guest_hermes"

echo "=== Phase 1: Installing Docker & Compose (if missing) ==="
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing docker.io and docker-compose-v2..."
    
    # Wait for apt lock
    echo "Waiting for any running apt lock..."
    while sudo fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 || sudo fuser /var/lib/dpkg/lock >/dev/null 2>&1; do
      echo "dpkg lock active, sleeping 5s..."
      sleep 5
    done

    sudo apt-get update -y
    sudo apt-get install -y docker.io docker-compose-v2
    sudo systemctl enable --now docker
    sudo usermod -aG docker ubuntu
    echo "Docker installed successfully!"
else
    echo "Docker is already installed: $(docker --version)"
fi

echo "=== Phase 2: Preparing isolated folders ==="
mkdir -p "$BOT_DIR"
mkdir -p "$WORKSPACE_DIR"

# Change ownership of the workspace so container non-root user (UID 1000) can read/write to it
sudo chown -R 1000:1000 "$WORKSPACE_DIR"

echo "=== Phase 3: Copying files into place ==="
# Move mcp servers and family configs to the workspace directory so they are visible as /workspace/...
cp "$BOT_DIR/next_step_mcp.py" "$WORKSPACE_DIR/next_step_mcp.py"
cp "$BOT_DIR/daily_journal_mcp.py" "$WORKSPACE_DIR/daily_journal_mcp.py"
cp "$BOT_DIR/guest_family.json" "$WORKSPACE_DIR/guest_family.json"

# Make sure permissions allow UID 1000 to read/execute them
sudo chown 1000:1000 "$WORKSPACE_DIR/next_step_mcp.py" "$WORKSPACE_DIR/daily_journal_mcp.py" "$WORKSPACE_DIR/guest_family.json"
chmod +x "$WORKSPACE_DIR/next_step_mcp.py" "$WORKSPACE_DIR/daily_journal_mcp.py"

echo "=== Phase 4: Setting up environment variable template ==="
if [ ! -f "$BOT_DIR/.env" ]; then
    cat << 'EOF' > "$BOT_DIR/.env"
# Guest Bot Environment Variables
# Get this from @BotFather on Telegram (without quotes)
GUEST_TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE

# Your numeric Telegram user ID (get this from @userinfobot)
GUEST_TELEGRAM_ALLOWED_USERS=YOUR_NUMERIC_TELEGRAM_ID_HERE

# Budgeted OpenRouter API Key (without quotes)
GUEST_OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY_HERE
EOF
    echo "Created environment template at $BOT_DIR/.env"
    echo "IMPORTANT: Please fill in GUEST_TELEGRAM_BOT_TOKEN, GUEST_TELEGRAM_ALLOWED_USERS, and GUEST_OPENROUTER_API_KEY in $BOT_DIR/.env before running compose."
else
    echo "Environment file already exists."
fi

echo "=== Phase 5: Building container & Starting stack ==="
cd "$BOT_DIR"

# Apply executable permissions to script
chmod +x block_egress.sh

# Run block egress script first to establish firewall posture
./block_egress.sh

# Build and start container
echo "Starting guest bot container stack..."
sudo docker compose up -d --build

echo "=== Deployment Completed Successfully ==="
echo "Container status:"
sudo docker compose ps
