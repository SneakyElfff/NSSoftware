import socket
import struct
import threading
import time

ICMP_ECHO_REQUEST = 8


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

def create_packet(id):
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, id, 1)  # ICMP-header: type (8), code (8), checksum (16), id (16), sequence (16)
    data = struct.pack('d', time.time())

    checksum = calculate_checksum(header + data)
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, socket.htons(checksum), id, 1)
    return header + data

def ping_host(destination_addr, host_id):
    global sock
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
        sock.settimeout(2)

        ip = socket.gethostbyname(destination_addr)

        packet = create_packet(host_id)

        while packet:
            sent = sock.sendto(packet, (ip, 1))
            packet = packet[sent:]

        while True:
            # MSG_PEEK is used to peek data (get a copy) still saving it in the buffer
            peeked_data, addr = sock.recvfrom(1024, socket.MSG_PEEK)

            # if the address belongs to the host, the packet should be finally accepted
            if addr[0] == ip:
                # finally erasing data from the buffer
                response_data, addr = sock.recvfrom(1024)
                print(f"Получен ответ от {destination_addr} ({ip})")
                break

    except socket.error as e:
        print(f"Ошибка при отправке ping {destination_addr}: {e}")
    finally:
        sock.close()

def ping_hosts(hosts):
    threads = []
    for idx, host in enumerate(hosts):
        thread = threading.Thread(target=ping_host, args=(host, idx))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

hosts = [
    "localhost", "1.1.1.1", "8.8.8.8"
]
ping_hosts(hosts)
