#!/usr/bin/env python3
import pynetbox

# Connect to NetBox
nb = pynetbox.api(
    "https://netbox.networkforai.com",
    token="debazCPl3k95Y9CTfyfB9iEPIKcDfBUxhS3LKoZn"
)

# Step 1 — Create Site
site = nb.dcim.sites.get(slug="dc-lab") or \
       nb.dcim.sites.create(name="DC-Lab", slug="dc-lab", status="active")
print(f"Created site: {site.name}")

# Step 2 — Create Manufacturer
manufacturer = nb.dcim.manufacturers.create(name="Generic", slug="generic")
manufacturer = nb.dcim.manufacturers.get(slug="generic") or \
               nb.dcim.manufacturers.create(name="Generic", slug="generic")
print(f"Created manufacturer: {manufacturer.name}")

# Step 3 — Create Device Type
device_type = nb.dcim.device_types.get(slug="linux-container") or \
              nb.dcim.device_types.create(
                  manufacturer=manufacturer.id,
                  model="Linux Container",
                  slug="linux-container"
              )
print(f"Created device type: {device_type.model}")

# Step 4 — Create Device Roles
roles = {}
for role in ["spine", "leaf", "router", "server"]:
    r = nb.dcim.device_roles.get(slug=role) or \
        nb.dcim.device_roles.create(name=role, slug=role, color="0000ff")
    roles[role] = r.id

# Step 5 — Define all devices
devices = [
    {"name": "router1", "role": "router"},
    {"name": "SP1",     "role": "spine"},
    {"name": "SP2",     "role": "spine"},
    {"name": "SP3",     "role": "spine"},
    {"name": "SP4",     "role": "leaf"},
    {"name": "SP5",     "role": "leaf"},
    {"name": "SP6",     "role": "leaf"},
    {"name": "SP7",     "role": "leaf"},
    {"name": "SRV1",    "role": "server"},
    {"name": "SRV2",    "role": "server"},
    {"name": "SRV3",    "role": "server"},
    {"name": "SRV4",    "role": "server"},
]

# Step 6 — Create all devices
device_ids = {}
for d in devices:
    dev = nb.dcim.devices.create(
        name=d["name"],
        device_type=device_type.id,
        role=roles[d["role"]],
        site=site.id,
        status="active"
    )
    device_ids[d["name"]] = dev.id
    print(f"Created device: {d['name']}")

# Step 7 — Define interfaces and IPs
interfaces = {
    "router1": [
        {"name": "eth1", "ip": "10.0.1.1/30"},
        {"name": "eth2", "ip": "10.0.2.1/30"},
        {"name": "eth3", "ip": "10.0.3.1/30"},
    ],
    "SP1": [
        {"name": "eth1", "ip": "10.0.1.2/30"},
        {"name": "eth2", "ip": "10.1.1.1/30"},
        {"name": "eth3", "ip": "10.1.2.1/30"},
        {"name": "eth4", "ip": "10.1.3.1/30"},
        {"name": "eth5", "ip": "10.1.4.1/30"},
    ],
    "SP2": [
        {"name": "eth1", "ip": "10.0.2.2/30"},
        {"name": "eth2", "ip": "10.2.1.1/30"},
        {"name": "eth3", "ip": "10.2.2.1/30"},
        {"name": "eth4", "ip": "10.2.3.1/30"},
        {"name": "eth5", "ip": "10.2.4.1/30"},
    ],
    "SP3": [
        {"name": "eth1", "ip": "10.0.3.2/30"},
        {"name": "eth2", "ip": "10.3.1.1/30"},
        {"name": "eth3", "ip": "10.3.2.1/30"},
        {"name": "eth4", "ip": "10.3.3.1/30"},
        {"name": "eth5", "ip": "10.3.4.1/30"},
    ],
    "SP4": [
        {"name": "eth1", "ip": "10.1.1.2/30"},
        {"name": "eth2", "ip": "10.2.1.2/30"},
        {"name": "eth3", "ip": "10.3.1.2/30"},
        {"name": "eth4", "ip": "10.4.1.1/30"},
    ],
    "SP5": [
        {"name": "eth1", "ip": "10.1.2.2/30"},
        {"name": "eth2", "ip": "10.2.2.2/30"},
        {"name": "eth3", "ip": "10.3.2.2/30"},
        {"name": "eth4", "ip": "10.4.2.1/30"},
    ],
    "SP6": [
        {"name": "eth1", "ip": "10.1.3.2/30"},
        {"name": "eth2", "ip": "10.2.3.2/30"},
        {"name": "eth3", "ip": "10.3.3.2/30"},
        {"name": "eth4", "ip": "10.4.3.1/30"},
    ],
    "SP7": [
        {"name": "eth1", "ip": "10.1.4.2/30"},
        {"name": "eth2", "ip": "10.2.4.2/30"},
        {"name": "eth3", "ip": "10.3.4.2/30"},
        {"name": "eth4", "ip": "10.4.4.1/30"},
    ],
    "SRV1": [{"name": "eth1", "ip": "10.4.1.2/30"}],
    "SRV2": [{"name": "eth1", "ip": "10.4.2.2/30"}],
    "SRV3": [{"name": "eth1", "ip": "10.4.3.2/30"}],
    "SRV4": [{"name": "eth1", "ip": "10.4.4.2/30"}],
}

# Step 8 — Create interfaces and assign IPs
for device_name, ifaces in interfaces.items():
    for iface in ifaces:
        interface = nb.dcim.interfaces.create(
            device=device_ids[device_name],
            name=iface["name"],
            type="virtual"
        )
        ip = nb.ipam.ip_addresses.create(
            address=iface["ip"],
            assigned_object_type="dcim.interface",
            assigned_object_id=interface.id,
            status="active"
        )
        print(f"  {device_name} {iface['name']} = {iface['ip']}")

print("\nDone — all devices and IPs added to NetBox!")
