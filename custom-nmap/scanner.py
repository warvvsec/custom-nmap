
import socket
import threading
import argparse
from queue import Queue

print_lock = threading.Lock()

def scan_port(target, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)

        result = s.connect_ex((target, port))
        if result == 0:
            with print_lock:
                print(f"[OPEN] Port {port}")

            try:
                s.send(b"Hello\r\n")
                banner = s.recv(1024).decode().strip()
                if banner:
                    with print_lock:
                        print(f"    └─ Banner: {banner}")
            except:
                pass

        s.close()
    except:
        pass

def worker():
    while True:
        port = q.get()
        scan_port(target, port)
        q.task_done()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Custom Nmap-like Port Scanner")
    parser.add_argument("-t", "--target", required=True, help="Target IP or hostname")
    parser.add_argument("-p", "--ports", default="1-1024", help="Port range (ex: 1-65535)")
    parser.add_argument("-th", "--threads", type=int, default=100, help="Number of threads")

    args = parser.parse_args()
    target = args.target
    start_port, end_port = map(int, args.ports.split("-"))

    q = Queue()

    print(f"\n🔎 Scanning {target} ports {start_port}-{end_port}\n")

    for _ in range(args.threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    for port in range(start_port, end_port + 1):
        q.put(port)

    q.join()
    print("\n✔ Scan completed.")
