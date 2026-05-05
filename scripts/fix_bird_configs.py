#!/usr/bin/env python3
"""
fix_bird_configs.py
Writes correct BIRD configs with static routes directly into each container.
This version includes graceful BIRD reloads to prevent BGP session drops
and proper exit-code evaluation for validation testing.
"""
import subprocess
import time

PREFIX = "clab-enterprise-spine-leaf"

CONFIGS = {
    "SP1": """router id 10.0.0.1;
protocol kernel { ipv4 { export all; import all; }; }
protocol device { scan time 10; }
protocol static {
    ipv4;
    route 10.1.1.0/30 blackhole;
    route 10.1.2.0/30 blackhole;
    route 10.1.3.0/30 blackhole;
    route 10.1.4.0/30 blackhole;
}
protocol bgp upstream { local 10.0.1.2 as 65001; neighbor 10.0.1.1 as 65000; ipv4 { import all; export all; }; }
protocol bgp sp4 { local 10.1.1.1 as 65001; neighbor 10.1.1.2 as 65004; ipv4 { import all; export all; }; }
protocol bgp sp5 { local 10.1.2.1 as 65001; neighbor 10.1.2.2 as 65005; ipv4 { import all; export all; }; }
protocol bgp sp6 { local 10.1.3.1 as 65001; neighbor 10.1.3.2 as 65006; ipv4 { import all; export all; }; }
protocol bgp sp7 { local 10.1.4.1 as 65001; neighbor 10.1.4.2 as 65007; ipv4 { import all; export all; }; }
""",
    "SP2": """router id 10.0.0.2;
protocol kernel { ipv4 { export all; import all; }; }
protocol device { scan time 10; }
protocol static {
    ipv4;
    route 10.2.1.0/30 blackhole;
    route 10.2.2.0/30 blackhole;
    route 10.2.3.0/30 blackhole;
    route 10.2.4.0/30 blackhole;
}
protocol bgp upstream { local 10.0.2.2 as 65001; neighbor 10.0.2.1 as 65000; ipv4 { import all; export all; }; }
protocol bgp sp4 { local 10.2.1.1 as 65001; neighbor 10.2.1.2 as 65004; ipv4 { import all; export all; }; }
protocol bgp sp5 { local 10.2.2.1 as 65001; neighbor 10.2.2.2 as 65005; ipv4 { import all; export all; }; }
protocol bgp sp6 { local 10.2.3.1 as 65001; neighbor 10.2.3.2 as 65006; ipv4 { import all; export all; }; }
protocol bgp sp7 { local 10.2.4.1 as 65001; neighbor 10.2.4.2 as 65007; ipv4 { import all; export all; }; }
""",
    "SP3": """router id 10.0.0.3;
protocol kernel { ipv4 { export all; import all; }; }
protocol device { scan time 10; }
protocol static {
    ipv4;
    route 10.3.1.0/30 blackhole;
    route 10.3.2.0/30 blackhole;
    route 10.3.3.0/30 blackhole;
    route 10.3.4.0/30 blackhole;
}
protocol bgp upstream { local 10.0.3.2 as 65001; neighbor 10.0.3.1 as 65000; ipv4 { import all; export all; }; }
protocol bgp sp4 { local 10.3.1.1 as 65001; neighbor 10.3.1.2 as 65004; ipv4 { import all; export all; }; }
protocol bgp sp5 { local 10.3.2.1 as 65001; neighbor 10.3.2.2 as 65005; ipv4 { import all; export all; }; }
protocol bgp sp6 { local 10.3.3.1 as 65001; neighbor 10.3.3.2 as 65006; ipv4 { import all; export all; }; }
protocol bgp sp7 { local 10.3.4.1 as 65001; neighbor 10.3.4.2 as 65007; ipv4 { import all; export all; }; }
""",
    "SP4": """router id 10.0.0.4;
protocol kernel { ipv4 { export all; import all; }; }
protocol device { scan time 10; }
protocol static {
    ipv4;
    route 10.4.1.0/30 blackhole;
}
protocol bgp sp1 { local 10.1.1.2 as 65004; neighbor 10.1.1.1 as 65001; ipv4 { import all; export all; }; }
protocol bgp sp2 { local 10.2.1.2 as 65004; neighbor 10.2.1.1 as 65001; ipv4 { import all; export all; }; }
protocol bgp sp3 { local 10.3.1.2 as 65004; neighbor 10.3.1.1 as 65001; ipv4 { import all; export all; }; }
""",
    "SP5": """router id 10.0.0.5;
protocol kernel { ipv4 { export all; import all; }; }
protocol device { scan time 10; }
protocol static {
    ipv4;
    route 10.4.2.0/30 blackhole;
}
protocol bgp sp1 { local 10.1.2.2 as 65005; neighbor 10.1.2.1 as 65001; ipv4 { import all; export all; }; }
protocol bgp sp2 { local 10.2.2.2 as 65005; neighbor 10.2.2.1 as 65001; ipv4 { import all; export all; }; }
protocol bgp sp3 { local 10.3.2.2 as 65005; neighbor 10.3.2.1 as 65001; ipv4 { import all; export all; }; }
""",
    "SP6": """router id 10.0.0.6;
protocol kernel { ipv4 { export all; import all; }; }
protocol device { scan time 10; }
protocol static {
    ipv4;
    route 10.4.3.0/30 blackhole;
}
protocol bgp sp1 { local 10.1.3.2 as 65006; neighbor 10.1.3.1 as 65001; ipv4 { import all; export all; }; }
protocol bgp sp2 { local 10.2.3.2 as 65006; neighbor 10.2.3.1 as 65001; ipv4 { import all; export all; }; }
protocol bgp sp3 { local 10.3.3.2 as 65006; neighbor 10.3.3.1 as 65001; ipv4 { import all; export all; }; }
""",
    "SP7": """router id 10.0.0.7;
protocol kernel { ipv4 { export all; import all; }; }
protocol device { scan time 10; }
protocol static {
    ipv4;
    route 10.4.4.0/30 blackhole;
}
protocol bgp sp1 { local 10.1.4.2 as 65007; neighbor 10.1.4.1 as 65001; ipv4 { import all; export all; }; }
protocol bgp sp2 { local 10.2.4.2 as 65007; neighbor 10.2.4.1 as 65001; ipv4 { import all; export all; }; }
protocol bgp sp3 { local 10.3.4.2 as 65007; neighbor 10.3.4.1 as 65001; ipv4 { import all; export all; }; }
""",
    "router1": """router id 10.0.0.254;
protocol kernel { ipv4 { export all; import all; }; }
protocol device { scan time 10; }
protocol static {
    ipv4;
    route 10.0.1.0/30 blackhole;
    route 10.0.2.0/30 blackhole;
    route 10.0.3.0/30 blackhole;
}
protocol bgp sp1 { local 10.0.1.1 as 65000; neighbor 10.0.1.2 as 65001; ipv4 { import all; export all; }; }
protocol bgp sp2 { local 10.0.2.1 as 65000; neighbor 10.0.2.2 as 65001; ipv4 { import all; export all; }; }
protocol bgp sp3 { local 10.0.3.1 as 65000; neighbor 10.0.3.2 as 65001; ipv4 { import all; export all; }; }
""",
}


def write_config(device, config):
    """Write config directly into container using stdin pipe."""
    container = f"{PREFIX}-{device}"
    result = subprocess.run(
        ["sudo", "docker", "exec", "-i", container,
         "sh", "-c", "tee /etc/bird.conf > /dev/null"],
        input=config,
        text=True,
        capture_output=True
    )
    if result.returncode != 0:
        print(f"  {device}: ERROR writing - {result.stderr}")
        return False
    return True


def restart_bird(device):
    """Gracefully reload BIRD config, or start it if it isn't running."""
    container = f"{PREFIX}-{device}"
    subprocess.run(
        ["sudo", "docker", "exec", container,
         "sh", "-c", "birdc configure || bird -c /etc/bird.conf"],
        capture_output=True
    )


def verify(device):
    """Show protocols to confirm configuration is loaded."""
    container = f"{PREFIX}-{device}"
    result = subprocess.run(
        ["sudo", "docker", "exec", container,
         "sh", "-c", "birdc show protocols"],
        capture_output=True, text=True
    )
    print(f"\n--- {device} ---")
    print(result.stdout)


print("Writing correct BIRD configs into all containers...\n")
for device, config in CONFIGS.items():
    if write_config(device, config):
        restart_bird(device)
        print(f"  {device}: config written and BIRD gracefully reloaded")

print("\nWaiting 15 seconds for BGP to converge...")
time.sleep(15) # Reduced from 30s since hitless reloads are faster than full restarts

print("\nVerifying protocols...")
for device in ["SP1", "SP4", "SP7"]:
    verify(device)

print("\nTesting end to end connectivity...")
result = subprocess.run(
    ["sudo", "docker", "exec",
     f"{PREFIX}-SP4",
     "ping", "-c", "3", "10.4.4.1"],
    capture_output=True, text=True
)

print(result.stdout)

if result.returncode == 0:
    print("✅ Ping successful! Fabric is routing end-to-end.")
else:
    print("❌ Ping failed! Ensure 10.4.4.1 is assigned to a loopback on SP7, otherwise the blackhole route will drop the ICMP packet.")
    
print("Done!")
