import os
import sys

# 1. Отключаем GPU до импортов, чтобы избежать ошибки DLL
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import cv2
from PyQt5 import uic, QtWidgets, QtGui

# 2. Безопасный импорт нейросети
try:
    from ultralytics import YOLO
except Exception as e:
    print(f"Ошибка импорта YOLO: {e}")

# 3. Загружаем интерфейсы
try:
    MainForm, MainWindow = uic.loadUiType("main_window.ui")
    DbForm, DbWindow = uic.loadUiType("materials_dialog.ui")
except Exception as e:
    print(f"Ошибка загрузки UI файлов: {e}")
    sys.exit(1)


# Окно базы данных
class MaterialsDialog(DbWindow):
    def __init__(self):
        super().__init__()
        self.form = DbForm()
        self.form.setupUi(self)

        # В твоем файле есть кнопка btnDelete
        if hasattr(self.form, 'btnDelete'):
            self.form.btnDelete.clicked.connect(self.delete_row)

    def delete_row(self):
        # Логика удаления (пока просто вывод в консоль для лабы)
        target_id = self.form.editDeleteId.text()
        print(f"Удаление материала с ID: {target_id}")
        QtWidgets.QMessageBox.information(self, "БД", f"Запись {target_id} удалена (имитация)")


# Главное окно программы
class App(MainWindow):
    def __init__(self):
        super().__init__()
        self.form = MainForm()
        self.form.setupUi(self)

        # Загрузка модели YOLO (принудительно на CPU)
        try:
            self.model = YOLO('yolov8n.pt')
        except Exception as e:
            print(f"Модель не загружена: {e}")

        # ПРИВЯЗКА КНОПОК
        # 1. Меню "Open" (в твоем файле это actionOpen)
        self.form.actionOpen.triggered.connect(self.load_image)

        # 2. Кнопка "Изменить" (btnChange) для вызова БД
        if hasattr(self.form, 'btnChange'):
            self.form.btnChange.clicked.connect(self.open_db)

        # 3. Кнопка анализа (btnAnalyze)
        if hasattr(self.form, 'btnAnalyze'):
            self.form.btnAnalyze.clicked.connect(self.run_analysis)

        self.image_path = None

    def open_db(self):
        self.db_dialog = MaterialsDialog()
        self.db_dialog.exec_()

    def load_image(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Открыть фото', '', 'Images (*.png *.jpg *.jpeg)')
        if fname:
            self.image_path = fname
            # Показываем исходное фото
            pix = QtGui.QPixmap(fname)
            # В твоем UI должен быть QLabel (например, внутри ScrollArea)
            # Если ты его не создал, добавь в дизайнере и назови label_img
            if hasattr(self.form, 'label_img'):
                self.form.label_img.setPixmap(pix)
                self.form.label_img.adjustSize()

    def run_analysis(self):
        if not self.image_path:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Сначала выберите фото через меню!")
            return

        # Запуск нейросети на CPU
        results = self.model(self.image_path, device='cpu')
        res_plot = results[0].plot()  # Картинка с рамками

        # Конвертация для вывода в интерфейс
        rgb_image = cv2.cvtColor(res_plot, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        qt_img = QtGui.QImage(rgb_image.data, w, h, ch * w, QtGui.QImage.Format_RGB888)

        if hasattr(self.form, 'label_img'):
            self.form.label_img.setPixmap(QtGui.QPixmap.fromImage(qt_img))
            self.form.label_img.adjustSize()

        # Пример логики СППР: выводим количество найденных объектов
        count = len(results[0].boxes)
        # В твоем UI есть поле lblResult или аналогичное?
        print(f"Найдено дефектов: {count}")
        QtWidgets.QMessageBox.information(self, "Результат СППР", f"Анализ завершен. Найдено объектов: {count}")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())