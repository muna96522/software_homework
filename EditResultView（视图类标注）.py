from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from .models import Subject, Staff, Student, StudentResult
from .forms import EditResultForm
from django.urls import reverse


"""
成绩编辑视图 - 基于类的成绩管理视图
功能：提供学生成绩的查询、编辑和更新操作
特色：使用Django类视图，支持GET/POST分离，包含权限控制
"""

# 类级别：成绩编辑视图类
# 职责：提供学生成绩的编辑功能
# 设计意图：使用基于类的视图实现成绩管理的CRUD操作
class EditResultView(View):
    """
    类级别：成绩编辑视图
    职责：处理学生成绩的查询和更新操作
    使用方法：GET请求显示编辑表单，POST请求处理成绩更新
    """

    def get(self, request, *args, **kwargs):
        """
        方法级别：GET请求处理
        功能：显示成绩编辑表单页面
        参数：request - HTTP请求对象
        返回值：渲染后的编辑页面
        """
        resultForm = EditResultForm()
        staff = get_object_or_404(Staff, admin=request.user)

        # 关键语句级别：限制教师只能编辑自己教授的科目
        resultForm.fields['subject'].queryset = Subject.objects.filter(staff=staff)

        context = {
            'form': resultForm,
            'page_title': "Edit Student's Result"
        }
        return render(request, "staff_template/edit_student_result.html", context)

    def post(self, request, *args, **kwargs):
        """
        方法级别：POST请求处理
        功能：处理成绩表单提交和更新数据库
        参数：request - 包含表单数据的HTTP请求
        返回值：重定向到编辑页面或显示错误信息
        """
        form = EditResultForm(request.POST)
        context = {'form': form, 'page_title': "Edit Student's Result"}

        if form.is_valid():
            try:
                # 获取表单验证后的数据
                student = form.cleaned_data.get('student')
                subject = form.cleaned_data.get('subject')
                test = form.cleaned_data.get('test')  # 平时成绩
                exam = form.cleaned_data.get('exam')  # 期末成绩

                # 关键语句级别：查询并更新成绩记录
                result = StudentResult.objects.get(student=student, subject=subject)
                result.exam = exam
                result.test = test
                result.save()

                messages.success(request, "Result Updated")
                return redirect(reverse('edit_student_result'))

            except Exception as e:
                # 异常处理：成绩更新失败
                messages.warning(request, "Result Could Not Be Updated")
        else:
            # 表单验证失败处理
            messages.warning(request, "Result Could Not Be Updated")

        return render(request, "staff_template/edit_student_result.html", context)