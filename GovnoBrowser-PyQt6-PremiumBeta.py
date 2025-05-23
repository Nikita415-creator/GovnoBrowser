import sys
import os
import json
from PyQt6.QtCore import QUrl, Qt, QTimer, QRectF, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QToolBar, QLineEdit, QPushButton, 
    QTabBar, QStyle, QWidget, QMessageBox, QLabel, QVBoxLayout, QComboBox,
    QHBoxLayout, QDialog, QFormLayout, QScrollArea, QListWidget, QListWidgetItem
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PyQt6.QtGui import QPainter, QBrush, QPen, QColor, QDesktopServices, QIcon, QGuiApplication
from PyQt6.QtNetwork import QNetworkProxy

class ProxyManager:
    def __init__(self):
        self.proxy = QNetworkProxy()
        self.proxy_types = {
            "Без прокси": QNetworkProxy.ProxyType.NoProxy,
            "США": ("ex.com", 8022),
            "Германия": ("de.com", 8022),
            "Япония": ("jp.com", 3228)
        }
    
    def set_proxy(self, location):
        if location == "Без прокси":
            QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.ProxyType.NoProxy))
        elif location in self.proxy_types:
            host, port = self.proxy_types[location]
            self.proxy.setType(QNetworkProxy.ProxyType.HttpProxy)
            self.proxy.setHostName(host)
            self.proxy.setPort(port)
            QNetworkProxy.setApplicationProxy(self.proxy)

class SnakeGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Змейка.app")
        self.setFixedSize(420, 420)
        self.setStyleSheet("background-color: #0a192f;")
        
        self.cell_size = 20
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_snake)
        self.direction = Qt.Key.Key_Right
        self.snake = []
        self.food = None
        self.score = 0
        
        self.init_game()
        self.timer.start(200)
    
    def init_game(self):
        start_x, start_y = 100, 100
        for i in range(3):
            self.snake.append(QRectF(
                start_x - i * self.cell_size, 
                start_y, 
                self.cell_size, 
                self.cell_size
            ))
        self.spawn_food()
    
    def spawn_food(self):
        from random import randint
        cols = self.width() // self.cell_size
        rows = self.height() // self.cell_size
        self.food = QRectF(
            randint(0, cols-1) * self.cell_size,
            randint(0, rows-1) * self.cell_size,
            self.cell_size,
            self.cell_size
        )
    
    def move_snake(self):
        head = self.snake[0]
        new_head = QRectF(head)
        
        if self.direction == Qt.Key.Key_Left:
            new_head.moveLeft(head.left() - self.cell_size)
        elif self.direction == Qt.Key.Key_Right:
            new_head.moveLeft(head.left() + self.cell_size)
        elif self.direction == Qt.Key.Key_Up:
            new_head.moveTop(head.top() - self.cell_size)
        elif self.direction == Qt.Key.Key_Down:
            new_head.moveTop(head.top() + self.cell_size)
        
        if (new_head.left() < 0 or 
            new_head.right() > self.width() or
            new_head.top() < 0 or 
            new_head.bottom() > self.height() or
            any(new_head.intersects(segment) for segment in self.snake[:-1])):
            self.game_over()
            return
        
        self.snake.insert(0, new_head)
        
        if new_head.intersects(self.food):
            self.score += 1
            self.spawn_food()
        else:
            self.snake.pop()
        
        self.update()
    
    def game_over(self):
        self.timer.stop()
        QMessageBox.information(self, "Game Over", f"Счёт: {self.score}")
        self.close()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setBrush(QBrush(QColor(100, 255, 100)))
        for segment in self.snake:
            painter.drawRect(segment)
        
        painter.setBrush(QBrush(QColor(255, 100, 100)))
        painter.drawRect(self.food)
        
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(10, 20, f"Счёт: {self.score}")
    
    def keyPressEvent(self, event):
        key = event.key()
        if (key == Qt.Key.Key_Left and self.direction != Qt.Key.Key_Right or
            key == Qt.Key.Key_Right and self.direction != Qt.Key.Key_Left or
            key == Qt.Key.Key_Up and self.direction != Qt.Key.Key_Down or
            key == Qt.Key.Key_Down and self.direction != Qt.Key.Key_Up):
            self.direction = key

class PasswordItemWidget(QWidget):
    def __init__(self, site, username, password, parent=None):
        super().__init__(parent)
        self.setup_ui(site, username, password)
        
    def setup_ui(self, site, username, password):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(0)
        
        self.top_widget = QWidget()
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        self.site_label = QLabel(f"🌐 {site}")
        self.site_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 16px; 
            color: #64ffda;
            padding: 8px 0;
        """)
        
        self.toggle_btn = QPushButton()
        self.toggle_btn.setIcon(QIcon.fromTheme("arrow-down"))
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #64ffda;
                font-size: 16px;
            }
        """)
        self.toggle_btn.setFixedSize(24, 24)
        
        top_layout.addWidget(self.site_label)
        top_layout.addStretch()
        top_layout.addWidget(self.toggle_btn)
        self.top_widget.setLayout(top_layout)
        
        self.bottom_widget = QWidget()
        self.bottom_widget.setVisible(False)
        bottom_layout = QVBoxLayout()
        bottom_layout.setContentsMargins(15, 0, 0, 5)
        
        user_layout = QHBoxLayout()
        user_label = QLabel("👤 Имя пользователя:")
        user_label.setStyleSheet("color: #e6f1ff;")
        
        self.username_value = QLabel(username)
        self.username_value.setStyleSheet("""
            color: #e6f1ff;
            background: #172a45;
            padding: 5px;
            border-radius: 3px;
        """)
        
        self.copy_user_btn = QPushButton("📋")
        self.copy_user_btn.setStyleSheet("""
            QPushButton {
                background: #64ffda;
                color: #0a192f;
                padding: 5px;
                border-radius: 3px;
                font-weight: bold;
                min-width: 30px;
            }
            QPushButton:hover { background: #52e3c2; }
        """)
        self.copy_user_btn.clicked.connect(lambda: self.copy_to_clipboard(username))
        
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.username_value)
        user_layout.addWidget(self.copy_user_btn)
        user_layout.setSpacing(10)
        
        pass_layout = QHBoxLayout()
        pass_label = QLabel("🔑 Пароль:")
        pass_label.setStyleSheet("color: #e6f1ff;")
        
        self.password_value = QLabel("••••••••")
        self.password_value.setStyleSheet("""
            color: #e6f1ff;
            background: #172a45;
            padding: 5px;
            border-radius: 3px;
        """)
        
        self.show_pass_btn = QPushButton("👁")
        self.show_pass_btn.setStyleSheet("""
            QPushButton {
                background: #1e3a5a;
                color: #e6f1ff;
                padding: 5px;
                border-radius: 3px;
                min-width: 30px;
            }
            QPushButton:hover { background: #2a4a6a; }
        """)
        self.show_pass_btn.setCheckable(True)
        self.show_pass_btn.toggled.connect(self.toggle_password_visibility)
        
        self.copy_pass_btn = QPushButton("📋")
        self.copy_pass_btn.setStyleSheet("""
            QPushButton {
                background: #64ffda;
                color: #0a192f;
                padding: 5px;
                border-radius: 3px;
                font-weight: bold;
                min-width: 30px;
            }
            QPushButton:hover { background: #52e3c2; }
        """)
        self.copy_pass_btn.clicked.connect(lambda: self.copy_to_clipboard(password))
        
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.password_value)
        pass_layout.addWidget(self.show_pass_btn)
        pass_layout.addWidget(self.copy_pass_btn)
        pass_layout.setSpacing(10)
        
        btn_layout = QHBoxLayout()
        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background: #1e3a5a;
                color: #e6f1ff;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover { background: #2a4a6a; }
        """)
        
        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: #ff5555;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover { background: #ff3333; }
        """)
        
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        
        bottom_layout.addLayout(user_layout)
        bottom_layout.addLayout(pass_layout)
        bottom_layout.addLayout(btn_layout)
        self.bottom_widget.setLayout(bottom_layout)
        
        self.layout.addWidget(self.top_widget)
        self.layout.addWidget(self.bottom_widget)
        self.setLayout(self.layout)
        
        self.animation = QPropertyAnimation(self.bottom_widget, b"maximumHeight")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.real_password = password
        self.is_expanded = False
        
        self.toggle_btn.clicked.connect(self.toggle_expand)
    
    def toggle_expand(self):
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.bottom_widget.setVisible(True)
            self.animation.setStartValue(0)
            self.animation.setEndValue(self.bottom_widget.sizeHint().height())
            self.toggle_btn.setIcon(QIcon.fromTheme("arrow-up"))
        else:
            self.animation.setStartValue(self.bottom_widget.height())
            self.animation.setEndValue(0)
            self.toggle_btn.setIcon(QIcon.fromTheme("arrow-down"))
            self.animation.finished.connect(lambda: self.bottom_widget.setVisible(False) if not self.is_expanded else None)
        
        self.animation.start()
    
    def toggle_password_visibility(self, checked):
        if checked:
            self.password_value.setText(self.real_password)
        else:
            self.password_value.setText("••••••••")
    
    def copy_to_clipboard(self, text):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Скопировано")
        msg.setText("Текст скопирован в буфер обмена!")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #0a192f;
                color: #e6f1ff;
            }
            QLabel { color: #e6f1ff; }
        """)
        msg.show()
        QTimer.singleShot(1000, msg.close)

class PasswordDialog(QDialog):
    def __init__(self, parent=None, site="", username="", password="", edit_mode=False):
        super().__init__(parent)
        self.setWindowTitle("Добавить/Изменить пароль" if not edit_mode else "Редактировать пароль")
        self.resize(400, 250)
        self.setMinimumSize(350, 200)
        self.setStyleSheet("""
            background-color: #0a192f;
            color: #e6f1ff;
            font-family: Arial;
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel("Добавление пароля" if not edit_mode else "Редактирование пароля")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #64ffda;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        form = QFormLayout()
        form.setContentsMargins(20, 20, 20, 20)
        
        self.site_input = QLineEdit()
        self.site_input.setText(site)
        self.site_input.setPlaceholderText("example.com")
        self.site_input.setStyleSheet("""
            padding: 8px;
            border: 1px solid #64ffda;
            border-radius: 4px;
            background: #172a45;
            color: white;
        """)
        
        self.username_input = QLineEdit()
        self.username_input.setText(username)
        self.username_input.setPlaceholderText("username123")
        self.username_input.setStyleSheet("""
            padding: 8px;
            border: 1px solid #64ffda;
            border-radius: 4px;
            background: #172a45;
            color: white;
        """)
        
        self.password_input = QLineEdit()
        self.password_input.setText(password)
        self.password_input.setPlaceholderText("********")
        self.password_input.setStyleSheet("""
            padding: 8px;
            border: 1px solid #64ffda;
            border-radius: 4px;
            background: #172a45;
            color: white;
        """)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        show_pass_btn = QPushButton("👁")
        show_pass_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #64ffda;
                font-size: 16px;
                padding: 0;
                margin-left: 5px;
            }
        """)
        show_pass_btn.clicked.connect(self.toggle_password_visibility)
        
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(self.password_input)
        pass_layout.addWidget(show_pass_btn)
        
        form.addRow("Сайт:", self.site_input)
        form.addRow("Имя пользователя:", self.username_input)
        form.addRow("Пароль:", pass_layout)
        
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #ff5555;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background: #ff3333; }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Сохранить")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #64ffda;
                color: #0a192f;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background: #52e3c2; }
        """)
        save_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def get_data(self):
        return {
            "site": self.site_input.text().strip(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text().strip()
        }

class PasswordManagerWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Менеджер паролей")
        self.resize(700, 600)
        self.setMinimumSize(600, 400)
        self.setStyleSheet("""
            background-color: #0a192f;
            color: #e6f1ff;
            font-family: Arial;
        """)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        title = QLabel("🔐 Менеджер паролей")
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #64ffda;
            margin-bottom: 10px;
        """)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.password_list = QListWidget()
        self.password_list.setStyleSheet("""
            QListWidget {
                background: #172a45;
                border: 1px solid #64ffda;
                border-radius: 5px;
                color: white;
            }
            QListWidget::item {
                border-bottom: 1px solid #1e3a5a;
            }
            QListWidget::item:hover {
                background: #1e3a5a;
            }
        """)
        self.password_list.itemClicked.connect(self.show_password_details)
        layout.addWidget(self.password_list)
        
        self.details_widget = QWidget()
        self.details_widget.setVisible(False)
        details_layout = QVBoxLayout()
        
        # Username
        user_layout = QHBoxLayout()
        user_label = QLabel("👤 Имя пользователя:")
        user_label.setStyleSheet("color: #e6f1ff;")
        self.username_label = QLabel()
        self.username_label.setStyleSheet("color: #e6f1ff; font-weight: bold;")
        
        self.copy_user_btn = QPushButton("📋")
        self.copy_user_btn.setStyleSheet("""
            QPushButton {
                background: #64ffda;
                color: #0a192f;
                padding: 5px;
                border-radius: 3px;
                font-weight: bold;
                min-width: 30px;
            }
            QPushButton:hover { background: #52e3c2; }
        """)
        
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.username_label)
        user_layout.addWidget(self.copy_user_btn)
        
        # Password (исправленная часть)
        pass_layout = QHBoxLayout()
        pass_label = QLabel("🔑 Пароль:")
        pass_label.setStyleSheet("color: #e6f1ff;")
        
        self.password_line = QLineEdit()
        self.password_line.setReadOnly(True)
        self.password_line.setStyleSheet("""
            QLineEdit {
                color: #e6f1ff; 
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        self.password_line.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.show_pass_btn = QPushButton("👁")
        self.show_pass_btn.setStyleSheet("""
            QPushButton {
                background: #1e3a5a;
                color: #e6f1ff;
                padding: 5px;
                border-radius: 3px;
                min-width: 30px;
            }
            QPushButton:hover { background: #2a4a6a; }
        """)
        self.show_pass_btn.setCheckable(True)
        
        self.copy_pass_btn = QPushButton("📋")
        self.copy_pass_btn.setStyleSheet("""
            QPushButton {
                background: #64ffda;
                color: #0a192f;
                padding: 5px;
                border-radius: 3px;
                font-weight: bold;
                min-width: 30px;
            }
            QPushButton:hover { background: #52e3c2; }
        """)
        
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.password_line)
        pass_layout.addWidget(self.show_pass_btn)
        pass_layout.addWidget(self.copy_pass_btn)
        
        # Кнопки действий
        btn_layout = QHBoxLayout()
        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background: #1e3a5a;
                color: #e6f1ff;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover { background: #2a4a6a; }
        """)
        
        self.delete_btn = QPushButton("🗑️ Удалить")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: #ff5555;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover { background: #ff3333; }
        """)
        
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        
        details_layout.addLayout(user_layout)
        details_layout.addLayout(pass_layout)
        details_layout.addLayout(btn_layout)
        self.details_widget.setLayout(details_layout)
        layout.addWidget(self.details_widget)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Добавить пароль")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: #64ffda;
                color: #0a192f;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background: #52e3c2; }
        """)
        self.add_btn.clicked.connect(self.add_password)
        
        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background: #1e3a5a;
                color: #e6f1ff;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background: #2a4a6a; }
        """)
        self.refresh_btn.clicked.connect(self.load_passwords)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.refresh_btn)
        layout.addLayout(btn_layout)
        
        self.central_widget.setLayout(layout)
        
        # Текущий выбранный пароль
        self.current_password = None
        
        # Подключаем сигналы
        self.show_pass_btn.toggled.connect(self.toggle_password_visibility)
        self.copy_user_btn.clicked.connect(self.copy_username)
        self.copy_pass_btn.clicked.connect(self.copy_password)
        self.edit_btn.clicked.connect(self.edit_password)
        self.delete_btn.clicked.connect(self.delete_current_password)
        
        self.load_passwords()
    
    def load_passwords(self):
        self.password_list.clear()
        self.details_widget.setVisible(False)
        passwords = self.get_stored_passwords()
        self.password_list.setStyleSheet("""
            QListWidget {
                background: #172a45;
                border: 1px solid #64ffda;
                border-radius: 5px;
                color: white;
                font-size: 16px; 
            }
            QListWidget::item {
                border-bottom: 1px solid #1e3a5a;
                padding: 5px;  
            }
            QListWidget::item:hover {
                background: #1e3a5a;
            }

        """)
        
        if not passwords:
            item = QListWidgetItem("Нет сохранённых паролей")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.password_list.addItem(item)
            return
        
        for pwd in passwords:
            item = QListWidgetItem(f"🌐 {pwd['site']}")
            item.setData(Qt.ItemDataRole.UserRole, pwd)
            self.password_list.addItem(item)
    
    def show_password_details(self, item):
        if not item.data(Qt.ItemDataRole.UserRole):
            return
            
        self.current_password = item.data(Qt.ItemDataRole.UserRole)
        self.username_label.setText(self.current_password["username"])
        self.password_line.setText(self.current_password["password"])
        self.show_pass_btn.setChecked(False)
        self.password_line.setEchoMode(QLineEdit.EchoMode.Password)
        self.details_widget.setVisible(True)
    
    def toggle_password_visibility(self, checked):
        if checked:
            self.password_line.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_line.setEchoMode(QLineEdit.EchoMode.Password)
    
    def copy_username(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.username_label.text())
        self.show_notification("Имя пользователя скопировано")
    
    def copy_password(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.password_line.text())
        self.show_notification("Пароль скопирован")
    
    def show_notification(self, message):
        msg = QMessageBox(self)
        msg.setWindowTitle("Уведомление")
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #0a192f;
                color: #e6f1ff;
            }
            QLabel { color: #e6f1ff; }
        """)
        msg.show()
        QTimer.singleShot(1000, msg.close)
    
    def add_password(self):
        dialog = PasswordDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not all(data.values()):
                QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
                return
            
            passwords = self.get_stored_passwords()
            passwords.append(data)
            self.save_passwords(passwords)
            self.load_passwords()
    
    def edit_password(self):
        if not self.current_password:
            return
            
        dialog = PasswordDialog(
            self, 
            self.current_password["site"], 
            self.current_password["username"], 
            self.current_password["password"],
            True
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            if not all(new_data.values()):
                QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
                return
            
            passwords = self.get_stored_passwords()
            for i, pwd in enumerate(passwords):
                if (pwd["site"] == self.current_password["site"] and 
                    pwd["username"] == self.current_password["username"] and 
                    pwd["password"] == self.current_password["password"]):
                    passwords[i] = new_data
                    break
            
            self.save_passwords(passwords)
            self.load_passwords()
    
    def delete_current_password(self):
        if not self.current_password:
            return
            
        reply = QMessageBox.question(
            self, "Подтверждение", 
            f"Удалить пароль для {self.current_password['site']}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            passwords = self.get_stored_passwords()
            passwords = [p for p in passwords if not (
                p["site"] == self.current_password["site"] and 
                p["username"] == self.current_password["username"] and 
                p["password"] == self.current_password["password"]
            )]
            
            self.save_passwords(passwords)
            self.load_passwords()
    
    def get_stored_passwords(self):
        os.makedirs("user_data", exist_ok=True)
        if not os.path.exists("user_data/passwords.json"):
            return []
        
        try:
            with open("user_data/passwords.json", "r") as f:
                return json.load(f)
        except:
            return []
    
    def save_passwords(self, passwords):
        os.makedirs("user_data", exist_ok=True)
        with open("user_data/passwords.json", "w") as f:
            json.dump(passwords, f, indent=4)

class PremiumWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Премиум")
        self.resize(600, 400)
        self.setMinimumSize(500, 350)
        self.setStyleSheet("""
            background-color: #0a192f;
            color: #e6f1ff;
            font-family: Arial;
        """)
        
        self.PREMIUM_KEYS = [
            "AGLR71@!91vsUW", "9KLM#22@FFA1XZ", "PQ92$%AA11BB33", 
            "ZX45&*CC99DD88", "261189HGHJliq7", "5817JFJQOL<T34", 
            "DUYIK)!$$!5217", "JHQKjg76347437", "u3e812JGKLGFXH", 
            "7126484kajsh!@"
        ]
        
        self.premium_key = self.load_premium_key()
        if not self.premium_key:
            self.show_activation_screen()
        else:
            self.show_premium_features()

    def load_premium_key(self):
        os.makedirs("user_data", exist_ok=True)
        if not os.path.exists("user_data/premium.txt"):
            return None
        
        with open("user_data/premium.txt", "r") as f:
            key = f.read().strip()
        
        return key if key in self.PREMIUM_KEYS else None
    
    def apply_proxy(self):
        location = self.proxy_combo.currentText()
        self.proxy_manager.set_proxy(location)
        QMessageBox.information(self, "GB-ProxyMaster:", f"Прокси: {location} успешно изменен!")

    def show_activation_screen(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)    
        
        layout = QVBoxLayout()
        
        title = QLabel("Активируй спец. функции!")
        button = QPushButton("Как получить ключ?")
        button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://govno-browser.netlify.app/#premium")))
        button.setStyleSheet("""
            QPushButton {
                background: gold;
                color: black;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                min-width: 200px;
                max-width: 200px;   
            }
            QPushButton:hover {
                background: #FFD700;
            }
        """)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #64ffda;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Введите ключ...")
        self.key_input.setStyleSheet("""
            padding: 10px;
            border: 2px solid #64ffda;
            border-radius: 5px;
            background: #172a45;
            color: white;
        """)
        layout.addWidget(self.key_input)
        
        activate_btn = QPushButton("Активировать")
        activate_btn.setStyleSheet("""
            QPushButton {
                background: #64ffda;
                color: #0a192f;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background: #52e3c2; }
        """)
        activate_btn.clicked.connect(self.activate_premium)
        layout.addWidget(activate_btn)
        
        self.central_widget.setLayout(layout)

    def activate_premium(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Ошибка", "Введи ключ!")
            return
        
        if key not in self.PREMIUM_KEYS:
            QMessageBox.warning(self, "Ошибка", "Неверный ключ!")
            return
        
        os.makedirs("user_data", exist_ok=True)
        with open("user_data/premium.txt", "w") as f:
            f.write(key)
        
        self.fade_out_animation()
        QTimer.singleShot(1000, self.show_premium_features)

    def fade_out_animation(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()

    # def show_premium_features(self):
    #     self.setWindowOpacity(1)
    #     self.central_widget = QWidget()
    #     self.setCentralWidget(self.central_widget)
        
    #     layout = QVBoxLayout()
        
    #     title = QLabel("Специальные функции")
    #     title.setStyleSheet("font-size: 24px; font-weight: bold; color: #64ffda; padding-bottom: 40px;")
    #     layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
    #     snake_btn = QPushButton("Играть в змейку")
    #     snake_btn.setStyleSheet("""
    #         QPushButton {
    #             background: #64ffda;
    #             color: #0a192f;
    #             padding: 10px;
    #             border-radius: 5px;
    #             font-size: 16px;
    #             font-weight: bold;
    #         }
    #         QPushButton:hover { background: #52e3c2; }
    #     """)
    #     snake_btn.clicked.connect(self.start_snake_game)
    #     layout.addWidget(snake_btn)
        
    #     title2 = QLabel("Прокси")
    #     title2.setStyleSheet("font-size: 24px; font-weight: bold; color: white; padding: 10px")
    #     layout.addWidget(title2, alignment=Qt.AlignmentFlag.AlignCenter)

    #     proxy_label = QLabel("Выберите прокси:")
    #     proxy_label.setStyleSheet("color: #e6f1ff; font-size: 14px; margin-top: 10px;")
    #     layout.addWidget(proxy_label)

    #     self.proxy_combo = QComboBox()
    #     self.proxy_combo.addItems(["Без прокси", "США", "Германия", "Япония"])
    #     self.proxy_combo.setStyleSheet("""
    #         QComboBox {
    #             background: #172a45;
    #             color: white;
    #             padding: 8px;
    #             border: 1px solid #64ffda;
    #             border-radius: 5px;
    #         }
    #     """)

    #     proxy_btn = QPushButton("Активировать прокси")
    #     proxy_btn.setStyleSheet("""
    #         QPushButton {
    #             background: #64ffda;
    #             color: #0a192f;
    #             padding: 10px;
    #             border-radius: 5px;
    #             font-weight: bold;
    #             margin-top: 5px;
    #         }
    #         QPushButton:hover { background: #52e3c2; }
    #     """)
    #     proxy_btn.clicked.connect(self.apply_proxy)
    #     layout.addWidget(self.proxy_combo)
    #     layout.addWidget(proxy_btn)
        
    #     title3 = QLabel("Пароли")
    #     title3.setStyleSheet("font-size: 24px; font-weight: bold; color: white; padding: 10px; margin-top: 20px;")
    #     layout.addWidget(title3, alignment=Qt.AlignmentFlag.AlignCenter)
        
    #     passwords_btn = QPushButton("Управление паролями")
    #     passwords_btn.setStyleSheet("""
    #         QPushButton {
    #             background: #64ffda;
    #             color: #0a192f;
    #             padding: 10px;
    #             border-radius: 5px;
    #             font-weight: bold;
    #             margin-top: 5px;
    #         }
    #         QPushButton:hover { background: #52e3c2; }
    #     """)
    #     passwords_btn.clicked.connect(self.open_password_manager)
    #     layout.addWidget(passwords_btn)
        
    #     layout.addStretch()
    #     self.central_widget.setLayout(layout)
    #     self.proxy_manager = ProxyManager()
    
    def open_password_manager(self):
        self.password_window = PasswordManagerWindow(self)
        self.password_window.show()
    
    def start_snake_game(self):
        self.snake_game = SnakeGame()
        self.snake_game.show()

# ==================== ОСНОВНЫЕ КЛАССЫ БРАУЗЕРА ====================

class WebPage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createWindow(self, _type):
        return self.parent().window().create_new_tab()

class BrowserTab(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPage(WebPage(self))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.window().tab_widget.removeTab(self.window().tab_widget.indexOf(self))
        super().mousePressEvent(event)

class ModernTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setExpanding(False)
        self.setElideMode(Qt.TextElideMode.ElideRight)

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Govno Browser")
        self.resize(1200, 800)
        self.start_page = QUrl("https://gb-start.netlify.app")

        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent("GovnoBrovser/1.0")

        self.create_toolbar()
        self.setup_tabs()
        self.set_dark_theme()

    def set_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QToolBar { background-color: #252525; border: none; padding: 4px; spacing: 5px; }
            QPushButton {
                background-color: #3a3a3a; color: white; border: none; padding: 5px;
                border-radius: 4px; min-width: 28px; min-height: 28px;
            }
            QPushButton:hover { background-color: #4a4a4a; }
            QPushButton:pressed { background-color: #2a2a2a; }
            QLineEdit {
                background-color: #3a3a3a; color: white; border: 1px solid #444;
                border-radius: 14px; padding: 5px 15px; margin: 0 5px; min-height: 28px;
            }
            QTabBar { background-color: #252525; border: none; }
            QTabBar::tab {
                background-color: #2d2d2d; color""")

class WebPage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createWindow(self, _type):
        return self.parent().window().create_new_tab()

class BrowserTab(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPage(WebPage(self))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.window().tab_widget.removeTab(self.window().tab_widget.indexOf(self))
        super().mousePressEvent(event)

class ModernTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setExpanding(False)
        self.setElideMode(Qt.TextElideMode.ElideRight)

class PremiumWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GovnoBrowser | Меня спец. функций")
        self.resize(700, 500)
        self.setStyleSheet("""
            background-color: #0a192f;
            color: #e6f1ff;
            font-family: Arial;
        """)
        
        self.PREMIUM_KEYS = [
            "AGLR71@!91vsUW", #1
            "9KLM#22@FFA1XZ", #2
            "PQ92$%AA11BB33", #3
            "ZX45&*CC99DD88", #4
            "261189HGHJliq7", #5
            "5817JFJQOL<T34", #6
            "DUYIK)!$$!5217", #7
            "JHQKjg76347437", #8
            "u3e812JGKLGFXH", #9
            "7126484kajsh!@"  #10
        ]
        
        self.premium_key = self.load_premium_key()
        if not self.premium_key:
            self.show_activation_screen()
        else:
            self.show_premium_features()

    def load_premium_key(self):
        os.makedirs("user_data", exist_ok=True)
        if not os.path.exists("user_data/premium.txt"):
            return None
        
        with open("user_data/premium.txt", "r") as f:
            key = f.read().strip()
        
        return key if key in self.PREMIUM_KEYS else None
    
    def apply_proxy(self):
        location = self.proxy_combo.currentText()
        self.proxy_manager.set_proxy(location)
        QMessageBox.information(self, "GB-ProxyMaster:", f"Прокси: {location} успешно изменен!")

    def show_activation_screen(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)    
        
        layout = QVBoxLayout()
        
        title = QLabel("Активируй спец. функции!")
        button = QPushButton("Как получить ключ?")
        button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://govno-browser.netlify.app/#premium")))
        button.setStyleSheet("""
            QPushButton {
                background: gold;
                color: black;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                min-width: 200px;
                max-width: 200px;   
            }
            QPushButton:hover {
                background: #FFD700;
            }
        """)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #64ffda;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Введите ключ...")
        self.key_input.setStyleSheet("""
            padding: 10px;
            border: 2px solid #64ffda;
            border-radius: 5px;
            background: #172a45;
            color: white;
        """)
        layout.addWidget(self.key_input)
        
        activate_btn = QPushButton("Активировать")
        activate_btn.setStyleSheet("""
            QPushButton {
                background: #64ffda;
                color: #0a192f;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background: #52e3c2; }
        """)
        activate_btn.clicked.connect(self.activate_premium)
        layout.addWidget(activate_btn)
        
        self.central_widget.setLayout(layout)

    def activate_premium(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Ошибка", "Введи ключ!")
            return
        
        if key not in self.PREMIUM_KEYS:
            QMessageBox.warning(self, "Ошибка", "Неверный ключ!")
            return
        
        os.makedirs("user_data", exist_ok=True)
        with open("user_data/premium.txt", "w") as f:
            f.write(key)
        
        self.fade_out_animation()
        QTimer.singleShot(1000, self.show_premium_features)

    def fade_out_animation(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()

    def show_premium_features(self):
        self.setWindowOpacity(1)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        layout = QVBoxLayout()
        
        title = QLabel("🔥 Специальные функции")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #7161b8; padding-bottom: 40px;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Кнопка змейки
        snake_btn = QPushButton("Играть в змейку")
        snake_btn.setStyleSheet("""
            QPushButton {
                background: #1c4d9d;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background: #1a3c5e; }
        """)
        snake_btn.clicked.connect(self.start_snake_game)
        layout.addWidget(snake_btn)
        
        # Раздел прокси
        title2 = QLabel("Прокси")
        title2.setStyleSheet("font-size: 24px; font-weight: bold; color: white; padding: 10px")
        layout.addWidget(title2, alignment=Qt.AlignmentFlag.AlignCenter)

        proxy_label = QLabel("Выберите прокси:")
        proxy_label.setStyleSheet("color: #e6f1ff; font-size: 14px; margin-top: 10px;")
        layout.addWidget(proxy_label)

        self.proxy_combo = QComboBox()
        self.proxy_combo.addItems(["Без прокси", "США", "Германия", "Япония"])
        self.proxy_combo.setStyleSheet("""
            QComboBox {
                background: #172a45;
                color: white;
                padding: 8px;
                border: 1px solid #64ffda;
                border-radius: 5px;
            }
        """)

        proxy_btn = QPushButton("Активировать прокси")
        proxy_btn.setStyleSheet("""
            QPushButton {
                background: #1c4d9d;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover { background: #1a3c5e; }
        """)
        proxy_btn.clicked.connect(self.apply_proxy)
        layout.addWidget(self.proxy_combo)
        layout.addWidget(proxy_btn)
        
        # Раздел паролей
        title3 = QLabel("Пароли")
        title3.setStyleSheet("font-size: 24px; font-weight: bold; color: white; padding: 10px; margin-top: 20px;")
        layout.addWidget(title3, alignment=Qt.AlignmentFlag.AlignCenter)
        
        passwords_btn = QPushButton("Управление паролями")
        passwords_btn.setStyleSheet("""
            QPushButton {
                background: #1c4d9d;
                color: white;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover { background: #1a3c5e; }
        """)
        passwords_btn.clicked.connect(self.open_password_manager)
        layout.addWidget(passwords_btn)
        
        layout.addStretch()
        self.central_widget.setLayout(layout)
        self.proxy_manager = ProxyManager()
    
    def open_password_manager(self):
        self.password_window = PasswordManagerWindow(self)
        self.password_window.show()
    
    def start_snake_game(self):
        self.snake_game = SnakeGame()
        self.snake_game.show()

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Govno Browser")
        self.resize(1200, 800)
        self.start_page = QUrl("https://gb-start.netlify.app")

        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent("GovnoBrovser/1.0")

        self.create_toolbar()
        self.setup_tabs()
        self.set_dark_theme()

    def set_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QToolBar { background-color: #252525; border: none; padding: 4px; spacing: 5px; }
            QPushButton {
                background-color: #3a3a3a; color: white; border: none; padding: 5px;
                border-radius: 4px; min-width: 28px; min-height: 28px;
            }
            QPushButton:hover { background-color: #4a4a4a; }
            QPushButton:pressed { background-color: #2a2a2a; }
            QLineEdit {
                background-color: #3a3a3a; color: white; border: 1px solid #444;
                border-radius: 14px; padding: 5px 15px; margin: 0 5px; min-height: 28px;
            }
            QTabBar { background-color: #252525; border: none; }
            QTabBar::tab {
                background-color: #2d2d2d; color: #bbbbbb; padding: 8px 15px;
                border-top-left-radius: 4px; border-top-right-radius: 4px;
                border: 1px solid #444; margin-right: 2px;
            }
            QTabBar::tab:selected { background-color: #1e1e1e; color: white; border-bottom-color: #1e1e1e; }
            QTabBar::tab:hover { background-color: #3a3a3a; }
            QTabWidget::pane { border: none; background: #1e1e1e; }
        """)

    def create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        back_btn = QPushButton("⬅️")
        # back_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack))
        back_btn.clicked.connect(lambda: self.current_browser().back())

        forward_btn = QPushButton("➡️")
        # forward_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward))
        forward_btn.clicked.connect(lambda: self.current_browser().forward())

        reload_btn = QPushButton("🔄")
        # reload_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        reload_btn.clicked.connect(lambda: self.current_browser().reload())

        home_btn = QPushButton("🏠 Домой")
        home_btn.clicked.connect(self.navigate_home)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Введите URL или поисковый запрос...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        premium_btn = QPushButton("💎 Специальные функции")
        premium_btn.setStyleSheet("""
            QPushButton {
                padding: 5px;
                color: white;
                background: transparent;
                border: none;
            }
            QPushButton:hover { color: #64ffda; }
        """)
        premium_btn.clicked.connect(self.open_premium)
        
        toolbar.addWidget(back_btn)
        toolbar.addWidget(forward_btn)
        toolbar.addWidget(reload_btn)
        toolbar.addWidget(home_btn)
        toolbar.addWidget(self.url_bar)

        new_tab_btn = QPushButton("+")
        new_tab_btn.setFixedWidth(40)
        new_tab_btn.clicked.connect(self.add_new_tab)
        
        toolbar.addWidget(new_tab_btn)
        toolbar.addWidget(premium_btn)

    def setup_tabs(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(ModernTabBar())
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tab_widget)
        self.add_new_tab(self.start_page)

    def current_browser(self):
        return self.tab_widget.currentWidget()

    def create_new_tab(self):
        new_browser = BrowserTab(self)
        new_browser.urlChanged.connect(self.update_urlbar)
        new_browser.loadFinished.connect(self.update_tab_title)
        index = self.tab_widget.addTab(new_browser, "Новая вкладка")
        self.tab_widget.setCurrentIndex(index)
        return new_browser.page()

    def add_new_tab(self, url=None):
        browser = BrowserTab(self)
        browser.urlChanged.connect(self.update_urlbar)
        browser.loadFinished.connect(self.update_tab_title)
        self.tab_widget.addTab(browser, "Новая вкладка")
        self.tab_widget.setCurrentWidget(browser)
        browser.load(url or self.start_page)

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.widget(index).deleteLater()
            self.tab_widget.removeTab(index)

    def update_urlbar(self, url):
        self.url_bar.setText(url.toString())

    def update_tab_title(self):
        browser = self.sender()
        index = self.tab_widget.indexOf(browser)
        title = browser.page().title()
        self.tab_widget.setTabText(index, title[:20] + "..." if len(title) > 20 else title)

    def navigate_to_url(self):
        url_text = self.url_bar.text().strip()
        if not url_text:
            return
        if not url_text.startswith(('http://', 'https://', 'file://')):
            if '.' in url_text:
                url_text = 'http://' + url_text
            else:
                url_text = f'https://www.google.com/search?q={url_text.replace(" ", "+")}'
        self.current_browser().load(QUrl(url_text))

    def navigate_home(self):
        self.current_browser().load(self.start_page)

    def open_premium(self):
        self.premium_window = PremiumWindow()
        self.premium_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec())