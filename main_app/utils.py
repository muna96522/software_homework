"""
通用工具函数
"""
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


def paginate_queryset(request, queryset, per_page=10):
    """
    分页工具函数
    
    Args:
        request: Django request对象
        queryset: 查询集
        per_page: 每页显示数量，默认10
    
    Returns:
        page: 当前页对象
        paginator: 分页器对象
    """
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return page_obj, paginator


def search_students(queryset, search_query):
    """
    搜索学生
    支持多种搜索格式：
    - 简单搜索：直接匹配姓名、邮箱、专业
    - 逗号分隔：如 "li, hua" 匹配 last_name="li", first_name="hua"
    - 空格分隔：如 "li hua" 匹配 last_name="li", first_name="hua"
    
    Args:
        queryset: 学生查询集
        search_query: 搜索关键词
    
    Returns:
        过滤后的查询集
    """
    if not search_query:
        return queryset
    
    search_query = search_query.strip()
    
    # 处理逗号分隔的格式：如 "li, hua" 或 "li,hua"
    if ',' in search_query:
        parts = [p.strip() for p in search_query.split(',')]
        if len(parts) == 2:
            last_name_part = parts[0]
            first_name_part = parts[1]
            queryset = queryset.filter(
                Q(last_name__icontains=last_name_part) &
                Q(first_name__icontains=first_name_part)
            )
            return queryset
    
    # 处理空格分隔的格式：如 "li hua"
    if ' ' in search_query:
        parts = search_query.split()
        if len(parts) == 2:
            # 尝试两种组合：last_name first_name 或 first_name last_name
            queryset = queryset.filter(
                (Q(last_name__icontains=parts[0]) & Q(first_name__icontains=parts[1])) |
                (Q(last_name__icontains=parts[1]) & Q(first_name__icontains=parts[0]))
            )
            return queryset
    
    # 默认搜索：匹配姓名、邮箱、专业
    queryset = queryset.filter(
        Q(first_name__icontains=search_query) |
        Q(last_name__icontains=search_query) |
        Q(email__icontains=search_query) |
        Q(student__course__name__icontains=search_query)
    )
    return queryset


def search_staff(queryset, search_query):
    """
    搜索教师
    支持多种搜索格式：
    - 简单搜索：直接匹配姓名、邮箱
    - 逗号分隔：如 "li, hua" 匹配 last_name="li", first_name="hua"
    - 空格分隔：如 "li hua" 匹配 last_name="li", first_name="hua"
    
    Args:
        queryset: 教师查询集
        search_query: 搜索关键词
    
    Returns:
        过滤后的查询集
    """
    if not search_query:
        return queryset
    
    search_query = search_query.strip()
    
    # 处理逗号分隔的格式：如 "li, hua" 或 "li,hua"
    if ',' in search_query:
        parts = [p.strip() for p in search_query.split(',')]
        if len(parts) == 2:
            last_name_part = parts[0]
            first_name_part = parts[1]
            queryset = queryset.filter(
                Q(last_name__icontains=last_name_part) &
                Q(first_name__icontains=first_name_part)
            )
            return queryset
    
    # 处理空格分隔的格式：如 "li hua"
    if ' ' in search_query:
        parts = search_query.split()
        if len(parts) == 2:
            # 尝试两种组合：last_name first_name 或 first_name last_name
            queryset = queryset.filter(
                (Q(last_name__icontains=parts[0]) & Q(first_name__icontains=parts[1])) |
                (Q(last_name__icontains=parts[1]) & Q(first_name__icontains=parts[0]))
            )
            return queryset
    
    # 默认搜索：匹配姓名、邮箱
    queryset = queryset.filter(
        Q(first_name__icontains=search_query) |
        Q(last_name__icontains=search_query) |
        Q(email__icontains=search_query)
    )
    return queryset


def search_activities(queryset, search_query, status_filter=None):
    """
    搜索活动
    
    Args:
        queryset: 活动查询集
        search_query: 搜索关键词
        status_filter: 状态筛选（0=待审批，1=已通过，2=已拒绝）
    
    Returns:
        过滤后的查询集
    """
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(organizer__admin__first_name__icontains=search_query) |
            Q(organizer__admin__last_name__icontains=search_query)
        )
    
    if status_filter is not None and status_filter != '':
        queryset = queryset.filter(status=status_filter)
    
    return queryset

