from django import forms
from django.utils import timezone
from .models import NGOActivity

class NGOActivityForm(forms.ModelForm):
    class Meta:
        model = NGOActivity
        fields = [
            'ngo_name', 
            'description', 
            'location', 
            'service_type', 
            'date_time', 
            'max_employees', 
            'cut_off_date'
        ]

        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'cut_off_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_max_employees(self):
        max_emp = self.cleaned_data.get('max_employees')
        if max_emp is not None and max_emp <= 0:
            raise forms.ValidationError("Maximum employees must be a positive integer.")
        return max_emp

    def clean(self):
        cleaned_data = super().clean()
        date_time = cleaned_data.get('date_time')
        cut_off_date = cleaned_data.get('cut_off_date')

        if date_time and date_time < timezone.now():
            self.add_error('date_time', "Activity date cannot be in the past.")

        if cut_off_date and date_time:
            if cut_off_date > date_time:
                self.add_error('cut_off_date', "Cut-off date must be before the activity start time.")
            
            if cut_off_date < timezone.now():
                self.add_error('cut_off_date', "Cut-off date cannot be in the past.")
        
        return cleaned_data