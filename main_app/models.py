from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import AbstractUser




class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):

        """
        创建用户的核心方法

        Args:
            email: 用户邮箱
            password: 用户密码
            **extra_fields: 其他用户字段

        Returns:
            创建的用户实例
        """
        email = self.normalize_email(email)  # 规范化邮箱格式
        user = CustomUser(email=email, **extra_fields)  # 创建用户实例
        user.password = make_password(password)  # 对密码进行加密处理
        user.save(using=self._db)  # 保存用户到数据库
        return user  # 返回创建的用户实例

    def create_user(self, email, password=None, **extra_fields):

        """
        创建普通用户方法

        Args:
            email: 用户邮箱
            password: 用户密码，默认为None
            **extra_fields: 其他用户字段

        Returns:
            创建的普通用户实例
        """
        extra_fields.setdefault("is_staff", False)  # 设置默认非员工权限
        extra_fields.setdefault("is_superuser", False)  # 设置默认非超级用户权限
        return self._create_user(email, password, **extra_fields)  # 调用核心创建方法

    def create_superuser(self, email, password=None, **extra_fields):

        """
        创建超级用户方法

        Args:
            email: 用户邮箱
            password: 用户密码，默认为None
            **extra_fields: 其他用户字段

        Returns:
            创建的超级用户实例
        """
        extra_fields.setdefault("is_staff", True)  # 设置员工权限为True
        extra_fields.setdefault("is_superuser", True)  # 设置超级用户权限为True

        assert extra_fields["is_staff"]  # 确保用户有员工权限
        assert extra_fields["is_superuser"]  # 确保用户有超级用户权限
        return self._create_user(email, password, **extra_fields)  # 调用核心创建方法


class Session(models.Model):

    """
    会话模型类，用于表示一个会话的时间范围。
    继承自models.Model，表示这是一个Django模型类。
    """
    start_year = models.DateField()  # 会话开始日期，使用DateField类型存储
    end_year = models.DateField()    # 会话结束日期，使用DateField类型存储

    def __str__(self):
        """
        返回会话对象的字符串表示形式。
        格式为："From 开始日期 to 结束日期"
        """
        return "From " + str(self.start_year) + " to " + str(self.end_year)


class CustomUser(AbstractUser):

    """
    自定义用户模型，继承自AbstractUser，用于扩展默认用户模型。
    使用邮箱作为用户名，并添加了额外的用户信息字段。
    """
    USER_TYPE = ((1, "HOD"), (2, "Staff"), (3, "Student"))  # 用户类型选项：部门主管(HOD)、员工(Staff)、学生(Student)
    GENDER = [("M", "Male"), ("F", "Female")]  # 性别选项：男性(M)、女性(F)
    
    
    username = None  # Removed username, using email instead
    email = models.EmailField(unique=True)
    user_type = models.CharField(default=1, choices=USER_TYPE, max_length=1)
    gender = models.CharField(max_length=1, choices=GENDER)
    profile_pic = models.ImageField()
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='联系电话')
    fcm_token = models.TextField(default="")  # For firebase notifications
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.last_name + ", " + self.first_name


class Admin(models.Model):
    # 管理员模型，与CustomUser模型建立一对一关系
    # 当关联的CustomUser用户被删除时，管理员记录也会被级联删除
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)



class Course(models.Model):

    """
    课程模型类，用于存储课程相关信息

    继承自Django的models.Model，表示这是一个数据库模型
    包含课程名称、创建时间和更新时间三个字段
    """
    name = models.CharField(max_length=120)  # 课程名称，使用CharField类型，最大长度为120个字符
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间，使用DateTimeField类型，auto_now_add=True表示在创建记录时自动设置为当前时间
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间，使用DateTimeField类型，auto_now=True表示每次更新记录时自动设置为当前时间

    def __str__(self):

        """
        返回对象的字符串表示形式

        当需要将对象转换为字符串时调用此方法，例如在Django admin界面显示
        返回课程名称作为对象的字符串表示
        """
        return self.name  # 返回课程名称


class Student(models.Model):
    # 与CustomUser模型建立一对一关系，当关联的CustomUser被删除时，该学生记录也会被级联删除
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    # 与Course模型建立多对一关系，当关联的Course被删除时，该学生记录不会被影响
    # 课程字段允许为空(null=True)，但在表单提交时不能为空(blank=False)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, null=True, blank=False)
    # 与Session模型建立多对一关系，当关联的Session被删除时，该学生记录不会被影响
    # 会话字段允许为空(null=True)
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING, null=True)

    # 定义对象的字符串表示形式，返回格式为"姓, 名"
    def __str__(self):
        return self.admin.last_name + ", " + self.admin.first_name


class Staff(models.Model):
    # 移除course字段，允许教师跨专业授课
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.admin.last_name + " " + self.admin.first_name


class Subject(models.Model):

    """
    科目模型类，用于存储课程科目的相关信息。
    继承自 models.Model，表示这是一个 Django 模型类。
    """
    name = models.CharField(max_length=120)  # 科目名称，使用 CharField 类型，最大长度为120字符
    staff = models.ForeignKey(Staff,on_delete=models.CASCADE,)  # 关联到教职工模型，设置级联删除
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # 关联到课程模型，设置级联删除
    updated_at = models.DateTimeField(auto_now=True)  # 更新时间，每次保存时自动更新为当前时间
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间，仅在对象创建时自动设置为当前时间

    def __str__(self):
        """
        返回对象的字符串表示形式，用于在 Django admin 等界面中显示。
        :return: 科目名称
        """
        return self.name


class Attendance(models.Model):

    """
    考勤记录模型类
    用于记录学生在特定课程会话中的考勤情况
    """
    session = models.ForeignKey(Session, on_delete=models.DO_NOTHING)  # 关联课程会话，设置为不级联删除
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING)  # 关联课程科目，设置为不级联删除
    date = models.DateField()  # 考勤日期
    created_at = models.DateTimeField(auto_now_add=True)  # 记录创建时间，自动设置为当前时间
    updated_at = models.DateTimeField(auto_now=True)  # 记录更新时间，每次更新时自动设置为当前时间


class AttendanceReport(models.Model):
    """
    考勤报告模型，记录每个学生在每次考勤中的状态
    
    该模型作为 Attendance 和 Student 之间的中间表，
    记录了每个学生在每次考勤中的出席状态。
    每次考勤事件(Attendance)会为所有相关学生创建一条对应的考勤报告记录。
    """
    
    # 关联的学生，使用 DO_NOTHING 确保即使学生被删除，考勤记录仍保留
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    
    # 关联的考勤事件，使用 CASCADE 确保考勤事件被删除时，相关报告也被删除
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    
    # 考勤状态：True 表示出席，False 表示缺席
    status = models.BooleanField(default=False)
    
    # 记录创建时间，自动设置为记录创建时的时间
    created_at = models.DateTimeField(auto_now_add=True)
    
    # 记录更新时间，每次更新记录时自动设置为当前时间
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStudent(models.Model):
    """学生请假报告模型，记录学生的请假申请信息"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveReportStaff(models.Model):
    """教职工请假报告模型，记录教职工的请假申请信息"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.CharField(max_length=60)
    message = models.TextField()
    status = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStudent(models.Model):
    """学生反馈模型，记录学生的反馈信息及回复"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedbackStaff(models.Model):
    """教职工反馈模型，记录教职工的反馈信息及回复"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    feedback = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStaff(models.Model):
    """教职工通知模型，记录发送给教职工的通知信息"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NotificationStudent(models.Model):
    """学生通知模型，记录发送给学生的通知信息"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudentResult(models.Model):
    """学生成绩模型，记录学生在各科目的考试成绩"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test = models.FloatField(default=0)
    exam = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# 校园活动管理模块
class Activity(models.Model):
    """
    校园活动模型，记录校园活动的详细信息
    
    包括活动标题、描述、发起教师、地点、时间、参与人数限制、
    审批状态等信息，用于管理和跟踪校园活动的整个生命周期。
    """
    STATUS_CHOICES = [
        (0, '待审批'),
        (1, '已通过'),
        (2, '已拒绝'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='活动标题')
    description = models.TextField(verbose_name='活动描述')
    organizer = models.ForeignKey(Staff, on_delete=models.CASCADE, verbose_name='发起教师')
    location = models.CharField(max_length=200, verbose_name='活动地点')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    max_participants = models.IntegerField(default=0, verbose_name='最大参与人数', help_text='0表示不限制')
    status = models.SmallIntegerField(default=0, choices=STATUS_CHOICES, verbose_name='审批状态')
    admin_reply = models.TextField(blank=True, null=True, verbose_name='管理员回复')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '校园活动'
        verbose_name_plural = '校园活动'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class ActivityRegistration(models.Model):
    """
    活动报名模型，记录学生参加活动的报名信息
    
    作为Activity和Student之间的中间表，
    记录哪个学生报名参加了哪个活动，以及报名时间。
    每个学生对每个活动只能报名一次。
    """
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name='活动')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生')
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name='报名时间')
    
    class Meta:
        verbose_name = '活动报名'
        verbose_name_plural = '活动报名'
        unique_together = ['activity', 'student']  # 每个学生只能报名一次
        ordering = ['-registered_at']
    
    def __str__(self):
        return f"{self.student} - {self.activity.title}"


class ActivityAttendance(models.Model):
    """
    活动签到模型，记录学生参加活动的实际出席情况
    
    记录哪个学生实际参加了哪个活动，签到状态、
    确认签到的工作人员和签到时间。
    每个学生对每个活动只能签到一次。
    """
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name='活动')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生')
    is_present = models.BooleanField(default=False, verbose_name='是否出席')
    checked_by = models.ForeignKey(Staff, on_delete=models.CASCADE, verbose_name='签到确认人')
    checked_at = models.DateTimeField(auto_now_add=True, verbose_name='签到时间')
    
    class Meta:
        verbose_name = '活动签到'
        verbose_name_plural = '活动签到'
        unique_together = ['activity', 'student']  # 每个学生只能签到一次
        ordering = ['-checked_at']
    
    def __str__(self):
        status = '已签到' if self.is_present else '未签到'
        return f"{self.student} - {self.activity.title} - {status}"


class ActivityFeedback(models.Model):
    """
    活动评价模型，记录学生对活动的评价和反馈
    
    记录学生对参加过的活动的评分(1-5星)和文字评价，
    用于收集学生对活动的反馈，以便改进未来活动。
    每个学生对每个活动只能评价一次。
    """
    RATING_CHOICES = [
        (1, '1星'),
        (2, '2星'),
        (3, '3星'),
        (4, '4星'),
        (5, '5星'),
    ]
    
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, verbose_name='活动')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生')
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='评分')
    comment = models.TextField(verbose_name='评价内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评价时间')
    
    class Meta:
        verbose_name = '活动评价'
        verbose_name_plural = '活动评价'
        unique_together = ['activity', 'student']  # 每个学生只能评价一次
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student} - {self.activity.title} - {self.rating}星"


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    用户创建信号处理函数
    
    当CustomUser实例创建时，根据用户类型自动创建对应的
    Admin、Staff或Student关联实例。
    """
    if created:
        if instance.user_type == 1:
            Admin.objects.create(admin=instance)
        if instance.user_type == 2:
            Staff.objects.create(admin=instance)
        if instance.user_type == 3:
            Student.objects.create(admin=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    用户保存信号处理函数
    
    当CustomUser实例保存时，同时保存对应的
    Admin、Staff或Student关联实例，确保数据一致性。
    """
    if instance.user_type == 1:
        instance.admin.save()
    if instance.user_type == 2:
        instance.staff.save()
    if instance.user_type == 3:
        instance.student.save()
