import requests
import os
import sys
from collections import Counter
from datetime import datetime

CONFIG = {
    "log_file_path": "sample_logs.txt",
    "alert_threshold": 5,
    "abuseipdb_api_key": "PUT_YOUR_API_KEY_HERE"
}

def parse_logs(file_path):
    if not os.path.exists(file_path):
        print("[ERROR] Log file not found:", file_path)
        sys.exit(1)

    events = []
    with open(file_path, "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 2:
                events.append({
                    "ip": parts[0],
                    "event_type": parts[1]
                })
    return events

def detect_bruteforce(events, threshold):
    counter = Counter()
    alerts = []

    for event in events:
        if event["event_type"] == "FAILED_LOGIN":
            counter[event["ip"]] += 1

    for ip, count in counter.items():
        if count >= threshold:
            alerts.append({
                "ip": ip,
                "attack_type": "Brute Force Attack",
                "attempts": count
            })

    return alerts

def get_ip_reputation(ip, api_key):
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Key": api_key,
        "Accept": "application/json"
    }
    params = {
        "ipAddress": ip,
        "maxAgeInDays": 90
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()["data"]["abuseConfidenceScore"]
        else:
            return "Unknown"
    except Exception:
        return "Error"

def block_ip(ip):
    print(f"[AUTO-RESPONSE] Blocking IP Address: {ip}")

def generate_report(alerts):
    with open("security_report.txt", "w") as report:
        report.write("SOC SECURITY AUTOMATION REPORT\n")
        report.write(f"Generated On: {datetime.now()}\n")
        report.write("=" * 40 + "\n\n")

        if not alerts:
            report.write("No threats detected.\n")
        else:
            for alert in alerts:
                report.write(f"IP: {alert['ip']}\n")
                report.write(f"Type: {alert['attack_type']}\n")
                report.write(f"Attempts: {alert['attempts']}\n")
                report.write(f"Reputation: {alert['reputation']}\n")
                report.write("-" * 40 + "\n")

    print("[INFO] Security report generated")

def main():
    print("[INFO] Starting SOC Security Automation Pipeline")

    events = parse_logs(CONFIG["log_file_path"])
    alerts = detect_bruteforce(events, CONFIG["alert_threshold"])

    for alert in alerts:
        alert["reputation"] = get_ip_reputation(
            alert["ip"], CONFIG["abuseipdb_api_key"]
        )
        block_ip(alert["ip"])

    generate_report(alerts)
    print("[SUCCESS] SOC Automation Pipeline Completed")

main()
