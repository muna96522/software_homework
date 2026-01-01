# PowerShell 脚本：启动 Django 服务器并自动打开浏览器（项目1 - 端口8001）
Write-Host "正在启动 Django 开发服务器（项目1 - 端口8001）..." -ForegroundColor Green
Write-Host ""

# 延迟 2 秒后打开浏览器（给服务器启动时间）
Start-Sleep -Seconds 2
Start-Process "http://127.0.0.1:8001"

# 启动 Django 服务器（使用8001端口）
python manage.py runserver 8001
