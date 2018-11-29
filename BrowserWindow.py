from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QToolBar, QAction, QLineEdit, QProgressBar, QLabel, QMainWindow, QTabWidget

import About


class BrowserEngineView(QWebEngineView):
    tabs = []

    def __init__(self, Main, parent=None):
        super(BrowserEngineView, self).__init__(parent)
        self.mainWindow = Main

    def createWindow(self, QWebEnginePage_WebWindowType):
        webview = BrowserEngineView(self.mainWindow)
        tab = BrowserTab(self.mainWindow)
        tab.browser = webview
        tab.setCentralWidget(tab.browser)
        # 事件触发
        tab.back_button.triggered.connect(tab.browser.back)
        tab.next_button.triggered.connect(tab.browser.forward)
        tab.stop_button.triggered.connect(tab.browser.stop)
        tab.refresh_button.triggered.connect(tab.browser.reload)
        tab.home_button.triggered.connect(tab.navigate_to_home)
        tab.enter_button.triggered.connect(tab.navigate_to_url)
        tab.set_button.triggered.connect(tab.create_about_window)
        # 触发映射
        tab.url_text_bar.returnPressed.connect(tab.navigate_to_url)
        tab.browser.urlChanged.connect(tab.renew_urlbar)
        tab.browser.loadProgress.connect(tab.renew_progress_bar)
        self.tabs.append(tab)
        self.mainWindow.create_new_tab(tab)
        return webview


class BrowserTab(QMainWindow):
    def __init__(self, Main, parent=None):
        super(BrowserTab, self).__init__(parent)
        self.mainWindow = Main
        self.AboutDialog = About.AboutDialog()
        # 浏览器窗体
        self.browser = BrowserEngineView(self.mainWindow)
        self.browser.load(QUrl("about:blank"))
        self.setCentralWidget(self.browser)
        # 工具条
        self.navigation_bar = QToolBar('Navigation')
        self.navigation_bar.setIconSize(QSize(32, 32))
        self.navigation_bar.setMovable(False)
        self.addToolBar(self.navigation_bar)
        # 后退前进停止刷新按钮
        self.back_button = QAction(QIcon('Assets/back.png'), '后退', self)
        self.next_button = QAction(QIcon('Assets/forward.png'), '前进', self)
        self.stop_button = QAction(QIcon('Assets/stop.png'), '停止', self)
        self.refresh_button = QAction(QIcon('Assets/refresh.png'), '刷新', self)
        # 地址栏
        self.home_button = QAction(QIcon('Assets/home.png'), '主页', self)
        self.enter_button = QAction(QIcon('Assets/enter.png'), '转到', self)
        self.ssl_label1 = QLabel(self)
        self.ssl_label2 = QLabel(self)
        self.url_text_bar = QLineEdit(self)
        self.url_text_bar.setMinimumWidth(300)
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(120)
        # 设置按钮
        self.set_button = QAction(QIcon('Assets/setting.png'), '设置', self)
        # 工具条添加组件
        self.navigation_bar.addAction(self.back_button)
        self.navigation_bar.addAction(self.next_button)
        self.navigation_bar.addAction(self.stop_button)
        self.navigation_bar.addAction(self.refresh_button)
        self.navigation_bar.addAction(self.home_button)
        self.navigation_bar.addSeparator()
        self.navigation_bar.addWidget(self.ssl_label1)
        self.navigation_bar.addWidget(self.ssl_label2)
        self.navigation_bar.addWidget(self.url_text_bar)
        self.navigation_bar.addAction(self.enter_button)
        self.navigation_bar.addSeparator()
        self.navigation_bar.addWidget(self.progress_bar)
        self.navigation_bar.addAction(self.set_button)
        # 事件触发
        self.back_button.triggered.connect(self.browser.back)
        self.next_button.triggered.connect(self.browser.forward)
        self.stop_button.triggered.connect(self.browser.stop)
        self.refresh_button.triggered.connect(self.browser.reload)
        self.home_button.triggered.connect(self.navigate_to_home)
        self.enter_button.triggered.connect(self.navigate_to_url)
        self.set_button.triggered.connect(self.create_about_window)
        # 触发映射
        self.url_text_bar.returnPressed.connect(self.navigate_to_url)
        self.browser.urlChanged.connect(self.renew_urlbar)
        self.browser.loadProgress.connect(self.renew_progress_bar)

    def navigate_to_url(self):
        s = QUrl(self.url_text_bar.text())
        if s.scheme() == '':
            s.setScheme('http')
        self.browser.load(s)

    def navigate_to_home(self):
        s = QUrl("http://www.hao123.com/")
        self.browser.load(s)

    def renew_urlbar(self, s):
        prec = s.scheme()
        if prec == 'http':
            self.ssl_label1.setPixmap(QPixmap("Assets/unsafe.png").scaledToHeight(24))
            self.ssl_label2.setText(" 不安全 ")
            self.ssl_label2.setStyleSheet("color:red;")
        elif prec == 'https':
            self.ssl_label1.setPixmap(QPixmap("Assets/safe.png").scaledToHeight(24))
            self.ssl_label2.setText(" 安全 ")
            self.ssl_label2.setStyleSheet("color:green;")
        self.url_text_bar.setText(s.toString())
        self.url_text_bar.setCursorPosition(0)

    def renew_progress_bar(self, p):
        self.progress_bar.setValue(p)

    def create_about_window(self):
        self.AboutDialog.show()


class BrowserWindow(QMainWindow):
    name = "PyBrowser Powered by Y.Wang"
    version = "2.0.20181128"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 窗体
        self.setWindowTitle(self.name)
        self.setWindowIcon(QIcon('Assets/main.png'))
        self.resize(1200, 800)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.setCentralWidget(self.tabs)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.tabBarDoubleClicked.connect(self.add_blank_tab)
        self.add_blank_tab(0)

    def add_blank_tab(self, p):
        browsertab = BrowserTab(self)
        i = self.tabs.addTab(browsertab, "空白页")
        self.tabs.setCurrentIndex(i)
        browsertab.browser.titleChanged.connect(lambda title: self.tabs.setTabText(i, title))
        browsertab.browser.iconChanged.connect(lambda icon: self.tabs.setTabIcon(i, icon))

    def create_new_tab(self, tab):
        i = self.tabs.addTab(tab, "空白页")
        self.tabs.setCurrentIndex(i)
        tab.browser.titleChanged.connect(lambda title: self.tabs.setTabText(i, title))
        tab.browser.iconChanged.connect(lambda icon: self.tabs.setTabIcon(i, icon))

    def close_current_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)
        else:
            self.close()