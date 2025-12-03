from PyQt6 import uic
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QWidget

from Data.bot_widget import Ui_Form
from PieceManager import PieceManager


class BotWidget(Ui_Form, QWidget):
    def __init__(self, color: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        uic.loadUi("Data/bot_widget.ui", self)
        self.colorName.setText(PieceManager.COLOR_NAMES[color])
        palette = self.colorSwatch.palette()
        palette.setBrush(QPalette.ColorRole.Window, PieceManager.COLORS[color][0])
        self.colorSwatch.setPalette(palette)
