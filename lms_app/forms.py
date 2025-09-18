from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Quiz, Question, Answer
from .constants import USER_ROLES, STUDENT_ROLE


class UserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=USER_ROLES, 
        initial=STUDENT_ROLE,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'role':
                field.widget.attrs.update({'class': 'form-control'})

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role',)


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter quiz title'})
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Enter your question here...'
            })
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter answer text'
            }),
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
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                label=question.text,
                required=True
            )
    
    def clean(self):
        cleaned_data = super().clean()
        # Ensure all questions are answered
        for question in self.quiz.questions.all():
            field_name = f'question_{question.pk}'
            if not cleaned_data.get(field_name):
                raise forms.ValidationError(f"Please answer question: {question.text[:50]}...")
        return cleaned_data
