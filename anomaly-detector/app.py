#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import os
import subprocess
import datetime
from google import genai as google_genai
import time

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
PREFIX = "clab-enterprise-spine-leaf"
DEVICES = ["SP1", "SP2", "SP3", "SP4", "SP5", "SP6", "SP7", "router1"]


def redact_log(text, rules=None):
    if rules is None:
        rules = {"ip": True, "mac": True, "as": True, "host": True, "cred": True}
    out = text
    counts = {"ip": 0, "mac": 0, "as": 0, "host": 0, "cred": 0}
    ip_map = {}
    as_map = {}
    ip_idx = 1
    as_idx = 1

    if rules.get("cred"):
        def redact_cred(m):
            counts["cred"] += 1
            return m.group(1) + ": [REDACTED]"
        out = re.sub(
            r'(password|passwd|secret|community|auth[\s-]?key|md5|enable)\s*[:=]?\s*\S+',
            redact_cred, out, flags=re.IGNORECASE)

    if rules.get("mac"):
        def redact_mac(m):
            counts["mac"] += 1
            return "[MAC_REDACTED]"
        out = re.sub(r'([0-9a-fA-F]{2}[:\-]){5}[0-9a-fA-F]{2}', redact_mac, out)

    if rules.get("ip"):
        def redact_ip(m):
            nonlocal ip_idx
            counts["ip"] += 1
            full = m.group(0)
            key = re.sub(r'\/\d+$', '', full)
            suffix = full[len(key):]
            if key not in ip_map:
                ip_map[key] = f"[IP_{str(ip_idx).zfill(3)}]"
                ip_idx += 1
            return ip_map[key] + suffix
        out = re.sub(r'\b(\d{1,3}\.){3}\d{1,3}(\/\d{1,2})?\b', redact_ip, out)

    if rules.get("host"):
        def redact_host(m):
            counts["host"] += 1
            return "[HOST_REDACTED]"
        out = re.sub(
            r'\b(router|switch|sw|pe|ce|rr|spine|leaf|SP|SRV)-[\w\-]+\b',
            redact_host, out, flags=re.IGNORECASE)

    return {"redacted": out, "counts": counts}


def collect_device_logs(device):
    container = f"{PREFIX}-{device}"
    commands = ["birdc show protocols", "birdc show route count", "ip route show"]
    logs = []
    for cmd in commands:
        result = subprocess.run(
            ["sudo", "docker", "exec", container, "sh", "-c", cmd],
            capture_output=True, text=True, timeout=10)
        logs.append(f"=== {cmd} ===\n{result.stdout}")
    return "\n".join(logs)


def analyze_with_gemini(device, log_text):
    if not GEMINI_API_KEY:
        return {
            "analysis": "Gemini API key not configured",
            "severity": "UNKNOWN",
            "anomaly_detected": False,
            "recommendation": "Add GEMINI_API_KEY environment variable"
        }

    prompt = f"""You are a senior network operations engineer analyzing logs from a spine-leaf data center network.

Device: {device}
Time: {datetime.datetime.now().isoformat()}

Analyze the following network logs and identify any issues.

Respond in this EXACT format:
SEVERITY: [LOW/MEDIUM/HIGH/CRITICAL]
ANOMALY_DETECTED: [YES/NO]
ISSUES_FOUND: [describe specific issues or None detected]
ROOT_CAUSE: [likely root cause or N/A]
RECOMMENDED_ACTION: [specific steps to resolve or No action needed]
URGENCY: [immediate/scheduled/monitoring]

Network logs:
{log_text}"""

    for attempt in range(3):
        try:
            client = google_genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            text = response.text

            severity = "LOW"
            for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                if level in text.upper():
                    severity = level
                    break

            anomaly_detected = "ANOMALY_DETECTED: YES" in text.upper()

            recommendation = ""
            for line in text.split("\n"):
                if "RECOMMENDED_ACTION:" in line.upper():
                    recommendation = line.split(":", 1)[1].strip()
                    break

            return {
                "analysis": text,
                "severity": severity,
                "anomaly_detected": anomaly_detected,
                "recommendation": recommendation
            }

        except Exception as e:
            if "503" in str(e) and attempt < 2:
                time.sleep(10)
                continue
            return {
                "analysis": f"Error: {str(e)}",
                "severity": "UNKNOWN",
                "anomaly_detected": False,
                "recommendation": "Check API key and connectivity"
            }


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "network-anomaly-detector"})


@app.route("/redact", methods=["POST"])
def redact():
    body = request.get_json()
    log_text = body.get("log", "")
    rules = body.get("rules", None)
    result = redact_log(log_text, rules)
    return jsonify(result)


@app.route("/collect-and-analyze", methods=["POST"])
def collect_and_analyze():
    results = []
    anomalies_found = []
    for device in DEVICES:
        try:
            raw_logs = collect_device_logs(device)
            redacted = redact_log(raw_logs)
            analysis = analyze_with_gemini(device, redacted["redacted"])
            result = {
                "device": device,
                "timestamp": datetime.datetime.now().isoformat(),
                "severity": analysis["severity"],
                "anomaly_detected": analysis["anomaly_detected"],
                "analysis": analysis["analysis"],
                "recommendation": analysis["recommendation"],
                "redaction_counts": redacted["counts"]
            }
            results.append(result)
            if analysis["anomaly_detected"]:
                anomalies_found.append(result)
        except Exception as e:
            results.append({
                "device": device,
                "timestamp": datetime.datetime.now().isoformat(),
                "severity": "UNKNOWN",
                "anomaly_detected": False,
                "error": str(e)
            })
    return jsonify({
        "total_devices_checked": len(DEVICES),
        "anomalies_found": len(anomalies_found),
        "anomalies": anomalies_found,
        "all_results": results,
        "timestamp": datetime.datetime.now().isoformat()
    })


@app.route("/remediate", methods=["POST"])
def remediate():
    import sys
    result = subprocess.run(
        [sys.executable,
         "/home/ubuntu/network-automation/scripts/fix_bird_configs.py"],
        capture_output=True, text=True)
    return jsonify({
        "status": "remediation_complete",
        "output": result.stdout,
        "errors": result.stderr
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
