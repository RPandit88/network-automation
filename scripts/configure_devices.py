#!/usr/bin/env python3
import os
import yaml
import subprocess

# Directory containing host_vars
host_vars_dir = os.path.expanduser("~/network-automation/host_vars")

# Container name prefix
prefix = "clab-enterprise-spine-leaf"

def configure_device(device_name, data):
    container = f"{prefix}-{device_name}"
    print(f"\nConfiguring {device_name}...")

    for iface in data.get("interfaces", []):
        name = iface["name"]
        ip = iface["ip"]
        prefix_len = iface["prefix"]

        commands = [
            f"ip addr flush dev {name}",
            f"ip addr add {ip}/{prefix_len} dev {name}",
            f"ip link set {name} up",
        ]

        for cmd in commands:
            result = subprocess.run(
                ["sudo", "docker", "exec", container, "sh", "-c", cmd],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"  {name}: {ip}/{prefix_len} ✓")
            else:
                print(f"  {name}: ERROR - {result.stderr.strip()}")

def verify_device(device_name):
    container = f"{prefix}-{device_name}"
    result = subprocess.run(
        ["sudo", "docker", "exec", container, "ip", "addr", "show"],
        capture_output=True,
        text=True
    )
    print(f"\n--- {device_name} interfaces ---")
    print(result.stdout)

# Main
for filename in sorted(os.listdir(host_vars_dir)):
    if filename.endswith(".yml"):
        device_name = filename.replace(".yml", "")
        filepath = os.path.join(host_vars_dir, filename)

        with open(filepath, "r") as f:
            data = yaml.safe_load(f)

        if data and data.get("interfaces"):
            configure_device(device_name, data)

print("\nVerifying configurations...")
for filename in sorted(os.listdir(host_vars_dir)):
    if filename.endswith(".yml"):
        device_name = filename.replace(".yml", "")
        verify_device(device_name)

print("\nDone — all devices configured!")
