#!/usr/bin/env bash
# Cloudflare Tunnel Setup for Human Design Engine
# Run this AFTER registering domains on Cloudflare

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Human Design Engine — Cloudflare Tunnel Setup ===${NC}\n"

# Check cloudflared
if ! command -v cloudflared &>/dev/null; then
    echo -e "${RED}cloudflared not found. Install it first:${NC}"
    echo "  curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared"
    echo "  chmod +x /usr/local/bin/cloudflared"
    exit 1
fi
echo -e "${GREEN}✓${NC} cloudflared found: $(cloudflared --version)"

# Step 1: Authenticate
echo -e "\n${YELLOW}Step 1: Authenticate with Cloudflare${NC}"
echo "A browser window will open. Log in to your Cloudflare account."
echo "If running headless, use: cloudflared tunnel login --no-browser"
echo ""
cloudflared tunnel login

# Step 2: Create tunnel
echo -e "\n${YELLOW}Step 2: Create the tunnel${NC}"
TUNNEL_OUTPUT=$(cloudflared tunnel create hd-engine 2>&1)
echo "$TUNNEL_OUTPUT"

# Extract tunnel ID
TUNNEL_ID=$(echo "$TUNNEL_OUTPUT" | grep -oP 'id \K[\w-]+' | head -1)
if [ -z "$TUNNEL_ID" ]; then
    TUNNEL_ID=$(cloudflared tunnel list --output json 2>/dev/null | python3 -c "import sys,json; [print(t['id']) for t in json.load(sys.stdin) if t.get('name')=='hd-engine']" 2>/dev/null)
fi

if [ -z "$TUNNEL_ID" ]; then
    echo -e "${RED}Could not determine tunnel ID. Check 'cloudflared tunnel list'${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Tunnel created: ${TUNNEL_ID}"

# Step 3: Update config with tunnel ID
CONFIG_FILE="/home/ubuntu/work/hd-platform/infra/cloudflare-config.yml"
FINAL_CONFIG="/home/ubuntu/.cloudflared/config.yml"
mkdir -p /home/ubuntu/.cloudflared

sed "s/YOUR_TUNNEL_ID_HERE/${TUNNEL_ID}/g" "$CONFIG_FILE" > "$FINAL_CONFIG"
echo -e "${GREEN}✓${NC} Config written to ${FINAL_CONFIG}"

# Step 4: Install systemd service
echo -e "\n${YELLOW}Step 3: Install systemd service${NC}"
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
echo -e "${GREEN}✓${NC} cloudflared service installed and started"

# Step 5: DNS instructions
echo -e "\n${YELLOW}Step 4: Configure DNS (do this in Cloudflare dashboard)${NC}"
echo ""
echo "  Add these CNAME records (all pointing to the same tunnel):"
echo ""
echo "  ┌──────────────────────────────────┬─────────────────────────────────┐"
echo "  │ Name                            │ Target                          │"
echo "  ├──────────────────────────────────┼─────────────────────────────────┤"
echo "  │ humandesignengine.com           │ ${TUNNEL_ID}.cfargotunnel.com    │"
echo "  │ api.humandesignengine.com       │ ${TUNNEL_ID}.cfargotunnel.com    │"
echo "  │ reports.humandesignengine.com   │ ${TUNNEL_ID}.cfargotunnel.com    │"
echo "  │ sheplantedatree.com             │ ${TUNNEL_ID}.cfargotunnel.com    │"
echo "  └──────────────────────────────────┴─────────────────────────────────┘"
echo ""
echo -e "${GREEN}✓${NC} Setup complete! Check status: sudo systemctl status cloudflared"
echo ""
echo -e "${YELLOW}Next:${NC} Start your services on the local ports configured in config.yml"
