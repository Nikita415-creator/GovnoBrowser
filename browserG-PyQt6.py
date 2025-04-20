import sys
import os
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QToolBar, QLineEdit, QPushButton, QTabBar, QStyle
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

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
        profile.setHttpUserAgent("GovnoBrovser/1.0 (PyQt6 Edition)")

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

        home_btn = QPushButton()
        home_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        home_btn.clicked.connect(self.navigate_home)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Введите URL или поисковый запрос...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        new_tab_btn = QPushButton("+")
        new_tab_btn.setFixedWidth(40)
        new_tab_btn.clicked.connect(self.add_new_tab)

        toolbar.addWidget(back_btn)
        toolbar.addWidget(forward_btn)
        toolbar.addWidget(reload_btn)
        toolbar.addWidget(home_btn)
        toolbar.addWidget(self.url_bar)
        toolbar.addWidget(new_tab_btn)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec())