from PySide6.QtCore import Qt
from PySide6.QtGui import QRegion
from PySide6.QtWidgets import QLabel


class AvatarWidget(QLabel):
    def __init__(self, initials="V"):
        super().__init__(initials)
        self.setObjectName("avatarWidget")
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(48, 48)

    def resizeEvent(self, event):
        side = min(self.width(), self.height())
        self.setMask(QRegion(0, 0, side, side, QRegion.Ellipse))
        super().resizeEvent(event)
