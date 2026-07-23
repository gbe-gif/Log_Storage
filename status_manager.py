import random

from PySide6.QtCore import Qt, QTimer


class StatusManager:
    def __init__(self, label):
        self.label = label

        # QLabel 기본 스타일
        self.label.setStyleSheet("""
            QLabel {
                color: #D7D7D7;
                font-size: 13px;
                padding-right: 15px;
            }
        """)
        self.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.reset)

        self.success_kaomoji = [
            "(•ᴗ•)", "(^-^)", "(´▽`)", "(≧▽≦)",
            "٩(ˊᗜˋ*)و", "(๑•̀ㅂ•́)و",
            "( •̀ ω •́ )✧", "(˶ᵔ ᵕ ᵔ˶)"
        ]

        self.warning_kaomoji = [
            "(・・;)", "(´•ω•`)", "( •᷄⌓•᷅ )",
            "(;´Д`)", "(>_<)"
        ]

        self.error_kaomoji = [
            "(´･ω･`)", "( ;_; )",
            "( •︠ˍ•︡ )", "(T_T)", "(ToT)"
        ]

        self.last_kaomoji = ""

    def _get_kaomoji(self, pool):
        choices = [k for k in pool if k != self.last_kaomoji]
        if not choices:
            choices = pool

        kaomoji = random.choice(choices)
        self.last_kaomoji = kaomoji
        return kaomoji

    def _set_message(self, message, pool):
        kaomoji = self._get_kaomoji(pool)
        self.label.setText(f"💡 {message} {kaomoji}")
        self.timer.start(5000)

    def success(self, message):
        self.timer.stop()
        self._set_message(message, self.success_kaomoji)

    def warning(self, message):
        self.timer.stop()
        self._set_message(message, self.warning_kaomoji)

    def error(self, message):
        self.timer.stop()
        self._set_message(message, self.error_kaomoji)

    def reset(self):
        kaomoji = self._get_kaomoji(self.success_kaomoji)
        self.label.setText(f"💡 준비 완료 {kaomoji}")
        self.timer.stop()


"""
StatusManager

- 툴바 상태 메시지 관리
- QLabel 스타일 관리
- 카오모지 랜덤 출력
- 자동 초기화(5초)
- 성공/경고/오류 메시지 표시
"""