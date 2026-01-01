"""
多角色并行登录支持模块

该模块提供了在同一浏览器会话中支持多个角色（管理员、教师、学生）同时登录的功能。
每个角色使用独立的session key，互不干扰。
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()

# 角色类型映射
ROLE_SESSION_KEYS = {
    '1': 'admin_user_id',  # 管理员
    '2': 'teacher_user_id',  # 教师
    '3': 'student_user_id',  # 学生
}

ROLE_NAMES = {
    '1': 'admin',
    '2': 'teacher',
    '3': 'student',
}

REVERSE_ROLE_NAMES = {v: k for k, v in ROLE_NAMES.items()}


def get_role_session_key(user_type):
    """
    根据用户类型获取对应的session key
    
    Args:
        user_type: 用户类型字符串 ('1', '2', '3')
    
    Returns:
        str: session key名称
    """
    return ROLE_SESSION_KEYS.get(str(user_type), 'user_id')


def get_user_from_role_session(request, user_type):
    """
    从指定角色的session中获取用户对象
    
    Args:
        request: Django request对象
        user_type: 用户类型字符串 ('1', '2', '3')
    
    Returns:
        User对象或None
    """
    session_key = get_role_session_key(user_type)
    user_id = request.session.get(session_key)
    
    if user_id:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            # 如果用户不存在，清除session
            request.session.pop(session_key, None)
            return None
    return None


def set_user_to_role_session(request, user, user_type):
    """
    将用户ID存储到指定角色的session中
    
    Args:
        request: Django request对象
        user: User对象
        user_type: 用户类型字符串 ('1', '2', '3')
    """
    session_key = get_role_session_key(user_type)
    request.session[session_key] = user.id
    request.session[f'{session_key}_authenticated'] = True


def remove_user_from_role_session(request, user_type):
    """
    从指定角色的session中移除用户
    
    Args:
        request: Django request对象
        user_type: 用户类型字符串 ('1', '2', '3') 或角色名称 ('admin', 'teacher', 'student')
    """
    # 支持角色名称和用户类型
    if user_type in REVERSE_ROLE_NAMES:
        user_type = REVERSE_ROLE_NAMES[user_type]
    
    session_key = get_role_session_key(user_type)
    request.session.pop(session_key, None)
    request.session.pop(f'{session_key}_authenticated', None)


def get_current_role_user(request, view_module=None):
    """
    根据当前请求的视图模块或路径，获取对应角色的用户
    
    Args:
        request: Django request对象
        view_module: 视图模块名称 (如 'main_app.hod_views', 'main_app.staff_views', 'main_app.student_views')
    
    Returns:
        User对象或None
    """
    # 如果提供了视图模块，根据模块判断角色
    if view_module:
        if 'hod_views' in view_module:
            return get_user_from_role_session(request, '1')
        elif 'staff_views' in view_module:
            return get_user_from_role_session(request, '2')
        elif 'student_views' in view_module:
            return get_user_from_role_session(request, '3')
    
    # 根据URL路径判断角色
    path = request.path
    if path.startswith('/admin/'):
        return get_user_from_role_session(request, '1')
    elif path.startswith('/staff/'):
        return get_user_from_role_session(request, '2')
    elif path.startswith('/student/'):
        return get_user_from_role_session(request, '3')
    
    # 默认返回None
    return None


def is_role_authenticated(request, user_type):
    """
    检查指定角色是否已登录
    
    Args:
        request: Django request对象
        user_type: 用户类型字符串 ('1', '2', '3') 或角色名称 ('admin', 'teacher', 'student')
    
    Returns:
        bool: 是否已登录
    """
    # 支持角色名称和用户类型
    if user_type in REVERSE_ROLE_NAMES:
        user_type = REVERSE_ROLE_NAMES[user_type]
    
    session_key = get_role_session_key(user_type)
    return request.session.get(f'{session_key}_authenticated', False)

