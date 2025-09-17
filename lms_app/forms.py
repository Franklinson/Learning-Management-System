from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Quiz, Question, Answer


class UserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, initial='student')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role',)


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']
        widgets = {
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TakeQuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        quiz = kwargs.pop('quiz')
        super().__init__(*args, **kwargs)
        self.quiz = quiz
        for i, question in enumerate(quiz.questions.all()):
            choices = [(str(answer.pk), answer.text) for answer in question.answers.all()]
            self.fields[f'question_{question.pk}'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                label=question.text,
                required=True
            )
