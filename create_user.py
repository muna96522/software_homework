#!/usr/bin/env python
"""在终端创建新用户的脚本"""
import os
import django
import sys

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from main_app.models import *

def create_user():
    """创建新用户"""
    print("=" * 80)
    print("创建新用户")
    print("=" * 80)
    print()
    print("用户类型：")
    print("  1 - 管理员 (HOD)")
    print("  2 - 教师 (Staff)")
    print("  3 - 学生 (Student)")
    print()
    
    # 获取用户输入
    try:
        user_type = input("请选择用户类型 (1/2/3): ").strip()
        if user_type not in ['1', '2', '3']:
            print("❌ 无效的用户类型！")
            return
        
        email = input("请输入邮箱: ").strip()
        if not email:
            print("❌ 邮箱不能为空！")
            return
        
        # 检查邮箱是否已存在
        if CustomUser.objects.filter(email=email).exists():
            print(f"❌ 邮箱 {email} 已存在！")
            return
        
        password = input("请输入密码: ").strip()
        if not password:
            print("❌ 密码不能为空！")
            return
        
        first_name = input("请输入名字: ").strip()
        last_name = input("请输入姓氏: ").strip()
        
        gender = input("请输入性别 (M/F): ").strip().upper()
        if gender not in ['M', 'F']:
            print("❌ 性别必须是 M 或 F！")
            return
        
        phone_number = input("请输入电话号码（可选，直接回车跳过）: ").strip() or None
        
        # 对于学生，需要选择专业和学期
        course = None
        session = None
        if user_type == '3':
            print("\n请选择专业：")
            courses = Course.objects.all()
            if not courses.exists():
                print("❌ 没有可用的专业，请先创建专业！")
                return
            
            for i, c in enumerate(courses, 1):
                print(f"  {i}. {c.name}")
            
            try:
                course_idx = int(input("请输入专业编号: ").strip()) - 1
                if 0 <= course_idx < len(courses):
                    course = courses[course_idx]
                else:
                    print("❌ 无效的专业编号！")
                    return
            except ValueError:
                print("❌ 请输入有效的数字！")
                return
            
            print("\n请选择学期：")
            sessions = Session.objects.all()
            if not sessions.exists():
                print("❌ 没有可用的学期，请先创建学期！")
                return
            
            for i, s in enumerate(sessions, 1):
                print(f"  {i}. {s}")
            
            try:
                session_idx = int(input("请输入学期编号: ").strip()) - 1
                if 0 <= session_idx < len(sessions):
                    session = sessions[session_idx]
                else:
                    print("❌ 无效的学期编号！")
                    return
            except ValueError:
                print("❌ 请输入有效的数字！")
                return
        
        # 设置默认头像路径
        if user_type == '1':
            profile_pic = "/media/admin.png"
        elif user_type == '2':
            profile_pic = "/media/admin.png"
        else:
            profile_pic = "/media/student1.webp"
        
        # 创建用户
        print("\n正在创建用户...")
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            user_type=user_type,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            profile_pic=profile_pic,
            phone_number=phone_number
        )
        
        # 对于学生，设置专业和学期
        if user_type == '3' and course and session:
            user.student.course = course
            user.student.session = session
            user.student.save()
        
        user_type_name = {'1': '管理员', '2': '教师', '3': '学生'}[user_type]
        print(f"\n✅ 成功创建{user_type_name}用户！")
        print(f"   邮箱: {user.email}")
        print(f"   姓名: {user.last_name} {user.first_name}")
        print(f"   密码: {password}")
        if user_type == '3':
            print(f"   专业: {user.student.course.name}")
            print(f"   学期: {user.student.session}")
        print()
        
    except KeyboardInterrupt:
        print("\n\n❌ 操作已取消")
    except Exception as e:
        print(f"\n❌ 创建用户失败：{str(e)}")

if __name__ == "__main__":
    create_user()

