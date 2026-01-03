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
    学生首页视图
    显示学生的考勤统计信息，包括总科目数、总考勤次数、出勤次数和百分比
    为每个科目统计出勤和缺勤数据
    返回首页模板并传递相关数据
    """
    student = get_object_or_404(Student, admin=request.user)
    total_subject = Subject.objects.filter(course=student.course).count()
    total_attendance = AttendanceReport.objects.filter(student=student).count()
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


@ csrf_exempt
def student_view_attendance(request):
    """
    查看学生考勤记录的视图
    支持按科目和日期范围查询考勤记录
    """
    student = get_object_or_404(Student, admin=request.user)
    if request.method != 'POST':
        course = get_object_or_404(Course, id=student.course.id)
        context = {
            'subjects': Subject.objects.filter(course=course),
            'page_title': 'View Attendance'
        }
        return render(request, 'student_template/student_view_attendance.html', context)
    else:
        subject_id = request.POST.get('subject')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        try:
            subject = get_object_or_404(Subject, id=subject_id)
            start_date = datetime.strptime(start, "%Y-%m-%d")
            end_date = datetime.strptime(end, "%Y-%m-%d")
            attendance = Attendance.objects.filter(
                date__range=(start_date, end_date), subject=subject)
            attendance_reports = AttendanceReport.objects.filter(
                attendance__in=attendance, student=student)
            json_data = []
            for report in attendance_reports:
                data = {
                    "date":  str(report.attendance.date),
                    "status": report.status
                }
                json_data.append(data)
            return JsonResponse(json.dumps(json_data), safe=False)
        except Exception as e:
            return None


def student_apply_leave(request):
    """
    学生请假申请功能
    处理请假表单的提交
    显示历史请假记录
    包含表单验证和错误处理
    """
    form = LeaveReportStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStudent.objects.filter(student=student).order_by('-created_at'),
        'page_title': 'Apply for leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
                obj.student = student
                obj.save()
                messages.success(
                    request, "Application for leave has been submitted for review")
                return redirect(reverse('student_apply_leave'))
            except Exception:
                messages.error(request, "Could not submit")
        else:
            messages.error(request, "Form has errors!")
    return render(request, "student_template/student_apply_leave.html", context)


def student_feedback(request):
    """
    学生反馈功能
    处理反馈表单提交
    显示历史反馈记录
    """
    form = FeedbackStudentForm(request.POST or None)
    student = get_object_or_404(Student, admin_id=request.user.id)
    context = {
        'form': form,
        'feedbacks': FeedbackStudent.objects.filter(student=student),
        'page_title': 'Student Feedback'

    }
    if request.method == 'POST':
        if form.is_valid():
            try:
                obj = form.save(commit=False)
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
    """
    学生查看/编辑个人资料功能
    """
    student = get_object_or_404(Student, admin=request.user)
    form = StudentEditForm(request.POST or None, request.FILES or None,
                           instance=student)
    context = {'form': form,
               'page_title': 'View/Edit Profile'
               }
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                phone_number = form.cleaned_data.get('phone_number')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = student.admin
                if password != None:
                    admin.set_password(password)
                if passport != None:
                    fs = FileSystemStorage()
                    filename = fs.save(passport.name, passport)
                    passport_url = fs.url(filename)
                    admin.profile_pic = passport_url
                admin.first_name = first_name
                admin.last_name = last_name
                admin.phone_number = phone_number
                admin.gender = gender
                admin.save()
                student.save()
                messages.success(request, "Profile Updated!")
                return redirect(reverse('student_view_profile'))
            else:
                messages.error(request, "Invalid Data Provided")
        except Exception as e:
            messages.error(request, "Error Occured While Updating Profile " + str(e))

    return render(request, "student_template/student_view_profile.html", context)


@csrf_exempt
def student_fcmtoken(request):
    """处理FCM（Firebase Cloud Messaging）令牌"""
    token = request.POST.get('token')
    student_user = get_object_or_404(CustomUser, id=request.user.id)
    try:
        student_user.fcm_token = token
        student_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def student_view_notification(request):
    """
    查看通知功能
    显示学生的所有通知
    """
    student = get_object_or_404(Student, admin=request.user)
    notifications = NotificationStudent.objects.filter(student=student)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "student_template/student_view_notification.html", context)


def student_view_result(request):
    """
    查看成绩功能
    显示学生的所有成绩记录
    """
    student = get_object_or_404(Student, admin=request.user)
    results = StudentResult.objects.filter(student=student)
    context = {
        'results': results,
        'page_title': "View Results"
    }
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
