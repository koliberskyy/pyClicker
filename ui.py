import time

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QSlider, QLabel, \
    QFormLayout, QSpinBox, QLineEdit
from PyQt6.QtGui import QIcon, QShortcut, QKeySequence
from PyQt6 import QtCore
from PyQt6.QtCore import QDir, QSize, QObject
from pathlib import Path
import os
import pyautogui
import threading
from pynput import keyboard

CURRENT_DIRECTORY = Path(__file__).resolve().parent

# путь к папке с изображениями
path = 'items/'
# точность распознавания изображений
global_confidence = 0.3
# скорость (1 клик раз в global_click_rate ms)
global_click_rate = 1000
# количество кликов
global_click_count = 1

global_hotkey_hide_pref1 = 'ctrl'
global_hotkey_hide_pref2 = 'alt'
global_hotkey_show_pref1 = 'ctrl'
global_hotkey_show_pref2 = 'alt'
global_hotkey_hide = 'h'
global_hotkey_show = 'j'


def isGlobalsHKEmpty():
    if global_hotkey_hide_pref1 == '' and global_hotkey_hide_pref2 == '' and global_hotkey_show_pref1 == '' and global_hotkey_show_pref2 == '' and global_hotkey_hide == '' and global_hotkey_show == '':
        return True
    return False


class CreepButton(QPushButton):
    def __init__(self, creep_name, btn_size=QSize(300, 300)):
        super().__init__()
        self.setStyleSheet("QPushButton {border: 0px;}")
        self.__first_img = ""
        self.__second_img = ""
        self.__find_img = []
        self.setFixedSize(btn_size)
        self.__first_img = creep_name + "1.png"
        self.__second_img = creep_name + "2.png"
        self.setBackgroundImg(self.__first_img)

        self.find_images(creep_name)

        self.clicked.connect(self.onClicked)

    def setBackgroundImg(self, name):
        QDir.addSearchPath("icons", os.fspath(CURRENT_DIRECTORY / "icons"))
        icon = QIcon("icons:" + name)
        assert not icon.isNull()

        self.setIcon(icon)
        self.setIconSize(self.size())

    def find_images(self, creep_name):
        it = 1
        QDir.addSearchPath("items", os.fspath(CURRENT_DIRECTORY / "items"))
        while (True):
            icon = QIcon("items/" + creep_name + "_find" + str(it) + ".png")

            if icon.isNull():
                break

            self.__find_img.append(path + creep_name + "_find" + str(it) + ".png")
            it = it + 1

    def enterEvent(self, event):
        super(CreepButton, self).enterEvent(event)

        self.setBackgroundImg(self.__second_img)

    def leaveEvent(self, event):
        super(CreepButton, self).leaveEvent(event)

        self.setBackgroundImg(self.__first_img)

    def onClicked(self):
        thr = threading.Thread(target=self.click_circle, daemon=True)
        thr.start()

    def click_circle(self):
        img = []
        for it in self.__find_img:
            img.append(pyautogui.locateOnScreen(it, confidence=global_confidence))

        for i in range(global_click_count):
            for it in img:
                x, y = it.left, it.top
                pyautogui.moveTo(x, y)
                pyautogui.click(x, y)
                if global_click_rate < 999:
                    time.sleep(1 / global_click_rate)


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.shortcut_hide = QShortcut(
            QKeySequence(global_hotkey_hide_pref1 + '+' + global_hotkey_hide_pref2 + '+' + global_hotkey_hide),
            self)
        self.shortcut_show = QShortcut(
            QKeySequence(global_hotkey_show_pref1 + '+' + global_hotkey_show_pref2 + '+' + global_hotkey_show),
            self)
        self.shortcut_hide.activated.connect(self.hide_combination_pressed)
        self.shortcut_show.activated.connect(self.show_combination_pressed)

        self.ghk = keyboard.GlobalHotKeys({
            '<' + global_hotkey_hide_pref1 + '>+<' + global_hotkey_hide_pref2 + '>+' + global_hotkey_hide: self.hide_combination_pressed,
            '<' + global_hotkey_show_pref1 + '>+<' + global_hotkey_show_pref2 + '>+' + global_hotkey_show: self.show_combination_pressed})
        self.ghk.start()


        self.create_hotkeys()
        self.createInterface()

    def create_hotkeys(self):
        if not isGlobalsHKEmpty():
            self.ghk.stop()
            self.ghk = keyboard.GlobalHotKeys({
                '<' + global_hotkey_hide_pref1 + '>+<' + global_hotkey_hide_pref2 + '>+' + global_hotkey_hide: self.hide_combination_pressed,
                '<' + global_hotkey_show_pref1 + '>+<' + global_hotkey_show_pref2 + '>+' + global_hotkey_show: self.show_combination_pressed})
            self.ghk.start()

            self.shortcut_hide.setKey(
                QKeySequence(global_hotkey_hide_pref1 + '+' + global_hotkey_hide_pref2 + '+' + global_hotkey_hide))
            self.shortcut_show.setKey(
                QKeySequence(global_hotkey_show_pref1 + '+' + global_hotkey_show_pref2 + '+' + global_hotkey_show))

    def createInterface(self):
        # main grid
        grid = QGridLayout()

        # control unit
        control_wgt = QWidget()
        control_wgt_lay = QFormLayout()

        # confidence slider
        control_wgt_slider_confidence = QSlider(QtCore.Qt.Orientation.Horizontal)
        control_wgt_slider_confidence.setMinimum(1)
        control_wgt_slider_confidence.setMaximum(1000)
        control_wgt_slider_confidence.setTickInterval(1)
        control_wgt_slider_confidence.setValue(300)
        control_wgt_slider_confidence.valueChanged.connect(self.slider_confidence_changed)
        QFormLayout.addRow(control_wgt_lay, QLabel('Точность рапознавания'), control_wgt_slider_confidence)

        # click count spinbox
        control_wgt_spinbox_click_count = QSpinBox()
        control_wgt_spinbox_click_count.setMinimum(1)
        control_wgt_spinbox_click_count.setMaximum(100000)
        control_wgt_spinbox_click_count.setSingleStep(1)
        control_wgt_spinbox_click_count.valueChanged.connect(self.spinbox_click_count_changed)
        QFormLayout.addRow(control_wgt_lay, QLabel('Количество кликов'), control_wgt_spinbox_click_count)

        # click rate spinbox
        control_wgt_spinbox_click_rate = QSpinBox()
        control_wgt_spinbox_click_rate.setMinimum(1)
        control_wgt_spinbox_click_rate.setMaximum(1000)
        control_wgt_spinbox_click_rate.setSingleStep(1)
        control_wgt_spinbox_click_rate.setValue(1000)
        control_wgt_spinbox_click_rate.valueChanged.connect(self.spinbox_click_rate_changed)
        QFormLayout.addRow(control_wgt_lay, QLabel('Кликов в секунду'), control_wgt_spinbox_click_rate)

        control_wgt.setLayout(control_wgt_lay)

        # hotkey unit
        hotkey_wgt = QWidget()
        hotkey_wgt_lay = QFormLayout()
        self.hide_line_edit = QLineEdit(
            global_hotkey_hide_pref1 + '+' + global_hotkey_hide_pref2 + '+' + global_hotkey_hide)
        self.show_line_edit = QLineEdit(
            global_hotkey_show_pref1 + '+' + global_hotkey_show_pref2 + '+' + global_hotkey_show)
        self.hide_line_edit.editingFinished.connect(self.hide_line_edit_changed)
        self.show_line_edit.editingFinished.connect(self.show_line_edit_changed)

        QFormLayout.addRow(hotkey_wgt_lay, QLabel("Скрыть"), self.hide_line_edit)
        QFormLayout.addRow(hotkey_wgt_lay, QLabel("Показать"), self.show_line_edit)

        hotkey_wgt.setLayout(hotkey_wgt_lay)

        # btn_wgt contains all buttons
        btn_wgt = QWidget()
        btn_wgt_lay = QGridLayout()

        row = 0
        column = 0

        # create buttons
        for it in self.__creeps:
            btn = CreepButton(it)
            # btn.pressed.connect(self.hide_combination_pressed)
            btn_wgt_lay.addWidget(btn, row, column, 1, 1)
            column = column + 1
            if(column == 3):
                column = 0
                row = 1

        btn_wgt.setLayout(btn_wgt_lay)

        grid.addWidget(control_wgt, 0, 0, 1, 1)
        grid.addWidget(hotkey_wgt, 0, 1, 1, 1)
        grid.addWidget(btn_wgt, 1, 0, 1, 2)

        self.setLayout(grid)

    def slider_confidence_changed(self, value):
        global global_confidence
        global_confidence = value / 1000

    def spinbox_click_count_changed(self, value):
        global global_click_count
        global_click_count = value

    def spinbox_click_rate_changed(self, value):
        global global_click_rate
        global_click_rate = 1000 / value

    def show_combination_pressed(self):
        self.show()

    def hide_combination_pressed(self):
        self.hide()

    def hide_line_edit_changed(self):
        text = self.hide_line_edit.text()
        words = []
        word = ""
        for symbol in text:
            if symbol != '+':
                word = word + symbol
            else:
                words.append(word)
                word = ""
        if len(word) > 0:
            words.append(word)

        if len(words) > 0:
            global global_hotkey_hide_pref1
            global_hotkey_hide_pref1 = words[0]
        if len(words) > 1:
            global global_hotkey_hide_pref2
            global_hotkey_hide_pref2 = words[1]
        if len(words) > 2:
            global global_hotkey_hide
            global_hotkey_hide = words[2]

        self.create_hotkeys()

    def show_line_edit_changed(self):
        text = self.show_line_edit.text()
        words = []
        word = ""
        for symbol in text:
            if symbol != '+':
                word = word + symbol
            else:
                words.append(word)
                word = ""
        if len(word) > 0:
            words.append(word)

        if len(words) > 0:
            global global_hotkey_show_pref1
            global_hotkey_show_pref1 = words[0]
        if len(words) > 1:
            global global_hotkey_show_pref2
            global_hotkey_show_pref2 = words[1]
        if len(words) > 2:
            global global_hotkey_show
            global_hotkey_show = words[2]

        self.create_hotkeys()

    __creeps = ['creeper', 'spider', 'enderman', 'blaze', 'slime', 'ghast']
