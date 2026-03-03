import requests
from urllib.parse import urlparse
import ssl
import socket

def security_scanner():
    # Ввод URL
    url = input("Введите URL сайта (например https://example.com): ")
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc

    # 1️⃣ GET-запрос к сайту
    try:
        response = requests.get(url, timeout=10)
        headers = response.headers
        print("\nЗаголовки безопасности сайта:")
    except Exception as e:
        print("Ошибка запроса:", e)
        return

    # 2️⃣ Проверка заголовков
    results = {}

    # Strict-Transport-Security (HSTS)
    hsts = headers.get("Strict-Transport-Security")
    if hsts and "max-age=" in hsts:
        try:
            max_age = int(hsts.split("max-age=")[1].split(";")[0])
            results["HSTS"] = max_age >= 15552000  # ≥ 6 месяцев
        except:
            results["HSTS"] = False
    else:
        results["HSTS"] = False

    # X-Content-Type-Options
    results["X-Content-Type-Options"] = headers.get("X-Content-Type-Options","").lower() == "nosniff"

    # X-Frame-Options
    results["X-Frame-Options"] = headers.get("X-Frame-Options","").upper() in ["DENY", "SAMEORIGIN"]

    # Content-Security-Policy
    results["Content-Security-Policy"] = "Content-Security-Policy" in headers

    # X-XSS-Protection
    x_xss = headers.get("X-XSS-Protection","")
    results["X-XSS-Protection"] = x_xss.startswith("1")

    # Referrer-Policy
    referrer = headers.get("Referrer-Policy","").lower()
    results["Referrer-Policy"] = referrer in ["strict-origin-when-cross-origin","no-referrer","same-origin"]

    # 3️⃣ Проверка TLS (реальная версия)
    tls_results = {}
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                tls_version = ssock.version()
                # Помечаем старые версии как плохо
                tls_results["TLS 1.0"] = tls_version == "TLSv1"
                tls_results["TLS 1.1"] = tls_version == "TLSv1.1"
                tls_results["TLS 1.2"] = tls_version == "TLSv1.2"
                tls_results["TLS 1.3"] = tls_version == "TLSv1.3"
    except Exception as e:
        print("Ошибка TLS:", e)
        tls_results = {"TLS 1.0": False, "TLS 1.1": False, "TLS 1.2": False, "TLS 1.3": False}

    # 4️⃣ Вывод отчёта
    print("\n=== Security Headers ===")
    for k,v in results.items():
        print(f"{k}: {'✅' if v else '❌'}")

    print("\n=== TLS Versions ===")
    for k,v in tls_results.items():
        # TLS 1.0 / 1.1 — плохо
        if k in ["TLS 1.0","TLS 1.1"]:
            note = "❌" if v else "✅"
        else:
            note = "✅" if v else "❌"
        print(f"{k}: {note}")

# Запуск сканера
security_scanner()