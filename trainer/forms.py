from django import forms
from .models import Service, TrainerDescription, TrainerSchedule


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'category', 'price', 'level', 'duration']

    LEVEL_CHOICES = [
        ('', 'Select level'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    level = forms.ChoiceField(choices=LEVEL_CHOICES)


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