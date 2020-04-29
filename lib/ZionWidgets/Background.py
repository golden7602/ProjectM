from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPalette, QPixmap, QBrush
from Ui.Ui_FormBackGround import Ui_Form
from PyQt5.QtCore import Qt
from os import getcwd


class Form_Background(Ui_Form):
    def __init__(self, mainform):
        super().__init__()
        self.Widget = QWidget()
        self.setupUi(self.Widget)
        self.label.setPixmap(mainform.backPixmap)

        # palette1 = QPalette()
        # palette1.setBrush(self.widget_2.backgroundRole(), QBrush(QPixmap(getcwd() + "\\res\\mLogo.png",flags=Qt.Im)))
        # self.widget_2.setAutoFillBackground(True)
        # self.widget_2.setPalette(palette1)
        #self.label.setPixmap(QPixmap(getcwd() + "\\res\\mLogo.png"))
        mainform.addForm(self.Widget)

        # palette1 = QPalette()
        # palette1.setColor(self.backgroundRole(), QColor(255, 192, 203))
        # if isinstance(self, QComboBox_):
        #     if self.isEditable():
        #         self.lineEdit().setAutoFillBackground(True)
        #         self.lineEdit().setPalette(palette1)
        #     else:
        #         self.setPalette(palette1)
        # else:
