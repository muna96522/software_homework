#!/usr/bin/env python
"""生成测试数据并清理不完整数据"""
import os
import django
import random
from datetime import date, datetime, timedelta
from django.utils import timezone

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from main_app.models import *
from django.core.files.storage import FileSystemStorage

def get_user_type_display(user_type):
    """获取用户类型显示名称"""
    types = {'1': '管理员', '2': '教师', '3': '学生'}
    return types.get(str(user_type), '未知')

def clean_incomplete_data():
    """清理不完整的数据"""
    print("=" * 80)
    print("清理不完整数据...")
    print("=" * 80)
    
    # 删除没有姓名的用户
    incomplete_users = CustomUser.objects.filter(
        first_name__isnull=True
    ) | CustomUser.objects.filter(
        first_name=''
    ) | CustomUser.objects.filter(
        last_name__isnull=True
    ) | CustomUser.objects.filter(
        last_name=''
    )
    
    count = incomplete_users.count()
    if count > 0:
        print(f"删除 {count} 个不完整的用户...")
        incomplete_users.delete()
    
    print("清理完成！\n")

def generate_courses():
    """生成专业数据"""
    print("生成专业数据...")
    courses_data = [
        "计算机科学与技术", "软件工程", "数据科学与大数据技术",
        "人工智能", "物联网工程", "网络信息安全",
        "电子信息工程", "通信工程", "自动化",
        "数学与应用数学", "信息与计算科学", "统计学",
        "英语", "日语", "商务英语"
    ]
    
    existing_courses = Course.objects.all()
    existing_names = [c.name for c in existing_courses]
    
    created = 0
    for name in courses_data:
        if name not in existing_names:
            Course.objects.create(name=name)
            created += 1
    
    print(f"已生成 {created} 个专业，现有专业总数: {Course.objects.count()}\n")
    return Course.objects.all()

def generate_sessions():
    """生成学期数据"""
    print("生成学期数据...")
    sessions_data = [
        # 历史学期
        ("2022-09-01", "2023-01-15"),  # 2022秋季学期
        ("2023-02-20", "2023-06-30"),  # 2023春季学期
        ("2023-09-01", "2024-01-15"),  # 2023秋季学期
        ("2024-02-20", "2024-06-30"),  # 2024春季学期
        # 当前和未来学期
        ("2024-09-01", "2025-01-15"),  # 2024秋季学期
        ("2025-02-20", "2025-06-30"),  # 2025春季学期
        ("2025-09-01", "2026-01-16"),  # 2025秋季学期
        ("2026-02-20", "2026-06-30"),  # 2026春季学期
        ("2026-09-01", "2027-01-15"),  # 2026秋季学期
        ("2027-02-20", "2027-06-30"),  # 2027春季学期
    ]
    
    created = 0
    for start, end in sessions_data:
        if not Session.objects.filter(start_year=start, end_year=end).exists():
            Session.objects.create(
                start_year=date.fromisoformat(start),
                end_year=date.fromisoformat(end)
            )
            created += 1
    
    print(f"已生成 {created} 个学期，现有学期总数: {Session.objects.count()}\n")
    return Session.objects.all()

def generate_staff(courses):
    """生成教师数据"""
    print("生成教师数据...")
    
    # 中文姓名
    first_names = ["明", "华", "强", "伟", "芳", "娜", "敏", "静", "丽", "艳", 
                   "军", "勇", "磊", "涛", "鹏", "超", "刚", "辉", "杰", "浩"]
    last_names = ["张", "王", "李", "刘", "陈", "杨", "赵", "黄", "周", "吴",
                  "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗"]
    
    # 生成10个教师
    target_count = 10
    existing_count = Staff.objects.count()
    need_create = max(0, target_count - existing_count)
    
    created = 0
    attempt = 0
    max_attempts = need_create * 3  # 最多尝试3倍次数，避免无限循环
    
    while created < need_create and attempt < max_attempts:
        attempt += 1
        last_name = random.choice(last_names)
        first_name = random.choice(first_names)
        
        # 使用时间戳和随机数确保邮箱唯一
        timestamp = int(timezone.now().timestamp() * 1000)
        random_suffix = random.randint(100, 999)
        email = f"teacher{timestamp}{random_suffix}@school.edu.cn"
        
        # 检查邮箱是否已存在
        if CustomUser.objects.filter(email=email).exists():
            continue
        
        gender = random.choice(['M', 'F'])
        phone = f"1{random.randint(3, 9)}{random.randint(100000000, 999999999)}"
        
        # 使用默认头像路径
        profile_pic = "/media/admin.png"
        
        try:
            user = CustomUser.objects.create_user(
                email=email,
                password="teacher123",
                user_type=2,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                profile_pic=profile_pic,
                phone_number=phone
            )
            created += 1
        except Exception as e:
            print(f"创建教师失败 {email}: {e}")
    
    print(f"已生成 {created} 个教师，现有教师总数: {Staff.objects.count()}\n")
    return Staff.objects.all()

def generate_students(courses, sessions):
    """生成学生数据 - 确保每个学期每个专业都有学生"""
    print("生成学生数据...")
    
    first_names = ["伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "军", "洋",
                   "勇", "艳", "杰", "涛", "明", "超", "秀英", "霞", "平", "刚",
                   "红", "梅", "兰", "菊", "竹", "松", "柏", "枫", "雪", "雨"]
    last_names = ["李", "王", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴",
                  "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
                  "梁", "宋", "郑", "谢", "韩", "唐", "冯", "于", "董", "萧"]
    
    # 确保每个学期每个专业至少有2-3个学生
    created = 0
    attempt = 0
    max_attempts = len(courses) * len(sessions) * 5  # 每个组合最多尝试5次
    
    # 为每个学期每个专业生成学生
    for session in sessions:
        for course in courses:
            # 检查该学期该专业是否已有学生
            existing_students = Student.objects.filter(course=course, session=session).count()
            target_per_combination = random.randint(2, 4)  # 每个组合2-4个学生
            
            if existing_students >= target_per_combination:
                continue
            
            need_create = target_per_combination - existing_students
            
            for i in range(need_create):
                attempt += 1
                if attempt > max_attempts:
                    break
                
                last_name = random.choice(last_names)
                first_name = random.choice(first_names)
                
                # 使用时间戳和随机数确保邮箱唯一
                timestamp = int(timezone.now().timestamp() * 1000)
                random_suffix = random.randint(1000, 9999)
                email = f"student{timestamp}{random_suffix}{attempt}@school.edu.cn"
                
                if CustomUser.objects.filter(email=email).exists():
                    continue
                
                gender = random.choice(['M', 'F'])
                phone = f"1{random.randint(3, 9)}{random.randint(100000000, 999999999)}"
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
                except Exception as e:
                    print(f"创建学生失败 {email}: {e}")
    
    # 额外生成一些随机分布的学生
    target_total = 60  # 总目标学生数
    existing_total = Student.objects.count()
    need_create_extra = max(0, target_total - existing_total)
    
    for i in range(need_create_extra):
        attempt += 1
        if attempt > max_attempts * 2:
            break
        
        last_name = random.choice(last_names)
        first_name = random.choice(first_names)
        
        timestamp = int(timezone.now().timestamp() * 1000)
        random_suffix = random.randint(1000, 9999)
        email = f"student{timestamp}{random_suffix}{attempt}@school.edu.cn"
        
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
        except Exception as e:
            print(f"创建学生失败 {email}: {e}")
    
    print(f"已生成 {created} 个学生，现有学生总数: {Student.objects.count()}\n")
    
    # 打印每个学期每个专业的学生分布
    print("学生分布情况：")
    for session in sessions:
        print(f"  学期 {session.start_year} - {session.end_year}:")
        for course in courses:
            count = Student.objects.filter(course=course, session=session).count()
            print(f"    {course.name}: {count} 个学生")
    print()
    
    return Student.objects.all()

def generate_subjects(courses, staffs):
    """生成科目数据"""
    print("生成科目数据...")
    
    # 为每个专业生成2-3个科目
    subject_templates = {
        "计算机": ["计算机科学导论", "数据结构", "算法设计", "操作系统", "数据库原理"],
        "软件": ["软件工程", "面向对象程序设计", "Web开发", "移动应用开发"],
        "数据": ["数据科学导论", "机器学习", "数据挖掘", "大数据技术"],
        "人工智能": ["人工智能基础", "深度学习", "自然语言处理", "计算机视觉"],
        "物联网": ["物联网导论", "传感器技术", "嵌入式系统", "无线通信"],
        "网络": ["网络安全", "密码学", "网络协议", "信息安全"],
        "电子": ["电路分析", "数字电路", "模拟电路", "信号处理"],
        "通信": ["通信原理", "数字信号处理", "移动通信", "光纤通信"],
        "自动化": ["自动控制原理", "PLC技术", "工业自动化", "机器人技术"],
        "数学": ["高等数学", "线性代数", "概率论", "数学分析"],
        "统计": ["统计学", "数理统计", "应用统计", "数据分析"],
        "英语": ["英语精读", "英语写作", "英语口语", "英语翻译"],
        "日语": ["日语基础", "日语语法", "日语会话", "日语阅读"],
        "商务": ["商务英语", "国际贸易", "商务沟通", "跨文化交际"]
    }
    
    created = 0
    for course in courses:
        # 为每个专业分配2-3个科目
        num_subjects = random.randint(2, 3)
        
        # 根据专业名称选择科目模板
        course_key = None
        for key in subject_templates.keys():
            if key in course.name:
                course_key = key
                break
        
        if not course_key:
            course_key = "计算机"  # 默认使用计算机相关科目
        
        subjects_for_course = random.sample(subject_templates[course_key], 
                                           min(num_subjects, len(subject_templates[course_key])))
        
        for subject_name in subjects_for_course:
            # 检查是否已存在
            if Subject.objects.filter(name=subject_name, course=course).exists():
                continue
            
            # 随机分配教师
            staff = random.choice(staffs)
            
            try:
                Subject.objects.create(
                    name=subject_name,
                    course=course,
                    staff=staff
                )
                created += 1
            except Exception as e:
                print(f"创建科目失败 {subject_name}: {e}")
    
    print(f"已生成 {created} 个科目，现有科目总数: {Subject.objects.count()}\n")
    return Subject.objects.all()

def generate_attendance(subjects, sessions, students):
    """生成出勤数据 - 确保每个学期每门课都有出勤记录"""
    print("生成出勤数据...")
    
    created = 0
    reports_created = 0
    today = date.today()
    
    # 为每个学期每门课生成出勤记录
    for session in sessions:
        # 检查该学期是否在当前时间范围内
        session_start = session.start_year
        session_end = session.end_year
        
        # 为该学期的每门课生成出勤记录
        for subject in subjects:
            # 获取该科目所属专业该学期的学生
            course_students = Student.objects.filter(course=subject.course, session=session)
            
            if not course_students.exists():
                continue
            
            # 为该科目生成最近30天的出勤记录（如果学期在当前时间范围内）
            for i in range(30):
                attendance_date = today - timedelta(days=i)
                
                # 检查日期是否在学期范围内
                if attendance_date < session_start or attendance_date > session_end:
                    continue
                
                # 检查是否已存在该日期的出勤记录
                if Attendance.objects.filter(subject=subject, date=attendance_date, session=session).exists():
                    continue
                
                try:
                    attendance = Attendance.objects.create(
                        subject=subject,
                        session=session,
                        date=attendance_date
                    )
                    
                    # 为该科目的学生生成出勤报告
                    for student in course_students:
                        # 检查是否已存在该学生的该出勤记录
                        if AttendanceReport.objects.filter(student=student, attendance=attendance).exists():
                            continue
                        # 80%出勤率
                        status = random.random() < 0.8
                        try:
                            AttendanceReport.objects.create(
                                student=student,
                                attendance=attendance,
                                status=status
                            )
                            reports_created += 1
                        except Exception as e:
                            pass  # 忽略重复创建错误
                    
                    created += 1
                except Exception as e:
                    print(f"创建出勤记录失败: {e}")
    
    print(f"已生成 {created} 条出勤记录，现有出勤记录总数: {Attendance.objects.count()}\n")
    print(f"本次生成 {reports_created} 条出勤报告，现有出勤报告总数: {AttendanceReport.objects.count()}\n")

def generate_feedback(students, staffs):
    """生成反馈数据"""
    print("生成反馈数据...")
    
    student_feedbacks = [
        "希望老师能够提供更多的练习题和作业讲解",
        "课程内容很丰富，但进度有点快",
        "建议增加实践环节，理论结合实践会更好",
        "老师讲课很清晰，但希望能有更多互动",
        "希望增加一些实际案例的讲解",
        "课程安排合理，但作业量有点大",
        "希望老师能够提供课程录播视频",
        "建议增加小组讨论环节",
        "课程内容很好，但希望能有更多参考资料",
        "希望老师能够及时回复问题"
    ]
    
    staff_feedbacks = [
        "希望学校能够提供更好的教学设备",
        "建议增加教师培训机会",
        "希望学生能够更积极参与课堂讨论",
        "建议优化课程安排，避免时间冲突",
        "希望学校能够提供更多教学资源",
        "建议增加教师之间的交流活动",
        "希望学生能够按时完成作业",
        "建议改进教学评估方式",
        "希望学校能够支持教学创新",
        "建议增加对教师的支持力度"
    ]
    
    # 生成学生反馈
    student_created = 0
    for i in range(30):
        student = random.choice(students)
        feedback_text = random.choice(student_feedbacks)
        
        # 50%的反馈已有回复
        has_reply = random.random() < 0.5
        reply_text = "感谢您的反馈，我们会认真考虑您的建议并持续改进。" if has_reply else ""
        
        try:
            FeedbackStudent.objects.create(
                student=student,
                feedback=feedback_text,
                reply=reply_text
            )
            student_created += 1
        except Exception as e:
            print(f"创建学生反馈失败: {e}")
    
    # 生成教师反馈
    staff_created = 0
    for i in range(20):
        staff = random.choice(staffs)
        feedback_text = random.choice(staff_feedbacks)
        
        # 50%的反馈已有回复
        has_reply = random.random() < 0.5
        reply_text = "感谢您的反馈，我们会认真考虑您的建议。" if has_reply else ""
        
        try:
            FeedbackStaff.objects.create(
                staff=staff,
                feedback=feedback_text,
                reply=reply_text
            )
            staff_created += 1
        except Exception as e:
            print(f"创建教师反馈失败: {e}")
    
    print(f"已生成 {student_created} 条学生反馈，现有学生反馈总数: {FeedbackStudent.objects.count()}\n")
    print(f"已生成 {staff_created} 条教师反馈，现有教师反馈总数: {FeedbackStaff.objects.count()}\n")

def generate_leave_requests(students, staffs):
    """生成请假申请"""
    print("生成请假申请...")
    
    leave_reasons = [
        "因病请假",
        "家中有事",
        "参加重要考试",
        "参加学术会议",
        "个人原因",
        "家庭紧急情况",
        "参加比赛",
        "其他原因"
    ]
    
    # 生成学生请假
    student_created = 0
    for i in range(50):
        student = random.choice(students)
        leave_date = date.today() - timedelta(days=random.randint(1, 90))
        reason = random.choice(leave_reasons)
        
        # 随机状态：0待审批，1已批准，-1已拒绝
        status = random.choice([0, 1, -1])
        
        try:
            LeaveReportStudent.objects.create(
                student=student,
                date=str(leave_date),
                message=reason,
                status=status
            )
            student_created += 1
        except Exception as e:
            print(f"创建学生请假失败: {e}")
    
    # 生成教师请假
    staff_created = 0
    for i in range(25):
        staff = random.choice(staffs)
        leave_date = date.today() - timedelta(days=random.randint(1, 90))
        reason = random.choice(leave_reasons)
        
        # 随机状态
        status = random.choice([0, 1, -1])
        
        try:
            LeaveReportStaff.objects.create(
                staff=staff,
                date=str(leave_date),
                message=reason,
                status=status
            )
            staff_created += 1
        except Exception as e:
            print(f"创建教师请假失败: {e}")
    
    print(f"已生成 {student_created} 条学生请假申请，现有总数: {LeaveReportStudent.objects.count()}\n")
    print(f"已生成 {staff_created} 条教师请假申请，现有总数: {LeaveReportStaff.objects.count()}\n")

def generate_results(students, subjects):
    """生成成绩数据 - 确保每个学期每门课都有学生成绩"""
    print("生成成绩数据...")
    
    created = 0
    
    # 获取所有学期
    sessions = Session.objects.all()
    
    # 为每个学期、每门课生成成绩数据
    for session in sessions:
        # 获取该学期的所有学生
        session_students = Student.objects.filter(session=session)
        
        if not session_students.exists():
            continue
        
        # 为每门课生成成绩
        for subject in subjects:
            # 获取该科目所属专业的学生（该学期的）
            course_students = session_students.filter(course=subject.course)
            
            if not course_students.exists():
                continue
            
            # 确保该科目至少有该学期该专业50%的学生有成绩
            target_count = max(2, int(len(course_students) * 0.5))
            existing_count = StudentResult.objects.filter(
                student__in=course_students,
                subject=subject
            ).count()
            
            if existing_count >= target_count:
                continue
            
            need_create = target_count - existing_count
            selected_students = random.sample(list(course_students), min(need_create, len(course_students)))
            
            for student in selected_students:
                # 检查是否已存在该学生的该科目成绩
                if StudentResult.objects.filter(student=student, subject=subject).exists():
                    continue
                
                # 生成成绩：平时成绩20-40，考试成绩30-60
                test_score = round(random.uniform(20, 40), 1)
                exam_score = round(random.uniform(30, 60), 1)
                
                try:
                    StudentResult.objects.create(
                        student=student,
                        subject=subject,
                        test=test_score,
                        exam=exam_score
                    )
                    created += 1
                except Exception as e:
                    print(f"创建成绩失败: {e}")
    
    # 为每个学生补充成绩（确保每个学生至少有2-4门课的成绩）
    for student in students:
        # 只选择该学生专业下的科目
        student_subjects = Subject.objects.filter(course=student.course)
        
        if not student_subjects.exists():
            continue
        
        # 检查该学生已有成绩的科目数
        existing_results = StudentResult.objects.filter(student=student).count()
        target_results = random.randint(2, min(4, len(student_subjects)))
        
        if existing_results >= target_results:
            continue
        
        need_create = target_results - existing_results
        available_subjects = [s for s in student_subjects 
                            if not StudentResult.objects.filter(student=student, subject=s).exists()]
        
        if not available_subjects:
            continue
        
        selected_subjects = random.sample(available_subjects, min(need_create, len(available_subjects)))
        
        for subject in selected_subjects:
            # 生成成绩：平时成绩20-40，考试成绩30-60
            test_score = round(random.uniform(20, 40), 1)
            exam_score = round(random.uniform(30, 60), 1)
            
            try:
                StudentResult.objects.create(
                    student=student,
                    subject=subject,
                    test=test_score,
                    exam=exam_score
                )
                created += 1
            except Exception as e:
                print(f"创建成绩失败: {e}")
    
    print(f"已生成 {created} 条成绩记录，现有成绩总数: {StudentResult.objects.count()}\n")
    
    # 打印每个学期每门课的成绩分布
    print("成绩分布情况：")
    for session in sessions:
        print(f"  学期 {session.start_year} - {session.end_year}:")
        for subject in subjects:
            session_students = Student.objects.filter(session=session, course=subject.course)
            result_count = StudentResult.objects.filter(
                student__in=session_students,
                subject=subject
            ).count()
            if result_count > 0:
                print(f"    {subject.name} ({subject.course.name}): {result_count} 条成绩")
    print()

def generate_activities(staffs, students):
    """生成活动数据"""
    print("生成活动数据...")
    
    # 活动标题模板
    activity_titles = [
        "春季运动会", "校园文化节", "科技创新大赛", "英语演讲比赛",
        "数学建模竞赛", "编程马拉松", "摄影作品展", "书法比赛",
        "歌唱比赛", "舞蹈大赛", "辩论赛", "学术讲座",
        "志愿者活动", "环保宣传活动", "读书分享会", "职业规划讲座",
        "心理健康讲座", "创新创业大赛", "艺术节", "体育节"
    ]
    
    # 活动地点
    locations = [
        "体育馆", "大礼堂", "图书馆报告厅", "教学楼A101",
        "教学楼B201", "实验楼301", "艺术楼401", "运动场",
        "学生活动中心", "多媒体教室", "会议室", "阶梯教室"
    ]
    
    # 活动描述模板
    descriptions = [
        "本次活动旨在丰富校园文化生活，提高学生综合素质。",
        "通过本次活动，促进同学们之间的交流与合作。",
        "本次活动将为同学们提供一个展示才华的平台。",
        "欢迎所有感兴趣的同学积极参与本次活动。",
        "本次活动将邀请专业评委进行评审，优秀作品将获得奖励。",
        "本次活动旨在培养学生的创新思维和实践能力。",
        "通过本次活动，希望同学们能够拓展视野，增长见识。",
        "本次活动将为同学们提供宝贵的学习和交流机会。"
    ]
    
    created = 0
    now = date.today()
    
    for i in range(25):  # 生成25个活动
        organizer = random.choice(staffs)
        title = random.choice(activity_titles)
        
        # 随机生成活动时间（未来30天内）
        days_ahead = random.randint(1, 30)
        start_date = now + timedelta(days=days_ahead)
        start_time = timezone.make_aware(
            datetime.combine(start_date, datetime.min.time().replace(hour=random.randint(9, 16)))
        )
        
        # 活动持续1-4小时
        duration_hours = random.randint(1, 4)
        end_time = start_time + timedelta(hours=duration_hours)
        
        location = random.choice(locations)
        description = random.choice(descriptions)
        max_participants = random.choice([0, 20, 30, 50, 100])  # 0表示不限制
        
        # 随机审批状态：70%已通过，20%待审批，10%已拒绝
        status_weights = [1, 1, 1, 1, 1, 1, 1, 0, 0, 2]  # 1=通过, 0=待审批, 2=拒绝
        status = random.choice(status_weights)
        
        admin_reply = ""
        if status == 1:
            admin_reply = "活动内容健康向上，同意举办。"
        elif status == 2:
            admin_reply = "活动时间与学校其他活动冲突，暂不批准。"
        
        try:
            activity = Activity.objects.create(
                title=title,
                description=description,
                organizer=organizer,
                location=location,
                start_time=start_time,
                end_time=end_time,
                max_participants=max_participants,
                status=status,
                admin_reply=admin_reply
            )
            created += 1
        except Exception as e:
            print(f"创建活动失败: {e}")
    
    print(f"已生成 {created} 个活动，现有活动总数: {Activity.objects.count()}\n")
    return Activity.objects.all()

def generate_activity_registrations(activities, students):
    """生成活动报名数据"""
    print("生成活动报名数据...")
    
    created = 0
    # 只对已通过审批的活动进行报名
    approved_activities = [a for a in activities if a.status == 1]
    
    if not approved_activities:
        print("没有已通过审批的活动，跳过报名数据生成\n")
        return
    
    for activity in approved_activities:
        # 每个活动随机有3-10个学生报名
        num_registrations = random.randint(3, 10)
        
        # 检查人数限制
        if activity.max_participants > 0:
            num_registrations = min(num_registrations, activity.max_participants)
        
        # 随机选择学生
        selected_students = random.sample(list(students), min(num_registrations, len(students)))
        
        for student in selected_students:
            # 检查是否已报名
            if ActivityRegistration.objects.filter(activity=activity, student=student).exists():
                continue
            
            # 报名时间在活动创建后，活动开始前
            registration_time = activity.created_at + timedelta(
                hours=random.randint(1, 24 * 7)  # 1小时到7天内
            )
            
            try:
                registration = ActivityRegistration.objects.create(
                    activity=activity,
                    student=student
                )
                # 更新创建时间
                registration.registered_at = registration_time
                registration.save()
                created += 1
            except Exception as e:
                print(f"创建报名记录失败: {e}")
    
    print(f"已生成 {created} 条报名记录，现有报名总数: {ActivityRegistration.objects.count()}\n")

def generate_activity_attendance(activities, staffs):
    """生成活动签到数据"""
    print("生成活动签到数据...")
    
    created = 0
    # 只对已通过审批且有报名的活动进行签到
    approved_activities = [a for a in activities if a.status == 1]
    
    for activity in approved_activities:
        registrations = ActivityRegistration.objects.filter(activity=activity)
        
        if not registrations.exists():
            continue
        
        # 活动发起人负责签到
        organizer = activity.organizer
        
        for registration in registrations:
            # 检查是否已签到
            if ActivityAttendance.objects.filter(activity=activity, student=registration.student).exists():
                continue
            
            # 80%的学生已签到，20%未签到
            is_present = random.random() < 0.8
            
            # 签到时间在活动开始时间前后1小时内
            check_time = activity.start_time + timedelta(
                minutes=random.randint(-60, 60)
            )
            
            try:
                attendance = ActivityAttendance.objects.create(
                    activity=activity,
                    student=registration.student,
                    is_present=is_present,
                    checked_by=organizer
                )
                # 更新签到时间
                attendance.checked_at = check_time
                attendance.save()
                created += 1
            except Exception as e:
                print(f"创建签到记录失败: {e}")
    
    print(f"已生成 {created} 条签到记录，现有签到总数: {ActivityAttendance.objects.count()}\n")

def generate_activity_feedback(activities, students):
    """生成活动评价数据"""
    print("生成活动评价数据...")
    
    created = 0
    # 只对已通过审批的活动进行评价
    approved_activities = [a for a in activities if a.status == 1]
    
    # 评价内容模板
    feedback_comments = [
        "活动组织得很好，内容丰富，收获很大！",
        "活动很有趣，希望以后能多举办类似的活动。",
        "活动时间安排合理，场地也很合适。",
        "活动让我学到了很多新知识，感谢组织者。",
        "活动氛围很好，大家都很积极参与。",
        "活动内容有些简单，希望能增加一些挑战性。",
        "活动组织有序，工作人员很负责。",
        "活动很有意义，期待下次参与。",
        "活动时间有点长，建议缩短一些。",
        "活动很棒，希望以后还能参加。"
    ]
    
    for activity in approved_activities:
        # 获取已报名的学生
        registrations = ActivityRegistration.objects.filter(activity=activity)
        
        # 只有部分学生会评价（60%）
        for registration in registrations:
            if random.random() > 0.6:
                continue
            
            # 检查是否已评价
            if ActivityFeedback.objects.filter(activity=activity, student=registration.student).exists():
                continue
            
            rating = random.randint(3, 5)  # 评分3-5星
            comment = random.choice(feedback_comments)
            
            try:
                ActivityFeedback.objects.create(
                    activity=activity,
                    student=registration.student,
                    rating=rating,
                    comment=comment
                )
                created += 1
            except Exception as e:
                print(f"创建评价记录失败: {e}")
    
    print(f"已生成 {created} 条评价记录，现有评价总数: {ActivityFeedback.objects.count()}\n")

def generate_notifications(staffs, students):
    """生成通知数据"""
    print("生成通知数据...")
    
    # 通知消息模板
    staff_notifications = [
        "请各位教师注意，下周将进行教学检查，请提前准备好相关材料。",
        "新的教学大纲已发布，请各位教师及时查看并按照要求执行。",
        "教师培训会议将于本周五下午2点在会议室举行，请准时参加。",
        "学期末考试安排已确定，请各位教师查看并做好准备工作。",
        "请各位教师及时提交本学期教学总结报告。",
        "学校将组织教师参加教学技能大赛，有意向的教师请报名。",
        "新的教学设备已到位，请各位教师到设备处领取。",
        "请各位教师注意，学生评教系统已开放，请关注学生反馈。",
        "教师节活动安排已确定，请各位教师查看通知。",
        "请各位教师按时完成学生成绩录入工作。"
    ]
    
    student_notifications = [
        "请各位同学注意，期末考试时间已确定，请查看考试安排。",
        "图书馆将于本周末进行系统维护，期间暂停服务。",
        "学生证补办工作已开始，需要补办的同学请到学生处办理。",
        "奖学金申请已开放，符合条件的同学请及时提交申请。",
        "请各位同学注意，选课系统将于下周开放，请提前做好准备。",
        "校园招聘会将于下月举行，请各位同学关注相关信息。",
        "请各位同学按时完成作业，逾期将影响平时成绩。",
        "学生宿舍检查将于本周进行，请各位同学保持宿舍整洁。",
        "请各位同学注意，校园卡充值系统已升级，请使用新系统。",
        "请各位同学关注学校官方微信公众号，及时获取最新通知。",
        "学生活动报名已开始，感兴趣的同学请及时报名参加。",
        "请各位同学注意，课程表有调整，请查看最新版本。",
        "请各位同学按时参加早操，出勤情况将计入体育成绩。",
        "学生证年检工作已开始，请各位同学到学生处办理。",
        "请各位同学注意，食堂就餐时间有调整，请查看通知。"
    ]
    
    # 生成教师通知
    staff_created = 0
    for i in range(30):
        staff = random.choice(staffs)
        message = random.choice(staff_notifications)
        
        # 随机生成创建时间（过去30天内）
        days_ago = random.randint(1, 30)
        created_time = timezone.now() - timedelta(days=days_ago)
        
        try:
            notification = NotificationStaff.objects.create(
                staff=staff,
                message=message
            )
            # 更新创建时间
            notification.created_at = created_time
            notification.save()
            staff_created += 1
        except Exception as e:
            print(f"创建教师通知失败: {e}")
    
    # 生成学生通知
    student_created = 0
    for i in range(60):
        student = random.choice(students)
        message = random.choice(student_notifications)
        
        # 随机生成创建时间（过去30天内）
        days_ago = random.randint(1, 30)
        created_time = timezone.now() - timedelta(days=days_ago)
        
        try:
            notification = NotificationStudent.objects.create(
                student=student,
                message=message
            )
            # 更新创建时间
            notification.created_at = created_time
            notification.save()
            student_created += 1
        except Exception as e:
            print(f"创建学生通知失败: {e}")
    
    print(f"已生成 {staff_created} 条教师通知，现有教师通知总数: {NotificationStaff.objects.count()}\n")
    print(f"已生成 {student_created} 条学生通知，现有学生通知总数: {NotificationStudent.objects.count()}\n")

def main():
    print("=" * 80)
    print("开始生成测试数据")
    print("=" * 80)
    print()
    
    # 1. 清理不完整数据
    clean_incomplete_data()
    
    # 2. 生成基础数据
    courses = generate_courses()
    sessions = generate_sessions()
    
    # 3. 生成用户数据
    staffs = generate_staff(courses)
    students = generate_students(courses, sessions)
    
    # 4. 生成科目数据
    subjects = generate_subjects(courses, staffs)
    
    # 5. 生成业务数据
    generate_attendance(subjects, sessions, students)
    generate_feedback(students, staffs)
    generate_leave_requests(students, staffs)
    generate_results(students, subjects)
    
    # 6. 生成活动管理数据
    activities = generate_activities(staffs, students)
    generate_activity_registrations(activities, students)
    generate_activity_attendance(activities, staffs)
    generate_activity_feedback(activities, students)
    
    # 7. 生成通知数据
    generate_notifications(staffs, students)
    
    print("=" * 80)
    print("数据生成完成！")
    print("=" * 80)
    print("\n数据统计：")
    print(f"  专业: {Course.objects.count()} 个")
    print(f"  学期: {Session.objects.count()} 个")
    print(f"  教师: {Staff.objects.count()} 个")
    print(f"  学生: {Student.objects.count()} 个")
    print(f"  科目: {Subject.objects.count()} 个")
    print(f"  出勤记录: {Attendance.objects.count()} 条")
    print(f"  出勤报告: {AttendanceReport.objects.count()} 条")
    print(f"  学生反馈: {FeedbackStudent.objects.count()} 条")
    print(f"  教师反馈: {FeedbackStaff.objects.count()} 条")
    print(f"  学生请假: {LeaveReportStudent.objects.count()} 条")
    print(f"  教师请假: {LeaveReportStaff.objects.count()} 条")
    print(f"  成绩记录: {StudentResult.objects.count()} 条")
    print(f"  活动: {Activity.objects.count()} 个")
    print(f"  活动报名: {ActivityRegistration.objects.count()} 条")
    print(f"  活动签到: {ActivityAttendance.objects.count()} 条")
    print(f"  活动评价: {ActivityFeedback.objects.count()} 条")
    print(f"  教师通知: {NotificationStaff.objects.count()} 条")
    print(f"  学生通知: {NotificationStudent.objects.count()} 条")
    print()

if __name__ == "__main__":
    main()

