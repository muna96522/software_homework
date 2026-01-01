#!/usr/bin/env python
"""
启动 Django 开发服务器并自动打开浏览器
"""
import os
import sys
import time
import threading
import webbrowser
from django.core.management import execute_from_command_line
from django.core.management.commands.runserver import Command as RunserverCommand

def open_browser():
    """延迟打开浏览器，给服务器启动时间"""
    time.sleep(2)  # 等待 2 秒让服务器启动
    url = "http://127.0.0.1:8001"
    print(f"\n正在打开浏览器: {url}")
    webbrowser.open(url)

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
    
    # 在后台线程中打开浏览器
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # 启动 Django 服务器（使用8001端口）
    sys.argv = ['manage.py', 'runserver', '8001']
    execute_from_command_line(sys.argv)

