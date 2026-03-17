# iot_default_ip_checker.py
# Проверка: находится ли IP-адрес устройства IoT в типичных заводских диапазонах
# Лабораторная работа №9 — Задание 1

import ipaddress   # для работы с IP-адресами и подсетями
import subprocess  # для запуска системной команды ping
import sys         # для завершения программы при ошибке
import platform    # для определения операционной системы

# Подключаем colorama для цветного вывода в терминале
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    # Если colorama не установлена — делаем заглушки, программа всё равно работает
    class DummyColor:
        RED = GREEN = YELLOW = CYAN = RESET_ALL = ''
    Fore = Style = DummyColor()

# -------------------------------------------------------
# Список опасных диапазонов IoT-устройств (2025–2026)
# Устройства с этими адресами вероятно не сменили заводские настройки
# -------------------------------------------------------
DANGEROUS_NETWORKS = [
    ipaddress.ip_network("192.168.0.0/16"),    # домашние роутеры и IoT
    ipaddress.ip_network("192.168.1.0/24"),    # классика TP-Link, D-Link
    ipaddress.ip_network("192.168.2.0/24"),    # Apple Airport, Belkin
    ipaddress.ip_network("192.168.8.0/24"),    # Huawei роутеры
    ipaddress.ip_network("192.168.100.0/24"),  # кабельные модемы провайдеров
    ipaddress.ip_network("192.168.178.0/24"),  # Fritz!Box
    ipaddress.ip_network("10.0.0.0/8"),        # корпоративный IoT, заводы
    ipaddress.ip_network("172.16.0.0/12"),     # офисные сети
    ipaddress.ip_network("100.64.0.0/10"),     # CGNAT провайдеров
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("192.168.1.1"),
    ipaddress.ip_network("192.168.0.1"),    # ненастроенные устройства
]


def is_dangerous_address_or_subnet(addr_str: str) -> bool:
    """
    Проверяет, входит ли адрес или подсеть в один из опасных диапазонов.
    Принимает как одиночный IP (192.168.1.5), так и подсеть (192.168.0.0/16).
    """
    addr_str = addr_str.strip()

    # --- Проверка 1: пробуем распознать ввод как подсеть (есть символ "/") ---
    try:
        net = ipaddress.ip_network(addr_str, strict=False)
        # Проверяем: является ли введённая подсеть частью опасного диапазона
        for dangerous_net in DANGEROUS_NETWORKS:
            if net.subnet_of(dangerous_net):
                return True
        return False
    except ValueError:
        pass  # это не подсеть — идём дальше

    # --- Проверка 2: пробуем распознать ввод как одиночный IP-адрес ---
    try:
        ip = ipaddress.ip_address(addr_str)
        # Проверяем: входит ли IP в один из опасных диапазонов
        for net in DANGEROUS_NETWORKS:
            if ip in net:
                return True
        return False
    except ValueError as e:
        # --- Проверка 3: обработка некорректного ввода ---
        err_text = str(e)
        if "does not appear to be" in err_text:
            # Пользователь ввёл что-то вообще не похожее на IP
            print(f"{Fore.RED}Ошибка: '{addr_str}' — некорректный IP-адрес или подсеть.")
            print(f"  Каждый октет должен быть от 0 до 255")
            print(f"  Примеры правильных адресов: 192.168.1.45   10.1.20.178")
            print(f"  Примеры подсетей:           192.168.1.0/24  10.0.0.0/8")
        else:
            print(f"{Fore.RED}Ошибка формата: {err_text}")
        print(f"{Fore.YELLOW}Пожалуйста, введите корректный адрес и попробуйте снова.")
        sys.exit(1)


def can_ping(ip: str, timeout_sec: int = 2) -> bool:
    """
    Проверяет доступность устройства через системную команду ping.
    Работает на Windows и Linux/macOS.
    Возвращает True если устройство ответило, False если нет.
    """
    # --- Проверка 4: определяем параметры ping в зависимости от ОС ---
    if platform.system().lower() == "windows":
        count_param = "-n"               # Windows: флаг количества пингов
        timeout_param = "-w"             # Windows: флаг таймаута
        timeout_ms = timeout_sec * 1000  # Windows ждёт миллисекунды
    else:
        count_param = "-c"               # Linux/macOS: флаг количества пингов
        timeout_param = "-W"             # Linux/macOS: флаг таймаута
        timeout_ms = timeout_sec         # Linux/macOS ждёт секунды

    try:
        # --- Проверка 5: запускаем ping через subprocess ---
        # Это то же самое что написать в терминале: ping -c 2 -W 2 <ip>
        output = subprocess.check_output(
            ["ping", count_param, "2", timeout_param, str(timeout_ms), ip],
            stderr=subprocess.STDOUT,    # захватываем ошибки вместе с выводом
            universal_newlines=True,     # возвращаем текст, а не байты
            timeout=timeout_sec + 3      # общий таймаут на всю команду
        )
        # --- Проверка 6: анализируем текст ответа от ping ---
        # lower() — переводим в нижний регистр, т.к. Windows пишет TTL=, Linux — ttl=
        # any() — возвращает True если хотя бы одно слово из списка найдено
        return any(word in output.lower() for word in ["ttl=", "time=", "bytes from"])

    except subprocess.CalledProcessError:
        return False  # ping вернул ошибку — устройство не отвечает
    except subprocess.TimeoutExpired:
        return False  # ping завис — устройство недоступно
    except FileNotFoundError:
        return False  # команда ping не найдена в системе


def main():
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}  IoT IP Checker — проверка заводских диапазонов")
    print(f"{Fore.CYAN}  Лабораторная работа №9, Задание 1")
    print(f"{Fore.CYAN}{'='*60}\n")

    # Запрашиваем у пользователя IP-адрес или подсеть
    user_input = input(
        "Введите IP-адрес или подсеть\n"
        "(пример: 192.168.1.45 или 192.168.0.0/16): "
    ).strip()

    if not user_input:
        print(f"{Fore.RED}Ошибка: ввод пустой.")
        sys.exit(1)

    print()

    # --- Основная проверка: входит ли адрес в опасный диапазон? ---
    if not is_dangerous_address_or_subnet(user_input):
        # Адрес не входит ни в один опасный диапазон — всё хорошо
        print(f"{Fore.GREEN}✔  {user_input} НЕ относится к типичным заводским диапазонам IoT.")
        print(f"{Fore.GREEN}   Угроза использования заводского адреса не обнаружена.")
        return

    # Адрес входит в опасный диапазон — выводим предупреждение
    print(f"{Fore.YELLOW}⚠  Внимание! {user_input} попадает в потенциально опасный диапазон.")
    print(f"{Fore.YELLOW}   Часто используется по умолчанию в IoT-устройствах, роутерах, камерах.")

    # --- Проверка ping: только для одиночного IP, не для подсети ---
    if '/' in user_input:
        # Для подсети ping не имеет смысла — нельзя пинговать целую сеть
        print(f"\n{Fore.CYAN}ℹ  Ping пропущен — введена подсеть, а не одиночный адрес.")
    else:
        print(f"\nПроверка доступности {user_input} через ping...", end=" ", flush=True)

        if can_ping(user_input):
            # Устройство отвечает + опасный диапазон = критическое предупреждение
            print(f"{Fore.RED}ОТВЕЧАЕТ!\n")
            print(f"{Fore.RED}{'!'*60}")
            print(f"{Fore.RED}  КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ:")
            print(f"{Fore.RED}  Устройство активно и использует заводской IP-адрес!")
            print(f"{Fore.RED}  Рекомендации:")
            print(f"{Fore.RED}  1. Смените IP-адрес устройства.")
            print(f"{Fore.RED}  2. Отключите ответ на ICMP-запросы (ping).")
            print(f"{Fore.RED}  3. Смените заводской пароль администратора.")
            print(f"{Fore.RED}{'!'*60}")
        else:
            # Не отвечает — лучше, но не гарантия безопасности
            print(f"{Fore.GREEN}Не отвечает.")
            print(f"{Fore.GREEN}✔  Это лучше, но не гарантирует безопасность —")
            print(f"{Fore.GREEN}   устройство всё равно может быть уязвимо.")

    print(f"\n{Fore.CYAN}{'-'*60}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма завершена пользователем.")
    except Exception as e:
        print(f"\n{Fore.RED}Неожиданная ошибка: {e}")