"""
    Web应用的部分视图函数
"""
import json
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect
from django.views.decorators.http import require_http_methods

from .models import Attendance, Session, Subject
from .multi_role_auth import (
    set_user_to_role_session,
    remove_user_from_role_session,
    get_user_from_role_session,
    is_role_authenticated
)

# Create your views here.


@ensure_csrf_cookie
def login_page(request):
    # 检查是否有任何角色已登录，如果有则重定向到对应首页
    if is_role_authenticated(request, '1'):
            return redirect(reverse("admin_home"))
    elif is_role_authenticated(request, '2'):
            return redirect(reverse("staff_home"))
    elif is_role_authenticated(request, '3'):
            return redirect(reverse("student_home"))
    return render(request, 'main_app/login.html')


def doLogin(request, **kwargs):
    """兼容旧的登录方式，保持向后兼容"""
    if request.method != 'POST':
        return HttpResponse("<h4>拒绝访问</h4>")
    else:
        # Google recaptcha - 已注释，不再使用
        # captcha_token = request.POST.get('g-recaptcha-response')
        # captcha_url = "https://www.google.com/recaptcha/api/siteverify"
        # captcha_key = "6LfswtgZAAAAABX9gbLqe-d97qE2g1JP8oUYritJ"
        # data = {
        #     'secret': captcha_key,
        #     'response': captcha_token
        # }
        # # Make request
        # try:
        #     captcha_server = requests.post(url=captcha_url, data=data)
        #     response = json.loads(captcha_server.text)
        #     if response['success'] == False:
        #         messages.error(request, '验证码无效，请重试')
        #         return redirect('/')
        # except:
        #     messages.error(request, '验证码验证失败，请重试')
        #     return redirect('/')
        
        #Authenticate
        user = authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user != None:
            login(request, user)
            if user.user_type == '1':
                return redirect(reverse("admin_home"))
            elif user.user_type == '2':
                return redirect(reverse("staff_home"))
            else:
                return redirect(reverse("student_home"))
        else:
            messages.error(request, "登录信息无效")
            return redirect("/")


def do_admin_login(request):
    """管理员登录"""
    if request.method != 'POST':
        return HttpResponse("<h4>拒绝访问</h4>")
    else:
        # Google recaptcha - 已注释，不再使用
        # captcha_token = request.POST.get('g-recaptcha-response')
        # captcha_url = "https://www.google.com/recaptcha/api/siteverify"
        # captcha_key = "6LfswtgZAAAAABX9gbLqe-d97qE2g1JP8oUYritJ"
        # data = {
        #     'secret': captcha_key,
        #     'response': captcha_token
        # }
        # # Make request
        # try:
        #     captcha_server = requests.post(url=captcha_url, data=data, timeout=5)
        #     response = json.loads(captcha_server.text)
        #     if response.get('success') == False:
        #         messages.error(request, '验证码无效，请重试')
        #         return redirect('/')
        # except Exception as e:
        #     # 在开发环境中，如果验证码验证失败，记录错误但继续
        #     import logging
        #     logger = logging.getLogger(__name__)
        #     logger.warning(f'reCAPTCHA验证失败: {str(e)}')
        #     # 可以选择在开发环境中跳过验证码验证
        #     # messages.error(request, '验证码验证失败，请重试')
        #     # return redirect('/')
        
        #Authenticate
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            # 验证用户类型
            if str(user.user_type) != '1':
                messages.error(request, "该账号不是管理员账号，请使用正确的登录入口")
                return redirect("/")
            # 使用多角色session存储，而不是Django默认的login()
            set_user_to_role_session(request, user, '1')
            messages.success(request, f"管理员 {user.email} 登录成功")
            return redirect(reverse("admin_home"))
        else:
            messages.error(request, "邮箱或密码错误")
            return redirect("/")


def do_teacher_login(request):
    """教师登录"""
    if request.method != 'POST':
        return HttpResponse("<h4>拒绝访问</h4>")
    else:
        # Google recaptcha - 已注释，不再使用
        # captcha_token = request.POST.get('g-recaptcha-response')
        # captcha_url = "https://www.google.com/recaptcha/api/siteverify"
        # captcha_key = "6LfswtgZAAAAABX9gbLqe-d97qE2g1JP8oUYritJ"
        # data = {
        #     'secret': captcha_key,
        #     'response': captcha_token
        # }
        # # Make request
        # try:
        #     captcha_server = requests.post(url=captcha_url, data=data, timeout=5)
        #     response = json.loads(captcha_server.text)
        #     if response.get('success') == False:
        #         messages.error(request, '验证码无效，请重试')
        #         return redirect('/')
        # except Exception as e:
        #     # 在开发环境中，如果验证码验证失败，记录错误但继续
        #     import logging
        #     logger = logging.getLogger(__name__)
        #     logger.warning(f'reCAPTCHA验证失败: {str(e)}')
        #     # 可以选择在开发环境中跳过验证码验证
        #     # messages.error(request, '验证码验证失败，请重试')
        #     # return redirect('/')
        
        #Authenticate
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            # 验证用户类型
            if str(user.user_type) != '2':
                messages.error(request, "该账号不是教师账号，请使用正确的登录入口")
                return redirect("/")
            # 使用多角色session存储，而不是Django默认的login()
            set_user_to_role_session(request, user, '2')
            messages.success(request, f"教师 {user.email} 登录成功")
            return redirect(reverse("staff_home"))
        else:
            messages.error(request, "邮箱或密码错误")
            return redirect("/")


def do_student_login(request):
    """学生登录"""
    if request.method != 'POST':
        return HttpResponse("<h4>拒绝访问</h4>")
    else:
        # Google recaptcha - 已注释，不再使用
        # captcha_token = request.POST.get('g-recaptcha-response')
        # captcha_url = "https://www.google.com/recaptcha/api/siteverify"
        # captcha_key = "6LfswtgZAAAAABX9gbLqe-d97qE2g1JP8oUYritJ"
        # data = {
        #     'secret': captcha_key,
        #     'response': captcha_token
        # }
        # # Make request
        # try:
        #     captcha_server = requests.post(url=captcha_url, data=data, timeout=5)
        #     response = json.loads(captcha_server.text)
        #     if response.get('success') == False:
        #         messages.error(request, '验证码无效，请重试')
        #         return redirect('/')
        # except Exception as e:
        #     # 在开发环境中，如果验证码验证失败，记录错误但继续
        #     import logging
        #     logger = logging.getLogger(__name__)
        #     logger.warning(f'reCAPTCHA验证失败: {str(e)}')
        #     # 可以选择在开发环境中跳过验证码验证
        #     # messages.error(request, '验证码验证失败，请重试')
        #     # return redirect('/')
        
        #Authenticate
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            # 验证用户类型
            if str(user.user_type) != '3':
                messages.error(request, "该账号不是学生账号，请使用正确的登录入口")
                return redirect("/")
            # 使用多角色session存储，而不是Django默认的login()
            set_user_to_role_session(request, user, '3')
            messages.success(request, f"学生 {user.email} 登录成功")
            return redirect(reverse("student_home"))
        else:
            messages.error(request, "邮箱或密码错误")
            return redirect("/")



def logout_user(request):
    """统一登出函数，登出所有角色"""
    remove_user_from_role_session(request, '1')
    remove_user_from_role_session(request, '2')
    remove_user_from_role_session(request, '3')
    # 同时清除Django默认的session（如果存在）
    try:
        if hasattr(request, 'user') and request.user.is_authenticated:
            logout(request)
    except:
        pass  # 忽略错误，继续执行
    messages.success(request, "已成功登出所有角色")
    return redirect("/")


def logout_role(request, role):
    """按角色登出函数
    
    Args:
        role: 角色名称 ('admin', 'teacher', 'student')
    """
    remove_user_from_role_session(request, role)
    role_name = {'admin': '管理员', 'teacher': '教师', 'student': '学生'}.get(role, '用户')
    messages.success(request, f"{role_name}已成功登出")
    
    # 根据角色重定向到对应首页（如果其他角色已登录）
    if role == 'admin':
        if is_role_authenticated(request, '2'):
            return redirect(reverse("staff_home"))
        elif is_role_authenticated(request, '3'):
            return redirect(reverse("student_home"))
    elif role == 'teacher':
        if is_role_authenticated(request, '1'):
            return redirect(reverse("admin_home"))
        elif is_role_authenticated(request, '3'):
            return redirect(reverse("student_home"))
    elif role == 'student':
        if is_role_authenticated(request, '1'):
            return redirect(reverse("admin_home"))
        elif is_role_authenticated(request, '2'):
            return redirect(reverse("staff_home"))
    
    return redirect("/")


@csrf_exempt
def get_attendance(request):
    """获取指定课程和学期的出勤记录"""
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = Attendance.objects.filter(subject=subject, session=session)
        attendance_list = []
        for attd in attendance:
            data = {
                    "id": attd.id,
                    "attendance_date": str(attd.date),
                    "session": attd.session.id
                    }
            attendance_list.append(data)
        return JsonResponse(json.dumps(attendance_list), safe=False)
    except Exception as e:
        return None


def showFirebaseJS(request):
    data = """
    // Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here, other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-messaging.js');

// Initialize the Firebase app in the service worker by passing in
// your app's Firebase config object.
// https://firebase.google.com/docs/web/setup#config-object
firebase.initializeApp({
    apiKey: "AIzaSyBarDWWHTfTMSrtc5Lj3Cdw5dEvjAkFwtM",
    authDomain: "sms-with-django.firebaseapp.com",
    databaseURL: "https://sms-with-django.firebaseio.com",
    projectId: "sms-with-django",
    storageBucket: "sms-with-django.appspot.com",
    messagingSenderId: "945324593139",
    appId: "1:945324593139:web:03fa99a8854bbd38420c86",
    measurementId: "G-2F2RXTL9GT"
});

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {
    const notification = JSON.parse(payload);
    const notificationOption = {
        body: notification.body,
        icon: notification.icon
    }
    return self.registration.showNotification(payload.notification.title, notificationOption);
});
    """
    return HttpResponse(data, content_type='application/javascript')
