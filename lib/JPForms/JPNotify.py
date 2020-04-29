#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webbrowser

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QPoint, QPropertyAnimation, Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QWidget, QApplication

#from Lib.UiNotify import Ui_NotifyForm  # @UnresolvedImport

__version__ = "0.0.1"


class Ui_NotifyForm(object):
    def setupUi(self, NotifyForm):
        NotifyForm.setObjectName("NotifyForm")
        NotifyForm.resize(300, 200)
        NotifyForm.setStyleSheet("QWidget#widgetTitle {\n"
                                 "    background-color: rgb(76, 169, 106);\n"
                                 "}\n"
                                 "QWidget#widgetBottom {\n"
                                 "    border-top-style: solid;\n"
                                 "    border-top-width: 2px;\n"
                                 "    border-top-color: rgb(185, 218, 201);\n"
                                 "}\n"
                                 "QLabel#labelTitle {\n"
                                 "    color: rgb(255, 255, 255);\n"
                                 "}\n"
                                 "QLabel#labelContent {\n"
                                 "    padding: 5px;\n"
                                 "}\n"
                                 "QPushButton {\n"
                                 "    border: none;\n"
                                 "    background: transparent;\n"
                                 "}\n"
                                 "QPushButton#buttonClose {\n"
                                 "    font-family: \"webdings\";\n"
                                 "    color: rgb(255, 255, 255);\n"
                                 "}\n"
                                 "QPushButton#buttonClose:hover {\n"
                                 "    background-color: rgb(212, 64, 39);\n"
                                 "}\n"
                                 "QPushButton#buttonView {\n"
                                 "    color: rgb(255, 255, 255);\n"
                                 "    border-radius: 5px;\n"
                                 "    border: solid 1px rgb(76, 169, 106);\n"
                                 "    background-color: rgb(76, 169, 106);\n"
                                 "}\n"
                                 "QPushButton#buttonView:hover {\n"
                                 "    color: rgb(0, 0, 0);\n"
                                 "}")
        self.verticalLayout = QtWidgets.QVBoxLayout(NotifyForm)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widgetTitle = QtWidgets.QWidget(NotifyForm)
        self.widgetTitle.setMinimumSize(QtCore.QSize(0, 26))
        self.widgetTitle.setObjectName("widgetTitle")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widgetTitle)
        self.horizontalLayout_3.setContentsMargins(10, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.labelTitle = QtWidgets.QLabel(self.widgetTitle)
        self.labelTitle.setText("")
        self.labelTitle.setObjectName("labelTitle")
        self.horizontalLayout_3.addWidget(self.labelTitle)
        spacerItem = QtWidgets.QSpacerItem(40, 20,
                                           QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.buttonClose = QtWidgets.QPushButton(self.widgetTitle)
        self.buttonClose.setMinimumSize(QtCore.QSize(26, 26))
        self.buttonClose.setMaximumSize(QtCore.QSize(26, 26))
        self.buttonClose.setObjectName("buttonClose")
        self.horizontalLayout_3.addWidget(self.buttonClose)
        self.verticalLayout.addWidget(self.widgetTitle)
        self.labelContent = QtWidgets.QLabel(NotifyForm)
        self.labelContent.setText("")
        self.labelContent.setWordWrap(True)
        self.labelContent.setObjectName("labelContent")
        self.verticalLayout.addWidget(self.labelContent)
        self.widgetBottom = QtWidgets.QWidget(NotifyForm)
        self.widgetBottom.setObjectName("widgetBottom")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widgetBottom)
        self.horizontalLayout.setContentsMargins(0, 5, 5, 5)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(170, 20,
                                            QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        # self.buttonView = QtWidgets.QPushButton(self.widgetBottom)
        # self.buttonView.setMinimumSize(QtCore.QSize(75, 25))
        # self.buttonView.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # self.buttonView.setObjectName("buttonView")
        # self.horizontalLayout.addWidget(self.buttonView)
        self.verticalLayout.addWidget(self.widgetBottom)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(NotifyForm)
        QtCore.QMetaObject.connectSlotsByName(NotifyForm)

    def retranslateUi(self, NotifyForm):
        _translate = QtCore.QCoreApplication.translate
        NotifyForm.setWindowTitle(_translate("NotifyForm", "消息提示"))
        self.buttonClose.setText(_translate("NotifyForm", "r"))
        #self.buttonView.setText(_translate("NotifyForm", "查 看"))


class WindowNotify(QWidget, Ui_NotifyForm):

    SignalClosed = pyqtSignal()  # 弹窗关闭信号

    def __init__(self,
                 title="",
                 content="",
                 timeout=5000,
                 app=None,
                 *args,
                 **kwargs):
        super(WindowNotify, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setTitle(title).setContent(content)
        self._timeout = timeout
        self.app = app
        self._init()

    def setTitle(self, title):
        if title:
            self.labelTitle.setText(title)
        return self

    def title(self):
        return self.labelTitle.text()

    def setContent(self, content):
        if content:
            self.labelContent.setText(content)
        return self

    def content(self):
        return self.labelContent.text()

    def setTimeout(self, timeout):
        if isinstance(timeout, int):
            self._timeout = timeout
        return self

    def timeout(self):
        return self._timeout

    # def onView(self):
    #     print("onView")
    #     webbrowser.open_new_tab("http://alyl.vip")

    def onClose(self):
        #点击关闭按钮时
        print("onClose")
        self.isShow = False
        QTimer.singleShot(100, self.closeAnimation)  #启动弹回动画

    def _init(self):
        # 隐藏任务栏|去掉边框|顶层显示
        self.setWindowFlags(Qt.Tool | Qt.X11BypassWindowManagerHint
                            | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # 关闭按钮事件
        self.buttonClose.clicked.connect(self.onClose)
        # 点击查看按钮
        # self.buttonView.clicked.connect(self.onView)
        # 是否在显示标志
        self.isShow = True
        # 超时
        self._timeouted = False
        # 桌面
        self._desktop = QApplication.instance().desktop()
        # 窗口初始开始位置
        self._startPos = QPoint(
            self._desktop.screenGeometry().width() - self.width() - 5,
            self._desktop.screenGeometry().height())
        # 窗口弹出结束位置
        self._endPos = QPoint(
            self._desktop.screenGeometry().width() - self.width() - 5,
            self._desktop.availableGeometry().height() - self.height() - 5)
        # 初始化位置到右下角
        self.move(self._startPos)

        # 动画
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.finished.connect(self.onAnimationEnd)
        self.animation.setDuration(1000)  # 1s

        # 弹回定时器
        self._timer = QTimer(self, timeout=self.closeAnimation)

    def show(self, title="", content="", timeout=5000):
        self._timer.stop()  # 停止定时器,防止第二个弹出窗弹出时之前的定时器出问题
        self.hide()  # 先隐藏
        self.move(self._startPos)  # 初始化位置到右下角
        super(WindowNotify, self).show()
        self.setTitle(title).setContent(content).setTimeout(timeout)
        return self

    def showAnimation(self):
        print("showAnimation isShow = True")
        # 显示动画
        self.isShow = True
        self.animation.stop()  #先停止之前的动画,重新开始
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(self._endPos)
        self.animation.start()
        # 弹出5秒后,如果没有焦点则弹回去
        self._timer.start(self._timeout)


#         QTimer.singleShot(self._timeout, self.closeAnimation)

    def closeAnimation(self):
        print("closeAnimation hasFocus", self.hasFocus())
        # 关闭动画
        if self.hasFocus():
            # 如果弹出后倒计时5秒后还有焦点存在则失去焦点后需要主动触发关闭
            self._timeouted = True
            return  # 如果有焦点则不关闭
        self.isShow = False
        self.animation.stop()
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(self._startPos)
        self.animation.start()

    def onAnimationEnd(self):
        # 动画结束
        print("onAnimationEnd isShow", self.isShow)
        if not self.isShow:
            print("onAnimationEnd close()")
            self.close()
            print("onAnimationEnd stop timer")
            self._timer.stop()
            print("onAnimationEnd close and emit signal")
            self.SignalClosed.emit()

    def enterEvent(self, event):
        super(WindowNotify, self).enterEvent(event)
        # 设置焦点(好像没啥用,不过鼠标点击一下后,该方法就有用了)
        print("enterEvent setFocus Qt.MouseFocusReason")
        self.setFocus(Qt.MouseFocusReason)

    def leaveEvent(self, event):
        super(WindowNotify, self).leaveEvent(event)
        # 取消焦点
        print("leaveEvent clearFocus")
        self.clearFocus()
        if self._timeouted:
            QTimer.singleShot(1000, self.closeAnimation)

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QHBoxLayout
    app = QApplication(sys.argv)

    window = QWidget()
    notify = WindowNotify(app=app)
    notify.show(content='ljkhjkhk').showAnimation()
    # layout = QHBoxLayout(window)

    # b1 = QPushButton(
    #     "弹窗1",
    #     window,
    #     clicked=lambda: notify.show(content=b1.text()).showAnimation())
    # b2 = QPushButton(
    #     "弹窗2",
    #     window,
    #     clicked=lambda: notify.show(content=b2.text()).showAnimation())

    # layout.addWidget(b1)
    # layout.addWidget(b2)

    window.show()

    sys.exit(app.exec_())
