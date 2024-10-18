import socket
import struct
import threading
import netifaces


# Настройки
BROADCAST_IP = '192.168.0.255'  # IP для широковещательной передачи
MULTICAST_GROUP = '224.0.0.1'     # Многоадресный IP
PORT = 12345
BUFFER_SIZE = 1024

ignored_hosts = set()  # Список игнорируемых хостов
running = True  # Флаг для управления потоками


def list_running_ips():
    """Вывод списка IP-адресов запущенных приложений с масками и широковещательными адресами"""
    print("\nСписок IP-адресов запущенных приложений, маски и широковещательные адреса:")
    interfaces = netifaces.interfaces()

    for i in interfaces:
        data = netifaces.ifaddresses(i)
        if netifaces.AF_INET in data:
            ip_info = data[netifaces.AF_INET][0]
            ip_address = ip_info.get('addr', 'N/A')
            netmask = ip_info.get('netmask', 'N/A')
            broadcast = ip_info.get('broadcast', 'N/A')

            print(f"Интерфейс: {i}")
            print(f"IP-адрес: {ip_address}")
            print(f"Маска сети: {netmask}")
            print(f"Адрес широковещательной передачи: {broadcast}")
            print('-' * 50)


def setup_broadcast_socket():
    """Настройка UDP-сокета для широковещательной передачи"""
    sock_broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # SO_REUSEADDR - для запуска на одной машине
    # sock_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sock_broadcast.bind(('', PORT))  # привязка сокета к любому доступному адресу ('') и порту

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
    while running:
        try:
            data, address = sock.recvfrom(BUFFER_SIZE)

            if address[0] in ignored_hosts:
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
        print("5. Выйти из группы")

        choice = input("Выберите опцию: ").strip()

        if choice == '1':
            message = input("Введите сообщение для Broadcast: ").strip()
            sock_broadcast.sendto(message.encode('utf-8'), (BROADCAST_IP, PORT))

        elif choice == '2':
            message = input("Введите сообщение для Multicast: ").strip()
            sock_multicast.sendto(message.encode('utf-8'), (MULTICAST_GROUP, PORT))

        elif choice == '3':
            ignored_host = input("Введите IP-адрес для игнорирования: ").strip()
            ignored_hosts.add(ignored_host)
            print(f"Игнорирование адреса {ignored_host}.")

        elif choice == '4':
            unignored_host = input("Введите IP-адрес для отмены игнорирования: ").strip()
            ignored_hosts.discard(unignored_host)
            print(f"Адрес {unignored_host} больше не игнорируется.")

        elif choice == '5':
            print("Выход из многоадресной группы...")
            sock_multicast.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP,
                                       struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY))
            print("Вы вышли из многоадресной группы.")

            running = False
            continue

        else:
            print("Неверный выбор. Пожалуйста, выберите опцию из меню.")


def main():
    list_running_ips()

    sock_broadcast = setup_broadcast_socket()
    sock_multicast = setup_multicast_socket()

    receiving_broadcast_thread = threading.Thread(target=receive_messages, args=(sock_broadcast,))
    receiving_multicast_thread = threading.Thread(target=receive_messages, args=(sock_multicast,))

    sending_thread = threading.Thread(target=send_messages, args=(sock_broadcast, sock_multicast))

    receiving_broadcast_thread.start()
    receiving_multicast_thread.start()
    sending_thread.start()

    # send_messages(sock_broadcast, sock_multicast)

    # Ожидание завершения потоков приема
    # receiving_broadcast_thread.join()
    # receiving_multicast_thread.join()
    # sending_thread.join()


if __name__ == '__main__':
    main()
