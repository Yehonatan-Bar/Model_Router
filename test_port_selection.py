#!/usr/bin/env python3
"""
Port Selection Test
====================
Demonstrates the intelligent port selection logic.
"""

import socket


def is_port_available(port):
    """Check if a port is available for binding."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False


def find_available_port(preferred_ports):
    """Find the first available port from a list."""
    for port in preferred_ports:
        if is_port_available(port):
            return port
    return None


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔍 Port Availability Test")
    print("="*60)

    preferred_ports = [3791, 3003]

    print("\nChecking port availability:")
    for port in preferred_ports:
        status = "✅ Available" if is_port_available(port) else "❌ In use"
        print(f"  Port {port}: {status}")

    selected_port = find_available_port(preferred_ports)

    print("\n" + "-"*60)
    if selected_port:
        if selected_port == preferred_ports[0]:
            print(f"✨ Will use preferred port: {selected_port}")
        else:
            print(f"⚠️  Preferred port {preferred_ports[0]} is in use")
            print(f"✨ Will use fallback port: {selected_port}")
    else:
        print("❌ ERROR: All ports are in use!")
        print(f"   Tried: {', '.join(map(str, preferred_ports))}")

    print("="*60 + "\n")
