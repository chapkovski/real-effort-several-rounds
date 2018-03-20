from django import forms

SIZE_CHOICES= ((5, '5X5 matrix'), (10, '10X10 matrix'))


class ChooseTaskForm(forms.Form):
    task_choice = forms.IntegerField(widget=forms.RadioSelect(choices=SIZE_CHOICES))
