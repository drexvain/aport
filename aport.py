import socket
import argparse
import threading
import time
import sys
import ipaddress
import urllib.parse
import queue
import colorama
from colorama import Fore, Style
import os
import platform
import random

colorama.init(autoreset=True)

open_ports = []
print_lock = threading.Lock()
task_queue = queue.Queue()


def resolve_url(target):
    try:
        parsed = urllib.parse.urlparse(target)
        hostname = parsed.netloc if parsed.netloc else parsed.path
        ip = socket.gethostbyname(hostname)
        print(f"{Fore.YELLOW}[~]{Style.RESET_ALL} resolved url to ip: {ip}")
        return ip
    except socket.gaierror:
        print(f"{Fore.RED}[x]{Style.RESET_ALL} failed to resolve url")
        sys.exit(1)


def scan_port(ip, port, timeout, banner):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            result = s.connect_ex((ip, port))
            if result == 0:
                with print_lock:
                    print(f"{Fore.GREEN}[+]{Style.RESET_ALL} port {port} open")
                    if banner:
                        try:
                            s.send(b'\n')
                            banner_data = s.recv(1024).decode(errors="ignore").strip()
                            print(f"{Fore.CYAN}banner:{Style.RESET_ALL} {banner_data}")
                        except:
                            pass
                open_ports.append(port)
        except:
            pass


def worker(ip, timeout, banner):
    while not task_queue.empty():
        port = task_queue.get()
        scan_port(ip, port, timeout, banner)
        task_queue.task_done()


def random_ports(count):
    ports = random.sample(range(1, 65535), count)
    return ports


def os_detect():
    return platform.system().lower()


def main():
    parser = argparse.ArgumentParser(
        description="by drxvain",
        formatter_class=argparse.RawTextHelpFormatter)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-ip", help="target ip address")
    group.add_argument("-url", help="target url (auto resolves ip)")

    parser.add_argument("-p", "--ports", default="1-1024", help="port range to scan ex: 1-65535")
    parser.add_argument("-t", "--threads", type=int, default=100, help="number of threads (default 100)")
    parser.add_argument("--timeout", type=float, default=0.5, help="socket timeout (default 0.5s)")
    parser.add_argument("--banner", action="store_true", help="try to extract service banner")
    parser.add_argument("--top", type=int, help="scan a random number of ports ex: --top 100")
    parser.add_argument("--common", action="store_true", help="scan most common ports")
    parser.add_argument("--os", action="store_true", help="show user's detected os")
    parser.add_argument("--verbose", action="store_true", help="soon")

    args = parser.parse_args()

    if args.url:
        ip = resolve_url(args.url)
    else:
        try:
            ip = str(ipaddress.ip_address(args.ip))
        except ValueError:
            print(f"{Fore.RED}[x]{Style.RESET_ALL} invalid ip")
            sys.exit(1)

    if args.top:
        port_list = random_ports(args.top)
    elif args.common:
        port_list = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 3389, 8080]
    else:
        try:
            start_port, end_port = map(int, args.ports.split("-"))
            port_list = list(range(start_port, end_port + 1))
        except:
            print(f"{Fore.RED}[x]{Style.RESET_ALL} invalid port range")
            sys.exit(1)

    if args.os:
        print(f"{Fore.YELLOW}[~]{Style.RESET_ALL} detected os: {os_detect()}")

    print(f"{Fore.CYAN}[~]{Style.RESET_ALL} scanning {ip} with {args.threads} threads\n")

    for port in port_list:
        task_queue.put(port)

    threads = []
    for _ in range(args.threads):
        t = threading.Thread(target=worker, args=(ip, args.timeout, args.banner))
        t.daemon = True
        t.start()
        threads.append(t)

    task_queue.join()

    print(f"\n{Fore.MAGENTA}[*]{Style.RESET_ALL} scan complete, {len(open_ports)} ports open:")
    for port in open_ports:
        print(f"  {Fore.GREEN}- {port}")


if __name__ == '__main__':
    start_time = time.time()
    main()
    print(f"\n{Fore.BLUE}[i]{Style.RESET_ALL} done in {time.time() - start_time:.2f}s")
