from PyQt5 import uic
from PyQt5.QtWidgets import QApplication

# Загружаем интерфейс из файла .ui
# Убедись, что файл uisppr.ui находится в той же папке, что и этот скрипт
Form, Window = uic.loadUiType("uisppr.ui")

# Инициализация приложения
app = QApplication([])

# Создаем объекты окна и формы
window = Window()
form = Form()

# Настраиваем интерфейс внутри окна
form.setupUi(window)

# Отображаем окно
window.show()

# Запускаем цикл обработки событий приложения
app.exec_()