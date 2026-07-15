from django import forms
from .models import HealthRecord

class HealthRecordForm(forms.ModelForm):

    class Meta:
        model = HealthRecord

        fields = [
            'age',
            'weight',
            'height',
            'blood_pressure',
            'glucose_level'
        ]