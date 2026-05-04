#!/usr/bin/env python3
"""
configure_ospf.py
Reads host_vars for each device and pushes BIRD OSPF configuration
into each Containerlab container via docker exec.
OSPF allows all devices to discover routes to every subnet automatically.
"""
import os
import yaml
import subprocess

# Containerlab prefix for all container names
PREFIX = "clab-enterprise-spine-leaf"

# OSPF area — we use area 0 (backbone area) for simplicity
OSPF_AREA = "0.0.0.0"

# Directory where host_vars YAML files are stored
HOST_VARS_DIR = os.path.expanduser("~/network-automation/host_vars")

def generate_bird_config(device_name, interfaces):
    """
    Generate BIRD2 configuration for a device.
    BIRD config defines which interfaces participate in OSPF
    and exports/imports routes between the kernel and OSPF.
    """
    # Build interface blocks for each data plane interface
    # We skip eth0 which is the management interface
    iface_blocks = ""
    networks = ""
    for iface in interfaces:
        name = iface["name"]
        if name == "eth0":
            continue  # skip management interface
        ip = iface["ip"]
        prefix = iface["prefix"]
        iface_blocks += f"""
        interface "{name}" {{
            type broadcast;
            cost 10;
            hello 10;
            dead 40;
        }};"""
        networks += f"\n        {ip}/{prefix};"

    config = f"""# BIRD2 OSPF Configuration for {device_name}
# Generated automatically by configure_ospf.py
# BIRD is a routing daemon that runs OSPF to share routes between devices

router id {interfaces[1]["ip"] if len(interfaces) > 1 else "1.1.1.1"};

# Export routes from OSPF into the kernel routing table
# This makes the OS actually use the routes OSPF discovers
protocol kernel {{
    ipv4 {{
        export all;
        import all;
    }};
}}

# Import routes from the kernel into BIRD
protocol device {{
    scan time 10;
}}

# OSPF configuration
# Area 0 is the backbone area — all devices must be in the same area
# for them to share routing information
protocol ospf v2 {{
    area {OSPF_AREA} {{{iface_blocks}
    }};
    ipv4 {{
        export all;
        import all;
    }};
}}
"""
    return config

def push_config(device_name, config):
    """
    Write BIRD config file into the container and start BIRD daemon.
    We use docker exec to run commands inside the container
    without needing SSH.
    """
    container = f"{PREFIX}-{device_name}"

    # Write config file into container
    cmd = f"echo '{config}' > /etc/bird.conf"
    result = subprocess.run(
        ["sudo", "docker", "exec", container, "sh", "-c", cmd],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ERROR writing config: {result.stderr}")
        return False

    # Kill any existing BIRD process
    subprocess.run(
        ["sudo", "docker", "exec", container, "sh", "-c", "pkill bird || true"],
        capture_output=True
    )

    # Start BIRD daemon
    result = subprocess.run(
        ["sudo", "docker", "exec", container, "sh", "-c", "bird -c /etc/bird.conf"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ERROR starting BIRD: {result.stderr}")
        return False

    print(f"  BIRD started successfully")
    return True

def verify_ospf(device_name):
    """
    Check OSPF neighbor status to confirm routing is working.
    OSPF neighbors means two devices are exchanging routing information.
    """
    container = f"{PREFIX}-{device_name}"
    result = subprocess.run(
        ["sudo", "docker", "exec", container, "sh", "-c",
         "birdc show ospf neighbors"],
        capture_output=True, text=True
    )
    print(f"\n--- {device_name} OSPF neighbors ---")
    print(result.stdout if result.stdout else "No neighbors yet")

# Main execution
print("Configuring OSPF on all devices...\n")

for filename in sorted(os.listdir(HOST_VARS_DIR)):
    if not filename.endswith(".yml"):
        continue

    device_name = filename.replace(".yml", "")

    # Skip server devices — they don't need OSPF
    if device_name.startswith("SRV"):
        continue

    filepath = os.path.join(HOST_VARS_DIR, filename)
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)

    if not data or not data.get("interfaces"):
        continue

    print(f"Configuring {device_name}...")
    config = generate_bird_config(device_name, data["interfaces"])
    push_config(device_name, config)

# Wait a moment for OSPF to converge
print("\nWaiting 30 seconds for OSPF to converge...")
import time
time.sleep(30)

# Verify OSPF neighbors on spines
print("\nVerifying OSPF neighbors...")
for device in ["SP1", "SP2", "SP3"]:
    verify_ospf(device)

print("\nDone — OSPF configured on all devices!")
