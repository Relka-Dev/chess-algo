from __future__ import annotations

from BotWidget import BotWidget


class Player:
    #def __init__(self, team: int, color: str, rotation: int, widget: BotWidget):
    def __init__(self, color: str, widget: BotWidget):
        #self.team: int = team
        self.color: str = color
        #self.rotation: int = rotation
        self.widget: BotWidget = widget

    def get_budget(self) -> float:
        return self.widget.budgetValue.value()

    def get_func(self):
        return self.widget.playerBot.currentText(), self.widget.playerBot.currentData()
