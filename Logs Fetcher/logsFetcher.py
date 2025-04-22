import pexpect
import threading
import os
from datetime import datetime

#Change for your credentials for ssh, these ones are just for show.
USERNAME = "cisco"
PASSWORD = "cisco"

SSH_OPTS = "-oKexAlgorithms=+diffie-hellman-group1-sha1 -c 3des-cbc"

#CHANGE THIS IF YOU WANT THE FOLDER WITH ANY OTHER NAME OR REMOVE THIS IF ON ROOT
#IF you do not create the script with create for you dont worry.
OUTPUT_DIR = "configs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def log(msg):
    #Can remove timestamps if time is not important for you.
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
    #This must match your txt with you IP address.
    with open("ips.txt", "r") as f:
        ips = [line.strip() for line in f if line.strip()]

    threads = []
    for ip in ips:
        t = threading.Thread(target=get_running_config, args=(ip,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    log("[<<] All configs collected. Finished.")

if __name__ == "__main__":
    main()
