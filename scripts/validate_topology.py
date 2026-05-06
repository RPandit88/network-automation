#!/usr/bin/env python3
"""
validate_topology.py
Collects LLDP neighbors from all devices and compares with NetBox.
Reports mismatches between actual topology and source of truth.
"""
import subprocess
import os
import json
import pynetbox

PREFIX = "clab-enterprise-spine-leaf"
DEVICES = ["SP1", "SP2", "SP3", "SP4", "SP5", "SP6", "SP7", "router1"]

NETBOX_URL = "https://netbox.networkforai.com"
NETBOX_TOKEN = os.environ.get("NETBOX_TOKEN", "")


def get_lldp_neighbors(device):
    container = f"{PREFIX}-{device}"
    result = subprocess.run(
        ["sudo", "docker", "exec", container,
         "sh", "-c", "lldpcli show neighbors 2>/dev/null"],
        capture_output=True, text=True
    )
    return result.stdout


def parse_lldp_output(output):
    neighbors = []
    current = {}
    for line in output.split("\n"):
        line = line.strip()
        if "Interface:" in line and "via:" in line:
            if current.get("local_interface") and current.get("neighbor"):
                neighbors.append(current)
            iface = line.split("Interface:")[1].split(",")[0].strip()
            current = {"local_interface": iface}
        elif "SysName:" in line:
            current["neighbor"] = line.split("SysName:")[1].strip()
        elif "PortDescr:" in line and "remote_interface" not in current:
            current["remote_interface"] = line.split("PortDescr:")[1].strip()
    if current.get("local_interface") and current.get("neighbor"):
        neighbors.append(current)
    return neighbors


def get_netbox_connections(device):
    nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)
    connections = []
    try:
        interfaces = list(nb.dcim.interfaces.filter(device=device))
        for iface in interfaces:
            if iface.cable:
                cable = nb.dcim.cables.get(iface.cable.id)
                for term in cable.a_terminations + cable.b_terminations:
                    if str(term.object.device) != device:
                        connections.append({
                            "local_interface": iface.name,
                            "neighbor": str(term.object.device),
                            "remote_interface": term.object.name
                        })
    except Exception as e:
        print(f"  NetBox error for {device}: {e}")
    return connections


def compare_topology(device, actual, expected):
    mismatches = []
    matches = []
    for exp in expected:
        found = False
        for act in actual:
            if (exp["local_interface"] == act.get("local_interface") and
                    exp["neighbor"].lower() == act.get("neighbor", "").lower()):
                found = True
                matches.append(exp)
                break
        if not found:
            mismatches.append({
                "type": "MISSING_LINK",
                "device": device,
                "expected": exp,
                "actual": None,
                "severity": "HIGH"
            })
    for act in actual:
        if act.get("local_interface") == "eth0":
            continue
        found = False
        for exp in expected:
            if exp["local_interface"] == act.get("local_interface"):
                found = True
                break
        if not found and act.get("neighbor"):
            mismatches.append({
                "type": "UNEXPECTED_LINK",
                "device": device,
                "expected": None,
                "actual": act,
                "severity": "MEDIUM"
            })
    return matches, mismatches


def main():
    print("Starting topology validation...\n")
    all_mismatches = []
    all_matches = []

    for device in DEVICES:
        print(f"Checking {device}...")
        raw_lldp = get_lldp_neighbors(device)
        actual = parse_lldp_output(raw_lldp)
        expected = get_netbox_connections(device)
        matches, mismatches = compare_topology(device, actual, expected)
        all_matches.extend(matches)
        all_mismatches.extend(mismatches)
        print(f"  Matches:    {len(matches)}")
        print(f"  Mismatches: {len(mismatches)}")
        for m in mismatches:
            print(f"  WARNING: {m['type']} — {m}")

    print(f"\n{'='*50}")
    print(f"TOPOLOGY VALIDATION SUMMARY")
    print(f"{'='*50}")
    print(f"Total matches:    {len(all_matches)}")
    print(f"Total mismatches: {len(all_mismatches)}")

    if all_mismatches:
        print(f"\nMISMATCHES FOUND:")
        for m in all_mismatches:
            print(f"\n  Type:     {m['type']}")
            print(f"  Device:   {m['device']}")
            print(f"  Expected: {m['expected']}")
            print(f"  Actual:   {m['actual']}")
            print(f"  Severity: {m['severity']}")
    else:
        print("\nTopology matches NetBox — all good!")

    return {"matches": len(all_matches), "mismatches": len(all_mismatches), "details": all_mismatches}


if __name__ == "__main__":
    result = main()
    print(f"\nFinal: {json.dumps(result, indent=2)}")
