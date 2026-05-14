import warnings

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath
from utils.theme_helpers import ACCENT, TEXT0

_G = 10  # glow halo thickness (px on each side)


class Toast(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAutoFillBackground(False)
        self.hide()

        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setAutoFillBackground(False)

        lo = QHBoxLayout(self)
        # contentsMargins = glow pad + inner text padding
        lo.setContentsMargins(_G + 16, _G + 10, _G + 22, _G + 10)
        lo.addWidget(self._label)

        # Single effect — no nested-effect conflict
        self._effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._effect)
        self._effect.setOpacity(0.0)

        # Entrada: fade + slide desde abajo
        self._anim_fade_in = QPropertyAnimation(self._effect, b"opacity", self)
        self._anim_fade_in.setDuration(240)
        self._anim_fade_in.setStartValue(0.0)
        self._anim_fade_in.setEndValue(1.0)
        self._anim_fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._anim_pos_in = QPropertyAnimation(self, b"pos", self)
        self._anim_pos_in.setDuration(240)
        self._anim_pos_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Salida: solo fade
        self._anim_out = QPropertyAnimation(self._effect, b"opacity", self)
        self._anim_out.setDuration(300)
        self._anim_out.setStartValue(1.0)
        self._anim_out.setEndValue(0.0)
        self._anim_out.setEasingCurve(QEasingCurve.Type.InQuad)
        self._anim_out.finished.connect(self.hide)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._anim_out.start)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dark card rect (inset by glow margin)
        r = QRectF(self.rect()).adjusted(_G, _G, -_G, -_G)
        radius = 5.0

        # Outer glow — concentric semi-transparent gold strokes simulating blur
        for spread, alpha in [(8, 7), (6, 14), (4, 24), (2.5, 40), (1.0, 62)]:
            pen = QPen(QColor(201, 164, 74, alpha), spread * 2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            gr = r.adjusted(-spread, -spread, spread, spread)
            painter.drawRoundedRect(gr, radius + spread * 0.5, radius + spread * 0.5)

        # Dark background
        path = QPainterPath()
        path.addRoundedRect(r, radius, radius)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(path, QColor(0x16, 0x16, 0x1C))

        # Left accent bar clipped to card shape
        painter.setClipPath(path)
        painter.fillRect(QRectF(r.left(), r.top(), 3.0, r.height()), QColor(ACCENT))
        painter.setClipping(False)

        # Subtle gold border
        painter.setPen(QPen(QColor(201, 164, 74, 36), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(r.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

    def show_message(self, text: str, duration_ms: int = 2800):
        from styles.theme import fs

        self._anim_out.stop()
        self._anim_fade_in.stop()
        self._anim_pos_in.stop()
        self._timer.stop()

        self._label.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                color: {TEXT0};
                font-size: {fs(16)}px;
                font-weight: 500;
                letter-spacing: 0.2px;
            }}
        """)
        self._label.setText(text)
        self.adjustSize()

        p = self.parent()
        if p:
            # Position so the visible card lands 24px/28px from the parent edges
            fx = p.width() - self.width() - 24 + _G
            fy = p.height() - self.height() - 28 + _G
            self.move(fx, fy + 14)
            self._anim_pos_in.setStartValue(QPoint(fx, fy + 14))
            self._anim_pos_in.setEndValue(QPoint(fx, fy))

        self._effect.setOpacity(0.0)
        self.show()
        self.raise_()
        self._anim_fade_in.start()
        self._anim_pos_in.start()
        self._timer.start(duration_ms)
