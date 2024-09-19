import socket
import struct
import threading
import time

ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0
ICMP_TIME_EXCEEDED = 11
ICMP_DEST_UNREACH = 3
TIMEOUT = 2
MAX_TTL = 30


def calculate_checksum(source_string):
    """
    This function calculates the checksum of a given string.

    Parameters:
        source_string (str): The string to calculate the checksum of.

    Returns:
        int: The calculated checksum.
    """
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


def create_packet(host_id):
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, host_id, 1)  # ICMP-header: type (8), code (8), checksum (16), id (16), sequence (16)
    # time stamp
    data = struct.pack('d', time.time())

    checksum = calculate_checksum(header + data)
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, socket.htons(checksum), host_id, 1)
    return header + data


def parse_icmp_header(data):
    icmp_type, code, checksum = struct.unpack('bbH', data[20:24])
    return icmp_type, code


def traceroute_host(destination_addr, host_id):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
        sock.settimeout(TIMEOUT)

        ip = socket.gethostbyname(destination_addr)
        print(f"\nТрассировка до {destination_addr} ({ip}), max TTL = {MAX_TTL}")

        for ttl in range(1, MAX_TTL + 1):
            # set TTL for a packet
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)

            packet = create_packet(host_id)

            start_time = time.time()

            while packet:
                sent = sock.sendto(packet, (ip, 1))
                packet = packet[sent:]

            try:
                while True:
                    peeked_data, addr = sock.recvfrom(1024, socket.MSG_PEEK)

                    current_time = time.time()

                    if addr[0] == ip:
                        # finally erasing data from the buffer
                        response_data, addr = sock.recvfrom(1024)

                        icmp_type, code = parse_icmp_header(response_data)

                        time_sent = struct.unpack('d', response_data[28:28 + 8])[0]
                        # delay in ms
                        rtt = (current_time - time_sent) * 1000
                        print(f"{ttl}\t{addr[0]}\t{rtt:.2f} мс")

                        if icmp_type == ICMP_ECHO_REPLY:
                            print(f"{ttl}\t{addr[0]}\t{rtt:.2f} мс (Пинг-ответ)")
                            print(f"Достигнут узел {destination_addr}")
                            return
                        break

                    else:
                        # inner node (ICMP Time Exceeded)
                        response_data, addr = sock.recvfrom(1024)
                        icmp_type, code = parse_icmp_header(response_data)

                        rtt = (current_time - start_time) * 1000

                        if icmp_type == ICMP_TIME_EXCEEDED:
                            print(f"{ttl}\t{addr[0]}\t{rtt:.2f} мс (Время жизни истекло)")
                        elif icmp_type == ICMP_DEST_UNREACH:
                            print(f"{ttl}\t{addr[0]}\t(Хост недостижим)")
                            return

                        break

            except socket.timeout:
                print(f"{ttl}\t*")

    except socket.error as e:
        print(f"Ошибка при отправке пакета {destination_addr}: {e}")
    finally:
        sock.close()


def traceroute_hosts(hosts):
    for idx, host in enumerate(hosts):
        traceroute_host(host, idx)

hosts = [
    "localhost", "1.1.1.1", "8.8.8.8"
]
traceroute_hosts(hosts)
