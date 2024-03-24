
# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import sys
import subprocess
from threading import Thread
import json
import os
from flask import Flask, redirect
import requests
from pkl import porcelain as git
from pkl.errors import HangupException
from PyQt5.QtGui import QIcon
import psutil


running_pages =['']
calls = []

def kill(proc_pid):
    parent_proc = psutil.Process(proc_pid)
    for child_proc in parent_proc.children(recursive=True):
        child_proc.kill()
    parent_proc.kill()
def call_noconsole(cmd):
    global calls
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    noconsole_call = subprocess.Popen(cmd, startupinfo=si)
    calls.append(noconsole_call.pid)
def initial():

    app = Flask(__name__)

    @app.route('/')
    def wrong():
        return 'Sorry, but the port 80 is already used.'

    @app.route('/<url>/<ident>/<redirection>')
    def hello2(url, ident, redirection):
        server = 'gitcode.net'
        try:
            domain = ident + '/' + url
            print(running_pages)
            for x in running_pages:
                if x == url.split('/')[0]:
                    running = True
                    break
                else:
                    running = False
            if running:
                return redirect('http://localhost:' + str(
                    json.load(open(os.path.join(os.path.join('browser_cache', domain), 'config.json')))[
                        'port']) + redirection.replace('@', '/'))
            else:
                print(os.path.exists(os.path.join('browser_cache', domain)))
                if not os.path.exists(os.path.join('browser_cache', domain)):
                    clone_url = 'git@' + server + ':' + domain + '.git'
                    git.clone(clone_url, os.path.join('browser_cache',domain))
                cmd = json.load(open(os.path.join(os.path.join('browser_cache', domain), 'config.json')))['start_command']
                path = os.path.join('browser_cache', domain)
                call_noconsole('powershell -Command cd ' + path + ';' + cmd)

                running_pages.append(url.split('/')[0])

                while True:
                    try:
                        requests.get('http://localhost:' + str(
                            json.load(open(os.path.join('browser_cache', domain) + '/config.json'))['port']))
                    except:
                        continue
                    break
                return redirect('http://localhost:' + str(
                    json.load(open(os.path.join(os.path.join('browser_cache', domain), 'config.json')))[
                        'port']) + '/' + redirection.replace('@', '/'))
        except HangupException:
                return f"""<!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>{ident}:{url}.gdpn{redirection.replace('@','/')}</title>
                    </head>
                    <body>
                    <h1>OOPS</h1> <h3> Something went wrong </h3> <p> Be sure you entered the correct GDP link in the address bar, check your network connection, and retry </p>
                    </body>
                    </html>"""
    app.run(host='127.0.0.1', port=8765)


class MainWindow(QMainWindow):

    # constructor
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # creating a tab widget
        self.tabs = QTabWidget()

        # making document mode true
        self.tabs.setDocumentMode(True)

        # adding action when double clicked
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)

        # adding action when tab is changed
        self.tabs.currentChanged.connect(self.current_tab_changed)

        # making tabs closeable
        self.tabs.setTabsClosable(True)

        # adding action when tab close is requested
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        # making tabs as central widget
        self.setCentralWidget(self.tabs)

        # creating a status bar
        self.status = QStatusBar()

        # setting status bar to the main window
        self.setStatusBar(self.status)

        # creating a tool bar for navigation
        navtb = QToolBar("Navigation")

        # adding tool bar tot he main window
        self.addToolBar(navtb)

        # creating back action
        back_btn = QAction("Back", self)

        # setting status tip
        back_btn.setStatusTip("Back to previous page")

        # adding action to back button
        # making current tab to go back
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())

        # adding this to the navigation tool bar
        navtb.addAction(back_btn)

        # similarly adding next button
        next_btn = QAction("Forward", self)
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navtb.addAction(next_btn)

        # similarly adding reload button
        reload_btn = QAction("Reload", self)
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navtb.addAction(reload_btn)

        # creating home action
        # adding action to home button

        # adding a separator
        navtb.addSeparator()

        # creating a line edit widget for URL
        self.urlbar = QLineEdit()

        # adding action to line edit when return key is pressed
        self.urlbar.returnPressed.connect(self.navigate_to_url)

        # adding line edit to tool bar
        navtb.addWidget(self.urlbar)

        # similarly adding stop action
        stop_btn = QAction("Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navtb.addAction(stop_btn)

        # creating first tab
        self.add_new_tab(QUrl('http://www.bing.com/'), 'Homepage')

        # showing all the components
        self.show()

        # setting window title
        self.setWindowTitle("GDP Browser")

    # method for adding new tab
    def add_new_tab(self, qurl=None, label="Blank"):

        # if url is blank
        if qurl is None:
            # creating a google url
            qurl = QUrl('http://www.bing.com/')

        # creating a QWebEngineView object
        browser = QWebEngineView()

        # setting url to browser
        browser.setUrl(qurl)

        # setting tab index
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        # adding action to the browser when url is changed
        # update the url
        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))

        # adding action to the browser when loading is finished
        # set the tab title
        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tabs.setTabText(i, browser.page().title()))

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        url = self.urlbar.text()
        print(qurl.toString())
        print(url)
        if url.startswith('<'):
            self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return None
        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return None
        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle('% s - GDP Browser' % title)

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        url = self.urlbar.text()
        if url.split('/')[0].endswith('.gdpn'):
            server = 'github.com'
            domain = url.split(':')[1].split('/')[0].replace('.gdpn','')
            if '/' in url:
                url_re = 'http://127.0.0.1:8765/' + domain + '/' + url.split(':')[0] + '/' + url.split(':')[1].replace(domain+'.gdpn', '').replace('/', '@')
            else:
                url_re = 'http://127.0.0.1:8765/' + domain + '/' + url.split(':')[0] + '/@'

            self.tabs.currentWidget().setUrl(QUrl(url_re))
        else:
            if q.scheme() == '':
                    q.setScheme('http')

            self.tabs.currentWidget().setUrl(q)

    def update_urlbar(self, q, browser=(None,)):
        if browser != self.tabs.currentWidget():
            return None
        url = self.urlbar.text()
        if url.split('/')[0].endswith('.gdpn'):
            domain = url.split(':')[0].replace('<', '') + '/' + url.split(':')[1].split('/')[0].replace('.gdpn','')
            if url.split(':')[1].split('/')[0].replace('.gdpn', '') in running_pages and q.toString().startswith('http://localhost:' + str(
                    json.load(open(os.path.join(os.path.join('browser_cache', domain), 'config.json')))['port'])):

                self.urlbar.setText(
                    f"{url.split(':')[0]}:{url.split(':')[1].split('/')[0]}"+ q.toString().replace(
                        'http://localhost:' + str(
                            json.load(open(os.path.join(os.path.join('browser_cache', domain), 'config.json')))[
                                'port']), ''))

        else:
            self.urlbar.setText(q.toString())

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('GDP Browser')
    app_icon = QIcon('icons/icon1.png')
    app.setWindowIcon(app_icon)
    window = MainWindow()
    Thread(target=initial, daemon=True, ).start()
    app.exec_()
    for x in calls:
        kill(x)
