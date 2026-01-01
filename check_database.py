#!/usr/bin/env python
"""查看数据库中的所有数据"""
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

def get_gender_display(gender):
    """获取性别显示名称"""
    genders = {'M': '男', 'F': '女'}
    return genders.get(gender, '未知')

print("=" * 80)
print("数据库数据统计")
print("=" * 80)

# 用户数据
print("\n【用户数据】")
users = CustomUser.objects.all()
print(f"总用户数: {users.count()}")
if users.exists():
    for i, user in enumerate(users, 1):
        print(f"  {i}. {user.email}")
        print(f"     姓名: {user.last_name} {user.first_name}")
        print(f"     类型: {get_user_type_display(user.user_type)}")
        print(f"     性别: {get_gender_display(user.gender)}")
        print(f"     电话: {user.phone_number or '未填写'}")
        print()

# 管理员数据
print("\n【管理员数据】")
admins = Admin.objects.all()
print(f"总管理员数: {admins.count()}")
if admins.exists():
    for i, admin in enumerate(admins, 1):
        print(f"  {i}. {admin.admin.email} - {admin.admin.last_name} {admin.admin.first_name}")

# 专业数据
print("\n【专业数据】")
courses = Course.objects.all()
print(f"总专业数: {courses.count()}")
if courses.exists():
    for i, course in enumerate(courses, 1):
        print(f"  {i}. {course.name} (ID: {course.id})")

# 学期数据
print("\n【学期数据】")
sessions = Session.objects.all()
print(f"总学期数: {sessions.count()}")
if sessions.exists():
    for i, session in enumerate(sessions, 1):
        print(f"  {i}. {session} (ID: {session.id})")

# 学生数据
print("\n【学生数据】")
students = Student.objects.all()
print(f"总学生数: {students.count()}")
if students.exists():
    for i, student in enumerate(students, 1):
        course_name = student.course.name if student.course else "未分配专业"
        session_name = str(student.session) if student.session else "未分配学期"
        print(f"  {i}. {student.admin.last_name} {student.admin.first_name}")
        print(f"     邮箱: {student.admin.email}")
        print(f"     专业: {course_name}")
        print(f"     学期: {session_name}")
        print()

# 教师数据
print("\n【教师数据】")
staffs = Staff.objects.all()
print(f"总教师数: {staffs.count()}")
if staffs.exists():
    for i, staff in enumerate(staffs, 1):
        print(f"  {i}. {staff.admin.last_name} {staff.admin.first_name}")
        print(f"     邮箱: {staff.admin.email}")
        print(f"     电话: {staff.admin.phone_number or '未填写'}")
        print()

# 科目数据
print("\n【科目数据】")
subjects = Subject.objects.all()
print(f"总科目数: {subjects.count()}")
if subjects.exists():
    for i, subject in enumerate(subjects, 1):
        teacher_name = f"{subject.staff.admin.last_name} {subject.staff.admin.first_name}"
        print(f"  {i}. {subject.name}")
        print(f"     专业: {subject.course.name}")
        print(f"     授课教师: {teacher_name}")
        print()

# 出勤数据
print("\n【出勤记录】")
attendances = Attendance.objects.all()
print(f"总出勤记录数: {attendances.count()}")
if attendances.exists():
    for i, attendance in enumerate(attendances[:10], 1):  # 只显示前10条
        print(f"  {i}. {attendance.subject.name} - {attendance.date} - {attendance.session}")
    if attendances.count() > 10:
        print(f"  ... 还有 {attendances.count() - 10} 条记录")

# 出勤报告
print("\n【出勤报告】")
attendance_reports = AttendanceReport.objects.all()
print(f"总出勤报告数: {attendance_reports.count()}")

# 学生请假
print("\n【学生请假申请】")
student_leaves = LeaveReportStudent.objects.all()
print(f"总请假申请数: {student_leaves.count()}")
if student_leaves.exists():
    for i, leave in enumerate(student_leaves[:5], 1):  # 只显示前5条
        status_map = {0: '待审批', 1: '已批准', -1: '已拒绝'}
        status = status_map.get(leave.status, '未知')
        print(f"  {i}. {leave.student.admin.last_name} {leave.student.admin.first_name} - {leave.date} - {status}")
    if student_leaves.count() > 5:
        print(f"  ... 还有 {student_leaves.count() - 5} 条记录")

# 教师请假
print("\n【教师请假申请】")
staff_leaves = LeaveReportStaff.objects.all()
print(f"总请假申请数: {staff_leaves.count()}")
if staff_leaves.exists():
    for i, leave in enumerate(staff_leaves[:5], 1):  # 只显示前5条
        status_map = {0: '待审批', 1: '已批准', -1: '已拒绝'}
        status = status_map.get(leave.status, '未知')
        print(f"  {i}. {leave.staff.admin.last_name} {leave.staff.admin.first_name} - {leave.date} - {status}")
    if staff_leaves.count() > 5:
        print(f"  ... 还有 {staff_leaves.count() - 5} 条记录")

# 学生反馈
print("\n【学生反馈】")
student_feedbacks = FeedbackStudent.objects.all()
print(f"总反馈数: {student_feedbacks.count()}")

# 教师反馈
print("\n【教师反馈】")
staff_feedbacks = FeedbackStaff.objects.all()
print(f"总反馈数: {staff_feedbacks.count()}")

# 学生成绩
print("\n【学生成绩】")
results = StudentResult.objects.all()
print(f"总成绩记录数: {results.count()}")
if results.exists():
    for i, result in enumerate(results[:5], 1):  # 只显示前5条
        print(f"  {i}. {result.student.admin.last_name} {result.student.admin.first_name}")
        print(f"     科目: {result.subject.name}")
        print(f"     平时成绩: {result.test}, 考试成绩: {result.exam}")
        print()
    if results.count() > 5:
        print(f"  ... 还有 {results.count() - 5} 条记录")

print("\n" + "=" * 80)
print("数据统计完成")
print("=" * 80)

