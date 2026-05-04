#!/usr/bin/env python3
import os
import yaml
import pynetbox

# Connect to NetBox
nb = pynetbox.api(
    "https://netbox.networkforai.com",
    token="debazCPl3k95Y9CTfyfB9iEPIKcDfBUxhS3LKoZn"
)

output_dir = os.path.expanduser("~/network-automation/host_vars")
os.makedirs(output_dir, exist_ok=True)

# Get all devices from NetBox
devices = nb.dcim.devices.all()

for device in devices:
    device_name = device.name
    
    # Get interfaces for this device
    interfaces = list(nb.dcim.interfaces.filter(device=device_name))
    
    iface_list = []
    for iface in interfaces:
        ips = list(nb.ipam.ip_addresses.filter(interface_id=iface.id))
        for ip in ips:
            ip_addr = str(ip.address).split("/")[0]
            prefix = str(ip.address).split("/")[1]
            iface_list.append({
                "name": iface.name,
                "ip": ip_addr,
                "prefix": int(prefix)
            })

    data = {
        "interfaces": iface_list
    }

    filepath = os.path.join(output_dir, f"{device_name}.yml")
    with open(filepath, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
    print(f"Generated {filepath}")

print(f"\nDone — host_vars generated from NetBox")
