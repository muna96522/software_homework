from django import forms
from django.forms.widgets import DateInput, TextInput

from .models import *


class FormSettings(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormSettings, self).__init__(*args, **kwargs)
        # Here make some changes such as:
        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-control'


class CustomUserForm(FormSettings):
    email = forms.EmailField(required=True, label='邮箱')
    gender = forms.ChoiceField(choices=[('M', '男'), ('F', '女')], label='性别')
    first_name = forms.CharField(required=True, label='名')
    last_name = forms.CharField(required=True, label='姓')
    phone_number = forms.CharField(max_length=20, required=False, label='联系电话')
    password = forms.CharField(widget=forms.PasswordInput, label='密码')
    widget = {
        'password': forms.PasswordInput(),
    }
    profile_pic = forms.ImageField(label='头像')

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        # 设置字段标签和帮助文本
        self.fields['email'].help_text = '用于登录的邮箱地址'
        self.fields['gender'].help_text = '选择性别'
        self.fields['first_name'].help_text = '用户的名字'
        self.fields['last_name'].help_text = '用户的姓氏'
        self.fields['phone_number'].help_text = '手机号码或固定电话（选填）'
        self.fields['password'].help_text = '登录密码（至少8位）'
        self.fields['profile_pic'].help_text = '上传用户头像照片'

        if kwargs.get('instance'):
            instance = kwargs.get('instance').admin.__dict__
            self.fields['password'].required = False
            for field in CustomUserForm.Meta.fields:
                self.fields[field].initial = instance.get(field)
            if self.instance.pk is not None:
                self.fields['password'].widget.attrs['placeholder'] = "仅在需要更新密码时填写"

    def clean_email(self, *args, **kwargs):
        formEmail = self.cleaned_data['email'].lower()
        if self.instance.pk is None:  # Insert
            if CustomUser.objects.filter(email=formEmail).exists():
                raise forms.ValidationError(
                    "The given email is already registered")
        else:  # Update
            dbEmail = self.Meta.model.objects.get(
                id=self.instance.pk).admin.email.lower()
            if dbEmail != formEmail:  # There has been changes
                if CustomUser.objects.filter(email=formEmail).exists():
                    raise forms.ValidationError("The given email is already registered")

        return formEmail

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'gender',  'password','profile_pic', 'phone_number' ]


class StudentForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.fields['course'].label = '所属专业'
        self.fields['course'].help_text = '选择学生所属的专业'
        self.fields['session'].label = '所属学期'
        self.fields['session'].help_text = '选择学生所属的学期（学年）'

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields + \
            ['course', 'session']


class AdminForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(AdminForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Admin
        fields = CustomUserForm.Meta.fields


class StaffForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)
        # 移除专业字段，允许教师跨专业授课

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields


class CourseForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = '专业名称'
        self.fields['name'].help_text = '例如：计算机科学、数学、英语文学等'

    class Meta:
        fields = ['name']
        model = Course


class SubjectForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = '科目名称'
        self.fields['name'].help_text = '例如：高等数学、数据结构、英语写作等（具体的教学科目）'
        self.fields['course'].label = '所属专业'
        self.fields['course'].help_text = '选择此科目属于哪个专业'
        self.fields['staff'].label = '授课教师'
        self.fields['staff'].help_text = '选择负责教授此科目的教师'

    class Meta:
        model = Subject
        fields = ['name', 'staff', 'course']


class SessionForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)
        self.fields['start_year'].label = '开始日期'
        self.fields['start_year'].help_text = '学期或学年的开始日期'
        self.fields['end_year'].label = '结束日期'
        self.fields['end_year'].help_text = '学期或学年的结束日期'

    class Meta:
        model = Session
        fields = '__all__'
        widgets = {
            'start_year': DateInput(attrs={'type': 'date'}),
            'end_year': DateInput(attrs={'type': 'date'}),
        }


class LeaveReportStaffForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStaffForm, self).__init__(*args, **kwargs)
        self.fields['date'].label = '请假日期'
        self.fields['date'].help_text = '选择请假的日期'
        self.fields['message'].label = '请假原因'
        self.fields['message'].help_text = '详细说明请假原因'

    class Meta:
        model = LeaveReportStaff
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStaffForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStaffForm, self).__init__(*args, **kwargs)
        self.fields['feedback'].label = '反馈内容'
        self.fields['feedback'].help_text = '请输入您的反馈意见或建议'

    class Meta:
        model = FeedbackStaff
        fields = ['feedback']


class LeaveReportStudentForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(LeaveReportStudentForm, self).__init__(*args, **kwargs)
        self.fields['date'].label = '请假日期'
        self.fields['date'].help_text = '选择请假的日期'
        self.fields['message'].label = '请假原因'
        self.fields['message'].help_text = '详细说明请假原因'

    class Meta:
        model = LeaveReportStudent
        fields = ['date', 'message']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }


class FeedbackStudentForm(FormSettings):

    def __init__(self, *args, **kwargs):
        super(FeedbackStudentForm, self).__init__(*args, **kwargs)
        self.fields['feedback'].label = '反馈内容'
        self.fields['feedback'].help_text = '请输入您的反馈意见或建议'

    class Meta:
        model = FeedbackStudent
        fields = ['feedback']


class StudentEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StudentEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Student
        fields = CustomUserForm.Meta.fields 


class StaffEditForm(CustomUserForm):
    def __init__(self, *args, **kwargs):
        super(StaffEditForm, self).__init__(*args, **kwargs)

    class Meta(CustomUserForm.Meta):
        model = Staff
        fields = CustomUserForm.Meta.fields


class EditResultForm(FormSettings):
    session_list = Session.objects.all()
    session_year = forms.ModelChoiceField(
        label="学期", 
        queryset=session_list, 
        required=True,
        empty_label="请选择学期",
        widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(EditResultForm, self).__init__(*args, **kwargs)
        # 设置session_year字段
        self.fields['session_year'].label = '学期'
        self.fields['session_year'].help_text = '选择要录入成绩的学期'
        
        # 设置subject字段
        if 'subject' in self.fields:
            self.fields['subject'].label = '科目'
            self.fields['subject'].help_text = '选择要录入成绩的科目'
            self.fields['subject'].empty_label = "请选择科目"
            self.fields['subject'].widget.attrs.update({'class': 'form-control'})
        
        # 设置student字段
        if 'student' in self.fields:
            self.fields['student'].label = '学生'
            self.fields['student'].help_text = '选择要录入成绩的学生'
            self.fields['student'].empty_label = "请选择学生"
            self.fields['student'].widget.attrs.update({'class': 'form-control'})
        
        # 设置test字段（平时成绩）
        if 'test' in self.fields:
            self.fields['test'].label = '平时成绩 (0-100分)'
            self.fields['test'].help_text = '平时成绩（0-100分）'
            self.fields['test'].widget.attrs.update({
                'class': 'form-control',
                'type': 'number',
                'step': '0.1',
                'min': '0',
                'max': '100'
            })
        
        # 设置exam字段（考试成绩）
        if 'exam' in self.fields:
            self.fields['exam'].label = '考试成绩 (0-100分)'
            self.fields['exam'].help_text = '考试成绩（0-100分）'
            self.fields['exam'].widget.attrs.update({
                'class': 'form-control',
                'type': 'number',
                'step': '0.1',
                'min': '0',
                'max': '100'
            })

    class Meta:
        model = StudentResult
        fields = ['session_year', 'subject', 'student', 'test', 'exam']


# 校园活动管理表单
class ActivityForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(ActivityForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = '活动标题'
        self.fields['title'].help_text = '请输入活动的标题'
        self.fields['description'].label = '活动描述'
        self.fields['description'].help_text = '详细描述活动的内容、目的和要求'
        self.fields['location'].label = '活动地点'
        self.fields['location'].help_text = '活动举办的具体地点'
        self.fields['start_time'].label = '开始时间'
        self.fields['start_time'].help_text = '活动开始的时间'
        self.fields['end_time'].label = '结束时间'
        self.fields['end_time'].help_text = '活动结束的时间'
        self.fields['max_participants'].label = '最大参与人数'
        self.fields['max_participants'].help_text = '限制参与人数，0表示不限制'

    class Meta:
        model = Activity
        fields = ['title', 'description', 'location', 'start_time', 'end_time', 'max_participants']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }


class ActivityApprovalForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(ActivityApprovalForm, self).__init__(*args, **kwargs)
        self.fields['status'].label = '审批状态'
        self.fields['status'].help_text = '选择审批结果'
        self.fields['admin_reply'].label = '管理员回复'
        self.fields['admin_reply'].help_text = '审批意见或说明（选填）'

    class Meta:
        model = Activity
        fields = ['status', 'admin_reply']
        widgets = {
            'admin_reply': forms.Textarea(attrs={'rows': 3}),
        }


class ActivityFeedbackForm(FormSettings):
    def __init__(self, *args, **kwargs):
        super(ActivityFeedbackForm, self).__init__(*args, **kwargs)
        self.fields['rating'].label = '评分'
        self.fields['rating'].help_text = '请为活动评分（1-5星）'
        self.fields['comment'].label = '评价内容'
        self.fields['comment'].help_text = '请分享您对活动的感受和建议'

    class Meta:
        model = ActivityFeedback
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 5}),
        }
