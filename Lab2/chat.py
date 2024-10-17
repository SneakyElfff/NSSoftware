import socket
import struct
import threading
import psutil

# Настройки
BROADCAST_IP = '192.168.0.255'  # IP для широковещательной передачи
MULTICAST_GROUP = '239.0.0.1'     # Многоадресный IP
PORT = 12345
BUFFER_SIZE = 1024

ignore_hosts = set()  # Список игнорируемых хостов
running = True  # Флаг для управления потоками

def get_local_ip_addresses():
    """Получение IP-адресов локальных устройств"""
    interfaces = psutil.net_if_addrs()
    local_ips = []

    for interface, addrs in interfaces.items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address not in ['0.0.0.0', '127.0.0.1']:
                local_ips.append(addr.address)

    print("IP-адреса локальных устройств:")
    for ip in local_ips:
        print(ip)

def list_running_ips():
    """Вывод списка IP-адресов запущенных приложений"""
    connections = psutil.net_connections(kind='inet')
    running_ips = set(conn.laddr[0] for conn in connections)
    print("\nСписок IP-адресов запущенных приложений:")
    for ip in running_ips:
        print(ip)

def setup_broadcast_socket():
    """Настройка UDP-сокета для широковещательной передачи"""
    sock_broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_broadcast.bind(('', PORT))
    return sock_broadcast

def setup_multicast_socket():
    """Настройка UDP-сокета для многоадресной передачи"""
    sock_multicast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_multicast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                              struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY))
    sock_multicast.bind(('', PORT))
    return sock_multicast

def receive_messages(sock):
    """Функция для приема сообщений"""
    while running:
        try:
            data, address = sock.recvfrom(BUFFER_SIZE)
            if address[0] in ignore_hosts:
                continue  # Игнорируем сообщения от игнорируемых адресов
            print(f"\nПолучено сообщение от {address}: {data.decode('utf-8')}")
        except Exception as e:
            print(f"Ошибка при получении сообщения: {e}")
            break

def send_messages(sock_broadcast, sock_multicast):
    """Функция для отправки сообщений"""
    global running
    while True:
        print("\nМеню:")
        print("1. Broadcast")
        print("2. Multicast")
        print("3. Игнорировать адрес")
        print("4. Отменить игнорирование адреса")
        print("5. Выход")

        choice = input("Выберите опцию: ").strip()

        if choice == '1':
            message = input("Введите сообщение для Broadcast: ").strip()
            sock_broadcast.sendto(message.encode('utf-8'), (BROADCAST_IP, PORT))
        elif choice == '2':
            message = input("Введите сообщение для Multicast: ").strip()
            sock_multicast.sendto(message.encode('utf-8'), (MULTICAST_GROUP, PORT))
        elif choice == '3':
            ignore_host = input("Введите IP-адрес для игнорирования: ").strip()
            ignore_hosts.add(ignore_host)
            print(f"Игнорирование адреса {ignore_host}.")
        elif choice == '4':
            unignore_host = input("Введите IP-адрес для отмены игнорирования: ").strip()
            ignore_hosts.discard(unignore_host)
            print(f"Адрес {unignore_host} больше не игнорируется.")
        elif choice == '5':
            print("Выход из многоадресной группы...")
            sock_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP,
                                       struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY))
            print("Вы вышли из многоадресной группы.")
            running = False  # Флаг завершения
            break
        else:
            print("Неверный выбор. Пожалуйста, выберите опцию из меню.")

def main():
    get_local_ip_addresses()
    list_running_ips()

    sock_broadcast = setup_broadcast_socket()
    sock_multicast = setup_multicast_socket()

    receiving_broadcast_thread = threading.Thread(target=receive_messages, args=(sock_broadcast,))
    receiving_multicast_thread = threading.Thread(target=receive_messages, args=(sock_multicast,))

    receiving_broadcast_thread.start()
    receiving_multicast_thread.start()

    send_messages(sock_broadcast, sock_multicast)

    # Ожидание завершения потоков приема
    receiving_broadcast_thread.join()
    receiving_multicast_thread.join()

if __name__ == '__main__':
    main()