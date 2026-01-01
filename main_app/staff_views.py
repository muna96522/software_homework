import json

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import *
from .models import *


def staff_home(request):
    staff = get_object_or_404(Staff, admin=request.user)
    # 获取该教师教授的所有科目，然后统计这些科目下的所有学生
    subjects = Subject.objects.filter(staff=staff)
    # 获取这些科目所属的专业
    courses = Course.objects.filter(subject__in=subjects).distinct()
    # 统计这些专业下的所有学生
    total_students = Student.objects.filter(course__in=courses).count()
    total_leave = LeaveReportStaff.objects.filter(staff=staff).count()
    total_subject = subjects.count()
    attendance_list = Attendance.objects.filter(subject__in=subjects)
    total_attendance = attendance_list.count()
    attendance_list = []
    subject_list = []
    for subject in subjects:
        attendance_count = Attendance.objects.filter(subject=subject).count()
        subject_list.append(subject.name)
        attendance_list.append(attendance_count)
    context = {
        'page_title': '教师工作面板 - ' + str(staff.admin.last_name),
        'total_students': total_students,
        'total_attendance': total_attendance,
        'total_leave': total_leave,
        'total_subject': total_subject,
        'subject_list': subject_list,
        'attendance_list': attendance_list
    }
    return render(request, 'staff_template/home_content.html', context)


def staff_take_attendance(request):
    staff = get_object_or_404(Staff, admin=request.user)
    subjects = Subject.objects.filter(staff_id=staff)
    sessions = Session.objects.all()
    context = {
        'subjects': subjects,
        'sessions': sessions,
        'page_title': 'Take Attendance'
    }

    return render(request, 'staff_template/staff_take_attendance.html', context)


@csrf_exempt
def get_students(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        students = Student.objects.filter(
            course_id=subject.course.id, session=session)
        student_data = []
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
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    students = json.loads(student_data)
    try:
        session = get_object_or_404(Session, id=session_id)
        subject = get_object_or_404(Subject, id=subject_id)

        # Check if an attendance object already exists for the given date and session
        attendance, created = Attendance.objects.get_or_create(session=session, subject=subject, date=date)

        for student_dict in students:
            student = get_object_or_404(Student, id=student_dict.get('id'))

            # Check if an attendance report already exists for the student and the attendance object
            attendance_report, report_created = AttendanceReport.objects.get_or_create(student=student, attendance=attendance)

            # Update the status only if the attendance report was newly created
            if report_created:
                attendance_report.status = student_dict.get('status')
                attendance_report.save()

    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_update_attendance(request):
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
    attendance_date_id = request.POST.get('attendance_date_id')
    try:
        date = get_object_or_404(Attendance, id=attendance_date_id)
        attendance_data = AttendanceReport.objects.filter(attendance=date)
        student_data = []
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
    student_data = request.POST.get('student_ids')
    date = request.POST.get('date')
    students = json.loads(student_data)
    try:
        attendance = get_object_or_404(Attendance, id=date)

        for student_dict in students:
            student = get_object_or_404(
                Student, admin_id=student_dict.get('id'))
            attendance_report = get_object_or_404(AttendanceReport, student=student, attendance=attendance)
            attendance_report.status = student_dict.get('status')
            attendance_report.save()
    except Exception as e:
        return None

    return HttpResponse("OK")


def staff_apply_leave(request):
    form = LeaveReportStaffForm(request.POST or None)
    staff = get_object_or_404(Staff, admin_id=request.user.id)
    context = {
        'form': form,
        'leave_history': LeaveReportStaff.objects.filter(staff=staff).order_by('-created_at'),
        'page_title': 'Apply for Leave'
    }
    if request.method == 'POST':
        if form.is_valid():
            try:
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


def staff_feedback(request):
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


def staff_view_profile(request):
    staff = get_object_or_404(Staff, admin=request.user)
    form = StaffEditForm(request.POST or None, request.FILES or None,instance=staff)
    context = {'form': form, 'page_title': 'View/Update Profile'}
    if request.method == 'POST':
        try:
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                password = form.cleaned_data.get('password') or None
                phone_number = form.cleaned_data.get('phone_number')
                gender = form.cleaned_data.get('gender')
                passport = request.FILES.get('profile_pic') or None
                admin = staff.admin
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
    token = request.POST.get('token')
    try:
        staff_user = get_object_or_404(CustomUser, id=request.user.id)
        staff_user.fcm_token = token
        staff_user.save()
        return HttpResponse("True")
    except Exception as e:
        return HttpResponse("False")


def staff_view_notification(request):
    staff = get_object_or_404(Staff, admin=request.user)
    notifications = NotificationStaff.objects.filter(staff=staff)
    context = {
        'notifications': notifications,
        'page_title': "View Notifications"
    }
    return render(request, "staff_template/staff_view_notification.html", context)


def staff_add_result(request):
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
            student_id = request.POST.get('student_list')
            subject_id = request.POST.get('subject')
            test = request.POST.get('test')
            exam = request.POST.get('exam')
            student = get_object_or_404(Student, id=student_id)
            subject = get_object_or_404(Subject, id=subject_id)
            try:
                data = StudentResult.objects.get(
                    student=student, subject=subject)
                data.exam = exam
                data.test = test
                data.save()
                messages.success(request, "Scores Updated")
            except:
                result = StudentResult(student=student, subject=subject, test=test, exam=exam)
                result.save()
                messages.success(request, "Scores Saved")
        except Exception as e:
            messages.warning(request, "Error Occured While Processing Form")
    return render(request, "staff_template/staff_add_result.html", context)


@csrf_exempt
def fetch_student_result(request):
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


# 校园活动管理 - 教师功能
def staff_create_activity(request):
    """教师发起活动"""
    staff = get_object_or_404(Staff, admin=request.user)
    form = ActivityForm(request.POST or None)
    context = {
        'page_title': '发起活动',
        'form': form
    }
    
    if request.method == 'POST':
        if form.is_valid():
            activity = form.save(commit=False)
            activity.organizer = staff
            activity.status = 0  # 待审批
            activity.save()
            messages.success(request, "活动已提交，等待管理员审批")
            return redirect(reverse('staff_my_activities'))
        else:
            messages.error(request, "表单验证失败，请检查输入")
    
    return render(request, 'staff_template/create_activity.html', context)


def staff_my_activities(request):
    """教师查看自己发起的活动"""
    staff = get_object_or_404(Staff, admin=request.user)
    # 使用prefetch_related优化查询
    activities = Activity.objects.filter(organizer=staff).prefetch_related('activityregistration_set').order_by('-created_at')
    context = {
        'page_title': '我的活动',
        'activities': activities
    }
    return render(request, 'staff_template/my_activities.html', context)


def staff_view_registrations(request, activity_id):
    """教师查看活动报名情况"""
    activity = get_object_or_404(Activity, id=activity_id)
    # 检查是否是活动发起人
    staff = get_object_or_404(Staff, admin=request.user)
    if activity.organizer != staff:
        messages.error(request, "您无权查看此活动的报名情况")
        return redirect(reverse('staff_my_activities'))
    
    # 使用select_related和prefetch_related优化查询
    registrations = ActivityRegistration.objects.filter(activity=activity).select_related('student', 'student__admin').prefetch_related('student__activityattendance_set').order_by('-registered_at')
    
    # 获取签到记录，使用字典优化查找
    attendance_records = ActivityAttendance.objects.filter(activity=activity).select_related('student')
    attendance_dict = {record.student.id: record for record in attendance_records}
    
    # 为每个报名记录添加签到状态
    for reg in registrations:
        if reg.student.id in attendance_dict:
            reg.attendance = attendance_dict[reg.student.id]
        else:
            reg.attendance = None
    
    context = {
        'page_title': '查看报名情况',
        'activity': activity,
        'registrations': registrations
    }
    return render(request, 'staff_template/view_registrations.html', context)


def staff_check_attendance(request, activity_id):
    """教师确认活动签到"""
    activity = get_object_or_404(Activity, id=activity_id)
    # 检查是否是活动发起人
    staff = get_object_or_404(Staff, admin=request.user)
    if activity.organizer != staff:
        messages.error(request, "您无权管理此活动的签到")
        return redirect(reverse('staff_my_activities'))
    
    # 获取已报名的学生
    registrations = ActivityRegistration.objects.filter(activity=activity)
    students = [reg.student for reg in registrations]
    
    # 获取已签到的记录，为每个学生添加签到状态
    attendance_records = ActivityAttendance.objects.filter(activity=activity)
    attendance_dict = {record.student.id: record for record in attendance_records}
    
    # 为每个学生添加签到状态
    for student in students:
        if student.id in attendance_dict:
            student.attendance = attendance_dict[student.id]
        else:
            student.attendance = None
    
    context = {
        'page_title': '确认签到',
        'activity': activity,
        'students': students,
        'attendance_dict': attendance_dict
    }
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        is_present = request.POST.get('is_present') == 'true'
        
        try:
            student = get_object_or_404(Student, id=student_id)
            attendance, created = ActivityAttendance.objects.get_or_create(
                activity=activity,
                student=student,
                defaults={'is_present': is_present, 'checked_by': staff}
            )
            if not created:
                attendance.is_present = is_present
                attendance.checked_by = staff
                attendance.save()
            
            messages.success(request, f"签到记录已更新：{student.admin.last_name}{student.admin.first_name}")
        except Exception as e:
            messages.error(request, f"更新签到记录失败：{str(e)}")
        
        return redirect(reverse('staff_check_attendance', args=[activity_id]))
    
    return render(request, 'staff_template/check_attendance.html', context)
