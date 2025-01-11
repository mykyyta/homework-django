from django import forms
from .models import Service, TrainerDescription, TrainerSchedule




class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'category', 'price', 'level', 'duration']

    level_choices = [
        ('', 'Select level'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    level = forms.ChoiceField(choices=level_choices)


class TrainerDescriptionForm(forms.ModelForm):
    class Meta:
        model = TrainerDescription
        fields = ['name']

class TrainerScheduleForm(forms.ModelForm):
    class Meta:
        model = TrainerSchedule
        fields = ['datetime_start', 'datetime_end']
        widgets = {
            'datetime_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'datetime_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }