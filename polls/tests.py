import datetime

from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from .models import Question

# Create your tests here.

class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        '''
        was_published_recently() returns False for questions whose pub_date is in future
        '''
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        # future_question.was_published_recently()应该返回False
        # 因为是在未来时间发布的这个问题
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_with_old_question(self):
        '''
        was_published_recently() returns False for questions whose pub_date is older than 1 day
        '''
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        '''
        was_published_recently() return True for questions whose pub_data is within the last day
        '''
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    '''
    创建一个问题，创建时间为当前时间+days(负数表示问题在过去发布，正数表示尚未发布)
    :param question_text: 问题内容
    :param days: 从现在开始偏移的时间计算问题的创建时间
    '''
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        '''如果问题不存在,返回一个提示信息'''
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are avaliable")
        self.assertQuerysetEqual(response.context['lastest_question_list'], [])

    def test_past_questions(self):
        '''问题的pub_date是过去时间,返回问题的索引页'''
        create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], ['<Question: Past question>']
        )

    def test_future_question(self):
        '''问题的pub_date是未来时间，不会显示问题索引页'''
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        '''即使过去的问题和未来的问题同时存在,只显示过去问题'''
        create_question(question_text='Past question.', days=-30)
        create_question(question_text='Future question.', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        '''问题索引页面可能会显示多个问题。'''
        create_question(question_text='Past question 1.', days=-30)
        create_question(question_text='Past question 2.', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        '''
        The detail view of a question with a pub_date in the future return a 404 not found
        '''
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        '''
        The detail view of a question with a pub_date in the past displays the question's text
        '''
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)