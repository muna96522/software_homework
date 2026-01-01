#!/usr/bin/env python
"""强制生成数据到目标数量（忽略现有数据检查）"""
import os
import django
import random
from datetime import date, datetime, timedelta
from django.utils import timezone

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from main_app.models import *

def force_generate_students():
    """强制生成学生到40个"""
    print("强制生成学生数据...")
    
    first_names = ["伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋",
                   "勇", "艳", "杰", "涛", "明", "超", "秀英", "霞", "平", "刚",
                   "红", "梅", "兰", "竹", "菊", "春", "夏", "秋", "冬", "雪"]
    last_names = ["李", "王", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴",
                  "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
                  "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧"]
    
    target_count = 40
    existing_count = Student.objects.count()
    need_create = max(0, target_count - existing_count)
    
    if need_create == 0:
        print(f"学生数量已达到目标（{existing_count}个），无需生成\n")
        return
    
    courses = Course.objects.all()
    sessions = Session.objects.all()
    
    if not courses.exists():
        print("错误：没有专业数据，请先运行 generate_test_data.py\n")
        return
    
    if not sessions.exists():
        print("错误：没有学期数据，请先运行 generate_test_data.py\n")
        return
    
    created = 0
    attempt = 0
    max_attempts = need_create * 5
    
    while created < need_create and attempt < max_attempts:
        attempt += 1
        last_name = random.choice(last_names)
        first_name = random.choice(first_names)
        
        # 使用时间戳和随机数确保邮箱唯一
        timestamp = int(timezone.now().timestamp() * 1000000)  # 微秒级时间戳
        random_suffix = random.randint(1000, 9999)
        email = f"student{timestamp}{random_suffix}@school.edu.cn"
        
        if CustomUser.objects.filter(email=email).exists():
            continue
        
        gender = random.choice(['M', 'F'])
        phone = f"1{random.randint(3, 9)}{random.randint(100000000, 999999999)}"
        course = random.choice(courses)
        session = random.choice(sessions)
        profile_pic = "/media/student1.webp"
        
        try:
            user = CustomUser.objects.create_user(
                email=email,
                password="student123",
                user_type=3,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                profile_pic=profile_pic,
                phone_number=phone
            )
            user.student.course = course
            user.student.session = session
            user.student.save()
            created += 1
            if created % 5 == 0:
                print(f"  已生成 {created}/{need_create} 个学生...")
        except Exception as e:
            print(f"创建学生失败 {email}: {e}")
    
    print(f"已生成 {created} 个学生，现有学生总数: {Student.objects.count()}\n")

def force_generate_staff():
    """检查教师数据"""
    print("检查教师数据...")
    
    target_count = 10
    existing_count = Staff.objects.count()
    
    if existing_count < target_count:
        print(f"教师数量为 {existing_count}，目标为 {target_count}，请运行 generate_test_data.py 生成\n")
    else:
        print(f"教师数量: {existing_count}（目标: {target_count}）\n")

if __name__ == "__main__":
    print("=" * 80)
    print("强制生成数据到目标数量")
    print("=" * 80)
    print()
    
    force_generate_staff()
    force_generate_students()
    
    print("=" * 80)
    print("完成！")
    print("=" * 80)
    print(f"当前学生数: {Student.objects.count()}")
    print(f"当前教师数: {Staff.objects.count()}")
    print()
    print("提示：如果前端仍不显示数据，请：")
    print("1. 重启Django服务器（Ctrl+C 停止，然后重新运行 python manage.py runserver）")
    print("2. 清除浏览器缓存（Ctrl+F5 强制刷新）")
    print("3. 检查是否登录了正确的管理员账号")

