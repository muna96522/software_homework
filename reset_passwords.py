#!/usr/bin/env python
"""重置所有用户的密码为统一密码"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from main_app.models import *

def reset_passwords():
    """重置所有用户密码"""
    print("=" * 80)
    print("重置用户密码")
    print("=" * 80)
    print()
    
    # 管理员密码
    admin_password = "admin123"
    # 教师密码
    staff_password = "teacher123"
    # 学生密码
    student_password = "student123"
    
    # 重置管理员密码
    admins = CustomUser.objects.filter(user_type='1')
    for admin in admins:
        admin.set_password(admin_password)
        admin.save()
        print(f"✓ 管理员 {admin.email} 密码已重置为: {admin_password}")
    
    # 重置教师密码
    staffs = CustomUser.objects.filter(user_type='2')
    for staff in staffs:
        staff.set_password(staff_password)
        staff.save()
        print(f"✓ 教师 {staff.email} 密码已重置为: {staff_password}")
    
    # 重置学生密码
    students = CustomUser.objects.filter(user_type='3')
    for student in students:
        student.set_password(student_password)
        student.save()
        print(f"✓ 学生 {student.email} 密码已重置为: {student_password}")
    
    print()
    print("=" * 80)
    print("密码重置完成！")
    print("=" * 80)
    print()
    print("登录信息：")
    print(f"  管理员密码: {admin_password}")
    print(f"  教师密码: {staff_password}")
    print(f"  学生密码: {student_password}")
    print()

if __name__ == "__main__":
    # 自动重置，不需要确认
    reset_passwords()

