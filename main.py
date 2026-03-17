import os
import sys
import json
import cv2
import numpy as np
from datetime import datetime
from PyQt5 import uic, QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (QMainWindow, QDialog, QTableWidget,
                              QTableWidgetItem, QHeaderView, QMessageBox,
                              QScrollArea, QInputDialog)

try:
    MainForm, MainWindow = uic.loadUiType("main_window.ui")
    DbForm, DbWindow     = uic.loadUiType("materials_dialog.ui")
except Exception as e:
    print(f"Ошибка загрузки UI файлов: {e}")
    sys.exit(1)

TRANSLATIONS = {
    "ru": {
        "window_title":      "СППР — Качество пористого материала",
        "menu_data":         "Исходные данные для анализа",
        "menu_open":         "Открыть",
        "menu_webcam":       "Веб-камера",
        "menu_language":     "Язык",
        "menu_russian":      "Русский",
        "menu_english":      "Английский",
        "menu_help":         "Помощь",
        "btn_snapshot":      "Снимок",
        "btn_edit_db":       "Изменить",
        "btn_save_report":   "Сохранить в отчет",
        "lbl_contrast":      "Контрастность",
        "lbl_brightness":    "Яркость",
        "lbl_sharpness":     "Резкость",
        "lbl_pore_area":     "Площадь поры",
        "lbl_report_title":  "Отчет:",
        "lbl_porosity_eq":   "Пористость =",
        "lbl_porosity_word": "Пористость",
        "lbl_pores_exceed":  "Количество пор, площадь\nкоторых превышает норму:",
        "status_ok":         "в норме",
        "status_bad":        "превышает норму",
        "status_ok_short":   "Годен",
        "status_bad_short":  "Не годен",
        "source_file":       "📁 Источник: файл",
        "source_cam":        "📷 Источник: веб-камера",
        "source_none":       "⚠ Источник не выбран",
        "msg_no_image":      "Сначала выберите фото через меню 'Исходные данные'!",
        "msg_no_data":       "Нет данных для сохранения. Выполните анализ!",
        "msg_result_title":  "Результат анализа",
        "msg_result_body":   "Найдено пор: {count}\nПористость: {por:.8f}\nПор с превышением нормы: {bad}",
        "msg_saved":         "Сохранено",
        "msg_saved_body":    "Отчёт сохранён в {fname}",
        "dlg_open_title":    "Открыть фото",
        "dlg_save_title":    "Сохранить отчёт",
        "err_title":         "Ошибка",
        "db_title":          "База данных материалов",
        "db_add_group":      "Добавить запись",
        "db_del_group":      "Удалить запись",
        "db_btn_add":        "Добавить",
        "db_btn_delete":     "Удалить",
        "db_btn_ok":         "ОК",
        "db_ph_name":        "название материала",
        "db_ph_area":        "площадь поры",
        "db_ph_area_dev":    "откл. от площ.",
        "db_ph_porosity":    "пористость",
        "db_ph_por_dev":     "откл. от порист.",
        "db_ph_delete_id":   "номер записи",
        "db_msg_added":      "Материал '{name}' добавлен",
        "db_msg_deleted":    "Запись {id} удалена",
        "db_confirm_del":    "Удалить запись №{id}?\nМатериал: {name}",
        "db_confirm_title":  "Подтверждение удаления",
        "db_err_no_name":    "Введите название материала!",
        "db_err_no_id":      "Введите номер записи!",
        "db_filter_lbl":     "Фильтр по названию:",
        "db_filter_area":    "Площадь поры от:",
        "db_filter_to":      "до:",
        "db_filter_btn":     "Применить",
        "db_filter_reset":   "Сбросить",
        "history_title":     "История анализов",
        "history_num":       "№",
        "history_date":      "Дата",
        "history_time":      "Время",
        "history_material":  "Материал",
        "history_result":    "Результат",
        "history_user":      "Пользователь",
        "help_title":        "Помощь",
        "hist_title":        "Гистограмма пористости",
        "hist_placeholder":  "Гистограмма появится после анализа",
        "profiles_title":    "Профили настроек",
        "profile_save":      "Сохранить профиль",
        "profile_load":      "Загрузить",
        "profile_delete":    "Удалить",
        "profile_name_ask":  "Введите название профиля:",
        "profile_saved":     "Профиль '{name}' сохранён",
        "profile_loaded":    "Профиль '{name}' загружен",
        "profile_deleted":   "Профиль удалён",
        "profile_err_empty": "Выберите профиль из списка!",
        "profile_err_name":  "Введите название профиля!",
    },
    "en": {
        "window_title":      "DSS — Porous Material Quality",
        "menu_data":         "Source data",
        "menu_open":         "Open",
        "menu_webcam":       "Webcam",
        "menu_language":     "Language",
        "menu_russian":      "Russian",
        "menu_english":      "English",
        "menu_help":         "Help",
        "btn_snapshot":      "Snapshot",
        "btn_edit_db":       "Edit DB",
        "btn_save_report":   "Save report",
        "lbl_contrast":      "Contrast",
        "lbl_brightness":    "Brightness",
        "lbl_sharpness":     "Sharpness",
        "lbl_pore_area":     "Pore area",
        "lbl_report_title":  "Report:",
        "lbl_porosity_eq":   "Porosity =",
        "lbl_porosity_word": "Porosity",
        "lbl_pores_exceed":  "Pores exceeding\nthe norm by area:",
        "status_ok":         "within norm",
        "status_bad":        "exceeds norm",
        "status_ok_short":   "Pass",
        "status_bad_short":  "Fail",
        "source_file":       "📁 Source: file",
        "source_cam":        "📷 Source: webcam",
        "source_none":       "⚠ No source selected",
        "msg_no_image":      "Please open an image via 'Source data' menu first!",
        "msg_no_data":       "No data to save. Run the analysis first!",
        "msg_result_title":  "Analysis result",
        "msg_result_body":   "Pores found: {count}\nPorosity: {por:.8f}\nExceeding norm: {bad}",
        "msg_saved":         "Saved",
        "msg_saved_body":    "Report saved to {fname}",
        "dlg_open_title":    "Open image",
        "dlg_save_title":    "Save report",
        "err_title":         "Error",
        "db_title":          "Materials database",
        "db_add_group":      "Add record",
        "db_del_group":      "Delete record",
        "db_btn_add":        "Add",
        "db_btn_delete":     "Delete",
        "db_btn_ok":         "OK",
        "db_ph_name":        "material name",
        "db_ph_area":        "pore area",
        "db_ph_area_dev":    "area deviation",
        "db_ph_porosity":    "porosity",
        "db_ph_por_dev":     "porosity deviation",
        "db_ph_delete_id":   "record number",
        "db_msg_added":      "Material '{name}' added",
        "db_msg_deleted":    "Record {id} deleted",
        "db_confirm_del":    "Delete record #{id}?\nMaterial: {name}",
        "db_confirm_title":  "Confirm deletion",
        "db_err_no_name":    "Please enter material name!",
        "db_err_no_id":      "Please enter record number!",
        "db_filter_lbl":     "Filter by name:",
        "db_filter_area":    "Pore area from:",
        "db_filter_to":      "to:",
        "db_filter_btn":     "Apply",
        "db_filter_reset":   "Reset",
        "history_title":     "Analysis history",
        "history_num":       "#",
        "history_date":      "Date",
        "history_time":      "Time",
        "history_material":  "Material",
        "history_result":    "Result",
        "history_user":      "User",
        "help_title":        "Help",
        "hist_title":        "Porosity histogram",
        "hist_placeholder":  "Histogram will appear after analysis",
        "profiles_title":    "Settings profiles",
        "profile_save":      "Save profile",
        "profile_load":      "Load",
        "profile_delete":    "Delete",
        "profile_name_ask":  "Enter profile name:",
        "profile_saved":     "Profile '{name}' saved",
        "profile_loaded":    "Profile '{name}' loaded",
        "profile_deleted":   "Profile deleted",
        "profile_err_empty": "Please select a profile!",
        "profile_err_name":  "Please enter profile name!",
    }
}

current_lang = "ru"
PROFILES_FILE = "profiles.json"

def tr(key):
    return TRANSLATIONS[current_lang].get(key, key)


# ── Задание 8: Помощь ─────────────────────────────────────────────────
class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("help_title"))
        self.setMinimumSize(520, 440)
        layout = QtWidgets.QVBoxLayout(self)
        text = QtWidgets.QTextEdit()
        text.setReadOnly(True)
        text.setHtml("""
<h2>СППР — Определение качества поверхности пористого материала</h2>
<h3>Главное окно</h3>
<ul>
<li><b>Меню «Исходные данные» → Открыть</b> — загрузить фото материала.</li>
<li><b>Слайдеры</b> (Контрастность, Яркость, Резкость) — настройка изображения.</li>
<li><b>Кнопка «Снимок»</b> — запустить анализ пористости.</li>
<li><b>«История анализов»</b> — прокрутить вниз.</li>
<li><b>«Гистограмма пористости»</b> — прокрутить вниз.</li>
<li><b>«Профили настроек»</b> — прокрутить вниз.</li>
<li><b>«Участки поверхности»</b> — кнопки + Участок / - Удалить.</li>
</ul>
<h3>Задание 10: Компактный режим 1366x768</h3>
<p>Запуск: <b>python main.py --compact</b><br>
Три вкладки вместо трёх отдельных окон.<br>
Ползунки в верхней панели.<br>
История/гистограмма/профили в нижних вкладках.</p>
<h3>Задание 11: Несколько участков</h3>
<p>Прокрутите вниз до панели «Участки поверхности».
Кнопка «+ Участок» добавляет вкладку с отдельным изображением.</p>
<h3>Задание 12: Параметры отчёта</h3>
<p>Нажмите «Сохранить в отчёт». Откроется диалог с группами параметров.</p>
""")
        layout.addWidget(text)
        btn = QtWidgets.QPushButton("OK")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)


# ── Задание 12: Диалог параметров отчёта ─────────────────────────────
class ReportSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Параметры отчёта")
        self.setFixedSize(420, 490)
        lay = QtWidgets.QVBoxLayout(self)
        lay.setSpacing(6)

        lay.addWidget(QtWidgets.QLabel("Выберите поля для включения в отчёт:"))

        # Группа 1
        g1 = QtWidgets.QGroupBox("Общая информация")
        g1l = QtWidgets.QVBoxLayout(g1)
        self.chk_time    = QtWidgets.QCheckBox("Дата и время анализа")
        self.chk_time.setChecked(True)
        self.chk_image   = QtWidgets.QCheckBox("Имя файла изображения")
        self.chk_image.setChecked(True)
        self.chk_sliders = QtWidgets.QCheckBox("Настройки обработки (К/Я/Р)")
        self.chk_sliders.setChecked(False)
        for w in [self.chk_time, self.chk_image, self.chk_sliders]:
            g1l.addWidget(w)
        lay.addWidget(g1)

        # Группа 2
        g2 = QtWidgets.QGroupBox("Результаты анализа")
        g2l = QtWidgets.QVBoxLayout(g2)
        self.chk_por    = QtWidgets.QCheckBox("Вычисленная пористость")
        self.chk_por.setChecked(True)
        self.chk_status = QtWidgets.QCheckBox("Статус (Годен / Не годен)")
        self.chk_status.setChecked(True)
        self.chk_count  = QtWidgets.QCheckBox("Количество пор сверх нормы")
        self.chk_count.setChecked(True)
        for w in [self.chk_por, self.chk_status, self.chk_count]:
            g2l.addWidget(w)
        lay.addWidget(g2)

        # Группа 3
        g3 = QtWidgets.QGroupBox("Комментарий оператора")
        g3l = QtWidgets.QVBoxLayout(g3)
        self.chk_comment  = QtWidgets.QCheckBox("Включить комментарий в отчёт")
        self.chk_comment.setChecked(False)
        self.edit_comment = QtWidgets.QPlainTextEdit()
        self.edit_comment.setPlaceholderText("Введите комментарий оператора...")
        self.edit_comment.setMaximumHeight(55)
        self.edit_comment.setEnabled(False)
        self.chk_comment.toggled.connect(self.edit_comment.setEnabled)
        g3l.addWidget(self.chk_comment)
        g3l.addWidget(self.edit_comment)
        lay.addWidget(g3)

        # Группа 4
        g4 = QtWidgets.QGroupBox("Подпись")
        g4l = QtWidgets.QHBoxLayout(g4)
        self.chk_user  = QtWidgets.QCheckBox("Включить имя оператора")
        self.chk_user.setChecked(True)
        self.edit_user = QtWidgets.QLineEdit()
        self.edit_user.setText("Оператор")
        g4l.addWidget(self.chk_user)
        g4l.addWidget(self.edit_user)
        lay.addWidget(g4)

        # Кнопки выбрать всё / снять всё
        brow = QtWidgets.QHBoxLayout()
        ba = QtWidgets.QPushButton("Выбрать всё")
        bn = QtWidgets.QPushButton("Снять всё")
        ba.clicked.connect(self._check_all)
        bn.clicked.connect(self._uncheck_all)
        brow.addWidget(ba); brow.addWidget(bn); brow.addStretch()
        lay.addLayout(brow)

        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.button(QtWidgets.QDialogButtonBox.Ok).setText("Сформировать отчёт")
        btns.button(QtWidgets.QDialogButtonBox.Cancel).setText("Отмена")
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _all_chk(self):
        return [self.chk_time, self.chk_image, self.chk_sliders,
                self.chk_por, self.chk_status, self.chk_count,
                self.chk_comment, self.chk_user]

    def _check_all(self):
        for c in self._all_chk(): c.setChecked(True)

    def _uncheck_all(self):
        for c in self._all_chk(): c.setChecked(False)

    def get_settings(self):
        return {
            "time":         self.chk_time.isChecked(),
            "image":        self.chk_image.isChecked(),
            "sliders":      self.chk_sliders.isChecked(),
            "por":          self.chk_por.isChecked(),
            "status":       self.chk_status.isChecked(),
            "count":        self.chk_count.isChecked(),
            "comment":      self.chk_comment.isChecked(),
            "comment_text": self.edit_comment.toPlainText().strip(),
            "user":         self.chk_user.isChecked(),
            "username":     self.edit_user.text().strip() or "Оператор",
        }


# ── База данных (задания 3, 6, 9) ─────────────────────────────────────
class MaterialsDialog(DbWindow):
    _data = [
        [0, "Материал2", 12.0, 5.0, 0.1,  0.01],
        [1, "Материал3",  9.0, 8.0, 0.15, 0.01],
        [2, "Материал1",  6.0, 4.0, 0.2,  0.02],
    ]

    def __init__(self):
        super().__init__()
        self.form = DbForm()
        self.form.setupUi(self)
        self._filtered_data = list(self._data)
        self._build_filter_panel()
        if hasattr(self.form, 'tableMaterials'):
            self.form.tableMaterials.horizontalHeader().sectionClicked.connect(self._sort_by_column)
            self.form.tableMaterials.horizontalHeader().setSortIndicatorShown(True)
        self._sort_col = -1
        self._sort_asc = True
        self._fill_table(self._data)
        self._apply_language()
        if hasattr(self.form, 'btnDelete'):   self.form.btnDelete.clicked.connect(self.delete_row)
        if hasattr(self.form, 'btnAdd'):      self.form.btnAdd.clicked.connect(self.add_row)
        if hasattr(self.form, 'btnDelete_2'): self.form.btnDelete_2.clicked.connect(self.accept)

    def _build_filter_panel(self):
        if not hasattr(self.form, 'tableMaterials'): return
        parent = self.form.tableMaterials.parent()
        self.filter_widget = QtWidgets.QWidget(parent)
        self.filter_widget.setGeometry(0, 0, 1031, 36)
        fl = QtWidgets.QHBoxLayout(self.filter_widget)
        fl.setContentsMargins(4, 2, 4, 2)
        self.lbl_filter     = QtWidgets.QLabel(tr("db_filter_lbl"))
        self.edit_filter    = QtWidgets.QLineEdit(); self.edit_filter.setFixedWidth(160)
        self.lbl_area_from  = QtWidgets.QLabel(tr("db_filter_area"))
        self.edit_area_from = QtWidgets.QLineEdit(); self.edit_area_from.setFixedWidth(60)
        self.lbl_area_to    = QtWidgets.QLabel(tr("db_filter_to"))
        self.edit_area_to   = QtWidgets.QLineEdit(); self.edit_area_to.setFixedWidth(60)
        self.btn_filter     = QtWidgets.QPushButton(tr("db_filter_btn"))
        self.btn_reset      = QtWidgets.QPushButton(tr("db_filter_reset"))
        for w in [self.lbl_filter, self.edit_filter, self.lbl_area_from,
                  self.edit_area_from, self.lbl_area_to, self.edit_area_to,
                  self.btn_filter, self.btn_reset]:
            fl.addWidget(w)
        fl.addStretch()
        self.btn_filter.clicked.connect(self._apply_filter)
        self.btn_reset.clicked.connect(self._reset_filter)
        tbl = self.form.tableMaterials
        tbl.setGeometry(tbl.x(), tbl.y() + 36, tbl.width(), tbl.height() - 36)
        self.filter_widget.show()

    def _apply_filter(self):
        nf = self.edit_filter.text().strip().lower()
        try:
            af = float(self.edit_area_from.text()) if self.edit_area_from.text() else None
            at = float(self.edit_area_to.text())   if self.edit_area_to.text()   else None
        except ValueError:
            af = at = None
        result = [r for r in self._data
                  if (not nf or nf in str(r[1]).lower())
                  and (af is None or float(r[2]) >= af)
                  and (at is None or float(r[2]) <= at)]
        self._filtered_data = result
        self._fill_table(result)

    def _reset_filter(self):
        self.edit_filter.clear(); self.edit_area_from.clear(); self.edit_area_to.clear()
        self._filtered_data = list(self._data)
        self._fill_table(self._data)

    def _sort_by_column(self, col):
        self._sort_asc = not self._sort_asc if self._sort_col == col else True
        self._sort_col = col
        try:
            self._filtered_data.sort(
                key=lambda r: (float(r[col]) if isinstance(r[col], (int, float)) else str(r[col]).lower()),
                reverse=not self._sort_asc)
        except Exception:
            self._filtered_data.sort(key=lambda r: str(r[col]).lower(), reverse=not self._sort_asc)
        order = QtCore.Qt.AscendingOrder if self._sort_asc else QtCore.Qt.DescendingOrder
        self.form.tableMaterials.horizontalHeader().setSortIndicator(col, order)
        self._fill_table(self._filtered_data)

    def _fill_table(self, data):
        if not hasattr(self.form, 'tableMaterials'): return
        tbl = self.form.tableMaterials
        tbl.setRowCount(len(data))
        for r, row in enumerate(data):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                tbl.setItem(r, c, item)

    def _apply_language(self):
        self.setWindowTitle(tr("db_title"))
        if hasattr(self.form, 'groupBox'):    self.form.groupBox.setTitle(tr("db_add_group"))
        if hasattr(self.form, 'groupBox_2'):  self.form.groupBox_2.setTitle(tr("db_del_group"))
        if hasattr(self.form, 'btnAdd'):      self.form.btnAdd.setText(tr("db_btn_add"))
        if hasattr(self.form, 'btnDelete'):   self.form.btnDelete.setText(tr("db_btn_delete"))
        if hasattr(self.form, 'btnDelete_2'): self.form.btnDelete_2.setText(tr("db_btn_ok"))
        for attr, key in [('editName','db_ph_name'), ('editArea','db_ph_area'),
                          ('editAreaDev','db_ph_area_dev'), ('editPorosity','db_ph_porosity'),
                          ('editPorosityDev','db_ph_por_dev'), ('editDeleteId','db_ph_delete_id')]:
            if hasattr(self.form, attr): getattr(self.form, attr).setPlaceholderText(tr(key))
        if hasattr(self, 'lbl_filter'):
            self.lbl_filter.setText(tr("db_filter_lbl"))
            self.lbl_area_from.setText(tr("db_filter_area"))
            self.lbl_area_to.setText(tr("db_filter_to"))
            self.btn_filter.setText(tr("db_filter_btn"))
            self.btn_reset.setText(tr("db_filter_reset"))

    def delete_row(self):
        idx_text = self.form.editDeleteId.text().strip()
        if not idx_text:
            QMessageBox.warning(self, tr("err_title"), tr("db_err_no_id")); return
        try:
            idx = int(idx_text) - 1
        except ValueError:
            QMessageBox.warning(self, tr("err_title"), tr("db_err_no_id")); return
        if 0 <= idx < len(self._filtered_data):
            row = self._filtered_data[idx]
            if QMessageBox.question(self, tr("db_confirm_title"),
                    tr("db_confirm_del").format(id=idx_text, name=row[1]),
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
                self._data = [r for r in self._data if r[0] != row[0]]
                self._filtered_data.pop(idx)
                self._fill_table(self._filtered_data)
                QMessageBox.information(self, tr("db_title"), tr("db_msg_deleted").format(id=idx_text))
                self.form.editDeleteId.clear()
        else:
            QMessageBox.warning(self, tr("err_title"), "Запись не найдена!")

    def add_row(self):
        name = self.form.editName.text().strip()
        if not name:
            QMessageBox.warning(self, tr("err_title"), tr("db_err_no_name")); return
        area = self.form.editArea.text().strip()
        adev = self.form.editAreaDev.text().strip()
        por  = self.form.editPorosity.text().strip()
        pdev = self.form.editPorosityDev.text().strip()
        new_id = max((r[0] for r in self._data), default=-1) + 1
        new_row = [new_id, name,
                   float(area) if area else 0.0, float(adev) if adev else 0.0,
                   float(por)  if por  else 0.0, float(pdev) if pdev else 0.0]
        self._data.append(new_row)
        self._filtered_data.append(new_row)
        self._fill_table(self._filtered_data)
        QMessageBox.information(self, tr("db_title"), tr("db_msg_added").format(name=name))
        for attr in ['editName','editArea','editAreaDev','editPorosity','editPorosityDev']:
            if hasattr(self.form, attr): getattr(self.form, attr).clear()


# ── ГЛАВНОЕ ОКНО ──────────────────────────────────────────────────────
class App(MainWindow):
    def __init__(self):
        super().__init__()
        self.form = MainForm()
        self.form.setupUi(self)
        self.image_path       = None
        self.cv_image         = None
        self.last_result      = {}
        self._current_username = "Пользователь"
        self._profiles_data   = {}

        self._setup_sliders()
        self._setup_scroll()

        self.form.actionOpen.triggered.connect(self.load_image)
        self.form.actionWebcam.triggered.connect(self.use_webcam)
        self.form.actionRussian.triggered.connect(lambda: self.set_language("ru"))
        self.form.actionEnglish.triggered.connect(lambda: self.set_language("en"))

        help_action = QtWidgets.QAction(tr("menu_help"), self)
        help_action.triggered.connect(self.show_help)
        self.menuBar().addAction(help_action)
        self.help_action_ref = help_action

        if hasattr(self.form, 'btnEditDb'):    self.form.btnEditDb.clicked.connect(self.open_db)
        if hasattr(self.form, 'btnSnapshot'):  self.form.btnSnapshot.clicked.connect(self.run_analysis)
        if hasattr(self.form, 'btnSaveReport'):self.form.btnSaveReport.clicked.connect(self.save_report)

        self._build_source_indicator()
        self._build_history_panel()
        self._build_histogram_area()
        self._build_profiles_panel()
        self._build_sections_panel()   # Задание 11
        self._update_container_height()
        self._apply_language()

    def _setup_sliders(self):
        for attr in ['sliderContrast','sliderBrightness','sliderSharpness']:
            if hasattr(self.form, attr):
                getattr(self.form, attr).setRange(1, 30)
                getattr(self.form, attr).setValue(10)

    def _get_slider_values(self):
        c = self.form.sliderContrast.value()   if hasattr(self.form,'sliderContrast')   else 10
        b = self.form.sliderBrightness.value() if hasattr(self.form,'sliderBrightness') else 10
        s = self.form.sliderSharpness.value()  if hasattr(self.form,'sliderSharpness')  else 10
        return c, b, s

    def _set_slider_values(self, c, b, s):
        if hasattr(self.form,'sliderContrast'):   self.form.sliderContrast.setValue(c)
        if hasattr(self.form,'sliderBrightness'): self.form.sliderBrightness.setValue(b)
        if hasattr(self.form,'sliderSharpness'):  self.form.sliderSharpness.setValue(s)

    def _setup_scroll(self):
        orig = self.centralWidget()
        self._sc = QtWidgets.QWidget()
        self._sc.setMinimumWidth(1066)
        orig.setParent(self._sc); orig.move(0, 0)
        scroll = QScrollArea()
        scroll.setWidget(self._sc)
        scroll.setWidgetResizable(False)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setCentralWidget(scroll)

    def _update_container_height(self):
        needed = 750
        for attr in ('source_label','history_group','hist_group',
                     'profiles_group','sections_group'):
            if hasattr(self, attr):
                w = getattr(self, attr)
                needed = max(needed, w.y() + w.height() + 10)
        self._sc.setFixedSize(1066, needed)

    # ── Задание 7: индикатор источника ───────────────────────────────
    def _build_source_indicator(self):
        self.source_label = QtWidgets.QLabel(tr("source_none"), self._sc)
        self.source_label.setStyleSheet(
            "background:#fff3cd;color:#856404;border:1px solid #ffc107;"
            "border-radius:4px;padding:2px 8px;font-size:12px;")
        self.source_label.setGeometry(10, 745, 420, 26)
        self.source_label.show()

    def _set_source(self, mode):
        d = {"file":("background:#d4edda;color:#155724;border:1px solid #28a745;", tr("source_file")),
             "cam": ("background:#cce5ff;color:#004085;border:1px solid #007bff;", tr("source_cam")),
             "none":("background:#fff3cd;color:#856404;border:1px solid #ffc107;", tr("source_none"))}
        style, text = d.get(mode, d["none"])
        self.source_label.setStyleSheet(style + "border-radius:4px;padding:2px 8px;font-size:12px;")
        self.source_label.setText(text)

    # ── Задание 2: история ────────────────────────────────────────────
    def _build_history_panel(self):
        self.history_group = QtWidgets.QGroupBox(tr("history_title"), self._sc)
        self.history_group.setGeometry(10, 785, 1046, 170)
        layout = QtWidgets.QVBoxLayout(self.history_group)
        self.history_table = QTableWidget(0, 6)
        self.history_table.setHorizontalHeaderLabels([
            tr("history_num"), tr("history_date"), tr("history_time"),
            tr("history_material"), tr("history_result"), tr("history_user")])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.verticalHeader().setVisible(False)
        layout.addWidget(self.history_table)
        self.history_group.show()

    def _add_history_entry(self, material, is_ok):
        rn = self.history_table.rowCount() + 1
        self.history_table.insertRow(rn - 1)
        text  = tr("status_ok_short") if is_ok else tr("status_bad_short")
        color = QtGui.QColor("#28a745") if is_ok else QtGui.QColor("#dc3545")
        now   = datetime.now()
        for col, val in enumerate([str(rn), now.strftime("%d.%m.%Y"), now.strftime("%H:%M:%S"),
                                    material, text, self._current_username]):
            item = QTableWidgetItem(val)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            if col == 4: item.setForeground(color)
            self.history_table.setItem(rn - 1, col, item)
        self.history_table.scrollToBottom()

    # ── Задание 4: гистограмма ────────────────────────────────────────
    def _build_histogram_area(self):
        self.hist_group = QtWidgets.QGroupBox(tr("hist_title"), self._sc)
        self.hist_group.setGeometry(10, 965, 1046, 220)
        layout = QtWidgets.QVBoxLayout(self.hist_group)
        self.hist_label = QtWidgets.QLabel(tr("hist_placeholder"))
        self.hist_label.setMinimumHeight(180)
        self.hist_label.setAlignment(QtCore.Qt.AlignCenter)
        self.hist_label.setStyleSheet("background:white;border:1px solid #ccc;")
        layout.addWidget(self.hist_label)
        self.hist_group.show()

    def _draw_histogram(self, contours):
        areas = [cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 50]
        if not areas: self.hist_label.setText("Нет данных"); return
        W, H = max(self.hist_label.width(), 1020), max(self.hist_label.height(), 180)
        px = QtGui.QPixmap(W, H); px.fill(QtGui.QColor("white"))
        p  = QtGui.QPainter(px)
        mn, mx = min(areas), max(areas)
        if mn == mx: p.end(); return
        bins=10; step=(mx-mn)/bins; counts=[0]*bins
        for a in areas: counts[min(int((a-mn)/step), bins-1)] += 1
        mc=max(counts) or 1; ml,mb,mt=50,35,15; dw=W-ml-10; dh=H-mb-mt; bw=dw//bins
        p.setPen(QtGui.QPen(QtGui.QColor("#333"),2))
        p.drawLine(ml,mt,ml,H-mb); p.drawLine(ml,H-mb,W-10,H-mb)
        p.setFont(QtGui.QFont("Arial",8))
        p.setPen(QtGui.QPen(QtGui.QColor("#555"),1))
        p.drawText(2,mt+10,str(mc)); p.drawText(2,H-mb,"0")
        for i,cnt in enumerate(counts):
            bh=int((cnt/mc)*dh); x=ml+i*bw+2; y=H-mb-bh
            p.fillRect(x,y,bw-4,bh,QtGui.QColor("#4e79a7") if i<bins//2 else QtGui.QColor("#e15759"))
            if cnt>0:
                p.setPen(QtGui.QPen(QtGui.QColor("#333"),1)); p.drawText(x,y-2,str(cnt))
            p.setPen(QtGui.QPen(QtGui.QColor("#555"),1)); p.drawText(x,H-mb+14,f"{int(mn+i*step)}")
        p.end(); self.hist_label.setPixmap(px)

    # ── Задание 5: профили ────────────────────────────────────────────
    def _build_profiles_panel(self):
        self.profiles_group = QtWidgets.QGroupBox(tr("profiles_title"), self._sc)
        self.profiles_group.setGeometry(10, 1195, 1046, 58)
        row = QtWidgets.QHBoxLayout(self.profiles_group)
        row.setContentsMargins(10, 4, 10, 4)
        self.profiles_combo = QtWidgets.QComboBox()
        self.profiles_combo.setMinimumWidth(280)
        self.btn_ps = QtWidgets.QPushButton(tr("profile_save")); self.btn_ps.setFixedWidth(150)
        self.btn_pl = QtWidgets.QPushButton(tr("profile_load")); self.btn_pl.setFixedWidth(100)
        self.btn_pd = QtWidgets.QPushButton(tr("profile_delete")); self.btn_pd.setFixedWidth(100)
        for w in [self.profiles_combo, self.btn_ps, self.btn_pl, self.btn_pd]:
            row.addWidget(w)
        row.addStretch()
        self.btn_ps.clicked.connect(self._save_profile)
        self.btn_pl.clicked.connect(self._load_profile)
        self.btn_pd.clicked.connect(self._delete_profile)
        self.profiles_group.show()
        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE,"r",encoding="utf-8") as f:
                    self._profiles_data = json.load(f)
            except Exception: pass
        self._refresh_profiles_combo()

    def _refresh_profiles_combo(self):
        self.profiles_combo.clear()
        for name, v in self._profiles_data.items():
            self.profiles_combo.addItem(
                f"{name}  [К:{v.get('c',10)} Я:{v.get('b',10)} Р:{v.get('s',10)}]", userData=name)

    def _save_profiles_to_file(self):
        try:
            with open(PROFILES_FILE,"w",encoding="utf-8") as f:
                json.dump(self._profiles_data,f,ensure_ascii=False,indent=2)
        except Exception: pass

    def _save_profile(self):
        name, ok = QInputDialog.getText(self, tr("profiles_title"), tr("profile_name_ask"))
        if not ok or not name.strip():
            QMessageBox.warning(self, tr("err_title"), tr("profile_err_name")); return
        c,b,s = self._get_slider_values()
        self._profiles_data[name.strip()] = {"c":c,"b":b,"s":s}
        self._save_profiles_to_file(); self._refresh_profiles_combo()
        for i in range(self.profiles_combo.count()):
            if self.profiles_combo.itemData(i) == name.strip():
                self.profiles_combo.setCurrentIndex(i); break
        QMessageBox.information(self, tr("profiles_title"), tr("profile_saved").format(name=name.strip()))

    def _load_profile(self):
        idx = self.profiles_combo.currentIndex()
        if idx < 0 or not self.profiles_combo.count():
            QMessageBox.warning(self, tr("err_title"), tr("profile_err_empty")); return
        v = self._profiles_data.get(self.profiles_combo.itemData(idx), {})
        self._set_slider_values(v.get("c",10), v.get("b",10), v.get("s",10))
        QMessageBox.information(self, tr("profiles_title"),
            tr("profile_loaded").format(name=self.profiles_combo.itemData(idx)))

    def _delete_profile(self):
        idx = self.profiles_combo.currentIndex()
        if idx < 0 or not self.profiles_combo.count():
            QMessageBox.warning(self, tr("err_title"), tr("profile_err_empty")); return
        name = self.profiles_combo.itemData(idx)
        if QMessageBox.question(self, tr("db_confirm_title"), f"Удалить профиль «{name}»?",
                QMessageBox.Yes|QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self._profiles_data.pop(name, None)
            self._save_profiles_to_file(); self._refresh_profiles_combo()
            QMessageBox.information(self, tr("profiles_title"), tr("profile_deleted"))

    # ── Задание 11: несколько участков поверхности ───────────────────
    def _build_sections_panel(self):
        """
        Панель «Участки поверхности» — QTabWidget с вкладками.
        Каждая вкладка = один участок со своей кнопкой загрузки.
        Кнопки «+ Участок» и «− Удалить» управляют вкладками.
        Загрузка в участок 1 автоматически обновляет основной интерфейс.
        """
        Y = 1263

        # Метка и кнопки управления вкладками
        lbl = QtWidgets.QLabel("Участки поверхности:", self._sc)
        lbl.setStyleSheet("font-weight:bold;font-size:12px;")
        lbl.setGeometry(10, Y, 200, 22)
        lbl.show()

        btn_add = QtWidgets.QPushButton("+ Участок", self._sc)
        btn_add.setGeometry(856, Y, 96, 24)
        btn_add.clicked.connect(self._add_section)
        btn_add.show()

        btn_del = QtWidgets.QPushButton("− Удалить", self._sc)
        btn_del.setGeometry(957, Y, 96, 24)
        btn_del.clicked.connect(self._remove_section)
        btn_del.show()

        # QTabWidget для вкладок участков
        self.sections_group = QtWidgets.QTabWidget(self._sc)
        self.sections_group.setGeometry(10, Y + 26, 1046, 50)
        self.sections_group.show()

        # данные участков
        self._sections_data = []
        self._add_section()   # первый участок по умолчанию

    def _add_section(self):
        idx = self.sections_group.count()
        tab = QtWidgets.QWidget()
        row = QtWidgets.QHBoxLayout(tab)
        row.setContentsMargins(6, 4, 6, 4); row.setSpacing(8)

        btn = QtWidgets.QPushButton(f"📂  Загрузить участок {idx + 1}")
        btn.setFixedWidth(230)
        lbl = QtWidgets.QLabel("файл не выбран")
        lbl.setStyleSheet("color:#888;font-size:11px;")

        row.addWidget(btn); row.addWidget(lbl); row.addStretch()

        data = {"path": None, "cv_image": None, "lbl": lbl}
        self._sections_data.append(data)
        btn.clicked.connect(lambda _checked, i=idx: self._load_section_image(i))

        self.sections_group.addTab(tab, f"Участок {idx + 1}")
        self.sections_group.setCurrentIndex(idx)

    def _remove_section(self):
        if self.sections_group.count() <= 1:
            QMessageBox.information(self, "Участки", "Минимум один участок должен остаться.")
            return
        last = self.sections_group.count() - 1
        self.sections_group.removeTab(last)
        self._sections_data.pop(last)

    def _load_section_image(self, idx):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, f"Загрузить участок {idx + 1}", '', 'Images (*.png *.jpg *.jpeg *.bmp)')
        if not fname: return
        cv_img = cv2.imread(fname)
        self._sections_data[idx]["path"]     = fname
        self._sections_data[idx]["cv_image"] = cv_img
        self._sections_data[idx]["lbl"].setText(f"✅ {os.path.basename(fname)}")
        self._sections_data[idx]["lbl"].setStyleSheet("color:#155724;font-size:11px;")
        # участок 1 → в основной интерфейс
        if idx == 0:
            self.image_path = fname
            self.cv_image   = cv_img
            pix = QtGui.QPixmap(fname)
            if hasattr(self.form, 'labelCurrentImage'):
                self.form.labelCurrentImage.setPixmap(
                    pix.scaled(361,341,QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation))
            self._set_source('file')

    # ── Задание 1: язык ───────────────────────────────────────────────
    def set_language(self, lang):
        global current_lang; current_lang = lang; self._apply_language()

    def _apply_language(self):
        self.setWindowTitle(tr("window_title"))
        self.form.menu.setTitle(tr("menu_data"))
        self.form.actionOpen.setText(tr("menu_open"))
        self.form.actionWebcam.setText(tr("menu_webcam"))
        self.form.menuLanguage.setTitle(tr("menu_language"))
        self.form.actionRussian.setText(tr("menu_russian"))
        self.form.actionEnglish.setText(tr("menu_english"))
        self.help_action_ref.setText(tr("menu_help"))
        for attr, key in [('btnSnapshot','btn_snapshot'),('btnEditDb','btn_edit_db'),
                          ('btnSaveReport','btn_save_report'),('label','lbl_contrast'),
                          ('label_2','lbl_brightness'),('label_3','lbl_sharpness'),
                          ('label_4','lbl_pore_area'),('lblPorosityDev_2','lbl_report_title'),
                          ('label_5','lbl_porosity_eq'),('label_6','lbl_porosity_word'),
                          ('label_7','lbl_porosity_word'),('label_8','lbl_pores_exceed')]:
            if hasattr(self.form, attr): getattr(self.form, attr).setText(tr(key))
        if hasattr(self.form,'lblPorosityStatus'):
            s = self.form.lblPorosityStatus.text()
            if s in ("в норме","within norm"):
                self.form.lblPorosityStatus.setText(tr("status_ok"))
            elif s in ("превышает норму","exceeds norm"):
                self.form.lblPorosityStatus.setText(tr("status_bad"))
        if hasattr(self,'source_label'):
            t = self.source_label.text()
            self._set_source('file' if ("файл" in t or "file" in t.lower())
                             else 'cam' if ("камера" in t or "cam" in t.lower()) else 'none')
        if hasattr(self,'history_group'):
            self.history_group.setTitle(tr("history_title"))
            self.history_table.setHorizontalHeaderLabels([
                tr("history_num"), tr("history_date"), tr("history_time"),
                tr("history_material"), tr("history_result"), tr("history_user")])
        if hasattr(self,'hist_group'):
            self.hist_group.setTitle(tr("hist_title"))
        if hasattr(self,'profiles_group'):
            self.profiles_group.setTitle(tr("profiles_title"))
            self.btn_ps.setText(tr("profile_save"))
            self.btn_pl.setText(tr("profile_load"))
            self.btn_pd.setText(tr("profile_delete"))

    def show_help(self): HelpDialog(self).exec_()
    def open_db(self): MaterialsDialog().exec_()

    def use_webcam(self):
        self._set_source('cam')
        QMessageBox.information(self,"Веб-камера","Функция будет добавлена в следующей ЛР.")

    def load_image(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, tr("dlg_open_title"), '', 'Images (*.png *.jpg *.jpeg *.bmp)')
        if not fname: return
        self.image_path = fname; self.cv_image = cv2.imread(fname)
        pix = QtGui.QPixmap(fname)
        if hasattr(self.form,'labelCurrentImage'):
            self.form.labelCurrentImage.setPixmap(
                pix.scaled(361,341,QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation))
        for lbl in ['labelAnalysisImage','labelPoresImage']:
            if hasattr(self.form,lbl): getattr(self.form,lbl).clear()
        if hasattr(self.form,'lblPorosityValue'):  self.form.lblPorosityValue.setText("—")
        if hasattr(self.form,'lblPoresCount'):     self.form.lblPoresCount.setText("—")
        if hasattr(self.form,'lblPorosityStatus'): self.form.lblPorosityStatus.setText("")
        self._set_source('file')
        # синхронизируем с участком 1
        if self._sections_data:
            self._sections_data[0]["path"]     = fname
            self._sections_data[0]["cv_image"] = cv2.imread(fname)
            self._sections_data[0]["lbl"].setText(f"✅ {os.path.basename(fname)}")
            self._sections_data[0]["lbl"].setStyleSheet("color:#155724;font-size:11px;")

    def run_analysis(self):
        if self.cv_image is None:
            QMessageBox.warning(self, tr("err_title"), tr("msg_no_image")); return
        img  = self.cv_image.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(cv2.GaussianBlur(gray,(5,5),0),80,255,cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        good, bad = [], []
        for cnt in contours:
            a = cv2.contourArea(cnt)
            if a > 50: (good if a<=500 else bad).append(cnt)
        cv2.drawContours(img,good,-1,(0,255,0),2)
        cv2.drawContours(img,bad,-1,(0,0,255),2)
        total    = img.shape[0]*img.shape[1]
        porosity = sum(cv2.contourArea(c) for c in good+bad)/total
        count    = len(good)+len(bad)
        is_ok    = porosity <= 0.1
        h,w,ch   = img.shape
        rgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        qt  = QtGui.QImage(rgb.data,w,h,ch*w,QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(qt)
        if hasattr(self.form,'labelAnalysisImage'):
            self.form.labelAnalysisImage.setPixmap(
                pix.scaled(351,341,QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation))
        img2 = self.cv_image.copy(); cv2.drawContours(img2,bad,-1,(0,0,255),2)
        rgb2 = cv2.cvtColor(img2,cv2.COLOR_BGR2RGB)
        qt2  = QtGui.QImage(rgb2.data,w,h,ch*w,QtGui.QImage.Format_RGB888)
        if hasattr(self.form,'labelPoresImage'):
            self.form.labelPoresImage.setPixmap(
                QtGui.QPixmap.fromImage(qt2).scaled(361,371,QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation))
        if hasattr(self.form,'lblPoresCount'):    self.form.lblPoresCount.setText(str(count))
        if hasattr(self.form,'lblPorosityValue'): self.form.lblPorosityValue.setText(f"{porosity:.8f}")
        status = tr("status_ok") if is_ok else tr("status_bad")
        if hasattr(self.form,'lblPorosityStatus'):
            self.form.lblPorosityStatus.setText(status)
            self.form.lblPorosityStatus.setStyleSheet(f"color:{'green' if is_ok else 'red'};")
        self._draw_histogram(good+bad)
        mat = self.form.comboMaterial.currentText() if hasattr(self.form,'comboMaterial') else "—"
        self._add_history_entry(mat, is_ok)
        self.last_result = {"porosity":f"{porosity:.8f}","count":str(count),
                            "status":status,"time":datetime.now().strftime("%d.%m.%Y %H:%M:%S")}
        QMessageBox.information(self,tr("msg_result_title"),
            tr("msg_result_body").format(count=count,por=porosity,bad=len(bad)))

    def save_report(self):
        if self.cv_image is None:
            QMessageBox.warning(self,tr("err_title"),tr("msg_no_data")); return
        dlg = ReportSettingsDialog(self)
        if dlg.exec_() != QDialog.Accepted: return
        cfg = dlg.get_settings()
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,tr("dlg_save_title"),"report.txt","Text Files (*.txt)")
        if not fname: return
        c,b,s = self._get_slider_values()
        sep = "="*52+"\n"
        with open(fname,"w",encoding="utf-8") as f:
            f.write(sep+"  ОТЧЁТ — СППР АНАЛИЗА ПОРИСТОГО МАТЕРИАЛА\n"+sep+"\n")
            if cfg["time"]:    f.write(f"Дата и время:..........{self.last_result.get('time','—')}\n")
            if cfg["image"] and self.image_path:
                               f.write(f"Файл изображения:......{self.image_path}\n")
            if cfg["sliders"]: f.write(f"К / Я / Р:.............{c} / {b} / {s}\n")
            if any([cfg["por"],cfg["status"],cfg["count"]]):
                               f.write("\n--- Результат анализа ---\n")
            if cfg["por"]:     f.write(f"Пористость:............{self.last_result.get('porosity','—')}\n")
            if cfg["status"]:  f.write(f"Статус:................{self.last_result.get('status','—')}\n")
            if cfg["count"]:   f.write(f"Пор сверх нормы:.......{self.last_result.get('count','—')}\n")
            if cfg["comment"] and cfg["comment_text"]:
                               f.write(f"\n--- Комментарий оператора ---\n{cfg['comment_text']}\n")
            if cfg["user"]:    f.write(f"\nОператор: {cfg['username']}\n")
            f.write("\n"+sep)
        QMessageBox.information(self,tr("msg_saved"),tr("msg_saved_body").format(fname=fname))


# ── Задание 10: Компактный интерфейс 1366x768 ────────────────────────
class App1366(MainWindow):
    """
    Компактный вариант интерфейса для экранов 1366x768.
    Изменения по сравнению с основным App:
      - Окно фиксировано 1360x740, без прокрутки
      - Три изображения размещены во вкладках (QTabWidget)
        вместо трёх отдельных окон — экономит высоту экрана
      - Ползунки вынесены в горизонтальную панель вверху
      - История / гистограмма / профили в нижних вкладках
      - Кнопка скрыть/показать правую панель
    """
    def __init__(self):
        super().__init__()
        self.form = MainForm()
        self.form.setupUi(self)
        self.image_path     = None
        self.cv_image       = None
        self.last_result    = {}
        self._profiles_data = {}
        self._right_shown   = True

        self.setWindowTitle("СППР — Качество пористого материала  [1366x768]")
        self.setFixedSize(1360, 740)

        # скрываем все виджеты из .ui — строим интерфейс сами поверх
        cw = self.centralWidget()
        for child in cw.findChildren(QtWidgets.QWidget):
            child.hide()

        # ползунки — создаём новые, независимые от .ui
        self._sl_c = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._sl_b = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._sl_s = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        for sl in [self._sl_c, self._sl_b, self._sl_s]:
            sl.setRange(1, 30); sl.setValue(10)

        self._build(cw)

        # меню
        self.form.actionOpen.triggered.connect(self.load_image)
        self.form.actionWebcam.triggered.connect(self._webcam)
        help_act = QtWidgets.QAction("Помощь", self)
        help_act.triggered.connect(self._help)
        self.menuBar().addAction(help_act)

    def _sl_vals(self):
        return self._sl_c.value(), self._sl_b.value(), self._sl_s.value()

    def _sl_set(self, c, b, s):
        self._sl_c.setValue(c); self._sl_b.setValue(b); self._sl_s.setValue(s)

    def _build(self, cw):
        TOP  = 40
        IMGW = 876
        RIMX = IMGW + 4
        RIMW = 1360 - RIMX - 2
        IMGH = 388
        BOTY = TOP + IMGH + 4
        BOTH = 240

        # ── Верхняя панель ────────────────────────────────────────
        tp = QtWidgets.QWidget(cw)
        tp.setGeometry(0, 0, 1360, TOP)
        tp.setStyleSheet("background:#ececec;border-bottom:1px solid #ccc;")
        tl = QtWidgets.QHBoxLayout(tp)
        tl.setContentsMargins(6, 3, 6, 3); tl.setSpacing(4)

        for txt, slot, w in [("📂 Открыть", self.load_image, 108),
                               ("🔍 Снимок",  self.run_analysis, 100),
                               ("📄 Отчёт",   self.save_report, 88),
                               ("🗄 БД",      lambda: MaterialsDialog().exec_(), 68)]:
            b = QtWidgets.QPushButton(txt); b.setFixedWidth(w)
            b.clicked.connect(slot); tl.addWidget(b)

        sep = QtWidgets.QFrame(); sep.setFrameShape(QtWidgets.QFrame.VLine)
        sep.setStyleSheet("color:#bbb;"); tl.addWidget(sep)

        for lbl_txt, sl, lw in [("Контраст:", self._sl_c, 65),
                                  ("Яркость:",  self._sl_b, 55),
                                  ("Резкость:", self._sl_s, 60)]:
            lb = QtWidgets.QLabel(lbl_txt); lb.setFixedWidth(lw)
            sl.setParent(tp); sl.setFixedWidth(94); sl.show()
            tl.addWidget(lb); tl.addWidget(sl)

        self._src = QtWidgets.QLabel("⚠ Источник не выбран")
        self._src.setStyleSheet(
            "background:#fff3cd;color:#856404;border-radius:3px;padding:1px 6px;font-size:11px;")
        tl.addWidget(self._src); tl.addStretch()

        self._btn_tog = QtWidgets.QPushButton("◀ Скрыть панель")
        self._btn_tog.setFixedWidth(128)
        self._btn_tog.clicked.connect(self._toggle)
        tl.addWidget(self._btn_tog)
        tp.show()

        # ── Вкладки изображений ────────────────────────────────────
        self._itabs = QtWidgets.QTabWidget(cw)
        self._itabs.setGeometry(0, TOP+2, IMGW, IMGH)

        self._lbl_orig  = self._mk_lbl()
        self._lbl_proc  = self._mk_lbl()
        self._lbl_pores = self._mk_lbl()
        for lbl, title in [(self._lbl_orig,  "📷  Исходное"),
                           (self._lbl_proc,  "🔬  Анализ"),
                           (self._lbl_pores, "⚠  Поры (сверх нормы)")]:
            w = QtWidgets.QWidget()
            QtWidgets.QVBoxLayout(w).addWidget(lbl)
            self._itabs.addTab(w, title)
        self._itabs.show()
        self._imgw = IMGW; self._imgh = IMGH; self._top = TOP

        # ── Правая панель ──────────────────────────────────────────
        self._right = QtWidgets.QWidget(cw)
        self._right.setGeometry(RIMX, TOP+2, RIMW, IMGH)
        self._right.setStyleSheet("background:#f8f8f8;border-left:1px solid #ddd;")
        rl = QtWidgets.QVBoxLayout(self._right)
        rl.setContentsMargins(8,6,8,6); rl.setSpacing(5)

        mr = QtWidgets.QHBoxLayout()
        mr.addWidget(QtWidgets.QLabel("Материал:"))
        self._mat = QtWidgets.QComboBox()
        self._mat.addItems(["Газоселикат","Материал2","Материал3"])
        mr.addWidget(self._mat); rl.addLayout(mr)

        gn = QtWidgets.QGroupBox("Нормы материала")
        gnl = QtWidgets.QFormLayout(gn); gnl.setSpacing(3); gnl.setContentsMargins(6,4,6,4)
        self._area = QtWidgets.QLabel("9.0");  self._adev = QtWidgets.QLabel("0.8")
        self._por  = QtWidgets.QLabel("0.09"); self._pdev = QtWidgets.QLabel("0.05")
        gnl.addRow("Площадь поры:", self._area); gnl.addRow("Откл.:", self._adev)
        gnl.addRow("Пористость:",   self._por);  gnl.addRow("Откл.:", self._pdev)
        rl.addWidget(gn)

        gr = QtWidgets.QGroupBox("Результат анализа")
        grl = QtWidgets.QFormLayout(gr); grl.setSpacing(3); grl.setContentsMargins(6,4,6,4)
        self._c_por  = QtWidgets.QLabel("—")
        self._c_stat = QtWidgets.QLabel("—")
        self._c_stat.setStyleSheet("font-weight:bold;font-size:13px;")
        self._c_cnt  = QtWidgets.QLabel("—")
        grl.addRow("Пористость =",     self._c_por)
        grl.addRow("Статус:",           self._c_stat)
        grl.addRow("Пор сверх нормы:", self._c_cnt)
        rl.addWidget(gr); rl.addStretch()
        self._right.show()

        # ── Нижние вкладки ─────────────────────────────────────────
        self._btabs = QtWidgets.QTabWidget(cw)
        self._btabs.setGeometry(0, BOTY, 1360, BOTH)

        # История
        ht = QtWidgets.QWidget(); htl = QtWidgets.QVBoxLayout(ht); htl.setContentsMargins(4,4,4,4)
        self._htbl = QTableWidget(0, 6)
        self._htbl.setHorizontalHeaderLabels(["№","Дата","Время","Материал","Результат","Пользователь"])
        self._htbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._htbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self._htbl.setAlternatingRowColors(True)
        self._htbl.verticalHeader().setVisible(False)
        htl.addWidget(self._htbl)
        self._btabs.addTab(ht, "📋  История анализов")

        # Гистограмма
        gt = QtWidgets.QWidget(); gtl = QtWidgets.QVBoxLayout(gt); gtl.setContentsMargins(4,4,4,4)
        self._glbl = QtWidgets.QLabel("Гистограмма появится после анализа")
        self._glbl.setAlignment(QtCore.Qt.AlignCenter)
        self._glbl.setStyleSheet("background:white;border:1px solid #ccc;")
        gtl.addWidget(self._glbl)
        self._btabs.addTab(gt, "📊  Гистограмма")

        # Профили
        pt = QtWidgets.QWidget(); ptl = QtWidgets.QHBoxLayout(pt)
        ptl.setContentsMargins(10,12,10,12); ptl.setSpacing(8)
        self._pcmb = QtWidgets.QComboBox(); self._pcmb.setMinimumWidth(250)
        bps = QtWidgets.QPushButton("💾 Сохранить профиль"); bps.setFixedWidth(160)
        bpl = QtWidgets.QPushButton("📂 Загрузить");         bpl.setFixedWidth(110)
        bpd = QtWidgets.QPushButton("🗑 Удалить");            bpd.setFixedWidth(100)
        bps.clicked.connect(self._psave); bpl.clicked.connect(self._pload)
        bpd.clicked.connect(self._pdel)
        for w in [self._pcmb, bps, bpl, bpd]: ptl.addWidget(w)
        ptl.addStretch()
        self._btabs.addTab(pt, "⚙  Профили настроек")
        self._btabs.show()

        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE,"r",encoding="utf-8") as f:
                    self._profiles_data = json.load(f)
            except Exception: pass
        self._pref()

    def _mk_lbl(self):
        l = QtWidgets.QLabel(); l.setAlignment(QtCore.Qt.AlignCenter)
        l.setStyleSheet("background:#1a1a1a;color:#555;font-size:12px;")
        l.setText("нет изображения"); return l

    def _toggle(self):
        self._right_shown = not self._right_shown
        if self._right_shown:
            self._right.show()
            self._itabs.setGeometry(0, self._top+2, self._imgw, self._imgh)
            self._btn_tog.setText("◀ Скрыть панель")
        else:
            self._right.hide()
            self._itabs.setGeometry(0, self._top+2, 1358, self._imgh)
            self._btn_tog.setText("▶ Показать панель")

    def _set_src(self, mode):
        d = {"file":("background:#d4edda;color:#155724;","📁 Источник: файл"),
             "cam": ("background:#cce5ff;color:#004085;","📷 Источник: камера"),
             "none":("background:#fff3cd;color:#856404;","⚠ Источник не выбран")}
        st, tx = d.get(mode, d["none"])
        self._src.setStyleSheet(st+"border-radius:3px;padding:1px 6px;font-size:11px;")
        self._src.setText(tx)

    def load_image(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,"Открыть изображение","","Images (*.png *.jpg *.jpeg *.bmp)")
        if not fname: return
        self.image_path = fname; self.cv_image = cv2.imread(fname)
        W = self._itabs.width()-10; H = self._imgh-30
        pix = QtGui.QPixmap(fname)
        self._lbl_orig.setPixmap(pix.scaled(W,H,QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation))
        self._lbl_orig.setStyleSheet("background:#111;")
        for l in [self._lbl_proc, self._lbl_pores]:
            l.setText("нет изображения"); l.setStyleSheet("background:#1a1a1a;color:#555;font-size:12px;")
        self._itabs.setCurrentIndex(0)
        self._c_por.setText("—"); self._c_stat.setText("—"); self._c_cnt.setText("—")
        self._c_stat.setStyleSheet("font-weight:bold;font-size:13px;")
        self._set_src("file")

    def _webcam(self):
        self._set_src("cam")
        QMessageBox.information(self,"Веб-камера","Функция будет добавлена в следующей ЛР.")

    def run_analysis(self):
        if self.cv_image is None:
            QMessageBox.warning(self,"Ошибка","Сначала откройте изображение!"); return
        img  = self.cv_image.copy()
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        _,thresh = cv2.threshold(cv2.GaussianBlur(gray,(5,5),0),80,255,cv2.THRESH_BINARY_INV)
        contours,_ = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        good,bad = [],[]
        for cnt in contours:
            a = cv2.contourArea(cnt)
            if a>50: (good if a<=500 else bad).append(cnt)

        W = self._itabs.width()-10; H = self._imgh-30

        def show(cv_img, lbl):
            rgb = cv2.cvtColor(cv_img,cv2.COLOR_BGR2RGB); h,w,ch = rgb.shape
            qt  = QtGui.QImage(rgb.data,w,h,ch*w,QtGui.QImage.Format_RGB888)
            lbl.setPixmap(QtGui.QPixmap.fromImage(qt).scaled(W,H,QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation))
            lbl.setStyleSheet("background:#111;")

        img2 = self.cv_image.copy()
        cv2.drawContours(img2,good,-1,(0,255,0),2); cv2.drawContours(img2,bad,-1,(0,0,255),2)
        show(img2, self._lbl_proc)
        img3 = self.cv_image.copy(); cv2.drawContours(img3,bad,-1,(0,0,255),2)
        show(img3, self._lbl_pores)
        self._itabs.setCurrentIndex(1)

        porosity = sum(cv2.contourArea(c) for c in good+bad)/(img.shape[0]*img.shape[1])
        count = len(good)+len(bad); is_ok = porosity<=0.1
        status = "Годен" if is_ok else "Не годен"
        self._c_por.setText(f"{porosity:.8f}"); self._c_cnt.setText(str(count))
        self._c_stat.setText(status)
        self._c_stat.setStyleSheet(f"font-weight:bold;font-size:13px;color:{'#155724' if is_ok else '#dc3545'};")

        now = datetime.now(); rn = self._htbl.rowCount()+1
        self._htbl.insertRow(rn-1)
        rc = QtGui.QColor("#28a745" if is_ok else "#dc3545")
        for col,val in enumerate([str(rn),now.strftime("%d.%m.%Y"),now.strftime("%H:%M:%S"),
                                   self._mat.currentText(),status,"Пользователь"]):
            item = QTableWidgetItem(val); item.setTextAlignment(QtCore.Qt.AlignCenter)
            if col==4: item.setForeground(rc)
            self._htbl.setItem(rn-1,col,item)
        self._htbl.scrollToBottom(); self._btabs.setCurrentIndex(0)
        self._draw_hist(good+bad)
        self.last_result = {"porosity":f"{porosity:.8f}","count":str(count),
                            "status":status,"time":now.strftime("%d.%m.%Y %H:%M:%S")}
        QMessageBox.information(self,"Результат",
            f"Пор: {count}\nПористость: {porosity:.8f}\nСверх нормы: {len(bad)}")

    def _draw_hist(self, contours):
        areas = [cv2.contourArea(c) for c in contours if cv2.contourArea(c)>50]
        if not areas: self._glbl.setText("Нет данных"); return
        W=1348; H=192
        px=QtGui.QPixmap(W,H); px.fill(QtGui.QColor("white"))
        p=QtGui.QPainter(px)
        mn,mx=min(areas),max(areas)
        if mn==mx: p.end(); return
        bins=10; step=(mx-mn)/bins; counts=[0]*bins
        for a in areas: counts[min(int((a-mn)/step),bins-1)]+=1
        mc=max(counts) or 1; ml,mb,mt=50,28,8; dw=W-ml-8; dh=H-mb-mt; bw=dw//bins
        p.setPen(QtGui.QPen(QtGui.QColor("#333"),2))
        p.drawLine(ml,mt,ml,H-mb); p.drawLine(ml,H-mb,W-8,H-mb)
        p.setFont(QtGui.QFont("Arial",8)); p.setPen(QtGui.QPen(QtGui.QColor("#555"),1))
        p.drawText(2,mt+10,str(mc)); p.drawText(2,H-mb,"0")
        for i,cnt in enumerate(counts):
            bh=int((cnt/mc)*dh); x=ml+i*bw+2; y=H-mb-bh
            p.fillRect(x,y,bw-4,bh,QtGui.QColor("#4e79a7") if i<5 else QtGui.QColor("#e15759"))
            if cnt>0:
                p.setPen(QtGui.QPen(QtGui.QColor("#333"),1)); p.drawText(x,y-2,str(cnt))
            p.setPen(QtGui.QPen(QtGui.QColor("#555"),1)); p.drawText(x,H-mb+12,f"{int(mn+i*step)}")
        p.end(); self._glbl.setPixmap(px); self._btabs.setCurrentIndex(1)

    def save_report(self):
        if self.cv_image is None:
            QMessageBox.warning(self,"Ошибка","Нет данных. Выполните анализ."); return
        dlg = ReportSettingsDialog(self)
        if dlg.exec_() != QDialog.Accepted: return
        cfg = dlg.get_settings()
        fname,_ = QtWidgets.QFileDialog.getSaveFileName(
            self,"Сохранить отчёт","report.txt","Text Files (*.txt)")
        if not fname: return
        c,b,s = self._sl_vals()
        sep="="*52+"\n"
        with open(fname,"w",encoding="utf-8") as f:
            f.write(sep+"  ОТЧЁТ — СППР\n"+sep+"\n")
            if cfg["time"]:    f.write(f"Дата и время:..........{self.last_result.get('time','—')}\n")
            if cfg["image"] and self.image_path: f.write(f"Файл:...................{self.image_path}\n")
            if cfg["sliders"]: f.write(f"К/Я/Р:.................{c}/{b}/{s}\n")
            if cfg["por"]:     f.write(f"Пористость:............{self.last_result.get('porosity','—')}\n")
            if cfg["status"]:  f.write(f"Статус:................{self.last_result.get('status','—')}\n")
            if cfg["count"]:   f.write(f"Пор сверх нормы:.......{self.last_result.get('count','—')}\n")
            if cfg["comment"] and cfg["comment_text"]: f.write(f"\n{cfg['comment_text']}\n")
            if cfg["user"]:    f.write(f"\nОператор: {cfg['username']}\n")
            f.write("\n"+sep)
        QMessageBox.information(self,"Сохранено",f"Отчёт сохранён в {fname}")

    def _help(self):
        dlg = QDialog(self); dlg.setWindowTitle("Помощь — 1366x768")
        dlg.setMinimumSize(440,300); lay = QtWidgets.QVBoxLayout(dlg)
        txt = QtWidgets.QTextEdit(); txt.setReadOnly(True)
        txt.setHtml("""<h3>Компактный режим 1366x768</h3>
<p>Запуск: <code>python main.py --compact</code></p>
<ul>
<li>Три вкладки изображений вместо трёх отдельных окон</li>
<li>Ползунки вынесены в верхнюю панель</li>
<li>Кнопка «◀ Скрыть панель» — прячет правую колонку</li>
<li>История / гистограмма / профили в нижних вкладках</li>
</ul>""")
        lay.addWidget(txt)
        b = QtWidgets.QPushButton("Закрыть"); b.clicked.connect(dlg.accept); lay.addWidget(b)
        dlg.exec_()

    def _pref(self):
        self._pcmb.clear()
        for name,v in self._profiles_data.items():
            self._pcmb.addItem(
                f"{name}  [К:{v.get('c',10)} Я:{v.get('b',10)} Р:{v.get('s',10)}]", userData=name)

    def _psave_data(self):
        try:
            with open(PROFILES_FILE,"w",encoding="utf-8") as f:
                json.dump(self._profiles_data,f,ensure_ascii=False,indent=2)
        except Exception: pass

    def _psave(self):
        name,ok = QInputDialog.getText(self,"Профили","Введите название:")
        if not ok or not name.strip(): return
        c,b,s = self._sl_vals()
        self._profiles_data[name.strip()] = {"c":c,"b":b,"s":s}
        self._psave_data(); self._pref()
        for i in range(self._pcmb.count()):
            if self._pcmb.itemData(i)==name.strip():
                self._pcmb.setCurrentIndex(i); break
        QMessageBox.information(self,"Профили",f"Профиль «{name.strip()}» сохранён")

    def _pload(self):
        idx=self._pcmb.currentIndex()
        if idx<0: QMessageBox.warning(self,"Профили","Выберите профиль!"); return
        v=self._profiles_data.get(self._pcmb.itemData(idx),{})
        self._sl_set(v.get("c",10),v.get("b",10),v.get("s",10))
        QMessageBox.information(self,"Профили",f"Профиль «{self._pcmb.itemData(idx)}» загружен")

    def _pdel(self):
        idx=self._pcmb.currentIndex()
        if idx<0: return
        name=self._pcmb.itemData(idx)
        if QMessageBox.question(self,"Удалить",f"Удалить профиль «{name}»?",
                QMessageBox.Yes|QMessageBox.No,QMessageBox.No)==QMessageBox.Yes:
            self._profiles_data.pop(name,None); self._psave_data(); self._pref()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = App1366() if '--compact' in sys.argv else App()
    window.show()
    sys.exit(app.exec_())