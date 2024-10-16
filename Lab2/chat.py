import socket
import struct
import threading

# Настройки
BROADCAST_IP = '172.20.10.15'  # IP для широковещательной передачи
MULTICAST_GROUP = '224.0.0.1'     # Многоадресный IP
PORT = 12345
BUFFER_SIZE = 1024


def setup_broadcast_socket():
    """Настройка UDP-сокета для широковещательной передачи"""
    sock_broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # SO_REUSEADDR - для запуска на одной машине
    # sock_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sock_broadcast.bind(('', PORT))

    return sock_broadcast

def setup_multicast_socket():
    """Настройка UDP-сокета для многоадресной передачи"""
    sock_multicast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_multicast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # sock_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                              struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY))

    sock_multicast.bind(('', PORT))

    return sock_multicast

def receive_messages(sock):
    """Функция для приема сообщений"""
    while True:
        data, address = sock.recvfrom(BUFFER_SIZE)
        print(f"Получено сообщение от {address}: {data.decode('utf-8')}")

def send_messages(sock_broadcast, sock_multicast):
    """Функция для отправки сообщений"""
    while True:
        mode = input("Выберите режим (broadcast/multicast): ").strip().lower()
        message = input("Введите сообщение: ").strip()

        if mode == 'broadcast':
            sock_broadcast.sendto(message.encode('utf-8'), (BROADCAST_IP, PORT))
        elif mode == 'multicast':
            sock_multicast.sendto(message.encode('utf-8'), (MULTICAST_GROUP, PORT))
        else:
            print("Неверный режим. Введите 'broadcast' или 'multicast'.")


def main():
    sock_broadcast = setup_broadcast_socket()
    sock_multicast = setup_multicast_socket()

    receiving_broadcast_thread = threading.Thread(target=receive_messages, args=(sock_broadcast,))
    receiving_multicast_thread = threading.Thread(target=receive_messages, args=(sock_multicast,))

    sending_thread = threading.Thread(target=send_messages, args=(sock_broadcast, sock_multicast))

    receiving_broadcast_thread.start()
    receiving_multicast_thread.start()
    sending_thread.start()

    receiving_broadcast_thread.join()
    receiving_multicast_thread.join()
    sending_thread.join()


if __name__ == '__main__':
    main()