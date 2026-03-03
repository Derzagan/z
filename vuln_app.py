from flask import Flask, request
import os
import subprocess

app = Flask(__name__)

BASE_DIR = os.path.abspath("reports")

# Создаём секретный файл при запуске
os.makedirs("reports", exist_ok=True)
with open("reports/secret.txt", "w") as f:
    f.write("FLAG{path_traversal_success_2026}\n")
with open("reports/report.txt", "w") as f:
    f.write("This is a normal report file.\n")

@app.route("/view")
def view_file():
    filename = request.args.get("file", "")
    file_path = os.path.join(BASE_DIR, filename)
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return f"<pre style='font-size:16px; background:#f8f8f8; padding:15px;'>{content}</pre>"
    except Exception as e:
        return f"<pre>Файл не найден или ошибка: {str(e)}</pre>", 404

@app.route("/ping")
def ping():
    host = request.args.get("host", "")
    # Намеренно уязвимо — не экранируем ввод
    cmd = f"ping -n 2 {host}"
    try:
        output = subprocess.getoutput(cmd)
        return f"<pre>{output}</pre>"
    except Exception as e:
        return f"<pre>Ошибка: {str(e)}</pre>", 500

if __name__ == "__main__":
    print("Сервер запущен: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)