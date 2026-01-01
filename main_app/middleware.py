from django.utils.deprecation import MiddlewareMixin
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from .multi_role_auth import (
    get_user_from_role_session,
    get_current_role_user,
    is_role_authenticated
)


class MultiRoleAuthMiddleware(MiddlewareMixin):
    """
    多角色认证中间件
    在Django的AuthenticationMiddleware之后运行，根据URL路径或视图模块从对应角色的session中获取用户
    这个中间件会覆盖Django默认的request.user，使其指向对应角色的用户
    """
    def process_request(self, request):
        # 跳过静态文件和媒体文件
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
        
        # 跳过登录相关路径
        login_paths = ['/doLogin/', '/do-admin-login/', '/do-teacher-login/', '/do-student-login/', 
                      '/logout_user/', '/logout-role/']
        if any(request.path.startswith(path) for path in login_paths) or request.path == '/':
            return None
        
        # 根据URL路径确定需要的角色（初步判断）
        required_role = None
        path = request.path
        
        # 管理员路径识别（包括以admin_开头的路径）
        if path.startswith('/admin/') or path.startswith('/admin_'):
            required_role = '1'  # 管理员
        elif path.startswith('/staff/'):
            required_role = '2'  # 教师
        elif path.startswith('/student/'):
            required_role = '3'  # 学生
        # 其他管理员相关路径（这些路径通常由hod_views处理）
        elif any(keyword in path for keyword in [
            '/attendance/view', '/attendance/fetch',
            '/session/manage', '/session/edit', '/session/delete',
            '/staff/add', '/staff/manage', '/staff/edit', '/staff/delete',
            '/student/add', '/student/manage', '/student/edit', '/student/delete',
            '/course/add', '/course/manage', '/course/edit', '/course/delete',
            '/subject/add', '/subject/manage', '/subject/edit', '/subject/delete',
            '/send_student_notification', '/send_staff_notification',
            '/add_session', '/check_email_availability'
        ]):
            required_role = '1'  # 管理员
        
        # 如果确定了需要的角色，从对应角色的session中获取用户
        if required_role:
            role_user = get_user_from_role_session(request, required_role)
            if role_user:
                # 将角色用户设置到request.user，覆盖Django默认的认证用户
                request.user = role_user
                # 清除Django AuthenticationMiddleware设置的缓存
                if hasattr(request, '_cached_user'):
                    delattr(request, '_cached_user')
        
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        在process_view中再次检查，根据视图模块更准确地识别角色
        这样可以处理那些URL路径不明确但视图模块明确的情况
        """
        modulename = view_func.__module__
        
        # 如果request.user已经是正确角色的用户，就不需要再设置了
        # 但我们需要确保它是从对应角色的session中获取的
        required_role = None
        
        # 根据视图模块确定角色（更准确）
        if 'hod_views' in modulename:
            required_role = '1'  # 管理员
        elif 'staff_views' in modulename:
            required_role = '2'  # 教师
        elif 'student_views' in modulename:
            required_role = '3'  # 学生
        
        # 如果根据视图模块确定了角色，确保request.user是对应角色的用户
        if required_role:
            role_user = get_user_from_role_session(request, required_role)
            if role_user:
                # 如果当前request.user不是对应角色的用户，则替换
                if not hasattr(request.user, 'id') or request.user.id != role_user.id:
                    request.user = role_user
                    if hasattr(request, '_cached_user'):
                        delattr(request, '_cached_user')
        
        return None


class LoginCheckMiddleWare(MiddlewareMixin):
    """
    登录检查中间件
    检查用户是否有权限访问对应的页面
    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        
        # 允许登录页面和登录处理路径通过，不进行任何拦截
        login_path = reverse('login_page')
        login_paths = [
            login_path,
            reverse('user_login'),
            reverse('admin_login'),
            reverse('teacher_login'),
            reverse('student_login'),
            reverse('user_logout'),
        ]
        
        # 如果是登录相关路径，直接放行
        if request.path == login_path or request.path in login_paths or request.path.startswith('/do-') or request.path.startswith('/logout-role/'):
            return None  # 返回 None 让视图正常处理
        
        # 如果是静态文件或媒体文件，放行
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
        
        # 根据视图模块或URL路径确定需要的角色
        required_role = None
        if 'hod_views' in modulename or request.path.startswith('/admin/'):
            required_role = '1'  # 管理员
        elif 'staff_views' in modulename or request.path.startswith('/staff/'):
            required_role = '2'  # 教师
        elif 'student_views' in modulename or request.path.startswith('/student/'):
            required_role = '3'  # 学生
        
        # 如果确定了需要的角色，检查该角色是否已登录
        if required_role:
            role_user = get_user_from_role_session(request, required_role)
            if not role_user:
                # 该角色未登录，重定向到登录页面
                role_names = ['', '管理员', '教师', '学生']
                messages.error(request, f"请先登录{role_names[int(required_role)]}账号")
                return redirect(reverse('login_page'))
        else:
            # 无法确定角色，检查是否有任何角色已登录
            # 如果没有任何角色登录，重定向到登录页面
            if not (is_role_authenticated(request, '1') or 
                    is_role_authenticated(request, '2') or 
                    is_role_authenticated(request, '3')):
                return redirect(reverse('login_page'))
        
        return None  # 继续处理请求
