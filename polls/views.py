from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Question, Choice

# Create your views here.

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        '''返回最近的5个问题(不包括那些来自未来的问题)'''
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        '''排除任何尚未发布的问题'''
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        # request.POST 是一个类字典对象，让你可以通过关键字的名字获取提交的数据。
        # request.POST['choice'] 以字符串形式返回选择的 Choice 的 ID。 request.POST 的值永远是字符串。
        # 如果在 request.POST['choice'] 数据中没有提供 choice ， POST 将引发一个 KeyError.
        # 面的代码检查 KeyError ，如果没有给出 choice 将重新显示 Question 表单和一个错误信息。
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # 重新显示投票表单
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice"
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # 在成功的接受一个POST数据后总是返回HttpResponseRedirect
        # 这样做防止数据被传输两次如果用户点击了返回按钮
        # reverse函数避免了在视图函数中硬编码的URL。
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
