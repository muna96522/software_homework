#!/usr/bin/env python
"""测试前端数据查询"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from main_app.models import *

print("=" * 80)
print("测试前端数据查询")
print("=" * 80)
print()

# 测试学生查询（与前端视图一致）
students = CustomUser.objects.filter(user_type=3).select_related('student', 'student__course', 'student__session')
print(f"【学生查询结果】")
print(f"总学生数: {students.count()}")
print()

if students.exists():
    print("前10个学生（分页第一页）:")
    for i, student in enumerate(students[:10], 1):
        course_name = student.student.course.name if student.student.course else "未分配"
        print(f"  {i}. {student.last_name}, {student.first_name} - {student.email} - {course_name}")
else:
    print("⚠️ 没有找到学生数据！")

print()
print("=" * 80)

# 测试教师查询
staffs = CustomUser.objects.filter(user_type=2).select_related('staff')
print(f"【教师查询结果】")
print(f"总教师数: {staffs.count()}")
print()

if staffs.exists():
    print("前10个教师（分页第一页）:")
    for i, staff in enumerate(staffs[:10], 1):
        print(f"  {i}. {staff.last_name}, {staff.first_name} - {staff.email}")
else:
    print("⚠️ 没有找到教师数据！")

print()
print("=" * 80)
print("如果查询结果正常，但前端仍不显示，请：")
print("1. 重启Django服务器（停止后重新运行 python manage.py runserver）")
print("2. 清除浏览器缓存（Ctrl+F5 强制刷新）")
print("3. 确认使用管理员账号登录（user_type=1）")
print("4. 检查浏览器控制台是否有JavaScript错误")
print("=" * 80)

