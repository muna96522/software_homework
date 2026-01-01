from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.contrib import messages
from .models import Subject, Staff, Student, StudentResult
from .forms import EditResultForm
from django.urls import reverse


class EditResultView(View):
    def get(self, request, *args, **kwargs):
        resultForm = EditResultForm()
        staff = get_object_or_404(Staff, admin=request.user)
        resultForm.fields['subject'].queryset = Subject.objects.filter(staff=staff)
        context = {
            'form': resultForm,
            'page_title': "Edit Student's Result"
        }
        return render(request, "staff_template/edit_student_result.html", context)

    def post(self, request, *args, **kwargs):
        form = EditResultForm(request.POST)
        staff = get_object_or_404(Staff, admin=request.user)
        # 限制教师只能编辑自己教授的科目
        form.fields['subject'].queryset = Subject.objects.filter(staff=staff)
        
        context = {'form': form, 'page_title': "Edit Student's Result"}
        if form.is_valid():
            try:
                student = form.cleaned_data.get('student')
                subject = form.cleaned_data.get('subject')
                test = form.cleaned_data.get('test')
                exam = form.cleaned_data.get('exam')
                # Validating
                result = StudentResult.objects.get(student=student, subject=subject)
                result.exam = exam
                result.test = test
                result.save()
                messages.success(request, "Result Updated")
                return redirect(reverse('edit_student_result'))
            except StudentResult.DoesNotExist:
                messages.warning(request, "成绩记录不存在，请先添加成绩")
            except Exception as e:
                messages.warning(request, f"成绩更新失败：{str(e)}")
        else:
            # 显示表单验证错误
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.warning(request, f"{form.fields[field].label}: {error}")
            else:
                messages.warning(request, "请检查表单输入")
        return render(request, "staff_template/edit_student_result.html", context)
