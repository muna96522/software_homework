@echo off
echo 正在启动 Django 开发服务器（项目1 - 端口8001）...
echo.
start http://127.0.0.1:8001
python manage.py runserver 8001
pause

