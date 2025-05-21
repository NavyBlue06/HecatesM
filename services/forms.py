from django import forms
from .models import BirthChartRequest, WitchQuestion, RitualRequest, DreamSubmission, MediumContactRequest


class BirthChartRequestForm(forms.ModelForm):
    class Meta:
        model = BirthChartRequest
        fields = [
            'full_name', 'email', 'birth_date', 'birth_time', 'birth_place', 'question'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'birth_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class WitchQuestionForm(forms.ModelForm):
    class Meta:
        model = WitchQuestion
        fields = ['full_name', 'email', 'question']

class RitualRequestForm(forms.ModelForm):
    class Meta:
        model = RitualRequest
        fields = ['full_name', 'email', 'intention', 'details', 'urgency']

class DreamSubmissionForm(forms.ModelForm):
    class Meta:
        model = DreamSubmission
        fields = ['full_name', 'email', 'dream_description', 'recurring']

class MediumContactForm(forms.ModelForm):
    class Meta:
        model = MediumContactRequest
        fields = ['full_name', 'email', 'message', 'focus_area']
