#!/bin/bash
set -e
# Query subnet dynamically from Docker network configuration
BRIDGE_NAME="${GUEST_BRIDGE_NAME:-guest_bridge}"
echo "Fetching subnet for Docker network bridge: $BRIDGE_NAME"
SUBNET=$(docker network inspect "$BRIDGE_NAME" --format '{{(index .IPAM.Config 0).Subnet}}' 2>/dev/null || echo "")

if [ -z "$SUBNET" ]; then
    echo "WARNING: Docker network '$BRIDGE_NAME' not found or has no subnet yet. Retrying in 2 seconds..."
    sleep 2
    SUBNET=$(docker network inspect "$BRIDGE_NAME" --format '{{(index .IPAM.Config 0).Subnet}}' 2>/dev/null || echo "")
fi

if [ -z "$SUBNET" ]; then
    echo "ERROR: Subnet for bridge '$BRIDGE_NAME' could not be determined. Exiting."
    exit 1
fi

echo "=== Applying Egress Blocking Rules for Subnet $SUBNET ==="

# Helper to remove rule if it already exists (prevents duplicate logs/errors)
remove_rule() {
    local src="$1"
    local dst="$2"
    sudo iptables -D DOCKER-USER -s "$src" -d "$dst" -j DROP 2>/dev/null || true
}

# Apply drop rules to DOCKER-USER chain
echo "Removing any legacy rules for $SUBNET..."
remove_rule "$SUBNET" "192.168.0.0/16"
remove_rule "$SUBNET" "10.0.0.0/8"
remove_rule "$SUBNET" "172.16.0.0/12"

echo "Inserting drop rules for RFC 1918 private subnets..."
sudo iptables -I DOCKER-USER -s "$SUBNET" -d 192.168.0.0/16 -j DROP
sudo iptables -I DOCKER-USER -s "$SUBNET" -d 10.0.0.0/8 -j DROP
# Note: This blocks other subnets in 172.16.0.0/12 but allows internal 172.20.0.0/24 bridge routing
sudo iptables -I DOCKER-USER -s "$SUBNET" -d 172.16.0.0/12 -j DROP

# Allow access to host reports server on port 8081
sudo iptables -I DOCKER-USER -s "$SUBNET" -p tcp --dport 8081 -j ACCEPT

echo "=== Firewall Rules Applied Successfully ==="
echo "Current DOCKER-USER chain rules:"
sudo iptables -L DOCKER-USER -n -v

# Persist rules if iptables-persistent is installed
if [ -d /etc/iptables ]; then
    echo "Saving rules via iptables-persistent..."
    sudo sh -c 'iptables-save > /etc/iptables/rules.v4'
    echo "Rules saved to /etc/iptables/rules.v4"
fi
