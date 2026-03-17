

import re           # регулярные выражения для поиска ключевых слов
import json         # для сохранения отчёта в JSON
import csv          # для сохранения отчёта в CSV
import time         # для ожидания (сбор 60 секунд)
from datetime import datetime  # для временной метки в имени файла

# Подключаем paho-mqtt для работы с MQTT-брокером
try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("Ошибка: библиотека paho-mqtt не установлена.")
    print("Установите командой: pip install paho-mqtt")
    exit(1)

# Подключаем colorama для цветного вывода
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class DummyColor:
        RED = GREEN = YELLOW = CYAN = WHITE = MAGENTA = RESET_ALL = ''
    Fore = Style = DummyColor()

# ================================================================
# НАСТРОЙКИ — все константы в одном месте
# ================================================================
BROKER_IP    = "test.mosquitto.org"  # IP компьютера преподавателя с Mosquitto
BROKER_PORT  = 1883           # стандартный порт MQTT
TIMEOUT_SEC  = 60             # время сбора сообщений в секундах
TOPIC_FILTER = "#"            # '#' = все топики; можно поставить 'home/#'

# Аутентификация (раскомментируй если преподаватель включит)
# MQTT_USERNAME = "student"
# MQTT_PASSWORD = "secret"
MQTT_USERNAME = None
MQTT_PASSWORD = None
# ================================================================

# ----------------------------------------------------------------
# Ключевые слова для поиска конфиденциальных данных в payload
# re.IGNORECASE — ищем без учёта регистра (Password = password = PASSWORD)
# ----------------------------------------------------------------
SENSITIVE_PAYLOAD_RE = re.compile(
    r'\b(password|passwd|secret|token|apikey|api_key|key|admin|'
    r'admin123|12345|123456|pass|credential|auth_token|private_key)\b',
    re.IGNORECASE
)

# ----------------------------------------------------------------
# Ключевые слова для поиска подозрительных топиков
# ----------------------------------------------------------------
SUSPICIOUS_TOPIC_RE = re.compile(
    r'(config|setup|credential|auth|login|password|key|token|secret|admin)',
    re.IGNORECASE
)

# ----------------------------------------------------------------
# Глобальное состояние — сюда пишут колбэки, читает главный поток
# ----------------------------------------------------------------
state = {
    "messages":          [],    # все полученные сообщения
    "devices":           set(), # уникальные устройства
    "critical":          [],    # критические находки
    "suspicious_topics": set(), # подозрительные топики
    "connected":         False, # флаг подключения
}


# ================================================================
# КОЛБЭК on_connect — вызывается при подключении к брокеру
# ================================================================
def on_connect(client, userdata, flags, rc):
    # Словарь кодов ответа брокера
    codes = {
        0: "Успешно подключён",
        1: "Неверная версия протокола",
        2: "Недопустимый идентификатор клиента",
        3: "Сервер недоступен",
        4: "Неверные логин или пароль",
        5: "Нет прав доступа",
    }
    if rc == 0:
        state["connected"] = True
        print(f"{Fore.GREEN}✔  {codes[0]}: {BROKER_IP}:{BROKER_PORT}")
        # Подписываемся на топики сразу после подключения
        client.subscribe(TOPIC_FILTER)
        print(f"{Fore.CYAN}📡 Подписка на топик: '{TOPIC_FILTER}'")
        print(f"{Fore.CYAN}⏱  Сбор данных в течение {TIMEOUT_SEC} секунд...\n")
    else:
        print(f"{Fore.RED}✘  Ошибка подключения: {codes.get(rc, rc)}")


# ================================================================
# КОЛБЭК on_message — вызывается при получении каждого сообщения
# ================================================================
def on_message(client, userdata, msg):
    # Декодируем payload из байтов в текст
    topic   = msg.topic
    payload = msg.payload.decode("utf-8", errors="replace")
    ts      = datetime.now().isoformat(timespec="seconds")

    # Определяем устройство по первым 1-2 сегментам топика
    # Например: 'home/camera-01/status' → устройство = 'home/camera-01'
    parts  = topic.split("/")
    device = "/".join(parts[:2]) if len(parts) >= 2 else parts[0]
    state["devices"].add(device)

    # Проверяем payload на конфиденциальные слова через regex
    is_critical = bool(SENSITIVE_PAYLOAD_RE.search(payload))

    # Проверяем топик на подозрительные слова через regex
    is_suspicious = bool(SUSPICIOUS_TOPIC_RE.search(topic))
    if is_suspicious:
        state["suspicious_topics"].add(topic)

    # Сохраняем сообщение в общий список
    record = {
        "timestamp":  ts,
        "topic":      topic,
        "payload":    payload,
        "device":     device,
        "critical":   is_critical,
        "suspicious": is_suspicious,
    }
    state["messages"].append(record)

    # Если критическое — сохраняем отдельно и выводим сразу
    if is_critical:
        state["critical"].append(record)
        snippet = payload[:100]
        print(f"{Fore.RED}  🔴 КРИТИЧНО [{ts}] {topic}")
        print(f"{Fore.RED}     → {snippet}")
    elif is_suspicious:
        print(f"{Fore.YELLOW}  ⚠  Подозрительный топик [{ts}] {topic}")
    else:
        # Обычное сообщение — одна строка
        print(f"{Fore.WHITE}  📨 [{ts}] {topic[:50]:<50} | {payload[:40]}")


# ================================================================
# СОХРАНЕНИЕ ОТЧЁТОВ
# ================================================================

def save_json(data: dict, filename: str):
    """Сохраняет полный отчёт в JSON-файл с отступами."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{Fore.CYAN}💾 JSON сохранён: {filename}")


def save_csv(messages: list, filename: str):
    """Сохраняет все сообщения в CSV-файл."""
    if not messages:
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=messages[0].keys())
        writer.writeheader()
        writer.writerows(messages)
    print(f"{Fore.CYAN}💾 CSV сохранён:  {filename}")


# ================================================================
# ВЫВОД ИТОГОВОГО ОТЧЁТА В КОНСОЛЬ
# ================================================================

def print_report():
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}         ИТОГОВЫЙ ОТЧЁТ MQTT-СКАНИРОВАНИЯ")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.WHITE}  Брокер:                  {BROKER_IP}:{BROKER_PORT}")
    print(f"{Fore.WHITE}  Время сбора:             {TIMEOUT_SEC} сек.")
    print(f"{Fore.GREEN}  Уникальных устройств:    {len(state['devices'])}")
    print(f"{Fore.WHITE}  Всего сообщений:         {len(state['messages'])}")
    print(f"{Fore.YELLOW}  Подозрительных топиков: {len(state['suspicious_topics'])}")
    print(f"{Fore.RED}  Критических находок:    {len(state['critical'])}")

    # Список устройств
    print(f"\n{Fore.CYAN}  Список устройств:")
    for dev in sorted(state["devices"]):
        print(f"{Fore.WHITE}    • {dev}")

    # Список критических находок
    if state["critical"]:
        print(f"\n{Fore.RED}  Критические находки:")
        for rec in state["critical"]:
            snippet = rec["payload"][:120]
            print(f"{Fore.RED}    {rec['topic']}")
            print(f"{Fore.RED}      → {snippet}")

    print(f"{Fore.CYAN}{'='*60}\n")


# ================================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ================================================================

def main():
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}   MQTT IoT Sniffer — анализ трафика брокера")
    print(f"{Fore.CYAN}   Лабораторная работа №9, Задание 2")
    print(f"{Fore.CYAN}{'='*60}\n")

    # Создаём MQTT-клиент и привязываем колбэки
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Устанавливаем логин/пароль если заданы
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # Подключаемся к брокеру с обработкой ошибок
    try:
        print(f"{Fore.WHITE}Подключаюсь к {BROKER_IP}:{BROKER_PORT}...")
        client.connect(BROKER_IP, BROKER_PORT, keepalive=60)
    except ConnectionRefusedError:
        print(f"{Fore.RED}Ошибка: брокер отверг подключение. Проверьте IP и порт.")
        return
    except OSError as e:
        print(f"{Fore.RED}Сетевая ошибка: {e}")
        return

    # Запускаем сетевой цикл в фоне
    client.loop_start()

    # Ждём TIMEOUT_SEC секунд с обратным отсчётом
    try:
        for remaining in range(TIMEOUT_SEC, 0, -5):
            time.sleep(5)
            print(f"{Fore.CYAN}  ⏳ Осталось {remaining-5} сек. | "
                  f"Сообщений: {len(state['messages'])} | "
                  f"Критических: {len(state['critical'])}")
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Сбор прерван пользователем.")

    # Останавливаем клиент
    client.loop_stop()
    client.disconnect()

    # Выводим отчёт в консоль
    print_report()

    # Формируем имя файла с временной меткой
    ts_str    = datetime.now().strftime("%Y-%m-%d_%H-%M")
    json_file = f"mqtt_iot_scan_{ts_str}.json"
    csv_file  = f"mqtt_iot_scan_{ts_str}.csv"

    # Собираем данные для JSON
    report = {
        "scan_info": {
            "broker":       f"{BROKER_IP}:{BROKER_PORT}",
            "topic_filter": TOPIC_FILTER,
            "duration_sec": TIMEOUT_SEC,
            "timestamp":    ts_str,
        },
        "summary": {
            "total_messages":    len(state["messages"]),
            "unique_devices":    len(state["devices"]),
            "suspicious_topics": len(state["suspicious_topics"]),
            "critical_findings": len(state["critical"]),
        },
        "devices":           sorted(state["devices"]),
        "suspicious_topics": sorted(state["suspicious_topics"]),
        "critical_findings": state["critical"],
        "all_messages":      state["messages"],
    }

    # Сохраняем оба файла
    save_json(report, json_file)
    save_csv(state["messages"], csv_file)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Программа завершена пользователем.")
    except Exception as e:
        print(f"\n{Fore.RED}Неожиданная ошибка: {e}")