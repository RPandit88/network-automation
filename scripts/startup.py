#!/usr/bin/env python3
"""
startup.py
Master startup script - runs in correct order every time.
1. Configure IP addresses on all interfaces
2. Write correct BIRD configs with static routes into containers
"""
import subprocess
import sys
import time

scripts = [
    ("Configure device interfaces", "configure_devices.py"),
    ("Fix BIRD BGP configs with static routes", "fix_bird_configs.py"),
]

base = "/home/ubuntu/network-automation/scripts"

for description, script in scripts:
    print(f"\n{'='*50}")
    print(f"Step: {description}")
    print('='*50)
    result = subprocess.run(
        [sys.executable, f"{base}/{script}"],
        capture_output=False
    )
    if result.returncode != 0:
        print(f"ERROR in {script}")
        sys.exit(1)
    time.sleep(5)

print("\nAll done — network is fully configured!")
