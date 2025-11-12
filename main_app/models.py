"""
数据模型定义文件
职责：定义系统所有数据表结构和关系
设计意图：采用Django ORM实现数据库架构，支持用户管理、课程管理、考勤成绩等核心功能
"""
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUserManager(UserManager):
    """
    自定义用户管理类，继承自Django的UserManager
    用于处理用户的创建和管理逻辑
    """
    def _create_user(self, email, password, **extra_fields):

        """
        创建用户的核心方法
        参数:
            email: 用户邮箱
            password: 用户密码
            **extra_fields: 其他用户字段
        返回:
            创建好的用户对象
        """
        email = self.normalize_email(email)  # 规范化邮箱格式
        user = CustomUser(email=email, **extra_fields)  # 创建用户实例
        user.password = make_password(password)  # 对密码进行加密处理
        user.save(using=self._db)  # 保存到数据库
        return user  # 返回创建的用户对象

    def create_user(self, email, password=None, **extra_fields):

        """
        创建普通用户方法
        参数:
            email: 用户邮箱
            password: 用户密码，默认为None
            **extra_fields: 其他用户字段
        返回:
            创建好的普通用户对象
        """
        extra_fields.setdefault("is_staff", False)  # 设置默认不是员工
        extra_fields.setdefault("is_superuser", False)  # 设置默认不是超级用户
        return self._create_user(email, password, **extra_fields)  # 调用核心创建方法

    def create_superuser(self, email, password=None, **extra_fields):

        """
        创建超级用户方法
        参数:
            email: 用户邮箱
            password: 用户密码，默认为None
            **extra_fields: 其他用户字段
        返回:
            创建好的超级用户对象
        """
        extra_fields.setdefault("is_staff", True)  # 设置必须是员工
        extra_fields.setdefault("is_superuser", True)  # 设置必须是超级用户

        # 断言检查确保超级用户权限正确设置
        assert extra_fields["is_staff"]
        assert extra_fields["is_superuser"]
        return self._create_user(email, password, **extra_fields)  # 调用核心创建方法


class Session(models.Model):

    """
    学期模型类，管理学期时间周期
    """
    # 定义会话的开始日期字段
    start_year = models.DateField()
    # 定义会话的结束日期字段
    end_year = models.DateField()

    def __str__(self):
        # 返回学期的字符串表示，格式为"From 开始日期 to 结束日期"
        return "From " + str(self.start_year) + " to " + str(self.end_year)


class CustomUser(AbstractUser):

    """
    自定义用户模型，继承自AbstractUser
    替换了默认的用户名认证方式，使用邮箱作为唯一标识
    定义了用户类型和性别选项
    """
    USER_TYPE = ((1, "HOD"), (2, "Staff"), (3, "Student"))  # 用户类型选项：管理员、教师、学生
    GENDER = [("M", "Male"), ("F", "Female")]  # 性别选项：男性、女性
    
    
    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField()
    address = models.TextField()
    fcm_token = models.TextField(default="")  # For firebase notifications
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.last_name + ", " + self.first_name


class Admin(models.Model):
    """定义一个管理员模型，继承自Django的Model类"""
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

"""
CustomUser (基础用户)
    ├── Admin (管理员)
    ├── Staff (教职工) → Course (专业)
    │   └── Subject (课程)
    └── Student (学生) → Course + Session (专业+学期)
        ├── Attendance (考勤)
        ├── LeaveReport (请假)
        ├── Feedback (反馈)
        ├── Notification (通知)
        └── StudentResult (成绩)

"""

class Course(models.Model):
    """课程模型类，用于存储课程相关信息--有点不清楚感觉是专业"""
    # 课程名称
    name = models.CharField(max_length=120)
    # 创建时间
    created_at = models.DateTimeField(auto_now_add=True)
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True)

    # 返回课程名称，字符串类型
    def __str__(self):
        return self.name


class Student(models.Model):

    """
    学生模型类，继承自Django的Model类
    用于存储学生相关信息，包括与用户、课程和会话的关联
    """
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE) # 每个学生必须有一个对应的用户账号
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False) #关联学生所修读的课程
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True) # 关联学生所在的学期/学年

    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name


class Staff(models.Model):
    """教职工信息"""
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.admin.last_name + " " + self.admin.first_name


class Subject(models.Model):
    """科目信息"""
    name = models.CharField(max_length=120)
    # 关联到Staff模型的外键，表示该科目由哪位教职工负责
    staff = models.ForeignKey(Staff,on_delete=models.CASCADE,)
    # 关联到Course模型的外键，表示该科目属于哪个课程
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 定义模型的字符串表示方法，返回科目名称
    def __str__(self):
        return self.name


class Attendance(models.Model):

    """
    考勤记录模型类，记录单次考勤事件 eg：2023-12-20的"数据结构"课考勤
    继承自Django的models.Model，表示这是一个数据库模型
    """
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)
    date = models.DateField()  # 考勤日期
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AttendanceReport(models.Model):
    """
    考勤报告模型类，用于记录学生的考勤情况
    """
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    # 考勤状态，默认为False（可能表示缺勤）
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStudent(models.Model):
    """请假申请模型类，处理学生的请假申请"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStaff(models.Model):
    """请假申请模型类，处理教职工的请假申请"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStudent(models.Model):
    """反馈系统模型类,处理学生的反馈信息"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField() # 存储对反馈的回复内容
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStaff(models.Model):
    """反馈系统模型类,处理教职工的反馈信息"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStaff(models.Model):
    """通知系统模型类，处理教职工的通知信息"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStudent(models.Model):
    """通知系统模型类，处理学生的通知信息"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudentResult(models.Model):
    """学生成绩模型类，记录学生的成绩信息"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test = models.FloatField(default=0)
    exam = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """当创建用户时，根据用户类型创建相应的用户子类实例"""
    if created:
        if instance.user_type == 1:
            Admin.objects.create(admin=instance)
        if instance.user_type == 2:
            Staff.objects.create(admin=instance)
        if instance.user_type == 3:
            Student.objects.create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """当保存用户时，根据用户类型保存相应的用户子类实例"""
    if instance.user_type == 1:
        instance.admin.save()
    if instance.user_type == 2:
        instance.staff.save()
    if instance.user_type == 3:
        instance.student.save()
