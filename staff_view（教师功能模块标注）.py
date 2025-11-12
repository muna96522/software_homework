import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404, redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *

"""
教师视图模块 - 处理教师相关的所有业务逻辑
功能：教师工作台、考勤管理、成绩录入、请假反馈等核心功能
包含：教师主页统计、考勤记录、成绩管理、个人资料等视图函数
"""

# 教师主页视图
def staff_home(request):
    """
    类级别：教师主页视图
    职责：显示教师工作台的核心统计数据和图表
    设计意图：为教师提供教学活动的概览视图
    """
    # 获取当前登录的教师对象
    staff = get_object_or_404(Staff, admin=request.user)

    # 统计该教师负责课程的学生总数
    total_students = Student.objects.filter(course=staff.course).count()

    # 统计该教师的请假申请总数
    total_leave = LeaveReportStaff.objects.filter(staff=staff).count()

    # 获取该教师负责的所有科目
    subjects = Subject.objects.filter(staff=staff)
    total_subject = subjects.count()

    # 统计该教师所有科目的考勤记录总数
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()

    # 初始化图表数据列表
    attendance_list = []
    subject_list = []

    # 语句块级别：为每个科目生成考勤统计数据和科目名称列表
    for subject in subjects:
        # 统计当前科目的考勤次数
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name)  # 科目名称列表
        attendance_list.append(attendance_count)  # 考勤次数列表

    # 构建上下文数据传递给模板
    context = {
        'page_title': 'Staff Panel - ' + str(staff.admin.last_name) + ' (' + str(staff.course) + ')',
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_leave': total_leave,
        'total_subject': total_subject,
        'subject_list': subject_list,  # 用于图表显示的科目列表
        'attendance_list': attendance_list  # 用于图表显示的考勤数据
    }
    return render(request, 'staff_template/home_content.html', context)


# 教师考勤录入视图
def staff_take_attendance(request):
    """
    方法级别：教师考勤录入页面
    功能：显示考勤录入界面，包含科目和学期选择
    """
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Take Attendance'
    }
    return render(request, 'staff_template/staff_take_attendance.html', context)


@csrf_exempt  # 豁免CSRF保护，用于AJAX请求
def get_students(request):
    """
    方法级别：获取学生列表AJAX接口
    功能：根据选择的科目和学期动态加载学生名单
    参数：subject_id - 科目ID, session_id - 学期ID
    返回值：JSON格式的学生数据列表
    """
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)

        # 关键语句级别：筛选符合条件的学生（同一课程和学期）
        students = Student.objects.filter(
            course_id=subject.course.id, session=session)

        student_data = []
        # 语句块级别：构建学生数据JSON结构
        for student in students:
            data = {
                "id": student.id,
                "name": student.admin.last_name + " " + student.admin.first_name
            }
            student_data.append(data)

        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def save_attendance(request):
    """
    方法级别：保存考勤数据
    功能：处理前端提交的考勤记录并保存到数据库
    业务逻辑：使用get_or_create避免重复创建考勤记录
    """
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    students = json.loads(student_data)

    try:
        session = get_object_or_404(Session, id=session_id)
        subject = get_object_or_404(Subject, id=subject_id)

        # 关键语句级别：获取或创建考勤主记录（按日期、学期、科目）
        attendance, created = Attendance.objects.get_or_create(
            session=session, subject=subject, date=date)

        # 语句块级别：处理每个学生的考勤状态
        for student_dict in students:
            student = get_object_or_404(Student, id=student_dict.get('id'))

            # 关键语句级别：获取或创建考勤详情记录
            attendance_report, report_created = AttendanceReport.objects.get_or_create(
                student=student, attendance=attendance)

            # 仅在新创建记录时更新状态，避免覆盖已有数据
            if report_created:
                attendance_report.status = student_dict.get('status')
                attendance_report.save()

    except Exception as e:
        return None

    return HttpResponse("OK")


# 考勤更新视图
def staff_update_attendance(request):
    """
    方法级别：考勤更新页面
    功能：提供修改已有考勤记录的界面
    """
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Update Attendance'
    }
    return render(request, 'staff_template/staff_update_attendance.html', context)


@csrf_exempt
def get_student_attendance(request):
    """
    方法级别：获取学生考勤数据AJAX接口
    功能：根据考勤日期ID返回学生的考勤状态
    """
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        date = get_object_or_404(Attendance, id=attendance_date_id)
        attendance_data = AttendanceReport.objects.filter(attendance=date)
        student_data = []

        # 语句块级别：构建学生考勤状态数据
        for attendance in attendance_data:
            data = {"id": attendance.student.admin.id,
                    "name": attendance.student.admin.last_name + " " + attendance.student.admin.first_name,
                    "status": attendance.status}
            student_data.append(data)

        return JsonResponse(json.dumps(student_data), content_type='application/json', safe=False)
    except Exception as e:
        return e


@csrf_exempt
def update_attendance(request):
    """
    方法级别：更新考勤数据
    功能：批量更新学生的考勤状态
    """
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    students = json.loads(student_data)

    try:
        attendance = get_object_or_404(Attendance, id=date)

        # 语句块级别：遍历更新每个学生的考勤状态
        for student_dict in students:
            student = get_object_or_404(
                Student, admin_id=student_dict.get('id'))
            attendance_report = get_object_or_404(
                AttendanceReport, student=student, attendance=attendance)
            attendance_report.status = student_dict.get('status')
            attendance_report.save()

    except Exception as e:
        return None

    return HttpResponse("OK")


# 教师请假申请视图
def staff_apply_leave(request):
    """
    方法级别：教师请假申请处理
    功能：处理教师的请假申请表单提交和显示
    """
    form = LeaveReportStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStaff.objects.filter(staff=staff),
        'page_title': 'Apply for Leave'
    }

    if request.method == 'POST':
        if form.is_valid():
            try:
                # 关键语句级别：保存表单但不提交，先关联教师对象
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('staff_apply_leave'))
            except Exception:
                messages.error(request, "Could not apply!")
        else:
            messages.error(request, "Form has errors!")

    return render(request, "staff_template/staff_apply_leave.html", context)


# 教师反馈提交视图
def staff_feedback(request):
    """
    方法级别：教师反馈处理
    功能：处理教师的反馈信息提交和显示
    """
    form = FeedbackStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStaff.objects.filter(staff=staff),
        'page_title': 'Add Feedback'
    }

    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.staff = staff
                obj.save()
                messages.success(request, "Feedback submitted for review")
                return redirect(reverse('staff_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")

    return render(request, "staff_template/staff_feedback.html", context)


# 教师个人信息查看和更新视图
def staff_view_profile(request):
    """
    方法级别：教师个人信息管理
    功能：显示和更新教师个人资料，包括密码和头像
    """
    staff = get_object_or_404(Staff, admin=request.user)
    form = StaffEditForm(request.POST or None, request.FILES or None, instance=staff)
    context = {'form': form, 'page_title': 'View/Update Profile'}

    if request.method == 'POST':
        try:
            if form.is_valid():
                # 获取表单清理后的数据
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                address = form.cleaned_data.get('address')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = staff.admin

                # 关键语句级别：密码更新逻辑（仅在提供新密码时更新）
                if password != None:
                    admin.set_password(password)

                # 关键语句级别：头像文件处理
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url

                # 更新用户基本信息
                admin.first_name = first_name
                admin.last_name = last_name
                admin.address = address
                admin.gender = gender
                admin.save()
                staff.save()

                messages.success(request, "Profile Updated!")
                return redirect(reverse('staff_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
                return render(request, "staff_template/staff_view_profile.html", context)

        except Exception as e:
            messages.error(
                request, "Error Occured While Updating Profile " + str(e))
            return render(request, "staff_template/staff_view_profile.html", context)

    return render(request, "staff_template/staff_view_profile.html", context)


@csrf_exempt
def staff_fcmtoken(request):
    """
    方法级别：FCM令牌更新
    功能：更新教师的Firebase Cloud Messaging令牌用于推送通知
    参数：token - FCM设备令牌
    返回值：操作成功状态
    """
    token = request.POST.get('token')
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


# 教师通知查看视图
def staff_view_notification(request):
    """
    方法级别：教师通知管理
    功能：显示发送给教师的所有系统通知
    """
    staff = get_object_or_404(Staff, admin=request.user)
    notifications = NotificationStaff.objects.filter(staff=staff)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "staff_template/staff_view_notification.html", context)


# 学生成绩录入视图
def staff_add_result(request):
    """
    方法级别：学生成绩录入
    功能：教师录入或更新学生的考试成绩
    """
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff=staff)
    sessions = Session.objects.all()
    context = {
        'page_title': 'Result Upload',
        'subjects': subjects,
        'sessions': sessions
    }

    if request.method == 'POST':
        try:
            # 获取表单数据
            student_id = request.POST.get('student_list')
            subject_id = request.POST.get('subject')
            test = request.POST.get('test')  # 平时成绩
            exam = request.POST.get('exam')  # 考试成绩

            student = get_object_or_404(Student, id=student_id)
            subject = get_object_or_404(Subject, id=subject_id)

            try:
                # 关键语句级别：更新已有成绩记录
                data = StudentResult.objects.get(
                    student=student, subject=subject)
                data.exam = exam
                data.test = test
                data.save()
                messages.success(request, "Scores Updated")
            except:
                # 关键语句级别：创建新的成绩记录
                result = StudentResult(student=student, subject=subject, test=test, exam=exam)
                result.save()
                messages.success(request, "Scores Saved")

        except Exception as e:
            messages.warning(request, "Error Occured While Processing Form")

    return render(request, "staff_template/staff_add_result.html", context)


@csrf_exempt
def fetch_student_result(request):
    """
    方法级别：获取学生成绩AJAX接口
    功能：根据学生和科目查询已有的成绩记录
    返回值：JSON格式的成绩数据
    """
    try:
        subject_id = request.POST.get('subject')
        student_id = request.POST.get('student')
        student = get_object_or_404(Student, id=student_id)
        subject = get_object_or_404(Subject, id=subject_id)
        result = StudentResult.objects.get(student=student, subject=subject)
        result_data = {
            'exam': result.exam,
            'test': result.test
        }
        return HttpResponse(json.dumps(result_data))
    except Exception as e:
        return HttpResponse('False')