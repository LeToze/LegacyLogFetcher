import pexpect
import threading
import os
from datetime import datetime

USERNAME = "cisco"
PASSWORD = "cisco"

SSH_OPTS = "-oKexAlgorithms=+diffie-hellman-group1-sha1 -c 3des-cbc"

OUTPUT_DIR = "configs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def get_running_config(ip):
    try:
        log(f"[{{}}] Connecting to {ip}...")
        cmd = f"ssh {SSH_OPTS} {USERNAME}@{ip}"
        child = pexpect.spawn(cmd, timeout=30)

        child.expect("Password:")
        child.sendline(PASSWORD)

        child.expect("#")
        child.sendline("terminal length 0")
        child.expect("#")

        child.sendline("show version | include uptime")
        child.expect("#")
        version_output = child.before.decode()
        hostname = (f"{ip}")

        child.sendline("show running-config")
        child.expect("#")
        config_output = child.before.decode()

        filename = os.path.join(OUTPUT_DIR, f"{hostname}_running_config.txt")
        with open(filename, "w") as f:
            f.write(config_output)

        log(f"[>>] Saved config from {ip} as {filename}")

        child.sendline("exit")
        child.close()

    except Exception as e:
        log(f"[X] ERROR with {ip}: {e}")

def main():
    with open("ips.txt", "r") as f:
        ips = [line.strip() for line in f if line.strip()]

    threads = []
    for ip in ips:
        t = threading.Thread(target=get_running_config, args=(ip,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    log("[<<] All configs collected. Finishing...")

if __name__ == "__main__":
    main()
