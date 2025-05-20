import time
import json
import requests
import platform
import uuid
import os

# Simulate system checks (replace with actual system calls per OS)
def check_disk_encryption():
    # Placeholder for demo; real check varies by OS
    return "encrypted"

def check_os_update():
    # Simulate current vs latest
    return {"current": platform.release(), "latest": platform.release()}

def check_antivirus():
    # Placeholder: check for presence of common AV software
    return "active"

def check_inactivity_sleep():
    # Simulate inactivity sleep setting in minutes
    return 10

# Save last sent data to avoid sending duplicates
LAST_STATE_FILE = "last_state.json"

def load_last_state():
    if os.path.exists(LAST_STATE_FILE):
        with open(LAST_STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_last_state(state):
    with open(LAST_STATE_FILE, "w") as f:
        json.dump(state, f)

def get_system_state():
    return {
        "disk_encryption": check_disk_encryption(),
        "os_update": check_os_update(),
        "antivirus": check_antivirus(),
        "inactivity_sleep": check_inactivity_sleep(),
    }

def main():
    MACHINE_ID = str(uuid.getnode())  # use MAC address as machine ID
    API_ENDPOINT = "http://localhost:5000/api/report"  # your backend

    while True:
        current_state = get_system_state()
        last_state = load_last_state()

        if current_state != last_state:
            payload = {
                "machine_id": MACHINE_ID,
                "state": current_state,
                "timestamp": time.time()
            }
            try:
                response = requests.post(API_ENDPOINT, json=payload)
                if response.status_code == 200:
                    print("Reported update to server.")
                    save_last_state(current_state)
                else:
                    print("Failed to report:", response.text)
            except Exception as e:
                print("Error sending update:", e)
        else:
            print("No changes detected.")

        time.sleep(60 * 15)  # Sleep for 15 minutes

if __name__ == "__main__":
    main()
