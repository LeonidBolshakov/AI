import sys
from pathlib import Path
import os

from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QMainWindow,
    QDoubleSpinBox,
    QPushButton,
    QPlainTextEdit,
)
from openai import OpenAI


class AIClient:
    def __init__(self, key: str, path: str):
        self.client = self.create_client(key, path)

    @staticmethod
    def create_client(key: str, path: str) -> OpenAI:
        try:
            return OpenAI(
                api_key=os.getenv(key),
                base_url=path,
            )
        except Exception as e:
            # Получаем последнее исключение
            last_exception = e
            while last_exception.__cause__ is not None:
                last_exception = last_exception.__cause__
            raise ConnectionError(
                f"Ошибка соединения с {path}\n{last_exception.args[0]}"
            )

    def send_request(
            self, model: str, role: str, content: str, temperature: float
    ) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[{"role": role, "content": content}],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Ошибка при обработке задания\n{e}"


class ChatInterface(QMainWindow):
    comboModel: QComboBox
    spinboxCreativity: QDoubleSpinBox
    btnSubmitTask: QPushButton
    txtResponse: QPlainTextEdit
    txtSystem: QPlainTextEdit
    txtUser: QPlainTextEdit

    def __init__(self):
        super().__init__()

        self.ai_client = ""  # type = AIClient

        self.init_openai()
        self.init_vars()
        self.init_connections()

    def init_openai(self):
        try:
            self.ai_client = AIClient(
                "BOTHUB_API_KEY_", "https://bothub.chat/api/v2/openai/v1"
            )
        except ConnectionError as e:
            # Получаем последнее исключение
            last_exception = e
            while last_exception.__cause__ is not None:
                last_exception = last_exception.__cause__
            print(last_exception.args[0])
            sys.exit(1000)

    def init_vars(self):
        """Присвоение значений переменным"""

        self.init_ui()
        self.init_model_selector()

    def init_ui(self):
        # Загрузка UI и переменных в объект класса
        exe_directory = (  # Директория, из которой был запущен файл
            Path(sys.argv[0]).parent
            if hasattr(sys, "frozen")  # exe файл, получен с помощью PyInstaller
            else Path(__file__).parent
            # Если файл запущен как обычный Python-скрипт
        )

        ui_config_abs_path = exe_directory / "ai.ui"
        uic.loadUi(ui_config_abs_path, self)

    def init_model_selector(self):
        models = [
            "gpt-4o",
            "gpt-4o",
            "o1-mini",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-32k",
            "gpt-4-turbo",
            "Whisper",
            "claude-3.5-sonnet",
        ]
        self.comboModel.addItems(models)

    def init_connections(self):
        self.btnSubmitTask.clicked.connect(self.on_submit_task)

    def on_submit_setup(self):
        response = self.ai_client.send_request(
            self.comboModel.currentText(),
            "system",
            self.txtSystem.toPlainText(),
            self.spinboxCreativity.value(),
        )
        print(response)

    def on_submit_task(self):
        if self.txtSystem != "":
            self.on_submit_setup()

        response = self.ai_client.send_request(
            self.comboModel.currentText(),
            "user",
            self.txtUser.toPlainText(),
            self.spinboxCreativity.value(),
        )
        self.txtResponse.setPlainText(response)

    def start(self) -> int:
        """Запуск приложения и отображение главного окна."""

        self.show()  # Показ формы
        return QtWidgets.QApplication.exec()  # Запуск основного цикла приложения


# Запуск приложения
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # Создание экземпляра приложения
    calc_app = ChatInterface()  # Создание экземпляра чата
    sys.exit(calc_app.start())  # Запуск чата
