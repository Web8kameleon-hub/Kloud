#!/usr/bin/env python3
"""
Hetzner Cloud API - Connect and list server info
"""

import os
from hcloud import Client

# Token from environment
token = os.getenv('HCLOUD_TOKEN', 'U6mVjac7GnWAY4HI6igG2b4WM5hcpgrTgI6TysodWL0htMu4CowNPf8PwbVR10g5')

# Connect
client = Client(token=token)

print("=" * 60)
print("🔗 Connecting to Hetzner Cloud...")
print("=" * 60)

try:
    # List all servers
    servers = client.servers.get_all()
    
    print(f"\n✅ Connected! Found {len(servers)} server(s):\n")
    
    for server in servers:
        print(f"  Name: {server.name}")
        print(f"  ID: {server.id}")
        print(f"  Status: {server.status}")
        print(f"  Type: {server.server_type.name}")
        print(f"  Location: {server.location.name}")
        print(f"  Public IPs: {[ip.ip_address for ip in server.public_net.ipv4]}")
        if server.public_net.ipv6:
            print(f"  IPv6: {server.public_net.ipv6.ip_address}")
        print()
    
    # Find CPX62
    target_server = None
    for server in servers:
        if server.name == 'rocky-32gb-hel1-2' or '46.62.210.251' in str([ip.ip_address for ip in server.public_net.ipv4]):
            target_server = server
            break
    
    if target_server:
        print("=" * 60)
        print(f"✅ Target Server Found: {target_server.name}")
        print("=" * 60)
        print(f"ID: {target_server.id}")
        print(f"Status: {target_server.status}")
        print(f"IP: {target_server.public_net.ipv4[0].ip_address if target_server.public_net.ipv4 else 'N/A'}")
        print(f"Type: {target_server.server_type.name}")
        print(f"Location: {target_server.location.name}")
        print()
    else:
        print("⚠️  Target server not found!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
