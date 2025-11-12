from django import forms
from django.forms.widgets import DateInput, TextInput

from .models import *

"""
Django表单系统 - 定义所有数据验证和表单处理逻辑
功能：用户注册、信息编辑、业务表单（考勤、成绩、请假等）
设计：采用继承体系，统一表单样式，支持模型验证
"""

# 类级别：基础表单设置类
# 职责：为所有模型表单提供统一的样式和配置
# 设计意图：通过继承实现表单样式的统一管理
class FormSettings(forms.ModelForm):
    """
    类级别：表单设置基类
    职责：统一设置所有表单控件的CSS类
    设计意图：确保整个应用的表单样式一致性
    """
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # 语句块级别：为所有可见字段添加Bootstrap样式类
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'
# 类级别：自定义用户表单
# 职责：处理系统用户的创建和更新
class CustomUserForm(FormSettings):
    """
    类级别：用户基础表单
    职责：处理用户模型的通用字段验证和保存逻辑
    设计意图：作为其他用户类型表单的基类
    """
    email = forms.EmailField(required=True)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female')])
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    address = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput)
    widget = {
        'password': forms.PasswordInput(),
    }
    profile_pic = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)

        # 关键语句级别：更新操作时的特殊处理
        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False

            # 语句块级别：初始化表单字段值
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)

            # 关键语句级别：更新时密码字段的提示信息
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "Fill this only if you wish to update password"

    def clean_email(self, *args, **kwargs):
        """
        方法级别：邮箱验证
        功能：确保邮箱地址的唯一性
        业务逻辑：新建用户时检查唯一性，更新用户时检查是否修改
        """
        formEmail = self.cleaned_data['email'].lower()

        # 关键语句级别：新建用户时的邮箱唯一性检查
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            # 关键语句级别：邮箱变更时的唯一性检查
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("The given email is already registered")

        return formEmail

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'gender', 'password', 'profile_pic', 'address']


# 类级别：学生表单
# 职责：处理学生用户的创建和更新
class StudentForm(CustomUserForm):
    """
    类级别：学生专用表单
    职责：扩展基础用户表单，添加学生特定字段
    设计意图：复用用户基础功能，增加学生业务字段
    """
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + \
                 ['course', 'session']  # 学生特有字段：课程和学期


# 类级别：管理员表单
class AdminForm(CustomUserForm):
    """
    类级别：管理员表单
    职责：处理管理员用户的创建和更新
    """
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields  # 使用基础用户字段


# 类级别：教师表单
class StaffForm(CustomUserForm):
    """
    类级别：教师表单
    职责：处理教师用户的创建和更新
    设计意图：扩展基础用户表单，添加教师关联课程字段
    """
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields + \
                 ['course']  # 教师特有字段：负责课程


# 类级别：课程表单
class CourseForm(FormSettings):
    """
    类级别：课程管理表单
    职责：处理课程信息的创建和更新
    """
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['name']  # 课程名称字段
        model = Course


# 类级别：科目表单
class SubjectForm(FormSettings):
    """
    类级别：科目管理表单
    职责：处理科目信息的创建和更新
    业务逻辑：关联教师和课程信息
    """
    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Subject
        fields = ['name', 'staff', 'course']  # 科目名称、负责教师、所属课程


# 类级别：学期表单
class SessionForm(FormSettings):
    """
    类级别：学期管理表单
    职责：处理学期信息的创建和更新
    设计意图：使用日期选择器改善用户体验
    """
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Session
        fields = '__all__'
        # 关键语句级别：配置日期选择器控件
        widgets = {
            'start_year': DateInput(attrs={'type': 'date'}),
            'end_year': DateInput(attrs={'type': 'date'}),
        }


# 类级别：教师请假表单
class LeaveReportStaffForm(FormSettings):
    """
    类级别：教师请假申请表单
    职责：处理教师请假信息的提交和验证
    """
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']  # 请假日期和原因
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),  # 日期选择器
        }


# 类级别：教师反馈表单
class FeedbackStaffForm(FormSettings):
    """
    类级别：教师反馈表单
    职责：处理教师对系统的反馈信息
    """
    def __init__(self, *args, **kwargs):
        super(FeedbackStaffForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStaff
        fields = ['feedback']  # 反馈内容字段


# 类级别：学生请假表单
class LeaveReportStudentForm(FormSettings):
    """
    类级别：学生请假申请表单
    职责：处理学生请假信息的提交和验证
    """
    def __init__(self, *args, **kwargs):
        super(LeaveReportStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = LeaveReportStudent
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


# 类级别：学生反馈表单
class FeedbackStudentForm(FormSettings):
    """
    类级别：学生反馈表单
    职责：处理学生对系统的反馈信息
    """
    def __init__(self, *args, **kwargs):
        super(FeedbackStudentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeedbackStudent
        fields = ['feedback']


# 类级别：学生信息编辑表单
class StudentEditForm(CustomUserForm):
    """
    类级别：学生信息编辑表单
    职责：处理学生个人信息的更新（不包含课程和学期）
    设计意图：与学生创建表单区分，避免误修改关键信息
    """
    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields  # 仅基础信息字段


# 类级别：教师信息编辑表单
class StaffEditForm(CustomUserForm):
    """
    类级别：教师信息编辑表单
    职责：处理教师个人信息的更新
    """
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields


# 类级别：成绩编辑表单
class EditResultForm(FormSettings):
    """
    类级别：成绩编辑专用表单
    职责：提供成绩查询和编辑的完整字段集
    业务逻辑：包含学期、科目、学生和成绩字段
    """
    # 关键语句级别：动态获取所有学期选项
    session_list = Session.objects.all()
    session_year = forms.ModelChoiceField(
        label="Session Year", queryset=session_list, required=True)

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)

    class Meta:
        model = StudentResult
        fields = ['session_year', 'subject', 'student', 'test', 'exam']  # 完整成绩编辑字段