#!/usr/bin/env python
"""查看活动管理数据详情"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from main_app.models import *

def get_status_display(status):
    """获取状态显示名称"""
    status_map = {0: '待审批', 1: '已通过', 2: '已拒绝'}
    return status_map.get(status, '未知')

print("=" * 80)
print("活动管理数据详情")
print("=" * 80)
print()

# 活动列表
activities = Activity.objects.all().order_by('-created_at')
print(f"【活动列表】共 {activities.count()} 个活动\n")

for i, activity in enumerate(activities, 1):
    print(f"{i}. {activity.title}")
    print(f"   发起教师: {activity.organizer.admin.last_name}{activity.organizer.admin.first_name}")
    print(f"   活动地点: {activity.location}")
    print(f"   活动时间: {activity.start_time.strftime('%Y-%m-%d %H:%M')} 至 {activity.end_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"   最大人数: {'不限制' if activity.max_participants == 0 else activity.max_participants}")
    print(f"   审批状态: {get_status_display(activity.status)}")
    
    if activity.status == 1:  # 已通过
        reg_count = ActivityRegistration.objects.filter(activity=activity).count()
        att_count = ActivityAttendance.objects.filter(activity=activity, is_present=True).count()
        feedback_count = ActivityFeedback.objects.filter(activity=activity).count()
        print(f"   报名人数: {reg_count}")
        print(f"   已签到: {att_count}")
        print(f"   评价数: {feedback_count}")
    
    if activity.admin_reply:
        print(f"   管理员回复: {activity.admin_reply}")
    
    print()

print("=" * 80)
print("数据统计")
print("=" * 80)
print(f"活动总数: {Activity.objects.count()}")
print(f"  - 已通过审批: {Activity.objects.filter(status=1).count()}")
print(f"  - 待审批: {Activity.objects.filter(status=0).count()}")
print(f"  - 已拒绝: {Activity.objects.filter(status=2).count()}")
print(f"报名记录: {ActivityRegistration.objects.count()}")
print(f"签到记录: {ActivityAttendance.objects.count()}")
print(f"  - 已签到: {ActivityAttendance.objects.filter(is_present=True).count()}")
print(f"  - 未签到: {ActivityAttendance.objects.filter(is_present=False).count()}")
print(f"评价记录: {ActivityFeedback.objects.count()}")
print()

