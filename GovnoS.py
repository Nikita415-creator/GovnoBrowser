import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolBar, QAction, 
                             QLineEdit, QTabWidget, QStyleFactory)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon

class CustomWebEngineView(QWebEngineView):
    def createWindow(self, _type):
        # Открываем любые новые окна в текущем представлении
        return self

class GovnoSBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GovnoS Browser")
        self.setGeometry(100, 100, 1200, 800)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QToolBar {
                background-color: #353535;
                border: none;
                padding: 4px;
                spacing: 5px;
            }
            QToolButton {
                background-color: #454545;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                min-width: 30px;
            }
            QToolButton:hover {
                background-color: #5a5a5a;
            }
            QToolButton:pressed {
                background-color: #3a3a3a;
            }
            QLineEdit {
                background-color: #454545;
                color: white;
                border: 1px solid #555;
                padding: 5px 10px;
                border-radius: 15px;
                font-family: Arial;
                selection-background-color: #5a5a5a;
            }
            QTabWidget::pane {
                border: none;
                background: #2b2b2b;
            }
            QTabBar {
                background: #353535;
                border: none;
            }
            QTabBar::tab {
                background: #454545;
                color: white;
                padding: 8px 15px;
                border: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #2b2b2b;
                border-bottom: 2px solid #5a5a5a;
            }
            QTabBar::tab:hover {
                background: #5a5a5a;
            }
        """)

        # Вкладки
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(True)
        self.setCentralWidget(self.tabs)

        # Добавляем первую вкладку
        self.add_new_tab(self.get_home_url(), "Новая вкладка")

        # Панель инструментов
        nav_bar = QToolBar()
        nav_bar.setMovable(False)
        self.addToolBar(nav_bar)

        # Кнопки
        back_btn = QAction("Назад ←", self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        nav_bar.addAction(back_btn)

        forward_btn = QAction("Вперед →", self)
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        nav_bar.addAction(forward_btn)

        reload_btn = QAction("Обновить ⟳", self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        nav_bar.addAction(reload_btn)

        home_btn = QAction("Домой ⌂", self)
        home_btn.triggered.connect(self.go_home)
        nav_bar.addAction(home_btn)

        # Поле URL
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_bar.addWidget(self.url_bar)

        # Кнопка новой вкладки
        new_tab_btn = QAction("+", self)
        new_tab_btn.triggered.connect(lambda: self.add_new_tab(self.get_home_url(), "Новая вкладка"))
        nav_bar.addAction(new_tab_btn)

        # Обновление URL при переключении вкладок
        self.tabs.currentChanged.connect(self.update_current_tab)

    def get_home_url(self):
        start_page = os.path.abspath("start.html")
        return QUrl.fromLocalFile(start_page) if os.path.exists(start_page) else QUrl("https://yandex.ru")

    def add_new_tab(self, url, title="Новая вкладка"):
        """Добавляет новую вкладку"""
        browser = CustomWebEngineView()
        browser.setUrl(url)
        browser.urlChanged.connect(self.update_url)
        self.tabs.addTab(browser, title)
        self.tabs.setCurrentWidget(browser)

    def close_tab(self, index):
        """Закрывает вкладку"""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def update_current_tab(self):
        """Обновляет URL при переключении вкладок"""
        if self.tabs.currentWidget():
            self.url_bar.setText(self.tabs.currentWidget().url().toString())

    def navigate_to_url(self):
        """Переход по URL"""
        url = self.url_bar.text().strip()
        if not url:
            return

        if "." not in url and " " in url:
            url = f"https://yandex.ru/search/?text={url.replace(' ', '+')}"
        elif not url.startswith(("http://", "https://")):
            url = "https://" + url

        self.tabs.currentWidget().setUrl(QUrl(url))

    def update_url(self, q):
        """Обновляет URL в строке"""
        self.url_bar.setText(q.toString())

    def go_home(self):
        """Переход на домашнюю страницу"""
        self.tabs.currentWidget().setUrl(self.get_home_url())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    window = GovnoSBrowser()
    window.show()
    sys.exit(app.exec_())