from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget


def make_icon(icon_name, color_hex, size=22):
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    pen = QPen(QColor(color_hex), max(1.6, size * 0.1), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)

    if icon_name == "users":
        painter.drawEllipse(QRectF(size * 0.19, size * 0.2, size * 0.24, size * 0.24))
        painter.drawEllipse(QRectF(size * 0.52, size * 0.25, size * 0.2, size * 0.2))
        painter.drawArc(QRectF(size * 0.12, size * 0.45, size * 0.4, size * 0.3), 0, 180 * 16)
        painter.drawArc(QRectF(size * 0.45, size * 0.5, size * 0.3, size * 0.24), 0, 180 * 16)

    elif icon_name == "clock":
        painter.drawEllipse(QRectF(size * 0.15, size * 0.15, size * 0.7, size * 0.7))
        painter.drawLine(QPointF(size * 0.5, size * 0.5), QPointF(size * 0.5, size * 0.3))
        painter.drawLine(QPointF(size * 0.5, size * 0.5), QPointF(size * 0.64, size * 0.58))

    elif icon_name == "check":
        painter.drawEllipse(QRectF(size * 0.15, size * 0.15, size * 0.7, size * 0.7))
        painter.drawLine(QPointF(size * 0.33, size * 0.52), QPointF(size * 0.46, size * 0.66))
        painter.drawLine(QPointF(size * 0.46, size * 0.66), QPointF(size * 0.7, size * 0.36))

    elif icon_name == "alert":
        painter.drawEllipse(QRectF(size * 0.15, size * 0.15, size * 0.7, size * 0.7))
        painter.drawLine(QPointF(size * 0.5, size * 0.3), QPointF(size * 0.5, size * 0.56))
        painter.drawPoint(QPointF(size * 0.5, size * 0.7))

    elif icon_name == "camera":
        body = QPainterPath()
        body.addRoundedRect(QRectF(size * 0.15, size * 0.32, size * 0.46, size * 0.36), size * 0.08, size * 0.08)
        lens = QPainterPath()
        lens.moveTo(size * 0.61, size * 0.41)
        lens.lineTo(size * 0.83, size * 0.31)
        lens.lineTo(size * 0.83, size * 0.69)
        lens.lineTo(size * 0.61, size * 0.59)
        lens.closeSubpath()
        painter.drawPath(body)
        painter.drawPath(lens)

    elif icon_name == "user_plus":
        painter.drawEllipse(QRectF(size * 0.35, size * 0.18, size * 0.26, size * 0.26))
        painter.drawArc(QRectF(size * 0.24, size * 0.44, size * 0.48, size * 0.34), 0, 180 * 16)
        painter.drawLine(QPointF(size * 0.14, size * 0.33), QPointF(size * 0.28, size * 0.33))
        painter.drawLine(QPointF(size * 0.21, size * 0.26), QPointF(size * 0.21, size * 0.4))

    elif icon_name == "upload":
        painter.drawLine(QPointF(size * 0.2, size * 0.72), QPointF(size * 0.8, size * 0.72))
        painter.drawLine(QPointF(size * 0.5, size * 0.72), QPointF(size * 0.5, size * 0.24))
        painter.drawLine(QPointF(size * 0.5, size * 0.24), QPointF(size * 0.36, size * 0.38))
        painter.drawLine(QPointF(size * 0.5, size * 0.24), QPointF(size * 0.64, size * 0.38))

    elif icon_name == "profile":
        # Use a filled silhouette for better legibility at small and medium sizes.
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(color_hex))
        painter.drawEllipse(QRectF(size * 0.34, size * 0.17, size * 0.32, size * 0.32))
        torso = QPainterPath()
        torso.addRoundedRect(QRectF(size * 0.21, size * 0.52, size * 0.58, size * 0.3), size * 0.16, size * 0.16)
        painter.drawPath(torso)

    painter.end()
    return pix


def icon_for_variant(variant, stat=True):
    if stat:
        if variant == "patients":
            return make_icon("users", "#0F766E")
        if variant == "pending":
            return make_icon("clock", "#B45309")
        if variant == "uploaded":
            return make_icon("check", "#059669")
        if variant == "rejected":
            return make_icon("alert", "#BE123C")
        return make_icon("users", "#334155")

    if variant == "record":
        return make_icon("camera", "#0F766E")
    if variant == "patient":
        return make_icon("user_plus", "#0F766E")
    if variant == "upload":
        return make_icon("upload", "#0F766E")
    if variant == "profile":
        return make_icon("profile", "#0F766E")
    return make_icon("users", "#334155")


class ClickableFrame(QFrame):
    clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)
        self._apply_shadow(blur=10, y_offset=1, alpha=45)

    def _apply_shadow(self, blur, y_offset, alpha):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, y_offset)
        shadow.setColor(QColor(15, 23, 42, alpha))
        self.setGraphicsEffect(shadow)

    def enterEvent(self, event):
        self._apply_shadow(blur=22, y_offset=4, alpha=85)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._apply_shadow(blur=10, y_offset=1, alpha=45)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class HomeStatCard(ClickableFrame):
    def __init__(self, title, subtitle, value="0", variant="patients"):
        super().__init__()
        self.setObjectName("homeStatCard")
        self.setProperty("variant", variant)
        self.setCursor(Qt.PointingHandCursor)

        row = QHBoxLayout(self)
        row.setContentsMargins(12, 10, 12, 10)
        row.setSpacing(10)

        self.icon = QLabel(" ")
        self.icon.setObjectName("homeStatIcon")
        self.icon.setProperty("variant", variant)
        self.icon.setFixedSize(40, 40)
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setPixmap(icon_for_variant(variant, stat=True))
        row.addWidget(self.icon, 0, Qt.AlignTop)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("homeStatTitle")
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("homeStatValue")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("homeStatSubtitle")

        text_col.addWidget(self.title_label)
        text_col.addWidget(self.value_label)
        text_col.addWidget(self.subtitle_label)

        row.addLayout(text_col, 1)

    def set_value(self, value):
        self.value_label.setText(str(value))


class QuickActionCard(ClickableFrame):
    def __init__(self, title, subtitle, variant="default"):
        super().__init__()
        self.setObjectName("homeQuickAction")
        self.setProperty("variant", variant)
        self.setCursor(Qt.PointingHandCursor)

        row = QHBoxLayout(self)
        row.setContentsMargins(12, 10, 12, 10)
        row.setSpacing(10)

        self.icon = QLabel(" ")
        self.icon.setObjectName("homeQuickIcon")
        self.icon.setProperty("variant", variant)
        self.icon.setFixedSize(40, 40)
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setPixmap(icon_for_variant(variant, stat=False))
        row.addWidget(self.icon, 0, Qt.AlignTop)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("homeQuickTitle")
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setObjectName("homeQuickSubtitle")

        text_col.addWidget(self.title_label)
        text_col.addWidget(self.subtitle_label)
        row.addLayout(text_col, 1)


class DashboardPage(QWidget):
    recordRequested = Signal()
    addPatientRequested = Signal()
    viewUploadsRequested = Signal()
    profileRequested = Signal()
    cardActionRequested = Signal(str)

    def __init__(self):
        super().__init__()

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 6, 8, 10)
        root.setSpacing(10)

        hero_card = ClickableFrame()
        hero_card.setObjectName("homeHeroCard")
        hero_card.setCursor(Qt.PointingHandCursor)
        hero_card.clicked.connect(self.profileRequested.emit)
        hero_layout = QHBoxLayout(hero_card)
        hero_layout.setContentsMargins(12, 10, 12, 10)
        hero_layout.setSpacing(8)

        hero_left = QVBoxLayout()
        hero_left.setContentsMargins(0, 0, 0, 0)
        hero_left.setSpacing(4)

        hero_caption = QLabel("FIELD CONSOLE")
        hero_caption.setObjectName("homeHeroCaption")
        hero_name = QLabel("vivek")
        hero_name.setObjectName("homeHeroName")
        hero_role = QLabel("Healthcare Field Worker")
        hero_role.setObjectName("homeHeroRole")

        hero_left.addWidget(hero_caption)
        hero_left.addWidget(hero_name)
        hero_left.addSpacing(3)
        hero_left.addWidget(hero_role)
        hero_left.addStretch(1)

        hero_avatar = QLabel(" ")
        hero_avatar.setObjectName("homeHeroAvatar")
        hero_avatar.setFixedSize(70, 70)
        hero_avatar.setAlignment(Qt.AlignCenter)
        hero_avatar.setPixmap(make_icon("profile", "#E7F6F3", size=32))

        hero_layout.addLayout(hero_left, 1)
        hero_layout.addWidget(hero_avatar, 0, Qt.AlignVCenter)
        root.addWidget(hero_card)

        stats_title = QLabel("Statistics")
        stats_title.setObjectName("homeSectionTitle")
        stats_subtitle = QLabel("Operational overview for current patients and video review queue.")
        stats_subtitle.setObjectName("homeSectionSubtitle")
        root.addWidget(stats_title)
        root.addWidget(stats_subtitle)

        self.cards = {
            "Total Patients": HomeStatCard("Patients", "Registered records", variant="patients"),
            "Pending Uploads": HomeStatCard("Pending Uploads", "Awaiting review", variant="pending"),
            "Uploaded": HomeStatCard("Approved Uploads", "Completed reviews", variant="uploaded"),
            "Rejected": HomeStatCard("Rejected Uploads", "Need follow-up", variant="rejected"),
        }

        stats_grid = QGridLayout()
        stats_grid.setContentsMargins(0, 0, 0, 0)
        stats_grid.setHorizontalSpacing(8)
        stats_grid.setVerticalSpacing(0)
        for key in ["Total Patients", "Pending Uploads", "Uploaded", "Rejected"]:
            card = self.cards[key]
            card.clicked.connect(lambda t=key: self.cardActionRequested.emit(t))
            stats_grid.addWidget(card, 0, ["Total Patients", "Pending Uploads", "Uploaded", "Rejected"].index(key))
        stats_grid.setColumnStretch(0, 1)
        stats_grid.setColumnStretch(1, 1)
        stats_grid.setColumnStretch(2, 1)
        stats_grid.setColumnStretch(3, 1)
        root.addLayout(stats_grid)

        quick_title = QLabel("Quick Actions")
        quick_title.setObjectName("homeSectionTitle")
        quick_subtitle = QLabel("Start a new recording session or move directly into data operations.")
        quick_subtitle.setObjectName("homeSectionSubtitle")
        root.addSpacing(6)
        root.addWidget(quick_title)
        root.addWidget(quick_subtitle)

        self.record_action = QuickActionCard("Record New Video", "Capture a new video for a patient", variant="record")
        self.record_action.clicked.connect(self.recordRequested.emit)

        self.add_patient_action = QuickActionCard("Add New Patient", "Register a new patient record", variant="patient")
        self.add_patient_action.clicked.connect(self.addPatientRequested.emit)

        self.view_uploads_action = QuickActionCard("View Uploads", "Check your video upload history", variant="upload")
        self.view_uploads_action.clicked.connect(self.viewUploadsRequested.emit)

        self.profile_action = QuickActionCard("My Profile", "View and edit your profile", variant="profile")
        self.profile_action.clicked.connect(self.profileRequested.emit)

        quick_grid = QGridLayout()
        quick_grid.setContentsMargins(0, 0, 0, 0)
        quick_grid.setHorizontalSpacing(8)
        quick_grid.setVerticalSpacing(8)
        quick_grid.addWidget(self.record_action, 0, 0)
        quick_grid.addWidget(self.add_patient_action, 0, 1)
        quick_grid.addWidget(self.view_uploads_action, 1, 0)
        quick_grid.addWidget(self.profile_action, 1, 1)
        quick_grid.setColumnStretch(0, 1)
        quick_grid.setColumnStretch(1, 1)
        root.addLayout(quick_grid)

    def update_stats(self, values):
        for key, value in values.items():
            if key in self.cards:
                self.cards[key].set_value(value)
