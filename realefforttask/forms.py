from django import forms
from .models import Constants



class ChooseTaskForm(forms.Form):
    task_choice = forms.IntegerField(widget=forms.RadioSelect(choices=Constants.SIZE_CHOICES))
