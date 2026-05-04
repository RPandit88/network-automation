#!/usr/bin/env python3
"""
write_bgp_configs_v2.py
Fixed version for BIRD 3.x — adds explicit 'local' IP address to each
BGP peer block. BIRD 3.x requires knowing which local interface IP
to use when establishing the BGP TCP session.
"""
import subprocess
import time

PREFIX = "clab-enterprise-spine-leaf"

# Each device config now includes local IP for every BGP peer
CONFIGS = {
    "SP1": """
router id 10.0.0.1;

protocol kernel {
    ipv4 { export all; import all; };
}

protocol device { scan time 10; }

protocol bgp upstream {
    local 10.0.1.2 as 65001;
    neighbor 10.0.1.1 as 65000;
    ipv4 { import all; export all; };
}

protocol bgp sp4 {
    local 10.1.1.1 as 65001;
    neighbor 10.1.1.2 as 65004;
    ipv4 { import all; export all; };
}

protocol bgp sp5 {
    local 10.1.2.1 as 65001;
    neighbor 10.1.2.2 as 65005;
    ipv4 { import all; export all; };
}

protocol bgp sp6 {
    local 10.1.3.1 as 65001;
    neighbor 10.1.3.2 as 65006;
    ipv4 { import all; export all; };
}

protocol bgp sp7 {
    local 10.1.4.1 as 65001;
    neighbor 10.1.4.2 as 65007;
    ipv4 { import all; export all; };
}
""",
    "SP2": """
router id 10.0.0.2;

protocol kernel {
    ipv4 { export all; import all; };
}

protocol device { scan time 10; }

protocol bgp upstream {
    local 10.0.2.2 as 65001;
    neighbor 10.0.2.1 as 65000;
    ipv4 { import all; export all; };
}

protocol bgp sp4 {
    local 10.2.1.1 as 65001;
    neighbor 10.2.1.2 as 65004;
    ipv4 { import all; export all; };
}

protocol bgp sp5 {
    local 10.2.2.1 as 65001;
    neighbor 10.2.2.2 as 65005;
    ipv4 { import all; export all; };
}

protocol bgp sp6 {
    local 10.2.3.1 as 65001;
    neighbor 10.2.3.2 as 65006;
    ipv4 { import all; export all; };
}

protocol bgp sp7 {
    local 10.2.4.1 as 65001;
    neighbor 10.2.4.2 as 65007;
    ipv4 { import all; export all; };
}
""",
    "SP3": """
router id 10.0.0.3;

protocol kernel {
    ipv4 { export all; import all; };
}

protocol device { scan time 10; }

protocol bgp upstream {
    local 10.0.3.2 as 65001;
    neighbor 10.0.3.1 as 65000;
    ipv4 { import all; export all; };
}

protocol bgp sp4 {
    local 10.3.1.1 as 65001;
    neighbor 10.3.1.2 as 65004;
    ipv4 { import all; export all; };
}

protocol bgp sp5 {
    local 10.3.2.1 as 65001;
    neighbor 10.3.2.2 as 65005;
    ipv4 { import all; export all; };
}

protocol bgp sp6 {
    local 10.3.3.1 as 65001;
    neighbor 10.3.3.2 as 65006;
    ipv4 { import all; export all; };
}

protocol bgp sp7 {
    local 10.3.4.1 as 65001;
    neighbor 10.3.4.2 as 65007;
    ipv4 { import all; export all; };
}
""",
    "SP4": """
router id 10.0.0.4;

protocol kernel {
    ipv4 { export all; import all; };
}

protocol device { scan time 10; }

protocol bgp sp1 {
    local 10.1.1.2 as 65004;
    neighbor 10.1.1.1 as 65001;
    ipv4 { import all; export all; };
}

protocol bgp sp2 {
    local 10.2.1.2 as 65004;
    neighbor 10.2.1.1 as 65001;
    ipv4 { import all; export all; };
}

protocol bgp sp3 {
    local 10.3.1.2 as 65004;
    neighbor 10.3.1.1 as 65001;
    ipv4 { import all; export all; };
}
""",
    "SP5": """
router id 10.0.0.5;

protocol kernel {
    ipv4 { export all; import all; };
}

protocol device { scan time 10; }

protocol bgp sp1 {
    local 10.1.2.2 as 65005;
    neighbor 10.1.2.1 as 65001;
    ipv4 { import all; export all; };
}

protocol bgp sp2 {
    local 10.2.2.2 as 65005;
    neighbor 10.2.2.1 as 65001;
    ipv4 { import all; export all; };
}

protocol bgp sp3 {
    local 10.3.2.2 as 65005;
    neighbor 10.3.2.1 as 65001;
    ipv4 { import all; export all; };
}
""",
    "SP6": """
router id 10.0.0.6;

protocol kernel {
    ipv4 { export all; import all; };
}

protocol device { scan time 10; }

protocol bgp sp1 {
    local 10.1.3.2 as 65006;
    neighbor 10.1.3.1 as 65001;
    ipv4 { import all; export all; };
}

protocol bgp sp2 {
    local 10.2.3.2 as 65006;
    neighbor 10.2.3.1 as 65001;
    ipv4 { import all; export all; };
}

protocol bgp sp3 {
    local 10.3.3.2 as 65006;
    neighbor 10.3.3.1 as 65001;
    ipv4 { import all; export all; };
}
""",
    "SP7": """
router id 10.0.0.7;

protocol kernel {
    ipv4 { export all; import all; };
}

protocol device { scan time 10; }

protocol bgp sp1 {
    local 10.1.4.2 as 65007;
    neighbor 10.1.4.1 as 65001;
    ipv4 { import all; export all; };
}

protocol bgp sp2 {
    local 10.2.4.2 as 65007;
    neighbor 10.2.4.1 as 65001;
    ipv4 { import all; export all; };
}

protocol bgp sp3 {
    local 10.3.4.2 as 65007;
    neighbor 10.3.4.1 as 65001;
    ipv4 { import all; export all; };
}
""",
    "router1": """
router id 10.0.0.254;

protocol kernel {
    ipv4 { export all; import all; };
}

protocol device { scan time 10; }

protocol bgp sp1 {
    local 10.0.1.1 as 65000;
    neighbor 10.0.1.2 as 65001;
    ipv4 { import all; export all; };
}

protocol bgp sp2 {
    local 10.0.2.1 as 65000;
    neighbor 10.0.2.2 as 65001;
    ipv4 { import all; export all; };
}

protocol bgp sp3 {
    local 10.0.3.1 as 65000;
    neighbor 10.0.3.2 as 65001;
    ipv4 { import all; export all; };
}
""",
}

def write_and_start(device_name, config):
    """
    Write BIRD config using stdin pipe and restart BIRD.
    Using tee with stdin avoids all shell quoting and heredoc issues.
    """
    container = f"{PREFIX}-{device_name}"

    # Write config file using stdin pipe
    result = subprocess.run(
        ["sudo", "docker", "exec", "-i", container,
         "sh", "-c", "tee /etc/bird.conf > /dev/null"],
        input=config,
        text=True,
        capture_output=True
    )
    if result.returncode != 0:
        print(f"  {device_name}: ERROR writing config — {result.stderr}")
        return

    # Restart BIRD
    subprocess.run(
        ["sudo", "docker", "exec", container,
         "sh", "-c", "pkill bird 2>/dev/null; sleep 1; bird -c /etc/bird.conf"],
        capture_output=True
    )
    print(f"  {device_name}: configured and restarted")

def verify_bgp(device_name):
    """Show BGP session states — Established means working."""
    container = f"{PREFIX}-{device_name}"
    result = subprocess.run(
        ["sudo", "docker", "exec", container,
         "sh", "-c", "birdc show protocols"],
        capture_output=True, text=True
    )
    print(f"\n--- {device_name} ---")
    print(result.stdout)

print("Writing BGP v2 configs to all devices...\n")
for device, config in CONFIGS.items():
    print(f"Configuring {device}...")
    write_and_start(device, config)

print("\nWaiting 30 seconds for BGP sessions to establish...")
time.sleep(30)

print("\nVerifying BGP sessions...")
for device in ["SP1", "SP2", "SP3", "SP4", "router1"]:
    verify_bgp(device)

print("\nDone!")
