
import math
from typing import List, Optional
from PyQt6.QtCore import QObject, QPointF, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGraphicsPixmapItem

class PieceSignals(QObject):
    released = pyqtSignal(object, QPointF, QPointF)

class Piece(QGraphicsPixmapItem):
    def __init__(self, img: QPixmap, piece_type: str, color: str):
        super().__init__(img)

        self.type = piece_type
        self.color = color

        self.target = QPointF()
        self.move_timer = QTimer()
        self.explode_timer = QTimer()
        self.move_timer.timeout.connect(self._move_tick)
        self.explode_timer.timeout.connect(self._explode_tick)
        self.speed = 10
        self.fragments: List[List[QPixmap]] = []
        self.fragmentItems: List[Tuple[QGraphicsPixmapItem, QPointF]] = []
        self.cutting_number = 5

        self.old_pos = QPointF()
        
        self.released = False
        self.manual_enabled = False
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, False)

        self._fragment()

        self.signals = PieceSignals()

    def enableMovement(self, movable: bool):
        self.released = False
        self.manual_enabled = movable

        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, movable)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, movable)

    def mousePressEvent(self, event: Optional['QGraphicsSceneMouseEvent']) -> None:
        if not self.manual_enabled:
            return
        
        self.released = False
        self.old_pos = self.pos()

        self.setZValue(self.zValue() + 1)

        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: Optional['QGraphicsSceneMouseEvent']) -> None:
        if not self.manual_enabled:
            return

        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: Optional['QGraphicsSceneMouseEvent']) -> None:
        if not self.manual_enabled:
            return

        self.released = True

        self.signals.released.emit(self, self.old_pos, event.scenePos())

        self.setZValue(self.zValue() - 1)

        return super().mouseReleaseEvent(event)

    def move(self, y, x, w, h):
        self.target = QPointF(w * x, h * y)

        self.move_timer.start(16);

    def explode(self):
        self.explode_timer.start(16);

    def _fragment(self):
        self.fragments = []
        
        fragment_size = int(self.pixmap().height() / self.cutting_number)

        for i in range(self.cutting_number):
            self.fragments.append([])

            for j in range(self.cutting_number):
                x = i * fragment_size
                y = j * fragment_size
                self.fragments[i].append(self.pixmap().copy(x, y, fragment_size, fragment_size))
                

    def _explode_tick(self):
        for fragment, target in self.fragmentItems:
            pos = fragment.pos()

            dx, dy = target.x() - pos.x(), target.y() - pos.y()
            dist = math.hypot(dx, dy)

            d_opacity = abs(0 - fragment.opacity())

            if dist <= 1:
                fragment.setPos(target)
                self.explode_timer.stop()

            else:
                step = min(dist, 2)
                fragment.setPos(pos.x() + dx / dist * step, pos.y() + dy / dist * step)

            if d_opacity <= 0.1:
                fragment.setOpacity(0)

            else:
                fragment.setOpacity(fragment.opacity() - 0.03)

    def _move_tick(self):
        pos = self.pos()

        dx, dy = self.target.x() - pos.x(), self.target.y() - pos.y()
        dist = math.hypot(dx, dy)

        if dist < 1:
            self.setPos(self.target)
            self.move_timer.stop()

        else:
            step = min(dist, self.speed)
            self.setPos(pos.x() + dx / dist * step, pos.y() + dy / dist * step)

    def string(self):
        return f"{self.type}{self.color}"

    def upgrade(self, piece_type, new_pixmap):
        self.setPixmap(new_pixmap)
        self.type = piece_type

        self._fragment()

    def addFragmentItem(self, item: QGraphicsPixmapItem, target: QPointF):
        self.fragmentItems.append((item, target))

    def __eq__(self, value):
        if isinstance(value, str):
            return self.string() == value

        return False

    def __ne__(self, value):
        if isinstance(value, str):
            return self.string() != value
        return not self.__eq__(value)

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return self.string()[idx.start:idx.stop:idx.step]

        return self.string()[idx]

    def __len__(self):
        return len(self.string())
