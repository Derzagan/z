

import socket
import json
import datetime
import sys
import concurrent.futures
import os
os.system("")  # включает ANSI в Windows CMD

TARGET_HOST  = "192.168.56.101"          # IP виртуальной машины (VirtualBox Host-only)
TARGET_PORTS = [                     # Типичные IoT/сервисные порты
    21, 22, 23, 25, 53, 80, 443,
    1883, 8883,                      # MQTT и MQTT over TLS
    5683, 5684,                      # CoAP
    8080, 8443, 8888,
    554,                             # RTSP (IP-камеры)
    3306, 5432,                      # БД
    6379,                            # Redis
    9200,                            # Elasticsearch
    27017,                           # MongoDB
]
TIMEOUT_SEC  = 0.5                   # Таймаут соединения (сек)
MAX_WORKERS  = 50                    # Потоки для параллельного сканирования

# Известные сервисы по портам
KNOWN_SERVICES = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
    53: "dns", 80: "http", 443: "https",
    554: "rtsp", 1883: "mqtt", 3306: "mysql",
    5432: "postgresql", 5683: "coap", 5684: "coaps",
    6379: "redis", 8080: "http-alt", 8443: "https-alt",
    8883: "mqtt-tls", 8888: "http-alt2",
    9200: "elasticsearch", 27017: "mongodb",
}

# ANSI-цвета (без colorama)
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def scan_port(host: str, port: int) -> dict | None:
    """Проверяем один порт — открыт или нет."""
    try:
        with socket.create_connection((host, port), timeout=TIMEOUT_SEC) as s:
            # Пытаемся получить баннер (не более 256 байт)
            try:
                s.settimeout(0.3)
                banner = s.recv(256).decode("utf-8", errors="ignore").strip()
            except Exception:
                banner = ""
            return {
                "port": port,
                "state": "open",
                "service": KNOWN_SERVICES.get(port, "unknown"),
                "banner": banner[:120] if banner else ""
            }
    except (ConnectionRefusedError, socket.timeout, OSError):
        return None  # Порт закрыт или недоступен


def run_scan(host: str, ports: list[int]) -> dict:
    """Параллельное сканирование всех портов."""
    results = {}
    print(f"\n{BOLD}{CYAN}Запускаю сканирование портов для {host}...{RESET}")
    print(f"{YELLOW}(сканируется {len(ports)} портов, может занять несколько секунд){RESET}\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(scan_port, host, p): p for p in ports}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                port = result["port"]
                results[str(port)] = {
                    "state": result["state"],
                    "service": result["service"],
                    "version": result["banner"]
                }
                # Вывод в реальном времени
                svc  = result["service"]
                col  = RED if svc in ("telnet", "ftp", "mqtt") else GREEN
                print(f"  {col}[OPEN]{RESET}  Порт {BOLD}{port:5d}{RESET}  |  {col}{svc}{RESET}",
                      f" — {result['banner'][:60]}" if result["banner"] else "")

    return results


def save_results(host: str, open_ports: dict) -> str:
    """Сохраняем отчёт в JSON с временной меткой."""
    ts  = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    fname = f"simple_scan_{ts}.json"
    report = {
        "scan_target": host,
        "scan_time": datetime.datetime.now().isoformat(),
        "open_ports_count": len(open_ports),
        "results": {host: open_ports}
    }
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return fname


def main():
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  IoT Port Scanner — Задание 3 (Лабораторная №9){RESET}")
    print(f"{BOLD}  Цель: {TARGET_HOST} (VirtualBox ВМ — разрешено){RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    # Основное сканирование
    open_ports = run_scan(TARGET_HOST, TARGET_PORTS)

    # Итоговый вывод
    print(f"\n{BOLD}{'─'*60}{RESET}")
    if open_ports:
        print(f"\n{BOLD}Найденные открытые порты:{RESET}")
        print(json.dumps({TARGET_HOST: open_ports}, ensure_ascii=False, indent=2))

        # Предупреждения о потенциально опасных портах
        dangerous = {"23": "telnet (нешифрованный)", "21": "ftp (нешифрованный)",
                     "1883": "MQTT без TLS", "27017": "MongoDB без аутентификации"}
        found_dangerous = [(p, dangerous[p]) for p in open_ports if p in dangerous]
        if found_dangerous:
            print(f"\n{RED}{BOLD}⚠  ПРЕДУПРЕЖДЕНИЯ БЕЗОПАСНОСТИ:{RESET}")
            for port, desc in found_dangerous:
                print(f"  {RED}• Порт {port} — {desc}{RESET}")
    else:
        print(f"\n{GREEN}Открытых портов не обнаружено.{RESET}")

    # Сохранение отчёта
    fname = save_results(TARGET_HOST, open_ports)
    print(f"\n{GREEN}✓ Результат сохранён в {BOLD}{fname}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Сканирование прервано пользователем.{RESET}")
        sys.exit(0)