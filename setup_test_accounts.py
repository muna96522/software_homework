#!/usr/bin/env python
"""设置测试账号 - 创建或重置常用测试账号"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from main_app.models import *

def setup_test_accounts():
    """创建或重置测试账号"""
    print("=" * 80)
    print("设置测试账号")
    print("=" * 80)
    print()
    
    # 测试账号配置
    test_accounts = [
        {
            'email': 'muan96@qq.com',
            'password': 'admin123',
            'user_type': '1',
            'first_name': '管理员',
            'last_name': '测试',
            'gender': 'M',
            'profile_pic': '/media/admin.png'
        },
        {
            'email': 'muna96@qq.com',
            'password': 'admin123',
            'user_type': '1',
            'first_name': '管理员',
            'last_name': '测试',
            'gender': 'M',
            'profile_pic': '/media/admin.png'
        },
        {
            'email': 'admin@admin.com',
            'password': 'admin123',
            'user_type': '1',
            'first_name': 'Admin',
            'last_name': 'User',
            'gender': 'M',
            'profile_pic': '/media/admin.png'
        },
    ]
    
    for account in test_accounts:
        email = account['email']
        password = account['password']
        
        # 检查用户是否已存在
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            # 重置密码
            user.set_password(password)
            user.save()
            print(f"✓ 已重置账号: {email} (密码: {password})")
        else:
            # 创建新用户
            try:
                user = CustomUser.objects.create_user(
                    email=email,
                    password=password,
                    user_type=account['user_type'],
                    first_name=account['first_name'],
                    last_name=account['last_name'],
                    gender=account['gender'],
                    profile_pic=account['profile_pic']
                )
                print(f"✓ 已创建账号: {email} (密码: {password})")
            except Exception as e:
                print(f"✗ 创建账号失败 {email}: {e}")
    
    print()
    print("=" * 80)
    print("所有用户账号列表")
    print("=" * 80)
    print()
    
    # 显示所有管理员账号
    print("【管理员账号】密码: admin123")
    admins = CustomUser.objects.filter(user_type='1')
    for i, admin in enumerate(admins, 1):
        print(f"  {i}. {admin.email} - {admin.last_name}{admin.first_name}")
    print()
    
    # 显示所有教师账号（前5个）
    print("【教师账号】密码: teacher123")
    staffs = CustomUser.objects.filter(user_type='2')[:5]
    for i, staff in enumerate(staffs, 1):
        print(f"  {i}. {staff.email} - {staff.last_name}{staff.first_name}")
    if CustomUser.objects.filter(user_type='2').count() > 5:
        print(f"  ... 还有 {CustomUser.objects.filter(user_type='2').count() - 5} 个教师账号")
    print()
    
    # 显示所有学生账号（前5个）
    print("【学生账号】密码: student123")
    students = CustomUser.objects.filter(user_type='3')[:5]
    for i, student in enumerate(students, 1):
        print(f"  {i}. {student.email} - {student.last_name}{student.first_name}")
    if CustomUser.objects.filter(user_type='3').count() > 5:
        print(f"  ... 还有 {CustomUser.objects.filter(user_type='3').count() - 5} 个学生账号")
    print()
    
    print("=" * 80)
    print("登录信息")
    print("=" * 80)
    print("管理员密码: admin123")
    print("教师密码: teacher123")
    print("学生密码: student123")
    print()
    print("推荐测试账号：")
    print("  管理员: muan96@qq.com / admin123")
    print("  或: muna96@qq.com / admin123")
    print("  或: admin@admin.com / admin123")
    print()

if __name__ == "__main__":
    setup_test_accounts()

