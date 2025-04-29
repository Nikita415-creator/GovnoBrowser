import sys
import os
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QToolBar, QLineEdit, QPushButton, QTabBar, QStyle
)

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

from PyQt6.QtCore import Qt, QTimer, QRectF, QPropertyAnimation
from PyQt6.QtGui import QPainter, QBrush, QPen, QColor, QDesktopServices
from PyQt6.QtWidgets import QWidget, QMessageBox, QLabel, QPushButton, QVBoxLayout, QComboBox
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
        self.setWindowTitle("Премиум | Змейка.app")
        self.setFixedSize(420, 420)
        self.setStyleSheet("background-color: #0a192f;")
        
        # Настройки игры
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
        """Инициализация начального состояния игры"""
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
        """Создание новой еды в случайном месте"""
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
        """Перемещение змейки"""
        head = self.snake[0]
        new_head = QRectF(head)
        
        # Определение направления движения
        if self.direction == Qt.Key.Key_Left:
            new_head.moveLeft(head.left() - self.cell_size)
        elif self.direction == Qt.Key.Key_Right:
            new_head.moveLeft(head.left() + self.cell_size)
        elif self.direction == Qt.Key.Key_Up:
            new_head.moveTop(head.top() - self.cell_size)
        elif self.direction == Qt.Key.Key_Down:
            new_head.moveTop(head.top() + self.cell_size)
        
        # Проверка столкновений (исправленная строка)
        if (new_head.left() < 0 or 
            new_head.right() > self.width() or
            new_head.top() < 0 or 
            new_head.bottom() > self.height() or
            any(new_head.intersects(segment) for segment in self.snake[:-1])):
            self.game_over()
            return
        
        self.snake.insert(0, new_head)
        
        # Проверка съедения еды
        if new_head.intersects(self.food):
            self.score += 1
            self.spawn_food()
        else:
            self.snake.pop()
        
        self.update()
    
    def game_over(self):
        """Обработка завершения игры"""
        self.timer.stop()
        QMessageBox.information(self, "Game Over", f"Счёт: {self.score}")
        self.close()
    
    def paintEvent(self, event):
        """Отрисовка игровых объектов"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Рисуем змейку
        painter.setBrush(QBrush(QColor(100, 255, 100)))
        for segment in self.snake:
            painter.drawRect(segment)
        
        # Рисуем еду
        painter.setBrush(QBrush(QColor(255, 100, 100)))
        painter.drawRect(self.food)
        
        # Рисуем счёт
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(10, 20, f"Счёт: {self.score}")
    
    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        key = event.key()
        if (key == Qt.Key.Key_Left and self.direction != Qt.Key.Key_Right or
            key == Qt.Key.Key_Right and self.direction != Qt.Key.Key_Left or
            key == Qt.Key.Key_Up and self.direction != Qt.Key.Key_Down or
            key == Qt.Key.Key_Down and self.direction != Qt.Key.Key_Up):
            self.direction = key

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
        self.setWindowTitle("GovnoBrowser Премиум")
        self.setFixedSize(600, 400)
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

        
        title = QLabel("Активируй премиум!")
        button = QPushButton("Как получить ключ?")
        button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://govno-browser.netlify.app/#premium")))
        button.setStyleSheet("""
            QPushButton {
            background: gold;
            color: black;
            font-weight: bold;
            padding: 10px;
            border-radius: 5px;
            min-width: 200px;  /* Минимальная ширина */
            max-width: 200px;   
        }
            QPushButton:hover {
            background: #FFD700;
        }
        """)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #64ffda;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        # h_layout = QHBoxLayout()
        # h_layout.addStretch()  # Растягивающийся пустой элемент слева
        # h_layout.addWidget(button)  # Кнопка (ширина 200px)
        # h_layout.addStretch()
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
        
        title = QLabel("🔥 Премиум активирован!")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #64ffda; padding-bottom: 40px;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        # змея играть
        snake_btn = QPushButton("Играть в змейку")
        snake_btn.setStyleSheet("""
            QPushButton {
                background: #64ffda;
                color: #0a192f;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background: #52e3c2; }
        """)
        snake_btn.clicked.connect(self.start_snake_game)
        layout.addWidget(snake_btn)
        
        # прокси
        title2 = QLabel("Прокси")
        title2.setStyleSheet("font-size: 24px; font-weight: bold; color: white; padding: 10px")
        layout.addWidget(title2, alignment=Qt.AlignmentFlag.AlignCenter)


        proxy_label = QLabel("Выберите прокси:")
        proxy_label.setStyleSheet("color: #e6f1ff; font-size: 14px; morgin-top: 10px;")
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

        proxy_btn = QPushButton("Активировать")
        proxy_btn.setStyleSheet("""
            QPushButton {
                background: #64ffda;
                color: #0a192f;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 5px;
        }
            QPushButton:hover { background: #52e3c2; }
        """)

        proxy_btn.clicked.connect(self.apply_proxy) #----------------------

        layout.addWidget(self.proxy_combo)
        layout.addWidget(proxy_btn)
        layout.addStretch()
        
        
        self.central_widget.setLayout(layout)
        self.proxy_manager = ProxyManager()

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

        back_btn = QPushButton()
        back_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowBack))
        back_btn.clicked.connect(lambda: self.current_browser().back())

        forward_btn = QPushButton()
        forward_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowForward))
        forward_btn.clicked.connect(lambda: self.current_browser().forward())

        reload_btn = QPushButton()
        reload_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        reload_btn.clicked.connect(lambda: self.current_browser().reload())

        home_btn = QPushButton("Домой")
        # home_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        home_btn.clicked.connect(self.navigate_home)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Введите URL или поисковый запрос...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        premium_btn = QPushButton("🌟 Премиум")
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