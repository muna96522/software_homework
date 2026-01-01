#!/usr/bin/env python
"""查看用户密码哈希值和登录信息"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from main_app.models import *

def get_user_type_display(user_type):
    """获取用户类型显示名称"""
    types = {'1': '管理员', '2': '教师', '3': '学生'}
    return types.get(str(user_type), '未知')

print("=" * 80)
print("用户密码信息说明")
print("=" * 80)
print()
print("⚠️  重要说明：")
print("   Django 使用密码哈希机制，密码不会以明文形式存储！")
print("   这是 Django 的安全机制，即使数据库泄露，也无法直接获取原始密码。")
print()
print("=" * 80)
print("用户密码哈希值（前50个字符）")
print("=" * 80)
print()

# 显示所有用户的密码哈希值（只显示前50个字符）
users = CustomUser.objects.all()
print(f"总用户数: {users.count()}\n")

for i, user in enumerate(users[:10], 1):  # 只显示前10个
    password_hash = user.password
    hash_preview = password_hash[:50] + "..." if len(password_hash) > 50 else password_hash
    print(f"{i}. {user.email}")
    print(f"   类型: {get_user_type_display(user.user_type)}")
    print(f"   密码哈希: {hash_preview}")
    print(f"   哈希算法: {password_hash.split('$')[0] if '$' in password_hash else '未知'}")
    print()

if users.count() > 10:
    print(f"... 还有 {users.count() - 10} 个用户")
    print()

print("=" * 80)
print("如何查看登录信息？")
print("=" * 80)
print()
print("方法1：运行 show_login_info.py 查看所有账户信息")
print("   python show_login_info.py")
print()
print("方法2：使用 Django Shell 验证密码")
print("   python manage.py shell")
print("   然后输入：")
print("   from main_app.models import CustomUser")
print("   user = CustomUser.objects.get(email='your_email@example.com')")
print("   user.check_password('your_password')  # 返回 True 或 False")
print()
print("方法3：重置密码")
print("   python reset_passwords.py")
print("   这会重置所有用户的密码为统一密码")
print()

