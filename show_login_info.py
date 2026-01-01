#!/usr/bin/env python
"""显示所有用户的登录信息"""
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
print("用户登录信息")
print("=" * 80)
print()

# 管理员
print("【管理员账户】")
print("密码: admin123")
print()
admins = CustomUser.objects.filter(user_type='1')
for i, admin in enumerate(admins, 1):
    print(f"{i}. 邮箱: {admin.email}")
    print(f"   姓名: {admin.last_name} {admin.first_name}")
    print()

# 教师
print("\n【教师账户】")
print("密码: teacher123")
staffs = CustomUser.objects.filter(user_type='2')
print(f"总教师数: {staffs.count()}")
print()
for i, staff in enumerate(staffs, 1):
    print(f"{i}. 邮箱: {staff.email}")
    print(f"   姓名: {staff.last_name} {staff.first_name}")
    if i >= 10:  # 只显示前10个
        print(f"   ... 还有 {staffs.count() - 10} 个教师账户")
        break
    print()

# 学生
print("\n【学生账户】")
print("密码: student123")
students = CustomUser.objects.filter(user_type='3')
print(f"总学生数: {students.count()}")
print()
for i, student in enumerate(students, 1):
    print(f"{i}. 邮箱: {student.email}")
    print(f"   姓名: {student.last_name} {student.first_name}")
    if i >= 10:  # 只显示前10个
        print(f"   ... 还有 {students.count() - 10} 个学生账户")
        break
    print()

print("\n" + "=" * 80)
print("登录信息总结")
print("=" * 80)
print("✅ 所有密码已统一重置为：")
print("   管理员密码: admin123")
print("   教师密码: teacher123")
print("   学生密码: student123")
print()
print("📝 测试账户推荐：")
print("   管理员: muna96@qq.com / admin123")
print("   教师: teacher05@school.edu.cn / teacher123")
print("   学生: student004@school.edu.cn / student123")
print()

