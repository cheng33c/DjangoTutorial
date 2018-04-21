from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .models import Question, Choice

# Create your views here.

def index(request):
    ''' 展示发布日期排序的最近5个投票问题,以空格分割 '''
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

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
