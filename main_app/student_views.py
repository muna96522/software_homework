import json
import math
from datetime import datetime

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *


def student_home(request):
    """
    学生主页视图函数，用于获取并展示学生的出勤统计信息
    包括总课程数、出勤率、各科目的出勤情况等数据
    """
    # 获取当前登录用户对应的学生对象
    student = get_object_or_404(Student, admin=request.user)
    # 获取学生所在课程的总科目数
    total_subject = Subject.objects.filter(course=student.course).count()
    # 获取学生的总出勤记录数
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    # 获取学生出勤次数（状态为True的记录数）
    total_present = AttendanceReport.objects.filter(student=student, status=True).count()
    if total_attendance == 0:  # Don't divide. DivisionByZero
        percent_absent = percent_present = 0
    else:
        percent_present = math.floor((total_present/total_attendance) * 100)
        percent_absent = math.ceil(100 - percent_present)
    subject_name = []
    data_present = []
    data_absent = []
    subjects = Subject.objects.filter(course=student.course)
    for subject in subjects:
        attendance = Attendance.objects.filter(subject=subject)
        present_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=True, student=student).count()
        absent_count = AttendanceReport.objects.filter(
            attendance__in=attendance, status=False, student=student).count()
        subject_name.append(subject.name)
        data_present.append(present_count)
        data_absent.append(absent_count)
    context = {
        'total_attendance': total_attendance,
        'percent_present': percent_present,
        'percent_absent': percent_absent,
        'total_subject': total_subject,
        'subjects': subjects,
        'data_present': data_present,
        'data_absent': data_absent,
        'data_name': subject_name,
        'page_title': 'Student Homepage'

    }
    return render(request, 'student_template/home_content.html', context)


@ csrf_exempt  # 装饰器，用于免除当前视图的CSRF验证
def student_view_attendance(request):  # 学生查看考勤的视图函数
    # 获取当前登录用户对应的Student对象，如果不存在则返回404错误
    student = get_object_or_404(Student, admin=request.user)
    # 如果请求方法不是POST，则处理GET请求
    if request.method != 'POST':
        # 获取学生所在课程，如果不存在则返回404错误
        course = get_object_or_404(Course, id=student.course.id)
        # 构建上下文字典，包含该课程的所有科目和页面标题
        context = {
            'subjects': Subject.objects.filter(course=course),
            'page_title': 'View Attendance'
        }
        # 渲染学生查看考勤的模板页面
        return render(request, 'student_template/student_view_attendance.html', context)
    else:
        # 处理POST请求，获取科目ID、开始日期和结束日期
        subject_id = request.POST.get('subject')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        try:
            # 获取指定科目对象，如果不存在则返回404错误
            subject = get_object_or_404(Subject, id=subject_id)
            # 将字符串格式的日期转换为datetime对象
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            # 获取指定日期范围内和科目的考勤记录
            attendance = Attendance.objects.filter(
                date__range=(start_date, end_date), subject=subject)
            # 获取该学生的考勤报告
            attendance_reports = AttendanceReport.objects.filter(
                attendance__in=attendance, student=student)
            # 将考勤报告数据转换为JSON格式
            json_data = []
            for report in attendance_reports:
                data = {
                    "date":  str(report.attendance.date),
                    "status": report.status
                }
                json_data.append(data)
            # 返回JSON响应
            return JsonResponse(json.dumps(json_data), safe=False)
        except Exception as e:
            # 如果发生异常，返回None
            return None


def student_apply_leave(request):
    """
    处理学生请假申请的视图函数
    该函数负责显示请假表单、处理表单提交、保存请假记录，并提供请假历史记录
    """
    # 初始化请假表单，如果请求方法是POST则使用请求数据，否则为空
    form = LeaveReportStudentForm(request.POST or None)
    # 获取当前登录用户对应的学生信息，如果不存在则返回404错误
    student = get_object_or_404(Student, admin_id=request.user.id)
    # 构建上下文字典，包含表单、请假历史记录和页面标题
    context = {
        'form': form,  # 请假表单
        'leave_history': LeaveReportStudent.objects.filter(student=student).order_by('-created_at'),  # 按创建时间倒序排列的请假历史记录
        'page_title': 'Apply for leave'  # 页面标题
    }
    # 处理POST请求（表单提交）
    if request.method == 'POST':
        # 检查表单是否有效
        if form.is_valid():
            try:
                # 创建请假对象但不立即保存到数据库
                obj = form.save(commit=False)
                # 设置学生字段为当前学生
                obj.student = student
                # 保存请假记录到数据库
                obj.save()
                # 显示成功消息
                messages.success(
                    request, "Application for leave has been submitted for review")
                # 重定向到同一页面，显示提交成功后的状态
                return redirect(reverse('student_apply_leave'))
            except Exception:  # 处理可能出现的异常
                messages.error(request, "Could not submit")
        else:  # 表单验证失败
            messages.error(request, "Form has errors!")
    # 渲染请假申请页面模板并返回上下文
    return render(request, "student_template/student_apply_leave.html", context)


def student_feedback(request):
    # 创建反馈表单实例，如果请求方法是POST则使用请求数据，否则为空
    form = FeedbackStudentForm(request.POST or None)
    # 获取当前登录用户对应的学生对象，如果不存在则返回404错误
    student = get_object_or_404(Student, admin_id=request.user.id)
    # 准备模板上下文数据
    context = {
        'form': form,                    # 反馈表单
        'feedbacks': FeedbackStudent.objects.filter(student=student),  # 当前学生的所有反馈记录
        'page_title': 'Student Feedback'  # 页面标题

    }
    # 处理POST请求（表单提交）
    if request.method == 'POST':
        # 检查表单数据是否有效
        if form.is_valid():
            try:
                # 创建反馈对象但不立即保存到数据库
                obj = form.save(commit=False)
                # 关联当前学生对象
                obj.student = student
                obj.save()
                messages.success(
                    request, "Feedback submitted for review")
                return redirect(reverse('student_feedback'))
            except Exception:
                messages.error(request, "Could not Submit!")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/student_feedback.html", context)


def student_view_profile(request):
    # 获取当前登录用户对应的Student对象，如果不存在则返回404错误
    student = get_object_or_404(Student, admin=request.user)
    # 创建表单实例，用于编辑学生信息
    # 如果是POST请求，则使用提交的数据和文件初始化表单
    # 否则，使用当前学生信息初始化表单
    form = StudentEditForm(request.POST or None, request.FILES or None,
                           instance=student)
    # 初始化上下文字典，包含表单和页面标题
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    # 处理POST请求（表单提交）
    if request.method == 'POST':
        try:
            # 验证表单数据
            if form.is_valid():
                # 获取表单中的各个字段数据
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                phone_number = form.cleaned_data.get('phone_number')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                # 获取学生关联的admin账户
                admin = student.admin
                # 如果提供了新密码，则更新密码
                if password != None:
                    admin.set_password(password)
                # 如果上传了新头像，则保存头像文件并更新头像URL
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                # 更新admin账户的各项信息
                admin.first_name = first_name
                admin.last_name = last_name
                admin.phone_number = phone_number
                admin.gender = gender
                admin.save()
                student.save()
                # 显示成功消息并重定向回个人资料页面
                messages.success(request, "Profile Updated!")
                return redirect(reverse('student_view_profile'))
            else:
                # 如果表单数据无效，显示错误消息
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            # 捕获并处理更新过程中可能出现的任何异常
            messages.error(request, "Error Occured While Updating Profile " + str(e))

    # 渲染学生个人资料编辑模板并返回上下文
    return render(request, "student_template/student_view_profile.html", context)


@csrf_exempt  # 使用此装饰器来免除此视图的CSRF保护
def student_fcmtoken(request):
    """
    处理学生FCM(Firebase Cloud Messaging)令牌的视图函数
    用于更新学生的FCM令牌，以便接收推送通知
    Args:
        request: HTTP请求对象，包含客户端发送的数据
    Returns:
        HttpResponse: 成功时返回"True"，失败时返回"False"
    """
    # 从POST请求中获取FCM令牌
    token = request.POST.get('token')
    # 获取当前登录的用户对象，如果不存在则返回404错误
    student_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        # 更新用户的FCM令牌
        student_user.fcm_token = token
        # 保存用户对象到数据库
        student_user.save()
        # 返回成功响应
        return HttpResponse("True")
    except Exception as e:
        # 捕获任何可能的异常并返回失败响应
        return HttpResponse("False")


def student_view_notification(request):
    """
    学生查看通知的视图函数
    该函数用于获取当前登录学生用户的所有通知信息，并将其传递给前端模板进行展示
    参数:
        request: HTTP请求对象，包含请求的各类信息
    返回:
        渲染后的HTML页面，包含当前学生的所有通知信息
    """
    # 获取当前登录用户对应的学生对象，如果不存在则返回404错误
    student = get_object_or_404(Student, admin=request.user)
    # 获取该学生相关的所有通知记录
    notifications = NotificationStudent.objects.filter(student=student)
    # 创建上下文字典，包含通知列表和页面标题
    context = {
        'notifications': notifications,  # 通知列表
        'page_title': "View Notifications"  # 页面标题
    }
    # 渲染模板并返回响应
    return render(request, "student_template/student_view_notification.html", context)


def student_view_result(request):
    """
    学生查看自己成绩的视图函数
    该函数会获取当前登录学生的所有成绩信息，并渲染到模板中
    """
    # 获取当前登录用户对应的学生对象，如果不存在则返回404错误
    student = get_object_or_404(Student, admin=request.user)
    # 获取该学生的所有成绩记录
    results = StudentResult.objects.filter(student=student)
    # 创建上下文字典，包含成绩数据和页面标题
    context = {
        'results': results,  # 成绩结果列表
        'page_title': "View Results"  # 页面标题
    }
    # 渲染模板并返回响应
    return render(request, "student_template/student_view_result.html", context)


# 校园活动管理 - 学生功能
def student_view_activities(request):
    """学生查看可报名的活动列表"""
    student = get_object_or_404(Student, admin=request.user)
    
    # 只显示已通过审批的活动，使用select_related优化查询
    activities = Activity.objects.filter(status=1).select_related('organizer', 'organizer__admin').prefetch_related('activityregistration_set').order_by('-created_at')
    
    # 获取学生已报名的活动ID列表
    registered_activity_ids = ActivityRegistration.objects.filter(
        student=student
    ).values_list('activity_id', flat=True)
    
    # 获取学生已评价的活动ID列表
    feedback_activity_ids = ActivityFeedback.objects.filter(
        student=student
    ).values_list('activity_id', flat=True)
    
    context = {
        'page_title': '校园活动',
        'activities': activities,
        'registered_activity_ids': set(registered_activity_ids),
        'feedback_activity_ids': set(feedback_activity_ids)
    }
    return render(request, 'student_template/view_activities.html', context)


def student_register_activity(request, activity_id):
    """学生报名活动"""
    activity = get_object_or_404(Activity, id=activity_id)
    student = get_object_or_404(Student, admin=request.user)
    
    # 检查活动是否已通过审批
    if activity.status != 1:
        messages.error(request, "该活动尚未通过审批，无法报名")
        return redirect(reverse('student_view_activities'))
    
    # 检查是否已报名
    if ActivityRegistration.objects.filter(activity=activity, student=student).exists():
        messages.warning(request, "您已经报名过此活动")
        return redirect(reverse('student_view_activities'))
    
    # 检查人数限制
    if activity.max_participants > 0:
        current_count = ActivityRegistration.objects.filter(activity=activity).count()
        if current_count >= activity.max_participants:
            messages.error(request, "该活动报名人数已满")
            return redirect(reverse('student_view_activities'))
    
    # 创建报名记录
    try:
        ActivityRegistration.objects.create(activity=activity, student=student)
        messages.success(request, "报名成功！")
    except Exception as e:
        messages.error(request, f"报名失败：{str(e)}")
    
    return redirect(reverse('student_view_activities'))


def student_my_activities(request):
    """学生查看自己报名的活动"""
    student = get_object_or_404(Student, admin=request.user)
    # 使用select_related和prefetch_related优化查询
    registrations = ActivityRegistration.objects.filter(
        student=student
    ).select_related('activity', 'activity__organizer', 'activity__organizer__admin').prefetch_related('activity__activityattendance_set').order_by('-registered_at')
    
    # 获取已评价的活动ID
    feedback_activity_ids = ActivityFeedback.objects.filter(
        student=student
    ).values_list('activity_id', flat=True)
    
    # 获取所有签到记录，使用字典优化查找
    attendance_records = ActivityAttendance.objects.filter(
        student=student
    ).select_related('activity')
    attendance_dict = {record.activity.id: record for record in attendance_records}
    
    # 为每个报名记录添加签到状态
    for reg in registrations:
        if reg.activity.id in attendance_dict:
            reg.attendance = attendance_dict[reg.activity.id]
        else:
            reg.attendance = None
    
    context = {
        'page_title': '我的活动',
        'registrations': registrations,
        'feedback_activity_ids': set(feedback_activity_ids)
    }
    return render(request, 'student_template/my_activities.html', context)


def student_feedback_activity(request, activity_id):
    """学生对活动进行评价"""
    activity = get_object_or_404(Activity, id=activity_id)
    student = get_object_or_404(Student, admin=request.user)
    
    # 检查是否已报名
    if not ActivityRegistration.objects.filter(activity=activity, student=student).exists():
        messages.error(request, "您未报名此活动，无法评价")
        return redirect(reverse('student_my_activities'))
    
    # 检查是否已评价
    if ActivityFeedback.objects.filter(activity=activity, student=student).exists():
        messages.warning(request, "您已经评价过此活动")
        return redirect(reverse('student_my_activities'))
    
    form = ActivityFeedbackForm(request.POST or None)
    context = {
        'page_title': '活动评价',
        'activity': activity,
        'form': form
    }
    
    if request.method == 'POST':
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.activity = activity
            feedback.student = student
            feedback.save()
            messages.success(request, "评价提交成功！")
            return redirect(reverse('student_my_activities'))
        else:
            messages.error(request, "表单验证失败，请检查输入")
    
    return render(request, 'student_template/feedback_activity.html', context)
