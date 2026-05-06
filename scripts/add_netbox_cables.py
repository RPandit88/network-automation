#!/usr/bin/env python3
"""
add_netbox_cables.py
Adds cable connections to NetBox matching the Containerlab topology.
This creates the source of truth for topology validation.
"""
import pynetbox

NETBOX_URL = "https://netbox.networkforai.com"
NETBOX_TOKEN = "YOUR_TOKEN_HERE"

nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)

# All connections from topology.yml
# Format: (device_a, interface_a, device_b, interface_b)
CONNECTIONS = [
    ("router1", "eth1", "SP1", "eth1"),
    ("router1", "eth2", "SP2", "eth1"),
    ("router1", "eth3", "SP3", "eth1"),
    ("SP1", "eth2", "SP4", "eth1"),
    ("SP1", "eth3", "SP5", "eth1"),
    ("SP1", "eth4", "SP6", "eth1"),
    ("SP1", "eth5", "SP7", "eth1"),
    ("SP2", "eth2", "SP4", "eth2"),
    ("SP2", "eth3", "SP5", "eth2"),
    ("SP2", "eth4", "SP6", "eth2"),
    ("SP2", "eth5", "SP7", "eth2"),
    ("SP3", "eth2", "SP4", "eth3"),
    ("SP3", "eth3", "SP5", "eth3"),
    ("SP3", "eth4", "SP6", "eth3"),
    ("SP3", "eth5", "SP7", "eth3"),
    ("SP4", "eth4", "SRV1", "eth1"),
    ("SP5", "eth4", "SRV2", "eth1"),
    ("SP6", "eth4", "SRV3", "eth1"),
    ("SP7", "eth4", "SRV4", "eth1"),
]

def get_interface_id(device_name, interface_name):
    """Get NetBox interface ID for a device and interface name."""
    ifaces = list(nb.dcim.interfaces.filter(
        device=device_name,
        name=interface_name
    ))
    if ifaces:
        return ifaces[0].id
    print(f"  WARNING: Interface {interface_name} not found on {device_name}")
    return None

print("Adding cable connections to NetBox...\n")
success = 0
failed = 0

for dev_a, iface_a, dev_b, iface_b in CONNECTIONS:
    id_a = get_interface_id(dev_a, iface_a)
    id_b = get_interface_id(dev_b, iface_b)

    if not id_a or not id_b:
        failed += 1
        continue

    try:
        cable = nb.dcim.cables.create({
            "a_terminations": [{"object_type": "dcim.interface", "object_id": id_a}],
            "b_terminations": [{"object_type": "dcim.interface", "object_id": id_b}],
            "status": "connected"
        })
        print(f"  ✓ {dev_a}:{iface_a} <-> {dev_b}:{iface_b}")
        success += 1
    except Exception as e:
        print(f"  ✗ {dev_a}:{iface_a} <-> {dev_b}:{iface_b} — {e}")
        failed += 1

print(f"\nDone — {success} cables added, {failed} failed")
